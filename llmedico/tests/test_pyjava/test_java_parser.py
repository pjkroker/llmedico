from llmedico.java_utils.javapy import JavaParser


"""
    As only one JVM per thread is allowed, tests have to be executed separately. Else they will fail.
"""

def test_java_parser():
    java_parser = JavaParser()
    assert "javaparser-core-3.27.1.jar" in java_parser.__repr__()