from platform import java_ver

from llmedico.java_utils.javapy import JavaParser
from llmedico.java_utils.translator.translator import Translator


def test_translator():
    translator = Translator()
    java_assertions = translator.translate_javadoc("Checks whether a string is a valid Java assert statement.\n\n@param code the string to test\n@return true if valid, false otherwise\n")
    jp = JavaParser()
    for assertion in java_assertions:
        assert jp.is_valid_java_assert(assertion)
