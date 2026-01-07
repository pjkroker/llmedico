from llm_caller.utils.processing import extract_code_by_language
from llmedico.translator.condition_validator import ConditionValidator


def test_condition_translator():
    raw_response = """Here are the Java assertion statements generated from the Javadoc and input parameters:
    ```jso
    [{"description": "if the specified prevPathElementList or edge is null.",
    "assertion": "assert args[2]==null || args[3]==null;",
    "name": "NullPointerException"},
    {description="if maxSize is negative or 0.",
    "assertion": "assert args[1]<0 || args[1]==0;",
    "name": "IllegalArgumentException"}]
    ```
    """
    validator = ConditionValidator("json")
    assert validator.validate(raw_response, 2)[0].startswith("No code snippets found for language json.")
    raw_response = """Here are the Java assertion statements generated from the Javadoc and input parameters:
        ```json
        {"description": "if the specified prevPathElementList or edge is null.",
        "assertion": "assert args[2]==null || args[3]==null;",
        "name": "NullPointerException"},
        {"description": "if maxSize is negative or 0.",
        "assertion": "assert args[1]<0 || args[1]==0;",
        "name": "IllegalArgumentException"}]
        ```
        """
    print(validator.validate(raw_response, 2))
    assert validator.validate(raw_response, 2)[0].endswith("Extra data: line 3 column 40 (char 175)")
    raw_response = """Here are the Java assertion statements generated from the Javadoc and input parameters:
            ```json
            [{"description": "if the specified prevPathElementList or edge is null.",
            "assertion": "assert args[2]==null || args[3]==null;",
            "name": "NullPointerException"},
            {description": "if maxSize is negative or 0.",
            "assertion": "assert args[1]<0 || args[1]==0;",
            "name": "IllegalArgumentException"}]
            ```
            """
    assert validator.validate(raw_response, 2)[0].endswith("Expecting property name enclosed in double quotes: line 4 column 14 (char 199)")
    raw_response = """Here are the Java assertion statements generated from the Javadoc and input parameters:
                ```json
                [{"assertion": "assert args[2]==null || args[3]==null;",
                "name": "NullPointerException"},
                {"description": "if maxSize is negative or 0.",
                "assertion": "assert args[1]<0 || args[1]==0;",
                "name": "IllegalArgumentException"}]
                ```
                """
    assert validator.validate(raw_response, 2)[0].startswith("Entry 0 is missing keys: ")
    raw_response = """Here are the Java assertion statements generated from the Javadoc and input parameters:
                ```json
                [{"description": "if the specified prevPathElementList or edge is null.",
                "assertion": "assert args[2]==null || args[3]==null;",
                "name": "NullPointerException",
                "content": "test"},
                {"description": "if maxSize is negative or 0.",
                "assertion": "assertt args[1]<0 || args[1]==0;",
                "name": "IllegalArgumentException",
                "content": "test"}]
                ```
                """
    assert validator.validate(raw_response, 2)[0].startswith("the generated assertion")
    raw_response = """Here are the Java assertion statements generated from the Javadoc and input parameters:
                    ```json
                    [{"description": "if the specified prevPathElementList or edge is null.",
                    "assertion": "assert args[2]==null || args[3]==null;",
                    "name": "NullPointerException",
                    "content": "test"},
                    {"description": "if maxSize is negative or 0.",
                    "assertion": "assert args[1]<0 || args[1]==0;",
                    "name": "IllegalArgumentException",
                    "content": "test"}]
                    ```
                    """
    assert validator.validate(raw_response, 2) == []

def test_condition_validator_2_codeblocks():
    raw_response = """```json
    [
      {
        "description": "v must not be null",
        "assertion": "assert args[0] != null;",
        "name": "v",
        "content": "vertex to be added to this graph."
      },
      {
        "description": "this graph contains no vertex u such that u.equals(v)",
        "assertion": "assert !receiverObjectID.contains(args[0]);",
        "name": "v",
        "content": "More formally, adds the specified vertex, <code>v</code>, to this graph if this graph contains no vertex <code>u</code> such that <code> u.equals(v)</code>."
      }
    ]
    ```

    However, as per the feedback, I will remove one condition from the output. Since the first condition "v must not be null" is explicitly stated in the documentation, I will keep it and remove the second condition.

    Here is the corrected JSON:

    ```json
    [
      {
        "description": "v must not be null",
        "assertion": "assert args[0] != null;",
        "name": "v",
        "content": "vertex to be added to this graph."
      }
    ]
    ```

    """
    assert len(extract_code_by_language(raw_response, "json")) == 2
    validator = ConditionValidator("json")
    validator.validate(raw_response, 1)
    assert validator.validate(raw_response, 1)[0].startswith("Found more than one block of JSON elements.")







