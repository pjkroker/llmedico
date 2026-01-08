import json
from pathlib import Path
from typing import List

from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.builder.class_model_builder_jdoctor import ClassModelBuilderJdoctor
from llmedico.conditions.model import ClassModel
from llmedico.evaluation.evaluation_csv_writer import EvaluationCSVWriter
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation_metrics.evaluator_stats import _precision_jdoc, _recall_jdoc, \
    _compute_metrics_class
from llmedico.evaluation.evaluator import _evaluate_assertions, evaluate_class
from llmedico.evaluation.result import AssertionRelation
from llmedico.evaluation_metrics.writer_metrics import EvaluationMetricsCSVWriter


def get_row_evaluation() -> List[EvaluationRow]:
    # Graph
    builder = ClassModelBuilder()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.Graph_prompt_mit_methods.json"
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

def test_evaluate_expressions():
    result = _evaluate_assertions("x > 0", "")
    assert result.relation == AssertionRelation.MISSING

    result = _evaluate_assertions("", "x > 0")
    assert result.relation == AssertionRelation.UNEXPECTED

    result = _evaluate_assertions("x > 0", "x > 0")
    assert result.relation == AssertionRelation.IDENTICAL
    #identical but whitespace
    result = _evaluate_assertions("x > 0", "x >            0")
    assert result.relation == AssertionRelation.IDENTICAL

    result = _evaluate_assertions("x > 0", "x > 0 -1 +1")
    assert result.relation == AssertionRelation.EQUIVALENT

    result = _evaluate_assertions("x > 0", "x >= 0")
    assert result.relation == AssertionRelation.STRONGER

    result = _evaluate_assertions("x >= 0", "x > 0")
    assert result.relation == AssertionRelation.WEAKER

    result = _evaluate_assertions("x > 0", "y > 0")
    assert result.relation == AssertionRelation.INCOMPARABLE

    result = _evaluate_assertions("x == 0", "x == true")
    assert result.relation == AssertionRelation.UNSUPPORTED
    assert result.reason == "Variable 'x' used as both Type.INT and Type.BOOL"
    #instanceof
    result = _evaluate_assertions("args[0] instanceof org.jgrapht.Graph", "args[0].getClass().getName() == 'org.jgrapht.Graph'")
    assert result.relation == AssertionRelation.UNSUPPORTED
    assert result.reason.startswith("Error during parsing")

    #lambda
    result = _evaluate_assertions("args[1].stream().anyMatch(v -> v == null)", "args[0] == null")
    assert result.relation == AssertionRelation.UNSUPPORTED

def test_evaluate_class():
    ...



def test_evaluation_with_builder():
    builder = ClassModelBuilder()
    input_path = Path(__file__).parent.parent / "data" / "input" / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.Graph.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    generated_cls = builder.build_class(extracted_conditions[0])

    builder = ClassModelBuilderJdoctor()
    input_path = Path(__file__).parent.parent / "data" / "input" / "org.jgrapht.Graph_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    expected_cls = builder.build_class(extracted_conditions)
    result = evaluate_class(expected_cls, generated_cls)

def test_evaluation_with_writer():
    #Graph
    builder = ClassModelBuilder()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.Graph_prompt_mit_methods.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    generated_cls = builder.build_class(extracted_conditions[0])

    builder = ClassModelBuilderJdoctor()
    input_path = Path(__file__).parent.parent / "data" / "input" / "generated_conditions" / "toradocu-condition_translator-org.jgrapht.Graph.json"
    input_path = Path(__file__).parent.parent / "data" / "input" / "org.jgrapht.Graph_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    expected_cls = builder.build_class(extracted_conditions)
    result = evaluate_class(expected_cls, generated_cls)

    path_outputfile = Path(__file__).parent.parent / "data" / "output" / "result_Graph_neu_llm_mit_prompts_goal.csv"
    with EvaluationCSVWriter(path_outputfile) as writer:
        for row in result:
            writer.write(row)

    assert path_outputfile.is_file()

    #CompleteGraphGenerator
    builder = ClassModelBuilder()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.generate.CompleteGraphGenerator.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    generated_cls = builder.build_class(extracted_conditions[0])

    builder = ClassModelBuilderJdoctor()
    input_path = Path(__file__).parent.parent / "data" / "input" / "org.jgrapht.generate.CompleteGraphGenerator_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    expected_cls = builder.build_class(extracted_conditions)
    result = evaluate_class(expected_cls, generated_cls)

    path_outputfile = Path(__file__).parent.parent / "data" / "output" / "result_CompleteGraphGenerator.csv"
    with EvaluationCSVWriter(path_outputfile) as writer:
        for row in result:
            writer.write(row)

    assert path_outputfile.is_file()

    #Graphs
    builder = ClassModelBuilder()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.generate.Graphs.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    generated_cls = builder.build_class(extracted_conditions[0])

    builder = ClassModelBuilderJdoctor()
    input_path = Path(
        __file__).parent.parent / "data" / "input" / "org.jgrapht.Graphs_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    expected_cls = builder.build_class(extracted_conditions)
    result = evaluate_class(expected_cls, generated_cls)

    path_outputfile = Path(__file__).parent.parent / "data" / "output" / "result_Graphs_alt.csv"
    with EvaluationCSVWriter(path_outputfile) as writer:
        for row in result:
            writer.write(row)

    assert path_outputfile.is_file()



