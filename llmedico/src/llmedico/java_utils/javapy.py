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
    DEFAULT_CLASSPATH = Path(
        "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/jars/javaparser-core-3.27.1.jar"
    )

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

    def extract_to_json(self, java_file: str) -> str:
        """
        Extract classes, constructors, methods, full raw Javadoc,
        tags, and source code to JSON.
        """
        from com.github.javaparser import JavaParser as JP
        from com.github.javaparser.ast.body import ClassOrInterfaceDeclaration

        parser = JP()
        file_text = Path(java_file).read_text()

        parse_result = parser.parse(file_text)
        if not parse_result.isSuccessful() or not parse_result.getResult().isPresent():
            raise ValueError(f"Could not parse Java file: {java_file}")

        cu = parse_result.getResult().get()
        classes = []

        for clazz in cu.findAll(ClassOrInterfaceDeclaration):
            class_info = {
                "name": str(clazz.getName()),
                "javadoc": self._get_raw_javadoc(clazz),
                "code": str(clazz.toString()),
                "members": [],
            }

            # --------------------
            # Constructors
            # --------------------
            for ctor in clazz.getConstructors():
                ctor_info = {
                    "type": "constructor",
                    "name": str(clazz.getName()),
                    "parameters": [
                        f"{p.getType().toString()} {p.getNameAsString()}"
                        for p in ctor.getParameters()
                    ],
                    "javadoc": self._get_raw_javadoc(ctor),
                    "tags": [],
                    "code": str(ctor.toString()),
                }

                if ctor.getJavadoc().isPresent():
                    javadoc = ctor.getJavadoc().get()
                    for tag in javadoc.getBlockTags():
                        ctor_info["tags"].append({
                            "tag": str(tag.getTagName()),
                            "name": (
                                str(tag.getName().orElse(None))
                                if tag.getName().isPresent()
                                else None
                            ),
                            "content": str(tag.getContent().toText()),
                        })

                class_info["members"].append(ctor_info)

            # --------------------
            # Methods
            # --------------------
            for method in clazz.getMethods():
                method_info = {
                    "type": "method",
                    "name": str(method.getName()),
                    "returnType": str(method.getType().toString()),
                    "parameters": [
                        f"{p.getType().toString()} {p.getNameAsString()}"
                        for p in method.getParameters()
                    ],
                    "javadoc": self._get_raw_javadoc(method),
                    "tags": [],
                    "code": str(method.toString()),
                }

                if method.getJavadoc().isPresent():
                    javadoc = method.getJavadoc().get()
                    for tag in javadoc.getBlockTags():
                        method_info["tags"].append({
                            "tag": str(tag.getTagName()),
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
