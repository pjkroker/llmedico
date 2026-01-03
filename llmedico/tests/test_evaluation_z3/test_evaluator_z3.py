from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.evaluation.result import AssertionRelation
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_evaluator import AssertionEvaluatorZ


def test_evaluator_equal():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

def test_evaluator_equivalent():
    expr = normalize_expression("assert x >= 0;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x > -1;") #TODO they should be equal?
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()


    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

def test_evaluator_weaker():
    expr = normalize_expression("assert x >= 0 || x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x >=0;")
    tokens = tokenize(expr)
    print(tokens)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    print(result)

def test_evaluator_stronger():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x >=0;")
    tokens = tokenize(expr)
    print(tokens)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    print(result)

def test_null():
    expr = normalize_expression("assert null == null;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert null == null;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

def test_methods():
    expr = normalize_expression("assert getUser(x) != null;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert getUser(x) != null;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

    expr = normalize_expression("assert equals(x,y);")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x == y;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

    expr = normalize_expression("assert x.equals(y);")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x == y;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

    expr = normalize_expression("assert 0+1 > size(x);")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert 5-4 > size(x);")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

def test_terniary():
    expr = normalize_expression("assert x > y  ? true : false;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert y < x ? true : false;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT