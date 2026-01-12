import json
import pathlib
from pathlib import Path
from pprint import pprint

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

def test_java_parser_empty_constructor():
    empty_constructor_example = {
        "type": "constructor",
        "name": "FunctionUtils",
        "parameters": [],
        "javadoc": "/**\n * Class only contains static methods.\n */\n",
        "tags": [],
        "code": "/**\n * Class only contains static methods.\n */\nprivate FunctionUtils() {\n}"
      }
    jp = JavaParser()
    jar_path = Path(__file__).parent.parent / "data" / "input" / "commons-math3-3.6.1.jar"
    java_file = Path(__file__).parent.parent / "data" / "input" / "FunctionUtils.java"

    result_str = jp.extract_to_json(java_file, jar_path)
    result_json = json.loads(result_str)

    assert empty_constructor_example != result_json[0]["members"][0]

    #but not all empty constructors
    jar_path = Path(__file__).parent.parent / "data" / "input" / "commons-collections4-4.1.jar"
    java_file = Path(__file__).parent.parent / "data" / "input" / "ArrayStack.java"

    result_str = jp.extract_to_json(java_file, jar_path)
    result_json = json.loads(result_str)

    assert result_json[0]["members"][0]["name"] == "ArrayStack"
    assert result_json[0]["members"][0]["type"] == "constructor"
    assert result_json[0]["members"][0]["parameters"] == []
    assert result_json[0]["members"][0]["tags"] == []

def test_java_extractor_parameter_bug():
    jp = JavaParser()
    jar_path = Path(__file__).parent.parent / "data" / "input" / "commons-collections4-4.1.jar"
    java_file = Path(__file__).parent.parent / "data" / "input" / "BivariateGridInterpolator.java"
    result_str = jp.extract_to_json(java_file, jar_path)
    result_json = json.loads(result_str)

    assert result_json[0]["members"][0]["parameters"][2]["type"]["array_dimensions"] == 2



