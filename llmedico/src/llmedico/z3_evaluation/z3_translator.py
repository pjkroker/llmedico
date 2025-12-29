from z3 import *
from llmedico.z3_evaluation.model_ast import (
    Expr, And as AstAnd, Or as AstOr, Not as AstNot,
    Var, IntConst, Compare
)
from llmedico.z3_evaluation.z3_context import Z3Context


class Z3Translator:

    def __init__(self):
        self.ctx = Z3Context()

    def translate(self, expr: Expr) -> BoolRef:
        if isinstance(expr, AstAnd):
            return And(self.translate(expr.left), self.translate(expr.right))

        if isinstance(expr, AstOr):
            return Or(self.translate(expr.left), self.translate(expr.right))

        if isinstance(expr, AstNot):
            return Not(self.translate(expr.expr))

        if isinstance(expr, Var):  # default is bool
            return self.ctx.bool(expr.name)

        if isinstance(expr, IntConst):
            return IntVal(expr.value)

        if isinstance(expr, Compare):
            # Decide types BEFORE creating Z3 objects
            if isinstance(expr.left, Var):
                l = self.ctx.int(expr.left.name)
            else:
                l = self.translate(expr.left)

            if isinstance(expr.right, Var):
                r = self.ctx.int(expr.right.name)
            else:
                r = self.translate(expr.right)

            return {
                ">":  l > r,
                ">=": l >= r,
                "<":  l < r,
                "<=": l <= r,
                "==": l == r,
                "!=": l != r,
            }[expr.op]

        raise TypeError(expr)
