from collections import Counter
from collections import Counter
from typing import List

from llmedico.conditions.model import ConditionKind
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation.result import AssertionRelation
from llmedico.evaluation_metrics.evaluation_metrics_row import EvaluationMetricRow

CORRECT_RELATIONS = {
    AssertionRelation.IDENTICAL,
    AssertionRelation.EMPTY,
}

WRONG2_RELATIONS = {
    AssertionRelation.EQUIVALENT,
    AssertionRelation.DUAL,
    AssertionRelation.STRONGER,
    AssertionRelation.WEAKER,
    AssertionRelation.INCOMPARABLE,
    AssertionRelation.UNSUPPORTED,
}


def _compute_pr_from_rows(rows: list[EvaluationRow]):
    counts = Counter(r.relation for r in rows)

    correct = sum(counts[r] for r in CORRECT_RELATIONS)
    wrong1 = counts[AssertionRelation.UNEXPECTED]
    wrong2 = sum(counts[r] for r in WRONG2_RELATIONS)
    missing = counts[AssertionRelation.MISSING]

    try:
        precision = _precision_jdoc(correct, wrong1, wrong2)
    except ZeroDivisionError:
        precision = None
    try:
        recall = _recall_jdoc(correct, wrong2, missing)
    except ZeroDivisionError:
        recall = None

    return precision, recall

def _rows_of_kind(rows, kind: ConditionKind):
    return [r for r in rows if r.kind_exp == kind]


def _compute_metrics_class(evaluation_rows: list[EvaluationRow]) -> EvaluationMetricRow:
    fqn = evaluation_rows[0].class_name

    # Overall
    overall_precision, overall_recall = _compute_pr_from_rows(evaluation_rows)

    # Per kind
    param_precision, param_recall = _compute_pr_from_rows(
        _rows_of_kind(evaluation_rows, ConditionKind.PARAM)
    )

    return_precision, return_recall = _compute_pr_from_rows(
        _rows_of_kind(evaluation_rows, ConditionKind.RETURN)
    )

    throws_precision, throws_recall = _compute_pr_from_rows(
        _rows_of_kind(evaluation_rows, ConditionKind.THROWS)
    )

    return EvaluationMetricRow(
        class_fqn=fqn,
        param_precision=param_precision,
        param_recall=param_recall,
        return_precision=return_precision,
        return_recall=return_recall,
        throws_precision=throws_precision,
        throws_recall=throws_recall,
        overall_precision=overall_precision,
        overall_recall=overall_recall,
        overall_f1=None,  # or compute here if needed
    )


def _precision_jdoc(correct: int, wrong1:int, wrong2:int) -> float:
    """
    Computes precision with the definition from the Jdoctor paper.
    :param correct: (int) #generated_specifications that match the expected specification
    :param wrong1: (int) #generated_specifications when no specification is expected
    :param wrong2: (int) #generated_specifications that do not match the expected one
    :return: (float) the ratio between the number of correct outputs and the total number of outputs.
    """
    return correct / (correct + wrong1 + wrong2)

def _recall_jdoc(correct:int , wrong2:int, missing:int) -> float:
    """
    Recall measures completeness as the proportion of desired outputs that the tool produced.
    :param correct: (int) #generated_specifications that match the expected specification
    :param wrong2: (int) #generated_specifications that do not match the expected one
    :param missing: (int) #generated_specifications that did not get generated
    :return: (float) It is defined as the ratio between the number of correct outputs and the total number of desired outputs
    """
    return correct / (correct + wrong2 + missing)