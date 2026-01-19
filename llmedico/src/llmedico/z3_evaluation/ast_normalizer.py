from llmedico.z3_evaluation.model_ast import *
import logging

logger = logging.getLogger(__name__)

class UnsupportedAssertion(Exception):
    pass

class Normalizer:

    def normalize_expr(self, expr: Expr) -> Optional[Expr]:

        # ---- Method calls ----
        if isinstance(expr, Method):

            if expr.name == "Arrays" and isinstance(expr.receiver, Method) and expr.parameters == []: # java.utils.Array = Method=(receiver=(Method(receiver=Var(name='java'), name='util', parameters=[]), name='Arrays', parameters=[])
                return self.normalize_expr(expr.receiver)
                # normalized_reciever = self.normalize_expr(expr.receiver)
                # if normalized_reciever is None:
                #     return None
                # else:
                #     return normalized_reciever

            if expr.name == "util" and isinstance(expr.receiver, Var) and expr.receiver.name == "java": # java.utils = Method(receiver=Var(name='java'), name='util', parameters=[])
                return None

            if expr.name == "stream": # java.utils.Arrays.stream(args[0]) -> args[0].stream()

                receiver = self.normalize_expr(expr.receiver) if expr.receiver else None #reciever can be Method or Var (OBJ)
                parameters = expr.parameters

                if not receiver and parameters and len(parameters) == 1: #stream(args[0]) -> args[0].stream()
                    normalized_method = Method(receiver=parameters[0], name=expr.name, parameters=[])
                    logger.warning(f"Normalized Arrays.stream()\nbefore: {expr}\nafter: {normalized_method}")
                    return normalized_method
                elif receiver and parameters and len(parameters) == 1: # java.util.Arrays.stream(args[0])
                    #normalized_receiver = self.normalize_expr(expr.receiver)
                    # if receiver is None: # java.util.Arrays -> None (remove reciever)
                    #     return None
                    return Method(receiver=receiver, name=expr.name, parameters=expr.parameters)

            elif isinstance(expr.receiver, Method): #java.utils.Arrays.stream(args[0]).anyMatch(e -> e==null)
                normalized_receiver = self.normalize_expr(expr.receiver)
                return Method(receiver=normalized_receiver, name=expr.name, parameters=expr.parameters)

            return expr


        # # Normalize rest
        # if isinstance(expr, Conditional):
        #     return Conditional(self.normalize_expr(expr.cond), self.normalize_expr(expr.then),
        #                        self.normalize_expr(expr.otherwise))
        #
        # # Binary operators
        # if isinstance(expr, (Add, Sub, Mul, Div, Mod, Compare, And, Or)):
        #     return type(expr)(self.normalize_expr(expr.left), self.normalize_expr(expr.right))
        #
        # # Unary operators
        # if isinstance(expr, (Not, UnaryMinus)):
        #     return type(expr)(self.normalize_expr(expr.expr))

        # Atoms (Var, Const, etc.)
        return expr
