import json

from llm_caller.utils.processing import extract_code_by_language
from llmedico.java_utils.java_verifier import get_compile_errors
from llmedico.java_utils.javapy import JavaParser


class ConditionValidator:
    EXPECTED_KEYS = {"description", "assertion", "name", "content"} #python set TODO get from prompt template?
    def __init__(self, language: str):
        self.language = language

    def validate(self, raw_response:str, expected_len: int) -> list[str]:
        errors = []

        # 1. Code formatting check (checking if response contains code)
        try:
            code_blocks = extract_code_by_language(raw_response, self.language)
        except RuntimeError as e:
            errors.append(str(e))
            return errors  # early exit: nothing else makes sense

        # 2. Check if code matches the right format.
        for code_block in code_blocks:
            try:
                json.loads(code_block)
            except json.JSONDecodeError as e:
                errors.append("An Error occurred while trying to load the JSON element. Make sure the output is a valid List of JSON elements with no additional commas after '{'.\n Take into account this error message: " + str(e))
                return errors #the json string does not have the right format
        #3. Check if json actually has the right format TODO check static values like name and comment
        for code_block in code_blocks:
            json_list = json.loads(code_block)
            errors = self._validate_condition_schema(json_list, expected_len)
        if errors: #has at least one error, len(errors) > 1
            return errors
        #4. Check if the assertions are valid Java assertions TODO get compiler errors
        jp = JavaParser()
        for code_block in code_blocks:
            json_list = json.loads(code_block)
            for condition in json_list:
                if not jp.is_valid_java_assert(condition["assertion"]):
                    compiler_error = get_compile_errors(condition["assertion"])
                    errors.append(f"the generated assertion {condition['assertion']} for {condition['name']} is not a valid java assertion. Use the following errors from the java compiler: {compiler_error}")
        return errors

    #TODO expected_length means #tags in the mode
    def _validate_condition_schema(self, obj, expected_len):
        errors = []
        # Must be a list
        if not isinstance(obj, list):
            return ["Top-level JSON value must be a list"]

        if expected_len is not None and len(obj) != expected_len:
            if len(obj) > expected_len:
                errors.append(
                    f"Expected exactly {expected_len} conditions, but got {len(obj)}. Remove the additional condition(s) and make sure that you generate exactly one JSON element for each tag element!"
                )
            elif len(obj) < expected_len:
                errors.append(f"Expected exactly {expected_len} conditions, but only got {len(obj)}. Generate additional condition(s) and make sure that you generate exactly one JSON element for each tag element!")

        for i, entry in enumerate(obj):
            if not isinstance(entry, dict):
                errors.append(f"Entry {i} is not a proper dictionary/json")
                continue

            keys = set(entry.keys())
            missing = self.EXPECTED_KEYS - keys
            extra = keys - self.EXPECTED_KEYS

            if missing:
                errors.append(f"Entry {i} is missing keys: {missing}")
            if extra:
                errors.append(f"Entry {i} has unexpected keys: {extra}")

            for key in self.EXPECTED_KEYS & keys:
                if not isinstance(entry[key], str):#TODO return must be null
                    if not key == "name" and not expected_len == 1:
                     errors.append(f"Entry {i} key '{key}' must be a string")
        return errors
