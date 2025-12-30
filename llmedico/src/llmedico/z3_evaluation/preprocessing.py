import re

def normalize_expression(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("assert"):
        expr = expr[len("assert"):].strip()
    if expr.endswith(";"):
        expr = expr[:-1]
    return expr

TOKEN_REGEX = re.compile(
    r"\s*(>=|<=|==|!=|\|\||&&|[-+*/()]|[<>!]|[a-zA-Z_]\w*|\d+)\s*"
)

def tokenize(expr: str) -> list[str]:
    return TOKEN_REGEX.findall(expr)
