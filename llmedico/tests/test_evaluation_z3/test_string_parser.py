import pytest

from llmedico.z3_evaluation import model_ast
from llmedico.z3_evaluation.model_ast import And, Compare, Var, IntConst, UnaryMinus, Sub, Add, Mul, BoolConst, Type, \
    NullConst, Method, Expr, Conditional, LambdaExpr
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser, ParseError

def get_ast(expression: str) -> Expr:
    normalized_expression = normalize_expression(expression)
    tokens = tokenize(normalized_expression)
    parser = StringParser(tokens)
    return parser.parse()

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

def test_parser_boolean():
    expr = normalize_expression("assert true;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    ast = parser.parse()
    assert ast == BoolConst(value=True)

    expr = normalize_expression("assert x;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    ast = parser.parse()
    assert ast == Var(name="x")

    expr = normalize_expression("assert x == true;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    ast = parser.parse()
    assert ast == Compare(left=Var(name='x'), op='==', right=BoolConst(value=True))

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

def test_typeof():
    parser = StringParser(tokenize("1"))
    ast = parser.parse()
    assert model_ast.typeof(ast) == Type.INT

    parser = StringParser(tokenize("X"))
    ast = parser.parse()
    assert model_ast.typeof(ast) == None #has to be derived in the context

    parser = StringParser(tokenize("true"))
    ast = parser.parse()
    assert model_ast.typeof(ast) == Type.BOOL

    parser = StringParser(tokenize("x >= 0"))
    ast = parser.parse()
    assert model_ast.typeof(ast) == Type.BOOL

    parser = StringParser(tokenize("x == y;"))
    ast = parser.parse()
    assert model_ast.typeof(ast) == Type.BOOL #BOOL is default, but could also be INT!!!

    parser = StringParser(tokenize("null"))
    ast = parser.parse()
    assert model_ast.typeof(ast) == Type.REF

    parser = StringParser(tokenize("null == x"))
    ast = parser.parse()
    assert ast.left == NullConst()
    assert model_ast.typeof(ast) == Type.BOOL

def test_method():
    parser = StringParser(tokenize("isValid(x)"))
    ast = parser.parse()
    assert ast == Method(receiver=None, name='isValid', parameters=[Var(name='x')])

    parser = StringParser(tokenize("isValid(x) == true"))
    ast = parser.parse()
    assert ast == Compare(left=Method(receiver=None, name='isValid', parameters=[Var(name='x')]), op='==', right=BoolConst(value=True))
    assert model_ast.typeof(ast) == Type.BOOL

    parser = StringParser(tokenize("foo(x) == x"))
    ast = parser.parse()
    assert model_ast.typeof(ast.left) == Type.REF
    assert model_ast.typeof(ast.right) == None

    parser = StringParser(tokenize("getUser(x) != null"))
    ast = parser.parse()
    assert ast == Compare(left=Method(receiver=None, name='getUser', parameters=[Var(name='x')]), op='!=', right=NullConst())

    parser = StringParser(tokenize("size(x) == 0"))
    ast = parser.parse()
    assert model_ast.typeof(ast.left) == Type.INT
    assert model_ast.typeof(ast.right) == Type.INT
    assert  model_ast.typeof(ast) == Type.BOOL

    parser = StringParser(tokenize("equals(x,y)"))
    ast = parser.parse()
    assert ast == Method(receiver=None, name='equals', parameters=[Var(name='x'), Var(name='y')])
    assert model_ast.typeof(ast) == Type.BOOL

    parser = StringParser(tokenize("x.equals(y)"))
    ast = parser.parse()
    assert ast == Method(receiver=Var(name='x'), name='equals', parameters=[Var(name='y')])

def test_ternary():
    parser = StringParser(tokenize("x>0 ? true : false"))
    ast = parser.parse()
    print(ast)
#assert args[0] instanceof org.jgrapht.Graph;
def test_ignore_cast():
    parser = StringParser(tokenize("(int)x > 0"))
    ast = parser.parse()
    assert ast == Compare(left=Var(name='x'), op='>', right=IntConst(value=0))

    parser = StringParser(tokenize("(methodResultID != null) == ((org.jgrapht.Graph)args[0]).addEdge(args[1], args[2]) != null"))
    ast = parser.parse()
    assert ast == Compare(left=Compare(left=Compare(left=Var(name='methodResultID'), op='!=', right=NullConst()), op='==', right=Method(receiver=Var(name='args[0]'), name='addEdge', parameters=[Var(name='args[1]'), Var(name='args[2]')])), op='!=', right=NullConst())

    ast = get_ast("cond ? (Type) a : (Other) b")
    assert ast == Conditional(cond=Var(name='cond'), then=Var(name='a'), otherwise=Var(name='b'))

    ast = get_ast("((Foo.Bar) y).equals(z)")
    assert ast ==  Method(receiver=Var(name='y'), name='equals', parameters=[Var(name='z')])

def test_raise_error_instanceof():
    with pytest.raises(ParseError):
        parser = StringParser(tokenize("x instanceof Graph"))
        ast = parser.parse()

def test_lamda():
    tokens = tokenize("assert list.stream().anyMatch(x -> x > 0);")
    assert tokens == ['assert', 'list', '.', 'stream', '(', ')', '.', 'anyMatch', '(', 'x', '->', 'x', '>', '0', ')']

    parser = StringParser(tokenize("x -> x > 0"))
    ast = parser.parse()
    print(ast)
    assert ast == LambdaExpr(param='x', body=Compare(left=Var(name='x'), op='>', right=IntConst(value=0)))

    parser = StringParser(tokenize("anyMatch(x -> x > 0)"))
    ast = parser.parse()
    print(ast)
    assert ast == Method(receiver=None, name='anyMatch', parameters=[LambdaExpr(param='x', body=Compare(left=Var(name='x'), op='>', right=IntConst(value=0)))])

    #"list.stream().anyMatch(x -> x > 0)"
    parser = StringParser(tokenize("list.stream().anyMatch(x -> x > 0)"))
    ast = parser.parse()
    print(ast)
    assert ast == Method(receiver=Method(receiver=Var(name='list'), name='stream', parameters=[]), name='anyMatch', parameters=[LambdaExpr(param='x', body=Compare(left=Var(name='x'), op='>', right=IntConst(value=0)))])







