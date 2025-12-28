import pathlib
from pathlib import Path

from llmedico.java_utils.javapy import JavaPy, JavaParser
from se_helpers.files.files import save_json_to_file

"""
    As only one JVM per thread is allowed, tests have to be executed separately. Else they will fail.
"""

def test_java_parser_extractor():
    jp = JavaParser()
    jar_path = Path(__file__).parent.parent / "data" / "input" / "test-project" / "target" / "assertion-parser-1.0-SNAPSHOT.jar"
    java_file = Path(__file__).parent.parent / "data" / "input" / "test-project" / "src" / "main" / "java" / "com" / "example" / "assertions" / "TestJavaAssertion.java"
    result_json = jp.extract_to_json(java_file, jar_path)
    output_file = Path(__file__).parent.parent / "data" / "output" / "results.json"
    save_json_to_file(result_json,output_file)
    assert output_file.exists(), f"File not found: {output_file.absolute()}"



