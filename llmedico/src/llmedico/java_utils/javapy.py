from pathlib import Path
import jpype
import jpype.imports # Enable Java imports
import json
from jpype.types import *
from abc import ABC, abstractmethod

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
    DEFAULT_CLASSPATH = Path("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/jars/javaparser-core-3.27.1.jar") #TODO

    def __init__(self):
        super().__init__(self.DEFAULT_CLASSPATH)

    def is_valid_java_assert(self, code: str) -> bool:
        """
        Returns True if `code` is a valid Java assert statement. Syntax!!
        """
        #the following code gets executed by the JVM
        from com.github.javaparser import JavaParser as JP
        from com.github.javaparser.ast.stmt import AssertStmt
        from com.github.javaparser import ParseProblemException

        parser = JP()  # You can make this a class-level static parser if you want

        try:
            parse_result = parser.parseStatement(code)
            # Check if parsing was successful
            if parse_result.isSuccessful() and parse_result.getResult().isPresent():
                stmt = parse_result.getResult().get()
                return isinstance(stmt, AssertStmt)
            else:
                return False
        except ParseProblemException:
            return False


    def extract_to_json(self, java_file: str) -> str:
        """
        Extract classes, methods, full javadoc, tags, and actual source code to JSON.
        """
        import json
        from pathlib import Path
        from com.github.javaparser import JavaParser as JP
        from com.github.javaparser.ast.body import MethodDeclaration, ClassOrInterfaceDeclaration

        parser = JP()
        file_text = str(Path(java_file).read_text())

        parse_result = parser.parse(file_text)

        if not parse_result.isSuccessful() or not parse_result.getResult().isPresent():
            raise ValueError(f"Could not parse Java file: {java_file}")

        cu = parse_result.getResult().get()

        classes = []

        for clazz in cu.findAll(ClassOrInterfaceDeclaration):
            class_info = {
                "name": str(clazz.getName()),
                "javadoc": str(clazz.getJavadoc().get().toText()) if clazz.getJavadoc().isPresent() else None,
                "code": str(clazz.toString()),  # the full class code
                "methods": []
            }

            for method in clazz.getMethods():
                method_info = {
                    "name": str(method.getName()),
                    "returnType": str(method.getType().toString()),
                    "parameters": [str(f"{p.getType().toString()} {p.getNameAsString()}") for p in
                                   method.getParameters()],
                    "javadoc": str(method.getJavadoc().get().toText()) if method.getJavadoc().isPresent() else None,
                    "tags": [],
                    "code": str(method.toString())  # actual method code
                }

                if method.getJavadoc().isPresent():
                    javadoc = method.getJavadoc().get()
                    for tag in javadoc.getBlockTags():
                        method_info["tags"].append({
                            "tag": str(tag.getTagName()),
                            "name": str(tag.getName().orElse(None)) if tag.getName().isPresent() else None,
                            "content": str(tag.getContent().toText())
                        })

                class_info["methods"].append(method_info)

            classes.append(class_info)

        return json.dumps(classes, indent=2)



