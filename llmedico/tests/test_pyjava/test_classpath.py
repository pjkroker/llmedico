from pathlib import Path

from llmedico.java_utils.javapy import JavaPy

"""
    As only one JVM per thread is allowed, tests have to be executed separately. Else they will fail.
"""

def test_pyjava_classpath():
    java_parser = JavaPy([Path("../data/jars/javaparser-core-3.27.1.jar")])
    assert "javaparser-core-3.27.1.jar" in java_parser.__repr__()