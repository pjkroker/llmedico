from llmedico.z3_evaluation.model_ast import *


class UnsupportedAssertion(Exception):
    pass

class Normalizer:

    def normalize_expr(self, expr: Expr) -> Expr:
        # ---- Lambda ----
        if isinstance(expr, LambdaExpr):
            # Lambda itself is only allowed when consumed by a match method
            # If we see it here, it's in an invalid position
            raise UnsupportedAssertion(
                "Lambda expressions are only supported as arguments to anyMatch/allMatch/noneMatch"
            )

        # ---- Method calls ----
        if isinstance(expr, Method):
            receiver = self.normalize_expr(expr.receiver) if expr.receiver else None
            args = []

            for a in expr.parameters:
                if isinstance(a, LambdaExpr):
                    if expr.name not in MATCH_METHODS:
                        raise UnsupportedAssertion(
                            f"Lambda not allowed in call to '{expr.name}'"
                        )
                    args.append(a)  # lambda allowed here
                else:
                    args.append(self.normalize_expr(a))

            if expr.name in MATCH_METHODS:
                lambdas = [a for a in args if isinstance(a, LambdaExpr)]
                if len(lambdas) != 1 or len(args) != 1:
                    raise UnsupportedAssertion(
                        f"{expr.name} expects exactly one lambda argument")

            return Method(receiver=receiver, name=expr.name, parameters=args)

        # Normalize rest
        if isinstance(expr, Conditional):
            return Conditional(self.normalize_expr(expr.cond), self.normalize_expr(expr.then),
                               self.normalize_expr(expr.otherwise))

        # Binary operators
        if isinstance(expr, (Add, Sub, Mul, Div, Mod, Compare, And, Or)):
            return type(expr)(self.normalize_expr(expr.left), self.normalize_expr(expr.right))

        # Unary operators
        if isinstance(expr, (Not, UnaryMinus)):
            return type(expr)(self.normalize_expr(expr.expr))

        # Atoms (Var, Const, etc.)
        return expr
