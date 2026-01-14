from pathlib import Path
import jpype
import jpype.imports  # Enable Java imports
import json
import re
from jpype.types import *


class JavaPy:
    def __init__(self, classpath: Path | None = None):
        self.classpath = classpath

        if not jpype.isJVMStarted():
            if classpath:
                jpype.startJVM(classpath=[str(classpath)])
            else:
                jpype.startJVM()

    def __repr__(self):
        return self._get_classpath()

    def _get_classpath(self):
        from java.lang import System
        return str(System.getProperty("java.class.path"))

    def _shutdown(self):
        jpype.shutdownJVM()


class JavaParser(JavaPy):
    DEFAULT_CLASSPATH = Path(__file__).parent.parent.parent.parent / "data" / "jars" / "*"

    def __init__(self):
        super().__init__(self.DEFAULT_CLASSPATH)

    def is_valid_java_assert(self, code: str) -> bool:
        """
        Returns True if `code` is a valid Java assert statement (syntax only).
        """
        from com.github.javaparser import JavaParser as JP
        from com.github.javaparser.ast.stmt import AssertStmt
        from com.github.javaparser import ParseProblemException

        parser = JP()

        try:
            parse_result = parser.parseStatement(code)
            if parse_result.isSuccessful() and parse_result.getResult().isPresent():
                stmt = parse_result.getResult().get()
                return isinstance(stmt, AssertStmt)
            return False
        except ParseProblemException:
            return False

    def _get_raw_javadoc(self, node) -> str | None:
        """
        Recover raw Javadoc (/** ... */) immediately preceding a node
        by scanning the CompilationUnit token stream.
        Handles annotations, line comments, and block comments in between.
        """

        # Fast path: attached Javadoc
        if node.getJavadocComment().isPresent():
            return str(node.getJavadocComment().get().toString())

        cu = node.findCompilationUnit().orElse(None)
        if cu is None or not cu.getTokenRange().isPresent():
            return None

        if not node.getBegin().isPresent():
            return None

        node_begin = node.getBegin().get()
        tokens = list(cu.getTokenRange().get())

        # Find where the node starts
        start_index = None
        for i, tok in enumerate(tokens):
            if tok.getRange().isPresent() and tok.getRange().get().begin == node_begin:
                start_index = i
                break

        if start_index is None:
            return None

        # Walk backwards
        for tok in reversed(tokens[:start_index]):
            text = tok.getText().strip()

            # Skip whitespace
            if not text:
                continue

            # Skip annotations
            if text.startsWith("@"):
                continue

            # Skip line comments
            if text.startsWith("//"):
                continue

            # Skip non-Javadoc block comments
            if text.startsWith("/*") and not text.startsWith("/**"):
                continue

            # Found Javadoc
            if text.startsWith("/**"):
                return str(text)

            # Hit real code → stop
            break

        return None

    def _py_str(self, value):
        """Force Java strings → Python strings."""
        return str(value) if value is not None else None

    def _extract_type(self, t):
        """
        Returns a structured type model dict:
        {
          qualified_name,
          simple_name,
          is_array,
          array_dimensions
        }
        """

        # --- unwrap arrays recursively ---
        array_dimensions = 0
        while t.isArrayType():
            array_dimensions += 1
            t = t.asArrayType().getComponentType()

        is_array = array_dimensions > 0

        # --- Primitive types ---
        if t.isPrimitiveType():
            prim = str(t.asPrimitiveType().toString())
            return {
                "qualified_name": prim,
                "simple_name": prim,
                "is_array": is_array,
                "array_dimensions": array_dimensions,
            }

        # --- Reference types (classes, generics, etc.) ---
        try:
            resolved = t.resolve()

            # --- type variable (E, T, V, etc.) ---
            if resolved.isTypeVariable():
                return {
                    "qualified_name": "java.lang.Object",
                    "simple_name": "Object",
                    "is_array": is_array,
                    "array_dimensions": array_dimensions,
                }

            # --- reference type ---
            if resolved.isReferenceType():
                ref = resolved.asReferenceType()
                qualified = ref.getQualifiedName()
                simple = qualified.split(".")[-1]

                return {
                    "qualified_name": qualified,
                    "simple_name": simple,
                    "is_array": is_array,
                    "array_dimensions": array_dimensions,
                }

        except Exception:
            # --- Fallback: unresolved ---
            raw = str(t.toString())
            simple = raw.split("<")[0]
            return {
                "qualified_name": None,
                "simple_name": simple,
                "is_array": is_array,
                "array_dimensions": array_dimensions,
            }

    def _extract_parameter(self, p):
        return {
            "type": self._extract_type(p.getType()),
            "name": str(p.getNameAsString())
        }

    import re

    def _extract_javadoc_tags(self, raw_javadoc: str | None) -> list[dict]:
        """
        Extract Javadoc block tags from a raw Javadoc string.
        Returns a list of {tag, name, content}.
        """
        if not raw_javadoc:
            return []

        tags = []

        # Remove /** */ and leading *
        lines = raw_javadoc.splitlines()
        cleaned = []
        for line in lines:
            line = line.strip()
            if line.startswith("/**"):
                line = line[3:]
            if line.endswith("*/"):
                line = line[:-2]
            if line.startswith("*"):
                line = line[1:]
            cleaned.append(line.strip())

        # Regex for block tags
        tag_pattern = re.compile(r"^@(\w+)(?:\s+(\S+))?\s*(.*)")

        current = None

        for line in cleaned:
            if not line:
                continue

            m = tag_pattern.match(line)
            if m:
                # flush previous tag
                if current:
                    tags.append(current)

                tag_name = m.group(1)
                if tag_name == "exception":
                    tag_name = "throws"

                current = {
                    "tag": tag_name,
                    "name": m.group(2),
                    "content": m.group(3).strip(),
                }
                if current["tag"] == "return":
                    current["name"] = None

            else:
                # continuation of previous tag
                if current:
                    current["content"] += " " + line

        if current:
            tags.append(current)

        return tags

    def extract_to_json(self, java_file: str, jar_path: Path) -> str:
        """
        Extract classes, constructors, methods, full raw Javadoc,
        tags, and source code to JSON.
        """
        from com.github.javaparser import JavaParser as JP
        from com.github.javaparser.ast.body import ClassOrInterfaceDeclaration

        from com.github.javaparser.symbolsolver import JavaSymbolSolver
        from com.github.javaparser.symbolsolver.resolution.typesolvers import CombinedTypeSolver, ReflectionTypeSolver, JarTypeSolver

        type_solver = CombinedTypeSolver()
        type_solver.add(ReflectionTypeSolver())
        type_solver.add(JarTypeSolver(jar_path.as_posix()))

        symbol_solver = JavaSymbolSolver(type_solver)


        # parser = JP()
        # parser.getParserConfiguration().setSymbolResolver(symbol_solver)
        from com.github.javaparser import ParserConfiguration

        config = ParserConfiguration()
        config.setSymbolResolver(symbol_solver)
        config.setStoreTokens(True)


        parser = JP(config)

        file_text = Path(java_file).read_text()

        parse_result = parser.parse(file_text)
        if not parse_result.isSuccessful() or not parse_result.getResult().isPresent():
            raise ValueError(f"Could not parse Java file: {java_file}")

        cu = parse_result.getResult().get()

        package_name = None
        if cu.getPackageDeclaration().isPresent():
            package_name = str(cu.getPackageDeclaration().get().getNameAsString())

        classes = []

        for clazz in cu.findAll(ClassOrInterfaceDeclaration):

            class_name = clazz.getNameAsString()
            if package_name:
                qualified_name = f"{package_name}.{class_name}"
            else:
                qualified_name = class_name

            class_info = {
                "name": str(clazz.getName()),
                "package": package_name,
                "qualified_name": qualified_name,
                "javadoc": self._get_raw_javadoc(clazz),
                "code": str(clazz.toString()),
                "members": [],
            }

            # --------------------
            # Constructors
            # --------------------
            for ctor in clazz.getConstructors():
                # Exclude private constructors (jdoctor behavior)
                if ctor.isPrivate():
                    continue

                parameters = [
                    self._extract_parameter(p)
                    for p in ctor.getParameters()
                ]

                tags = []
                raw_javadoc = self._get_raw_javadoc(ctor)

                if ctor.getJavadoc().isPresent():
                    javadoc = ctor.getJavadoc().get()
                    for tag in javadoc.getBlockTags():
                        tag_name = str(tag.getTagName()) #normalize
                        if tag_name == "exception":
                            tag_name = "throws"
                        tags.append({
                            "tag": tag_name,
                            "name": (
                                str(tag.getName().orElse(None))
                                if tag.getName().isPresent()
                                else None
                            ),
                            "content": str(tag.getContent().toText()),
                        })

                # REFINED EXCLUSION RULE (docstring-aware)
                if not parameters and not tags:
                    has_docstring = raw_javadoc is not None and raw_javadoc.strip() != ""
                    body = ctor.getBody()

                    if not has_docstring and (body is None or body.getStatements().isEmpty()):
                        continue

                ctor_info = {
                    "type": "constructor",
                    "name": str(clazz.getName()),
                    "parameters": parameters,
                    "javadoc": raw_javadoc,
                    "tags": tags,
                    "code": str(ctor.toString()),
                }

                class_info["members"].append(ctor_info)

            # --------------------
            # Methods
            # --------------------
            for method in clazz.getMethods():
                # Exclude private methods (jdoctor behavior)
                if method.isPrivate():
                    continue

                method_info = {
                    "type": "method",
                    "name": str(method.getName()),
                    "return_type": self._extract_type(method.getType()),
                    "parameters": [
                        self._extract_parameter(p)
                        for p in method.getParameters()
                    ],
                    "javadoc": self._get_raw_javadoc(method),
                    "tags": [],
                    "code": str(method.toString()),
                }

                raw_javadoc = self._get_raw_javadoc(method)

                method_info = {
                    "type": "method",
                    "name": str(method.getName()),
                    "return_type": self._extract_type(method.getType()),
                    "parameters": [
                        self._extract_parameter(p)
                        for p in method.getParameters()
                    ],
                    "javadoc": raw_javadoc,
                    "tags": self._extract_javadoc_tags(raw_javadoc),
                    "code": str(method.toString()),
                }

                class_info["members"].append(method_info)

            classes.append(class_info)

        return json.dumps(classes, indent=2)
