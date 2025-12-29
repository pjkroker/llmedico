import z3

from llmedico.z3_evaluation.model_ast import And, Compare, Var, IntConst
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_context import Z3Context
from llmedico.z3_evaluation.z3_translator import Z3Translator

def test_normalize_expression():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    assert expr == "x >= 0 && x <= 10"

def test_tokenizer():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    assert tokens == ["x", ">=", "0", "&&" ,"x", "<=", "10"]

def test_parser():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    ast = parser.parse()
    assert ast == And(left=Compare(left=Var(name='x'), op='>=', right=IntConst(value=0)),
                      right=Compare(left=Var(name='x'), op='<=', right=IntConst(value=10)))


def test_translator_mini():
    parser = StringParser(tokenize("x >= 0"))
    logic_ast = parser.parse()

    trans = Z3Translator()
    z3_expr = trans.translate(logic_ast)
    assert type(z3_expr) == z3.z3.BoolRef
    assert z3_expr.__repr__() == "0 <= x"

def test_translator_full():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    logic_ast = parser.parse()

    trans = Z3Translator()
    z3_expr = trans.translate(logic_ast)

    assert type(z3_expr) == z3.z3.BoolRef
    assert z3_expr.__repr__() == "And(0 <= x, 10 >= x)"
