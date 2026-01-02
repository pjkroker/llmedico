from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize


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

def test_tokenizer_bool():
    tokens = tokenize("true")
    assert tokens == ["true"]

    tokens = tokenize("false")
    assert tokens == ["false"]