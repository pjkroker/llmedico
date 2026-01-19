from collections import Counter, defaultdict
from typing import List
import logging

from llmedico.z3_evaluation import model_ast
from llmedico.z3_evaluation.ast_normalizer import AstNormalizer
from llmedico.z3_evaluation.model_ast import Type

logger = logging.getLogger(__name__)

from llmedico.conditions.model import Condition, ClassModel, ConditionKind
from llmedico.evaluation.evaluation_csv_writer import EvaluationCSVWriter
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation.result import EvaluationResult, AssertionRelation
from llmedico.z3_evaluation.preprocessing import normalize_expression, tokenize, rewrite_method_references
from llmedico.z3_evaluation.string_parser import StringParser
from llmedico.z3_evaluation.z3_evaluator import AssertionEvaluatorZ


def _normalize(s: str) -> str:
    return "".join(s.split())

def _evaluate_assertions(expected: str, generated:str, return_type: model_ast.Type=None) -> EvaluationResult:
    relation: AssertionRelation
    # 1. Empty/Unexpected/Missing
    if expected.strip() == generated.strip() == "":
        return EvaluationResult(relation=AssertionRelation.EMPTY)
        #raise ValueError("Both assertions are empty")
    if expected.strip() == "":
        return EvaluationResult(relation=AssertionRelation.UNEXPECTED) #TODO evaluate anyway
    if generated.strip() == "":
        return EvaluationResult(relation=AssertionRelation.MISSING) #TODO evaluate anyway
    # 2. Identical (string-based)
    if _normalize(expected) == _normalize(generated):
        relation = AssertionRelation.IDENTICAL
        return EvaluationResult(relation=relation)

    # 3. Try Evaluation with z3
    #preprocessing
    try:
        #expected
        norm = AstNormalizer()
        expected_tokens = tokenize(rewrite_method_references(normalize_expression(expected)))
        parser = StringParser(expected_tokens)
        expected_ast = parser.parse()
        expected_ast = norm.normalize_expr(expected_ast)
        #generated
        generated_tokens = tokenize(rewrite_method_references(normalize_expression(generated)))
        parser = StringParser(generated_tokens)
        generated_ast = parser.parse()
        generated_ast = norm.normalize_expr(generated_ast)
    except Exception as e:
        # Include errors during parsing
        return EvaluationResult(relation=AssertionRelation.UNSUPPORTED,
                                reason="Error during parsing: " + str(e))


    evaluator = AssertionEvaluatorZ()
    return evaluator.evaluate(expected_ast, generated_ast, return_type)

def evaluate_class(expected: ClassModel, generated: ClassModel) -> List[EvaluationRow]:
    evaluation_rows = []
    class_name = expected.name
    if class_name != generated.name:
        raise ValueError(f"Class name mismatch: {class_name} != {generated.name}")
    if len(expected.methods) != len(generated.methods):
        logger.critical(f"len expected:{len(expected.methods)} generated:{len(generated.methods)}")
        raise ValueError("Number of Methods does not match!")
    for i, method_exp in enumerate(expected.methods):
        method_signature = method_exp.signature.name + "(" +  " ".join(p.name for p in method_exp.signature.parameters) + ")"
        logger.critical(f"expected method: {method_signature}")
        if method_exp.signature.name.split(".")[-1] != generated.methods[i].signature.name.split(".")[-1]:
            raise ValueError(f"Method signature mismatch method expected {method_exp.signature.name} but got {generated.methods[i].signature.name}")

        for j, condition_exp in enumerate(method_exp.conditions):
            return_type_model = method_exp.signature.return_type
            if return_type_model is None:
                return_type = None
            else:
                logger.critical(f"return_type_model_name:{return_type_model.simple_name}")
                return_type = Type("bool") if return_type_model.simple_name == "boolean" else (Type("int") if (return_type_model.simple_name == "int" or return_type_model.simple_name == "long" or return_type_model.simple_name == "double" or return_type_model.simple_name == "float" )else Type("ref")) # TODO check

            logger.critical(f"return_type:{return_type}")
            if len(method_exp.conditions) != len(generated.methods[i].conditions):
                if len(generated.methods[i].conditions) == 0:
                    logger.critical(f"Cannot compare {method_exp.signature.name} condition, generated methods has none!")
                    break
                logger.critical(f"Class: {class_name} with {method_signature}")
                logger.critical(f"Conditions don't match expected {len(method_exp.conditions)} but got {len(generated.methods[i].conditions)}\n trying to match them to one of expected conditions, but could be wrong!")

                for gen in generated.methods[i].conditions:
                    if gen.name == condition_exp.name:
                        logger.critical(f"matching condition {condition_exp} and {gen}")
                        result = _evaluate_assertions(condition_exp.expression, gen.expression, return_type)
                        evaluation_rows.append(EvaluationRow(class_name, method_signature,
                                                kind_exp=condition_exp.kind,
                                                name_exp=condition_exp.name,
                                                kind_gen=gen.kind,
                                                name_gen=gen.name,
                                                expected=condition_exp.expression,
                                                generated=gen.expression,
                                                relation=result.relation,
                                                reason=result.reason))
                        break
                logger.critical("could not match generated conditions!")
            else:
                expected_condition = condition_exp.expression
                generated_condition = generated.methods[i].conditions[j].expression

                result = _evaluate_assertions(expected_condition, generated_condition, return_type)

                evaluation_rows.append(EvaluationRow(class_name, method_signature,
                                                     kind_exp=condition_exp.kind,
                                                     name_exp=condition_exp.name,
                                                     kind_gen=generated.methods[i].conditions[j].kind,
                                                     name_gen=generated.methods[i].conditions[j].name,
                                                     expected=expected_condition,
                                                     generated=generated_condition,
                                                     relation=result.relation,
                                                     reason=result.reason))

    return evaluation_rows

