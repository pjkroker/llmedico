import json
from pathlib import Path
from typing import List



from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.builder.class_model_builder_jdoctor import ClassModelBuilderJdoctor
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation.evaluator import evaluate_class
from llmedico.evaluation.result import AssertionRelation
from llmedico.evaluation_metrics.evaluator_metrics import _compute_metrics_class, MetricMode
from llmedico.evaluation_metrics.evaluation_metrics_writer import EvaluationMetricsCSVWriter


def get_row_evaluation() -> List[EvaluationRow]:
    # Graph
    builder = ClassModelBuilder()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "result-translation" / "llmedico-condition_translator.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    generated_cls = builder.build_class(extracted_conditions[0])

    builder = ClassModelBuilderJdoctor()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "generated_conditions" / "toradocu-condition_translator-org.jgrapht.Graph.json"
    input_path = Path(__file__).parent.parent / "data" / "input" / "org.jgrapht.Graph_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    expected_cls = builder.build_class(extracted_conditions)
    result = evaluate_class(expected_cls, generated_cls)
    return result


def test_compute_metrics():
    results = get_row_evaluation()
    results_metrics = _compute_metrics_class(results)
    results_metrics_relaxed = _compute_metrics_class(results, MetricMode("llmedico"))

    path_outputfile = Path(__file__).parent.parent / "data" / "output" / "llmedico-metrics_jdoctor.csv"
    with EvaluationMetricsCSVWriter(path_outputfile) as writer:
        writer.write(results_metrics)

    path_outputfile = Path(__file__).parent.parent / "data" / "output" / "llmedico-metrics_relaxed.csv"
    with EvaluationMetricsCSVWriter(path_outputfile) as writer:
        writer.write(results_metrics_relaxed)