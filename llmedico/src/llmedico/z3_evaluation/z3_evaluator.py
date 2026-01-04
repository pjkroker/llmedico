import z3
from llmedico.z3_evaluation.z3_translator import Z3Translator
from llmedico.evaluation.result import EvaluationResult, AssertionRelation
from llmedico.z3_evaluation.model_ast import Expr


class AssertionEvaluatorZ:

    def evaluate(self, expected: Expr, generated: Expr) -> EvaluationResult:
        """
        Compare two logical AST expressions semantically.
        One evaluation == one Z3 context.
        """

        translator = Z3Translator()

        try:
            A = translator.translate(expected)
            B = translator.translate(generated)
        except Exception as e:
            # Includes type conflicts, unsupported constructs, etc.
            return EvaluationResult(
                relation=AssertionRelation.UNSUPPORTED,
                reason=str(e)
            )

        solver = z3.Solver()

        # 1. Equivalence: A <-> B
        solver.push()
        solver.add(z3.Xor(A, B))
        if solver.check() == z3.unsat:
            return EvaluationResult(AssertionRelation.EQUIVALENT)
        solver.pop()

        # 2. Generated is weaker: B => A
        solver.push()
        solver.add(z3.And(B, z3.Not(A)))
        if solver.check() == z3.unsat:
            return EvaluationResult(AssertionRelation.WEAKER)
        solver.pop()

        # 3. Generated is stronger: A => B
        solver.push()
        solver.add(z3.And(A, z3.Not(B)))
        if solver.check() == z3.unsat:
            return EvaluationResult(AssertionRelation.STRONGER)
        solver.pop()

        # 4. No implication either way
        return EvaluationResult(AssertionRelation.INCOMPARABLE)
