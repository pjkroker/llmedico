from llmedico.java_utils.javapy import JavaParser


"""
    As only one JVM per thread is allowed, tests have to be executed separately. Else they will fail.
"""

def test_java_parser_is_valid_assertion():
    java_parser = JavaParser()
    assert java_parser.is_valid_java_assert("assert 0 == 0;") == True
    assert java_parser.is_valid_java_assert("hallo") == False
    assert java_parser.is_valid_java_assert("assert true;") == True
    assert java_parser.is_valid_java_assert("assert false;") == True
    assert java_parser.is_valid_java_assert("assert 0====0") == False
    assert java_parser.is_valid_java_assert("assert (x==y) == false") == False
    assert java_parser.is_valid_java_assert("assert (x==y) == false;") == True
    assert java_parser.is_valid_java_assert("assert code != null;//this is a comment") == True

    assert java_parser.is_valid_java_assert("assert methodResultID == (args[0] + args[1]) / 2.0; //description: result must equal the average of a and b.") == True