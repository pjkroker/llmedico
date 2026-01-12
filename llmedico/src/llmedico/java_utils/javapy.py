from pathlib import Path
import jpype
import jpype.imports  # Enable Java imports
import json
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
        Returns the full raw Javadoc including /** and */ if present.
        """
        if node.getJavadocComment().isPresent():
            return str(node.getJavadocComment().get().toString())
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


        parser = JP()
        parser.getParserConfiguration().setSymbolResolver(symbol_solver)
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

                # REFINED EXCLUSION RULE
                if not parameters and not tags:
                    body = ctor.getBody()
                    if body is None or body.getStatements().isEmpty():
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

                if method.getJavadoc().isPresent():
                    javadoc = method.getJavadoc().get()
                    for tag in javadoc.getBlockTags():
                        tag_name = str(tag.getTagName())
                        if tag_name == "exception": #normalize
                            tag_name = "throws"
                        method_info["tags"].append({
                            "tag": tag_name,
                            "name": (
                                str(tag.getName().orElse(None))
                                if tag.getName().isPresent()
                                else None
                            ),
                            "content": str(tag.getContent().toText()),
                        })

                class_info["members"].append(method_info)

            classes.append(class_info)

        return json.dumps(classes, indent=2)
