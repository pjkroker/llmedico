from pathlib import Path
import jpype
import jpype.imports # Enable Java imports
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
