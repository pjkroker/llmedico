from platform import java_ver
from pprint import pprint

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator


def test_translator():
    translator = Translator()
    java_assertions = translator.translate_javadoc("Checks whether a string is a valid Java assert statement.\n\n@param code the string to test\n@return true if valid, false otherwise\n")
    jp = JavaParser()
    for assertion in java_assertions:
        assert jp.is_valid_java_assert(assertion)

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
