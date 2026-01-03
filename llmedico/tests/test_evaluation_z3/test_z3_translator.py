import z3
import pytest
from z3 import IntVal, BoolVal

from llmedico.z3_evaluation.model_ast import And, Compare, Var, IntConst, Add, UnaryMinus, BoolConst, Not, Type, Method
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_context import Z3Context
from llmedico.z3_evaluation.z3_translator import Z3Translator


def translate_expression(expr: str):
    parser = StringParser(tokenize(expr))
    logic_ast = parser.parse()

    trans = Z3Translator()
    z3_expr = trans.translate(logic_ast)
    return z3_expr

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

def test_division():
    types = infer("x / 2 > 0")
    assert types["x"] == Type.INT

def test_modulo():
    types = infer("x % 2 == 0")
    assert types["x"] == Type.INT

def test_bool_division_rejected():
    with pytest.raises(TypeError):
        infer("true / x == 1")

def test_bool_division_rejected_2():
    with pytest.raises(TypeError):
        infer("true / x")

def test_bool_multiplication_rejected_2():
    with pytest.raises(TypeError):
        infer("true * x")

def test_modulo_bool_rejected():
    with pytest.raises(TypeError):
        infer("true % 2 == 0")

def test_minus_bool_rejected():
    with pytest.raises(TypeError):
        infer("-true  == 0")

def test_not_integer_rejected():
    with pytest.raises(TypeError):
        infer("!1 == 0")


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

def test_ref_not_null():
    types = infer("x != null")
    assert types["x"] == Type.REF

def test_obj_not_null():
    types = infer("obj != null")
    assert types["obj"] == Type.REF

# def test_null_int_comparison_rejected():
#     with pytest.raises(TypeError):
#         infer("x > null")
#
# def test_null_boolean_rejected():
#     with pytest.raises(TypeError):
#         infer("true == null")

def test_methods():
    types = infer("isValid(x) == true")
    assert types["x"] == Type.REF

    types = infer("isValid(x) == y")
    assert types["x"] == Type.REF
    assert types["y"] == Type.BOOL

    types = infer("foo(x) == foo(y)")
    assert types["x"] == Type.REF
    assert types["y"] == Type.REF


    z3_expr = translate_expression("getUser(x)")
    assert type(z3_expr) == z3.z3.ExprRef

    z3_expr = translate_expression("getUser(x) != null")
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("equals(x,y)")
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("x.equals(y)")
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("0 > size(x)")
    assert type(z3_expr) == z3.z3.BoolRef

def test_terniary():
    z3_expr = translate_expression("x > y ? true : false")
    assert type(z3_expr) == z3.z3.BoolRef
    types = infer("x < y ? true : false")
    assert types == {'x': Type.INT, 'y': Type.INT}

def test_llmedico_examples():
    z3_expr = translate_expression("args[0] != null")
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("args[3] >= 0")
    assert type(z3_expr) == z3.z3.BoolRef

    #use as feedback in generation  loop
    # z3_expr = translate_expression("methodResultID == null ? methodResultID : (methodResultID != null && ((org.jgrapht.Graph)args[0]).containsEdge(((java.lang.Object)args[1]), ((java.lang.Object)args[2])))")
    # assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("methodResultID == true")
    assert type(z3_expr) == z3.z3.BoolRef

    #not supported
    # z3_expr = translate_expression("args[0] instanceof org.jgrapht.Graph")
    # assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("!Double.isNaN(args[3])")
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("methodResultID == null ? (g.containsKey(sourceVertex) && g.containsKey(targetVertex)) : true")
    assert type(z3_expr) == z3.z3.BoolRef

    #not supported
    # z3_expr = translate_expression("!(args[0] instanceof java.util.Observable)")
    # assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("methodResultID == (args[0].getVertexCount() != args[1].getVertexCount()) || (args[0].getEdgeSet().size() != args[1].getEdgeSet().size())")
    assert type(z3_expr) == z3.z3.BoolRef
    #lambda is no first oder logic, rewrite or reject
    # z3_expr = translate_expression("args[1].stream().anyMatch(v -> v == null) || args[0] == null")
    # assert type(z3_expr) == z3.z3.BoolRef

    #<> is the problem --> gets ignored like casts
    z3_expr = translate_expression("methodResultID != null && ((org.jgrapht.graph.DirectedGraph<? extends org.jgrapht.graph.DefaultEdge>) args[0]).getSuccessors(args[1]) == methodResultID")
    assert type(z3_expr) == z3.z3.BoolRef

    z3_expr = translate_expression("methodResultID == ((org.jgrapht.Graph)args[0]).containsEdge((java.lang.Object)args[1], (java.lang.Object)args[2])")
    assert type(z3_expr) == z3.z3.BoolRef


    #args[3] >= 0
    #methodResultID == null ? methodResultID : (methodResultID != null && ((org.jgrapht.Graph)args[0]).containsEdge(((java.lang.Object)args[1]), ((java.lang.Object)args[2])))
    #methodResultID == true
    #args[0] instanceof org.jgrapht.Graph
    #!Double.isNaN(args[3])
    #methodResultID == null ? (g.containsKey(sourceVertex) && g.containsKey(targetVertex)) : true
    #!(args[0] instanceof java.util.Observable)
    #methodResultID == (args[0].getVertexCount() != args[1].getVertexCount()) || (args[0].getEdgeSet().size() != args[1].getEdgeSet().size())
    #assert args[1].stream().anyMatch(v -> v == null) || args[0] == null
    #methodResultID != null && ((org.jgrapht.graph.DirectedGraph<? extends org.jgrapht.graph.DefaultEdge>) args[0]).getSuccessors(args[1]) == methodResultID
    #methodResultID == ((org.jgrapht.Graph)args[0]).containsEdge((java.lang.Object)args[1], (java.lang.Object)args[2])