import re
import logging
logger = logging.getLogger(__name__)

def normalize_expression(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("assert"):
        expr = expr[len("assert"):].strip()
    if expr.endswith(";"):
        expr = expr[:-1]

    #normalize floats
    expr = FLOAT_ZERO_RE.sub(r"\1", expr)

    return expr
FLOAT_ZERO_RE = re.compile(r'(?<!\w)(\d+)\.0(?!\d)')

TOKEN_REGEX = re.compile(
    r"\s*(>>>|>>|<<|"
    r"->|>=|<=|==|!=|\|\||&&|"
    r"[a-zA-Z_]\w*\[\d+\]|"
    r"[-+*/(),%.?:]|"
    r"[<>!]|"
    r"[a-zA-Z_]\w*|"
    r"\d+)\s*"
)

NULL_EQUALS_RE = re.compile(r"\bnull\s*::\s*equals\b")
OBJECTS_ISNULL_RE = re.compile(r'\bObjects\s*::\s*isNull\b')
CONTAINS_NULL_RE = re.compile(r"([a-zA-Z_][\w\[\]\.]*)\.contains\s*\(\s*null\s*\)")

def tokenize(expr: str) -> list[str]:
    return TOKEN_REGEX.findall(expr)

def rewrite_method_references(expr: str) -> str:
    """
    anyMatch(Objects::isNull) is equivalent to anyMatch(e -> e == null)
    anyMatch(null::equals) is equivalent to anyMatch(e -> e == null)
    X.contains(null) is equivalent to X.stream().anyMatch(_x -> _x == null)
    :param expr:
    :return:
    """
    if "->" in expr:
        logger.debug("Expression already contains ->", expr)
        return expr

    expr_old = expr
    # Use a deterministic but unlikely variable name
    expr = OBJECTS_ISNULL_RE.sub("_x -> _x == null", expr) #if nothing is found, expr stays unchanged
    expr = NULL_EQUALS_RE.sub("_x -> _x == null", expr)
    expr = CONTAINS_NULL_RE.sub(r"\1.stream().anyMatch(_x -> _x == null)", expr)
    if expr_old != expr:
        logger.warning(f"Rewriting method references in {expr_old} to \n {expr} ")
    return expr

