from llmedico.z3_evaluation.ast_normalizer import AstNormalizer
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize, rewrite_method_references
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

def test_type_mismatch():
    #assert (receiverObjectID.containsVertex(args[0]))==false ? methodResultID==true:methodResultID==false;
    #assert methodResultID == !receiverObjectID.containsVertex(args[0]);

    expr = normalize_expression("assert (receiverObjectID.containsVertex(args[0]))==false ? methodResultID==true:methodResultID==false;")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression(
        "assert methodResultID == !receiverObjectID.containsVertex(args[0]);")
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)
    assert result.relation == AssertionRelation.EQUIVALENT

    ground_truth = "assert receiverObjectID.size()<args[0];"
    llm = "assert receiverObjectID.empty() || args[0] >= receiverObjectID.size();"
    expr = normalize_expression(ground_truth)
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()

    expr = normalize_expression(llm)
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)

    assert result.relation == AssertionRelation.STRONGER

def test_normalizer_after_parsing():

    ground_truth = "assert args[0].stream().anyMatch(e -> e==null);"
    llm = "assert stream(args[0]).anyMatch(Objects::isNull);"
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


    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)

    assert result.relation == AssertionRelation.EQUIVALENT

    ground_truth = "assert args[0].stream().anyMatch(e -> e==null);"
    llm = "assert java.util.Arrays.stream(args[0]).anyMatch(Objects::isNull);"
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


    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)

    assert result.relation == AssertionRelation.EQUIVALENT

def test2():

    ground_truth = "assert receiverObjectID.containsVertex(args[0]) ? methodResultID==true : methodResultID==false;"
    llm = "assert methodResultID == (receiverObjectID.containsVertex(args[0]) && args[0] != null);"
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

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)

    assert result.relation == AssertionRelation.INCOMPARABLE


    #ConditionKind.RETURN,assert (receiverObjectID.containsVertex(args[0]))==false ? methodResultID==true:methodResultID==false;,assert methodResult == !receiverObjectID.containsVertex(args[0]);,AssertionRelation.INCOMPARABLE

    ground_truth = "assert (receiverObjectID.containsVertex(args[0]))==false ? methodResultID==true:methodResultID==false;"
    llm = "assert methodResultID == !receiverObjectID.containsVertex(args[0]);"
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

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)

    assert result.relation == AssertionRelation.EQUIVALENT

    #assert (args[0] instanceof BinaryChromosome) == false;,assert !(args[0] instanceof BinaryChromosome);
    ground_truth = "assert (args[0] instanceof BinaryChromosome) == false;"
    llm = "assert !(args[0] instanceof BinaryChromosome);"
    expr = rewrite_method_references(normalize_expression(ground_truth))
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    expected_ast = parser.parse()
    print(expected_ast)
    norm = AstNormalizer()
    expected_ast = norm.normalize_expr(expected_ast)

    expr = rewrite_method_references(normalize_expression(llm))
    tokens = tokenize(expr)
    parser = StringParser(tokens)
    generated_ast = parser.parse()
    print(generated_ast)
    generated_ast = norm.normalize_expr(generated_ast)

    evaluator = AssertionEvaluatorZ()
    result = evaluator.evaluate(expected_ast, generated_ast)

    assert result.relation == AssertionRelation.EQUIVALENT