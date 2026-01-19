import os
from collections import Counter
from pathlib import Path

from llmedico.conditions.model import ConditionKind
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation.result import AssertionRelation
from llmedico.evaluation_metrics.evaluation_metrics_row import EvaluationMetricRow
from enum import Enum

from llmedico.evaluation_metrics.evaluation_metrics_writer import EvaluationMetricsCSVWriter


class MetricMode(Enum):
    JDOCTOR = "jdoctor" # identical
    LLMEDICO = "llmedico"   # identical + equivalent + stronger
    RELAXED = "relaxed" # identical + equivalent + stronger + dual

METRIC_DEFINITIONS = {
    MetricMode.JDOCTOR: {
        "correct": {
            AssertionRelation.IDENTICAL,
            #AssertionRelation.EMPTY,
        },
        "wrong2": {
            AssertionRelation.EQUIVALENT,
            AssertionRelation.DUAL,
            AssertionRelation.STRONGER,
            AssertionRelation.WEAKER,
            AssertionRelation.INCOMPARABLE,
            AssertionRelation.UNSUPPORTED,
        },
    },
    MetricMode.LLMEDICO: {
        "correct": {
            AssertionRelation.IDENTICAL,
            #AssertionRelation.EMPTY,
            AssertionRelation.EQUIVALENT,
        },
        "wrong2": {
            AssertionRelation.DUAL,
            AssertionRelation.STRONGER,
            AssertionRelation.WEAKER,
            AssertionRelation.INCOMPARABLE,
            AssertionRelation.UNSUPPORTED,
        },
    },

    MetricMode.RELAXED: {
        "correct": {
            AssertionRelation.IDENTICAL,
            #AssertionRelation.EMPTY,
            AssertionRelation.EQUIVALENT,
            AssertionRelation.DUAL,
            AssertionRelation.STRONGER,
        },
        "wrong2": {
            AssertionRelation.WEAKER,
            AssertionRelation.INCOMPARABLE,
            AssertionRelation.UNSUPPORTED,
        },
    },
}



def _compute_pr_from_rows(rows: list[EvaluationRow], mode: MetricMode = MetricMode.JDOCTOR):
    counts = Counter(r.relation for r in rows)
    spec = METRIC_DEFINITIONS[mode]

    correct = sum(counts[r] for r in spec["correct"])
    wrong1 = counts[AssertionRelation.UNEXPECTED]
    wrong2 = sum(counts[r] for r in spec["wrong2"])
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

def _compute_metrics_class(evaluation_rows: list[EvaluationRow], mode: MetricMode = MetricMode.JDOCTOR) -> EvaluationMetricRow:

    fqn = evaluation_rows[0].class_name

    overall_precision, overall_recall = _compute_pr_from_rows(
        evaluation_rows, mode
    )

    param_precision, param_recall = _compute_pr_from_rows(
        _rows_of_kind(evaluation_rows, ConditionKind.PARAM), mode
    )

    return_precision, return_recall = _compute_pr_from_rows(
        _rows_of_kind(evaluation_rows, ConditionKind.RETURN), mode
    )

    throws_precision, throws_recall = _compute_pr_from_rows(
        _rows_of_kind(evaluation_rows, ConditionKind.THROWS), mode
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
        overall_f1=None,
    )

def compute_metrics_all_classes(classes_evaluation_rows: list[list[EvaluationRow]], project_name: str, path_output: str | Path | None, mode: MetricMode = MetricMode.JDOCTOR, path_result: str | Path | None=None, debug: bool=True, silent: bool=False, project: bool=False):
    if Path(path_output) is not None and not Path(path_output).exists():
        os.makedirs(path_output)

    rows = []
    for class_evaluation_rows in classes_evaluation_rows:
        rows.append(_compute_metrics_class(class_evaluation_rows, mode))

    if project:
        file_name = f"llmedico-evaluation-metrics-{mode}-{project_name}-project.csv"
    else:
        file_name = f"llmedico-evaluation-metrics-{mode}-{project_name}-classes.csv"
    path_outputfile = path_result if path_result is not None else Path(
        path_output) / file_name
    with EvaluationMetricsCSVWriter(path_outputfile) as writer:
        for metric_row in rows:
            writer.write(metric_row)

def compute_metrics_project(classes_evaluation_rows: list[list[EvaluationRow]], project_name: str, path_output: str | Path | None, mode: MetricMode = MetricMode.JDOCTOR, path_result: str | Path | None=None, debug: bool=True, silent: bool=False):
    rows = [row for rows_class in classes_evaluation_rows for row in rows_class]

    compute_metrics_all_classes([rows], project_name, path_output, mode, path_result, debug, silent, project=True)



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