from dataclasses import dataclass


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
class Var(Expr):
    name: str

@dataclass(frozen=True)
class IntConst(Expr):
    value: int

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

# Comparisons
@dataclass(frozen=True)
class Compare(Expr):
    left: Expr
    op: str   # ">", ">=", "<", "<=", "==", "!="
    right: Expr