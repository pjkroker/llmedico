import re

def normalize_expression(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("assert"):
        expr = expr[len("assert"):].strip()
    if expr.endswith(";"):
        expr = expr[:-1]
    return expr

TOKEN_REGEX = re.compile(
    r"\s*(>=|<=|==|!=|\|\||&&|"
    r"[a-zA-Z_]\w*\[\d+\]|"
    r"[-+*/(),%.?:]|"
    r"[<>!]|"
    r"[a-zA-Z_]\w*|"
    r"\d+)\s*"
)

def tokenize(expr: str) -> list[str]:
    return TOKEN_REGEX.findall(expr)
