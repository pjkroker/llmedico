from llmedico.z3_evaluation.model_ast import And, Compare, Var, IntConst, UnaryMinus, Sub, Add, Mul
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser


def test_parser():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    ast = parser.parse()
    assert ast == And(left=Compare(left=Var(name='x'), op='>=', right=IntConst(value=0)),
                      right=Compare(left=Var(name='x'), op='<=', right=IntConst(value=10)))

def test_parser_complex_arithmetic():
    expr = normalize_expression("assert x >= -(5-10);")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    ast = parser.parse()
    assert ast == Compare(left=Var(name='x'), op='>=', right=UnaryMinus(expr=Sub(left=IntConst(value=5), right=IntConst(value=10))))

def test_precedence():
    parser = StringParser(tokenize("-1 + 2"))
    ast = parser.parse()
    assert ast == Add(left=UnaryMinus(expr=IntConst(value=1)), right=IntConst(value=2))

    parser = StringParser(tokenize("-(1 + 2)"))
    ast = parser.parse()
    assert ast == UnaryMinus(expr=Add(left=IntConst(value=1), right=IntConst(value=2)))

    parser = StringParser(tokenize("2 + 3 * 4"))
    ast = parser.parse()
    assert ast == Add(left=IntConst(value=2), right=Mul(left=IntConst(value=3), right=IntConst(value=4)))

    parser = StringParser(tokenize("a*-b"))
    ast = parser.parse()
    assert ast == Mul(left=Var(name='a'), right=UnaryMinus(expr=Var(name='b')))

    parser = StringParser(tokenize("x > y + 1"))
    ast = parser.parse()
    assert ast == Compare(left=Var(name="x"), op=">", right=Add(left=Var(name='y'), right=IntConst(value=1)))
