from llmedico.java_utils.javapy import JavaPy

"""
    As only one JVM per thread is allowed, tests have to be executed separately. Else they will fail.
"""

def test_javapy():
    java_VM = JavaPy()
    assert "org.jpype.jar" in java_VM.__repr__()