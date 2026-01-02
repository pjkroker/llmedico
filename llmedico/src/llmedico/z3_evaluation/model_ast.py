from dataclasses import dataclass
from enum import Enum


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
class NullConst(Expr): #TODO check does this work?
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

# Comparisons
@dataclass(frozen=True)
class Compare(Expr):
    left: Expr
    op: str   # ">", ">=", "<", "<=", "==", "!="
    right: Expr

class Type(Enum):
    INT = "int"
    BOOL = "bool"
    REF = "ref" #objects, null

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

    raise TypeError(expr)

def expect(expr: Expr, expected: Type, translator=None):
    t = typeof(expr)
    if t is not None and t != expected:
        raise TypeError(f"Expected {expected}, got {t}")

    # t is None -> expr is a Var
    if isinstance(expr, Var) and translator is not None:
        translator._expect_var_type(expr, expected)
