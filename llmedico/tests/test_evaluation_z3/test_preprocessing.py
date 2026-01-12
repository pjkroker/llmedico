from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize, rewrite_method_references


def test_normalize_expression():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    assert expr == "x >= 0 && x <= 10"

def test_tokenizer():
    expr = normalize_expression("assert x >= 0 && x <= 10;")
    tokens = tokenize(expr)
    assert tokens == ["x", ">=", "0", "&&" ,"x", "<=", "10"]

def test_tokenizer_unary_minus():
    expr = normalize_expression("assert x >= -1;")
    tokens = tokenize(expr)
    assert tokens == ["x", ">=", "-", "1"]

def test_tokenizer_arithmetic():
    expr = normalize_expression("assert x >= -(5+1);")
    tokens = tokenize(expr)
    assert tokens == ["x", ">=", "-", "(", "5", "+", "1", ")"]

def test_tokenizer_modulo():
   tokens = tokenize("x % 2 == 0")
   assert tokens == ["x", "%", "2", "==", "0"]

def test_tokenizer_null():
    tokens = tokenize("x != null")
    assert tokens == ["x", "!=", "null"]

def test_tokenizer_obj():
    tokens = tokenize("x != obj")
    assert tokens == ["x", "!=", "obj"]

def test_tokenizer_bool():
    tokens = tokenize("true")
    assert tokens == ["true"]

    tokens = tokenize("false")
    assert tokens == ["false"]

def test_tokenize_functions():
    tokens = tokenize("isValid(x) == true")
    assert tokens == ["isValid","(","x",")", "==" ,"true"]

    tokens = tokenize("equals(x,y)")
    assert tokens == ['equals', '(', 'x', ',', 'y', ')']

    tokens = tokenize("x.equals(y)")
    assert tokens == ['x', '.', 'equals', '(', 'y', ')']

def test_ternary():
    tokens = tokenize("x > 5 ? true : false")
    assert tokens == ['x', '>', '5', '?', 'true', ":" ,'false']

def test_casts():
    tokens = tokenize("(int)x > 0")
    assert tokens == ['(', 'int', ')', "x", '>', '0']

    tokens = tokenize("(org.jgrapht.Graph)args[0]")
    print(tokens)
    assert tokens == ['(', 'org', '.', 'jgrapht', '.', 'Graph', ')', 'args[0]']

    tokens = tokenize("<? extends org.jgrapht.graph.DefaultEdge>x")
    assert tokens == ['<', '?', 'extends', 'org', '.', 'jgrapht', '.', 'graph', '.', 'DefaultEdge', '>', 'x']

def test_lambda_null_edge_case():
    expr = "receiverObjectID.vertices == null || receiverObjectID.vertices.stream().anyMatch(null::equals)"
    expr = rewrite_method_references(expr)
    assert expr == "receiverObjectID.vertices == null || receiverObjectID.vertices.stream().anyMatch(_x -> _x == null)"



