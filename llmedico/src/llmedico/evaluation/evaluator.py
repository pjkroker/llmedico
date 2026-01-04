from llmedico.conditions.model import Condition, ClassModel, ConditionKind
from llmedico.evaluation.result import EvaluationResult, AssertionRelation
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_evaluator import AssertionEvaluatorZ


def _normalize(s: str) -> str:
    return "".join(s.split())

def _evaluate_assertions(expected: str, generated:str) -> EvaluationResult:
    relation: AssertionRelation
    # 1. Error/Unexpected/Missing
    if expected == generated == "":
        raise ValueError("Both assertions are empty")
    if expected == "":
        return EvaluationResult(relation=AssertionRelation.UNEXPECTED) #TODO evaluate anyway
    if generated == "":
        return EvaluationResult(relation=AssertionRelation.MISSING)
    # 2. Identical (string-based)
    if _normalize(expected) == _normalize(generated):
        relation = AssertionRelation.IDENTICAL
        return EvaluationResult(relation=relation)

    # 3. Try Evaluation with z3
    #preprocessing
    try:
        #expected
        expected_tokens = tokenize(normalize_expression(expected))
        parser = StringParser(expected_tokens)
        expected_ast = parser.parse()
        #generated
        generated_tokens = tokenize(normalize_expression(generated))
        parser = StringParser(generated_tokens)
        generated_ast = parser.parse()
    except Exception as e:
        # Include errors during parsing
        return EvaluationResult(relation=AssertionRelation.UNSUPPORTED,
                                reason="Error during parsing: " + str(e))


    evaluator = AssertionEvaluatorZ()
    return evaluator.evaluate(expected_ast, generated_ast)

def evaluate_class(expected: ClassModel, generated: ClassModel) -> EvaluationResult:
    for i, method_exp in enumerate(expected.methods):
        params_exp = method_exp.param_conditions
        params_gen = generated.methods[i].param_conditions
        for j, condition_exp in enumerate(params_exp):
            print(f"expected: {condition_exp.expression}")
            print(f"generated: {params_gen[j].expression}")
            result = _evaluate_assertions(condition_exp.expression, params_gen[j].expression)
            print(result)

        throws_exp = method_exp.throws_conditions
        throws_gen = generated.methods[i].throws_conditions
        for j, condition_exp in enumerate(throws_exp):
            print(f"expected: {condition_exp.expression}")
            print(f"generated: {throws_gen[j].expression}")
            result = _evaluate_assertions(condition_exp.expression, throws_gen[j].expression)
            print(result)

        return_exp = method_exp.return_conditions
        return_gen = generated.methods[i].return_conditions
        if not return_exp and not return_gen: #contains no return
            EvaluationResult(relation=AssertionRelation.UNSUPPORTED)
            pass
        else:
            print(f"expected: {return_exp[0].expression}")
            print(f"generated: {return_gen[0].expression}")
            result = _evaluate_assertions(return_exp[0].expression, return_gen[0].expression)
            print(result)

    return EvaluationResult(relation=AssertionRelation.UNSUPPORTED)




