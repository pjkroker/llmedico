from pathlib import Path

from llmedico.java_utils.javapy import JavaPy, JavaParser

"""
    As only one JVM per thread is allowed, tests have to be executed separately. Else the will fail.
"""

def test_javapy():
    java_VM = JavaPy()
    assert "org.jpype.jar" in java_VM.__repr__()

def test_javapy_classpath():
    java_parser = JavaPy(Path("../data/jars/javaparser-core-3.27.1.jar"))
    assert "javaparser-core-3.27.1.jar" in java_parser.__repr__()

def test_java_parser():
    java_parser = JavaParser()
    assert "javaparser-core-3.27.1.jar" in java_parser.__repr__()

def test_java_parser_is_valid_assertion():
    java_parser = JavaParser()
    assert java_parser.is_valid_java_assert("assert 0 == 0;") == True
    assert java_parser.is_valid_java_assert("hallo") == False
    assert java_parser.is_valid_java_assert("assert true;") == True
    assert java_parser.is_valid_java_assert("assert false;") == True
    assert java_parser.is_valid_java_assert("assert 0====0") == False
    assert java_parser.is_valid_java_assert("assert (x==y) == false") == False
    assert java_parser.is_valid_java_assert("assert (x==y) == false;") == True


