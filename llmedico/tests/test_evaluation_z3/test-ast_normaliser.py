from llmedico.z3_evaluation.ast_normalizer import AstNormalizer
from llmedico.z3_evaluation.preprocessing import normalize_expression, rewrite_method_references, tokenize
from llmedico.z3_evaluation.string_parser import StringParser


def test_ast_normaliser():
    # assert !(args[0] instanceof org.jgrapht.DirectedGraph) && !(args[0] instanceof org.jgrapht.UndirectedGraph);
    # assert !(g instanceof DirectedGraph) && !(g instanceof UndirectedGraph);
    ground_truth = "!(args[0] instanceof org.jgrapht.DirectedGraph) && !(args[0] instanceof org.jgrapht.UndirectedGraph)"
    llm = "!(args[0] instanceof DirectedGraph) && !(args[0] instanceof UndirectedGraph)"
    expr = rewrite_method_references(normalize_expression(ground_truth))
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()


    norm = AstNormalizer()
    expected_ast = norm.normalize_expr(expected_ast)

    expr = rewrite_method_references(normalize_expression(llm))
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    generated_ast = norm.normalize_expr(generated_ast)

    assert expected_ast == generated_ast
