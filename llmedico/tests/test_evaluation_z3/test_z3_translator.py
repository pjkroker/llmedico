import z3
import pytest
from z3 import IntVal, BoolVal

from llmedico.z3_evaluation.model_ast import And, Compare, Var, IntConst, Add, UnaryMinus, BoolConst, Not, Type
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_context import Z3Context
from llmedico.z3_evaluation.z3_translator import Z3Translator



def infer(expr_str):
    tokens = tokenize(expr_str)
    ast = StringParser(tokens).parse()
    tr = Z3Translator()
    tr.translate(ast)
    return tr.var_types

def test_type_conflict_detected():
    with pytest.raises(TypeError):
        infer("x == 0 && x == true")

def test_consistent_variable_types():
    types = infer("x == 0 && x > -1")
    assert types["x"] == Type.INT

def test_y_equals_true_infers_bool():
    types = infer("y == true")
    assert types["y"] == Type.BOOL

def test_x_equals_zero_infers_int():
    types = infer("x == 0")
    assert types["x"] == Type.INT

def test_translator_equality():
    parser = StringParser(tokenize("x == 0"))
    logic_ast = parser.parse()

    trans = Z3Translator()
    z3_expr = trans.translate(logic_ast)
    assert type(z3_expr) == z3.z3.BoolRef
    assert z3_expr.__repr__() == "0 == x"

def test_types():
    trans = Z3Translator()

    parser = StringParser(["1"])
    logic_ast = parser.parse()
    z3_expr = trans.translate(logic_ast)
    assert z3_expr == IntVal(1)

    parser = StringParser(["true"])
    logic_ast = parser.parse()
    z3_expr = trans.translate(logic_ast)
    assert z3_expr == BoolVal(True)

def test_translator_full():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    logic_ast = parser.parse()

    trans = Z3Translator()
    z3_expr = trans.translate(logic_ast)

    assert type(z3_expr) == z3.z3.BoolRef
    assert z3_expr.__repr__() == "And(0 <= x, 10 >= x)"

def test_translator_arithmetic():
    ast = Add(left=UnaryMinus(expr=IntConst(value=1)), right=IntConst(value=2))

    trans = Z3Translator()
    z3_expr = trans.translate(ast)
    assert type(z3_expr) == z3.z3.ArithRef

    ast = Compare(left=Var(name="x"), op=">", right=Add(left=Var(name='y'), right=IntConst(value=1)))
    trans = Z3Translator()
    z3_expr = trans.translate(ast)
    assert type(z3_expr) == z3.z3.BoolRef

def test_translator_bool():
    ast = BoolConst(value=True)
    trans = Z3Translator()
    z3_expr = trans.translate(ast)
    assert type(z3_expr) == z3.z3.BoolRef

    parser = StringParser(tokenize("true"))
    z3_expr = trans.translate(parser.parse())
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = trans.translate(Not(BoolConst(value=False)))
    assert type(z3_expr) == z3.z3.BoolRef
    assert z3_expr == z3.Not(False)
