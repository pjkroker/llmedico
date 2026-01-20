from dataclasses import dataclass
from enum import Enum
from typing import List, Optional




class Expr:
    pass

# Boolean structure
@dataclass(frozen=True)
class And(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Or(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Not(Expr):
    expr: Expr

# Atoms
@dataclass(frozen=True)
class BoolVar(Expr):
    name: str

@dataclass(frozen=True)
class IntVar(Expr):
    name: str

@dataclass(frozen=True)
class NullConst(Expr):
    def __repr__(self):
        return "NullConst()"


@dataclass(frozen=True)
class Var(Expr):
    name: str

@dataclass(frozen=True)
class IntConst(Expr):
    value: int

@dataclass(frozen=True)
class BoolConst(Expr):
    value: bool

@dataclass(frozen=True)
class UnaryMinus(Expr):
    expr: Expr

@dataclass(frozen=True)
class Add(Expr): #Addition
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Sub(Expr): #Subtraction
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mul(Expr): #Multiplication
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Div(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mod(Expr):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Method(Expr):
    receiver: Expr | None #a.b(x), a is the reciever
    name: str
    parameters: List[Expr]

@dataclass(frozen=True)
class Conditional(Expr):
    cond: Expr
    then: Expr
    otherwise: Optional[Expr]

@dataclass(frozen=True)
class LambdaExpr(Expr):
    param: str         # "x"
    body: Expr         # e.g. (x > 0)

# Comparisons
@dataclass(frozen=True)
class Compare(Expr):
    left: Expr
    op: str   # ">", ">=", "<", "<=", "==", "!="
    right: Expr

@dataclass(frozen=True)
class InstanceOf(Expr):
    expr: Expr
    type_name: str

class Type(Enum):
    INT = "int"
    BOOL = "bool"
    REF = "ref" #objects, null
    FUNC = "func"

INT_RETURN_METHODS = {
        "size",
        "length",
        "count",
        "index",
        "max",
        "min",
        "minimal",
        "maximum",
        "average",
        "numberOf",
        "iteration",
        "norm",
        "int",
        "long"
    }

BOOL_RETURN_METHODS = {
    "isEmpty",
    "empty",
    "equals",
    "contains",
    "is",
    "has",
    "exists",
    "containsEdge",
    "containsVertex",
    "containsNode",
    "containsKey",
    "containsValue",
    "hasNext",
    "addEdge",
}

MATCH_METHODS = {"anyMatch", "allMatch", "noneMatch"} # for lambda ->

def is_bool(expr_name: str) -> bool:
    for name in BOOL_RETURN_METHODS:
        if name in expr_name:
            return True
    return False

def is_int(expr_name: str) -> bool:
    for name in INT_RETURN_METHODS:
        if name in expr_name:
            return True
    return False

def typeof(expr: Expr) -> Type:
    if isinstance(expr, IntConst):
        return Type.INT

    if isinstance(expr, BoolConst):
        return Type.BOOL

    if isinstance(expr, UnaryMinus):
        return Type.INT

    if isinstance(expr, (Add, Sub, Mul, Div, Mod)):
        return Type.INT

    if isinstance(expr, (And, Or, Not)):
        return Type.BOOL

    if isinstance(expr, Compare):
        # comparisons always return bool
        return Type.BOOL

    if isinstance(expr, Var):
        # minimal assumption:
        # - numeric vars appear in arithmetic
        # - boolean vars appear in logical contexts
        return None  # context-dependent (handled in translator)

    if isinstance(expr, NullConst):
        return Type.REF

    if isinstance(expr, Method): #check TODO
        if expr.name in MATCH_METHODS:
            return Type.BOOL

        if is_int(expr.name):
            return Type.INT
        # predicates
        if is_bool(expr.name) or \
                expr.name.startswith("is") or \
                expr.name.startswith("has"):
            return Type.BOOL

        # # equals() always boolean
        # if expr.name == "equals":
        #     return Type.BOOL

        # otherwise: object-valued method
        return Type.REF

    if isinstance(expr, Conditional):
        t_cond = typeof(expr.cond)
        if t_cond != Type.BOOL:
            raise TypeError("Condition of ?: must be boolean")

        t_then = typeof(expr.then)
        t_else = typeof(expr.otherwise)

        if t_then is not None and t_else is not None and t_then != t_else:
            raise TypeError("Both branches of ?: must have same type")

        return t_then or t_else

    if isinstance(expr, LambdaExpr):
        return Type.FUNC

    raise TypeError(expr)

def expect(expr: Expr, expected: Type, translator=None):
    t = typeof(expr)
    if t is not None and t != expected:
        raise TypeError(f"Expected {expected}, got {t}")

    # t is None -> expr is a Var
    if isinstance(expr, Var) and translator is not None:
        translator._expect_var_type(expr, expected)
