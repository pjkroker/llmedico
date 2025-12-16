from platform import java_ver
from pprint import pprint

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator, ToradocuCondition


def test_translator():
    translator = Translator()
    javadoc = """/**
     * Computes the average of two integers.
     *
     * <p>This method takes two integer values, adds them, and divides the result by two to compute
     * their arithmetic mean. The result is returned as a double to preserve fractional precision.
     *
     * @param a the first integer value
     * @param b the second integer value
     * @return the average of {@code a} and {@code b} as a double
     */
    """
    java_assertions = translator.translate_javadoc(javadoc,modes={"param","return"})
    jp = JavaParser()
    for mode in java_assertions:
        print("mode: ", mode)
        for assertion in java_assertions[mode]:
            print("assertion: ", assertion)
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

def test_translator_toradocu_condition():
    assertion = 'assert args[0] > 1; //description: n must be greater than 1'
    condition = ToradocuCondition(assertion, "PARAM")
    assert condition.to_dict() == {"comment": "n must be greater than 1",
                                  "kind": "PARAM",
                                  "condition": "args[0] > 1"}
