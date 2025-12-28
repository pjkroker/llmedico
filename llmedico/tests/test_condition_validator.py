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
    assert validator.validate(raw_response, 2)[0].endswith("is not a valid java assertion")
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






