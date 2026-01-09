import re

def normalize_expression(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("assert"):
        expr = expr[len("assert"):].strip()
    if expr.endswith(";"):
        expr = expr[:-1]
    return expr

TOKEN_REGEX = re.compile(
    r"\s*(->|>=|<=|==|!=|\|\||&&|"
    r"[a-zA-Z_]\w*\[\d+\]|"
    r"[-+*/(),%.?:]|"
    r"[<>!]|"
    r"[a-zA-Z_]\w*|"
    r"\d+)\s*"
)

NULL_EQUALS_RE = re.compile(r"\bnull\s*::\s*equals\b")

def tokenize(expr: str) -> list[str]:
    return TOKEN_REGEX.findall(expr)

def rewrite_method_references(expr: str) -> str:
    if "null::equals" not in expr:
        return expr

    # Use a deterministic but unlikely variable name
    return NULL_EQUALS_RE.sub("_x -> _x == null", expr)

