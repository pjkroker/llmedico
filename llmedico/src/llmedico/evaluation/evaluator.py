from typing import List

from llmedico.conditions.model import Condition, ClassModel, ConditionKind
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation.result import EvaluationResult, AssertionRelation
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize, rewrite_method_references
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_evaluator import AssertionEvaluatorZ


def _normalize(s: str) -> str:
    return "".join(s.split())

def _evaluate_assertions(expected: str, generated:str) -> EvaluationResult:
    relation: AssertionRelation
    # 1. Empty/Unexpected/Missing
    if expected == generated == "":
        return EvaluationResult(relation=AssertionRelation.EMPTY)
        #raise ValueError("Both assertions are empty")
    if expected == "":
        return EvaluationResult(relation=AssertionRelation.UNEXPECTED) #TODO evaluate anyway
    if generated == "":
        return EvaluationResult(relation=AssertionRelation.MISSING) #TODO evaluate anyway
    # 2. Identical (string-based)
    if _normalize(expected) == _normalize(generated):
        relation = AssertionRelation.IDENTICAL
        return EvaluationResult(relation=relation)

    # 3. Try Evaluation with z3
    #preprocessing
    try:
        #expected
        expected_tokens = tokenize(rewrite_method_references(normalize_expression(expected)))
        parser = StringParser(expected_tokens)
        expected_ast = parser.parse()
        #generated
        generated_tokens = tokenize(rewrite_method_references(normalize_expression(generated)))
        parser = StringParser(generated_tokens)
        generated_ast = parser.parse()
    except Exception as e:
        # Include errors during parsing
        return EvaluationResult(relation=AssertionRelation.UNSUPPORTED,
                                reason="Error during parsing: " + str(e))


    evaluator = AssertionEvaluatorZ()
    return evaluator.evaluate(expected_ast, generated_ast)

def evaluate_class(expected: ClassModel, generated: ClassModel) -> List[EvaluationRow]:
    evaluation_rows = []
    class_name = expected.name
    for i, method_exp in enumerate(expected.methods):
        method_signature = method_exp.signature.name + "(" +  " ".join(p.name for p in method_exp.signature.parameters) + ")"

        for j, condition_exp in enumerate(method_exp.conditions):
            expected_condition = condition_exp.expression
            generated_condition = generated.methods[i].conditions[j].expression
            result = _evaluate_assertions(expected_condition, generated_condition )
            evaluation_rows.append(EvaluationRow(class_name, method_signature,
                                                 kind_exp=condition_exp.kind,
                                                 name_exp=condition_exp.name,
                                                 kind_gen=generated.methods[i].conditions[j].kind,
                                                 name_gen=generated.methods[i].conditions[j].name,
                                                 expected=expected_condition,
                                                 generated=generated_condition,
                                                 relation=result.relation,
                                                 reason=result.reason))







        # params_exp = method_exp.param_conditions
        # params_gen = generated.methods[i].param_conditions
        # for j, condition_exp in enumerate(params_exp):
        #     result = _evaluate_assertions(condition_exp.expression, params_gen[j].expression)
        #     evaluation_rows.append(EvaluationRow(class_name,method_signature, expected=condition_exp.expression,
        #                                  generated=params_gen[j].expression,
        #                                  relation=result.relation,
        #                                  reason=result.reason))
        #
        # throws_exp = method_exp.throws_conditions
        # throws_gen = generated.methods[i].throws_conditions
        # for j, condition_exp in enumerate(throws_exp):
        #     result = _evaluate_assertions(condition_exp.expression, throws_gen[j].expression)
        #     evaluation_rows.append(EvaluationRow(class_name, method_signature, expected=condition_exp.expression,
        #                                  generated=throws_gen[j].expression,
        #                                  relation=result.relation,
        #                                  reason=result.reason))
        #
        # return_exp = method_exp.return_conditions
        # return_gen = generated.methods[i].return_conditions
        # if not return_exp and not return_gen: #contains no return
        #     pass
        # else:
        #     result = _evaluate_assertions(return_exp[0].expression, return_gen[0].expression)
        #     evaluation_rows.append(EvaluationRow(class_name, method_signature, expected=return_exp[0].expression,
        #                                  generated=return_gen[0].expression,
        #                                  relation=result.relation,
        #                                  reason=result.reason))

    return evaluation_rows




