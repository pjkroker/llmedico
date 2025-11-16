from llm_caller.utils.processing import extract_code_by_language

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
    #print(extract_code_by_language(code, "java"))
    assert extract_code_by_language(code,"java")[0] == 'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n        }\n    }'
    assert extract_code_by_language(code, "java")[0] == """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
        }
    }"""