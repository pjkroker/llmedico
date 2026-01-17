from llm_caller.models.ollama import Ollama
from llm_caller.utils.processing import extract_list_raw
from llmedico.translator.condition_validator import ConditionValidator
from llmedico.translator.translation_repair_loop import TranslationRepairLoop
from llmedico.translator.translator import Translator


def test_first_aid():
    raw_output = """
    Here is the corrected output:

    ```
    [{
        "description": "Returns a synchronized (thread-safe) bag backed by the given bag.",
        "assertion": "assert !methodResultID.isInstanceOf(Bag.class);",
        "name": null,
        "content": "Returns a synchronized (thread-safe) bag backed by the given bag."
    }]
    ```"""
    errors = ['No code snippets found for language json. \nMake sure the code blocks are wrapped exactly like shown in the provided example!\nInclude the code inbetween ```json and ```']
    validator = ConditionValidator("json")
    trans = Translator(Ollama("hallo"))
    repair_loop = TranslationRepairLoop(trans, validator)
    fixed = repair_loop._first_aid_repair(raw_response=raw_output, errors=errors, expected_len=1)

    corrected_string = """```json
[{
        "description": "Returns a synchronized (thread-safe) bag backed by the given bag.",
        "assertion": "assert !methodResultID.isInstanceOf(Bag.class);",
        "name": null,
        "content": "Returns a synchronized (thread-safe) bag backed by the given bag."
    }]
```"""

    assert fixed == corrected_string

    fixed = repair_loop._first_aid_repair(raw_response=raw_output, errors=["dummy"], expected_len=1)
    assert fixed is None

    raw_output_two_erros = """
        Here is the corrected output:

        ```
        [{
            "description": "Returns a synchronized (thread-safe) bag backed by the given bag.",
            "assertion": "assert !methodResultID.isInstanceOf(Bag.class)",
            "name": null,
            "content": "Returns a synchronized (thread-safe) bag backed by the given bag."
        }]
        ```"""
    errors = ['No code snippets found for language json.']
    fixed_two_erros = repair_loop._first_aid_repair(raw_response=raw_output_two_erros, errors=errors, expected_len=1)
    assert fixed_two_erros is None

def test_two_step_repair():
    raw_output ="""[
    {
        "description": "collection a must not be null",
        "assertion": "assert args[0] != null;",
        "name": "a",
        "content": "must not be null"
    },
    {
        "description": "collection b must not be null",
        "assertion": "assert args[1] != null;",
        "name": "b",
        "content": "must not be null"
    },
    {
        "description": "predicate p must not be null",
        "assertion": "assert args[2] != null;",
        "name": "p",
        "content": "must not be null"
    }
]"""

    errors = [
        'No code snippets found for language json. \nMake sure the code blocks are wrapped exactly like shown in the provided example!\nInclude the code inbetween ```json and ```']
    validator = ConditionValidator("json")
    trans = Translator(Ollama("hallo"))
    repair_loop = TranslationRepairLoop(trans, validator)
    fixed = repair_loop._first_aid_repair(raw_response=raw_output, errors=errors, expected_len=3)
    print(fixed)

    assert fixed is not  None
    assert fixed == "```json\n" + raw_output + "\n```"
