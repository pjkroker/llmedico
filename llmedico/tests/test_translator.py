import json
from platform import java_ver
from pprint import pprint
from typing import List

from llm_caller.models.ollama import Ollama
from llm_caller.utils.processing import extract_conditions
from llmedico.java_utils.javapy import JavaParser
from llmedico.translator.translator import Translator, ToradocuCondition


# def test_translator():
#     translator = Translator(Ollama("llama3.1"))
#     javadoc = """/**
#      * Returns a {@code Complex} whose value is
#      * {@code (this + addend)}.
#      * Uses the definitional formula
#      * <p>
#      *   {@code (a + bi) + (c + di) = (a+c) + (b+d)i}
#      * </p>
#      * If either {@code this} or {@code addend} has a {@code NaN} value in
#      * either part, {@link #NaN} is returned; otherwise {@code Infinite}
#      * and {@code NaN} values are returned in the parts of the result
#      * according to the rules for {@link java.lang.Double} arithmetic.
#      *
#      * @param  addend Value to be added to this {@code Complex}.
#      * @return {@code this + addend}.
#      * @throws NullArgumentException if {@code addend} is {@code null}.
#      */
#     """
#     parameters = ["Complex addend"] #todo make same layout as in real prompt
#     java_assertions = translator.translate_javadoc(javadoc,parameters, modes={"PARAM": 1,"RETURN": 1, "THROWS": 1})
#     jp = JavaParser()
#     for mode in java_assertions:
#         print("mode: ", mode)
#         for assertion in java_assertions[mode]:
#             print("assertion: ", assertion["assertion"])
#             assert jp.is_valid_java_assert(assertion["assertion"])

def test_translator_pre_assertion_to_json():
    #translator = Translator()
    # java_assertions = translator.translate_javadoc("""/**
    #  * <p>Checks if a CharSequence is not empty ("") and not null.</p>
    #  *
    #  * <pre>
    #  * StringUtils.isNotEmpty(null)      = false
    #  * StringUtils.isNotEmpty("")        = false
    #  * StringUtils.isNotEmpty(" ")       = true
    #  * StringUtils.isNotEmpty("bob")     = true
    #  * StringUtils.isNotEmpty("  bob  ") = true
    #  * </pre>
    #  *
    #  * @param cs  the CharSequence to check, may be null
    #  * @return {@code true} if the CharSequence is not empty and not null
    #  * @since 3.0 Changed signature from isNotEmpty(String) to isNotEmpty(CharSequence)
    #  */""")
    java_assertions = ['assert cs != null; //description: the CharSequence must not be null', 'assert !cs.isEmpty(); //description: the CharSequence must not be empty', 'assert cs != null && !cs.isEmpty(); //description: the CharSequence must not be null and not empty']
    jsons = []
    for assertion in java_assertions:
        jsons.append(Translator.assertion_to_json(assertion))
    assert jsons[0] == {'description': 'the CharSequence must not be null', 'guard': {'condition': 'cs != null', 'description': 'the CharSequence must not be null'}}
    assert jsons[1] == {'description': 'the CharSequence must not be empty', 'guard': {'condition': '!cs.isEmpty()', 'description': 'the CharSequence must not be empty'}}
    assert jsons[2] == {'description': 'the CharSequence must not be null and not empty', 'guard': {'condition': 'cs != null && !cs.isEmpty()', 'description': 'the CharSequence must not be null and not empty'}}

def test_translator_toradocu_condition():
    assertion = 'assert args[0] > 1; //description: n must be greater than 1'
    condition = ToradocuCondition(assertion, "PARAM")
    assert condition.to_dict() == {"comment": "n must be greater than 1",
                                  "kind": "PARAM",
                                  "condition": "args[0] > 1"}

def test_extract_conditions():
    raw_response = """```json
    [
        {"description": "maxSize must be positive",
        "assertion": "assert args[0] > 0;",
        "name": "maxSize"},
        {"description": "elementList cannot be null",
        "assertion": "assert args[1] != null;",
        "name": "elementList"},
        {"description": "edge cannot be null",
        "assertion": "assert args[2] != null;",
        "name": "edge"}
    ]
    ```"""
    condition = extract_conditions(raw_response)

    assert condition == [{"description": "maxSize must be positive","assertion": "assert args[0] > 0;","name": "maxSize"},
                        {"description": "elementList cannot be null","assertion": "assert args[1] != null;", "name": "elementList"},
                        {"description": "edge cannot be null", "assertion": "assert args[2] != null;","name": "edge"}]

    assert type(condition) == list
    assert condition[0]["assertion"] == "assert args[0] > 0;"
    assert condition[2]["assertion"] == "assert args[2] != null;"