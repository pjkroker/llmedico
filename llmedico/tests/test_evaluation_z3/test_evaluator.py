from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_evaluator import AssertionEvaluator


def test_evaluator_equality():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluator()
    result = evaluator.evaluate(expected_ast, generated_ast)
    print(result)

def test_evaluator():
    expr = normalize_expression("assert x >= 0;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression("assert x > -1;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluator()
    result = evaluator.evaluate(expected_ast, generated_ast)
    print(result)