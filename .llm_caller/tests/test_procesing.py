import pytest

from llm_caller.utils.processing import extract_code_by_language, extract_java_assertions


def test_extract_code():
    code = """
    ```java
    public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
        }
    }
    ```
    """
    assert extract_code_by_language(code, "java")[0] == 'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n        }\n    }'
    assert extract_code_by_language(code, "java")[0] == """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
        }
    }"""

    code = """
    public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
        }
    }
    ```
    """
    with pytest.raises(RuntimeError):
        extract_code_by_language(code, "java")


    code = "```json\n```"
    assert extract_code_by_language(code, "json")[0] == ''

    code = "```json\n[]\n```"


    assert extract_code_by_language(code, "json")[0] == "[]"


def test_extract_java_assertions():
    llm_response = """
    ```java
    assert args[0] != null; //description: a must not be null
    assert args[1] != null; //description: b must not be null
    ```
    """
    java_assertions = extract_java_assertions(llm_response)
    assert len(java_assertions) == 2
    assert java_assertions[0] == 'assert args[0] != null; //description: a must not be null'
    assert java_assertions[1] == 'assert args[1] != null; //description: b must not be null'