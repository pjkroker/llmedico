import json
import os
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import List

from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.builder.class_model_builder_jdoctor import ClassModelBuilderJdoctor
from llmedico.config.config import Config
from llmedico.evaluation.evaluation_csv_writer import EvaluationCSVWriter
from llmedico.evaluation.evaluation_row import EvaluationRow
from llmedico.evaluation.evaluator import evaluate_class
from llmedico.evaluation.result import AssertionRelation


class InputFormat(Enum):
    JDOCTOR = "jdoctor"
    LLMEDICO = "llmedico"

def _write_evaluation_rows_by_type(rows: List[EvaluationRow], types: [AssertionRelation], path_outputfile) -> None:
    assertion_relation_counts = Counter(row.relation for row in rows)
    rows_by_type = []
    for type in types:
        rows_by_type.append([assertion for assertion in rows if assertion.relation == type])

    with EvaluationCSVWriter(path_outputfile) as writer:
        for type_row in rows_by_type:
            for row in type_row:
                writer.write(row)


def evaluate(path_expected: str | Path, type_expected: InputFormat, path_generated: str | Path, type_generated: InputFormat,path_output: str | Path | None, path_result: str | Path | None=None,debug: bool=True, silent: bool=False) -> List[EvaluationRow]:
    if Path(path_output) is not None and not Path(path_output).exists():
        os.makedirs(path_output)

    config_path = Path(
        os.getenv("LLMEDICO_CONFIG", Path.cwd() / "config.toml")  # TODO test environment variable
    ).expanduser().resolve()

    cnfg = Config(config_path)
    evaluation_config = cnfg.section("evaluation")

    llmed_builder = ClassModelBuilder()
    jdoc_builder = ClassModelBuilderJdoctor()

    if type_expected == InputFormat.LLMEDICO:
        with open(path_expected, "r") as f:
            expected_conditions = json.load(f)
        expected_clsm = llmed_builder.build_class(expected_conditions[0])
    elif type_expected == InputFormat.JDOCTOR:
        with open(path_expected, "r") as f:
            expected_conditions = json.load(f)
        expected_clsm = jdoc_builder.build_class(expected_conditions)

    if type_generated == InputFormat.LLMEDICO:
        with open(path_generated, "r") as f:
            generated_conditions = json.load(f)
        generated_clsm = llmed_builder.build_class(generated_conditions[0])
    elif type_generated == InputFormat.JDOCTOR:
        with open(path_generated, "r") as f:
            generated_conditions = json.load(f)
        generated_clsm = jdoc_builder.build_class(generated_conditions)

    if expected_clsm.qualified_name != generated_clsm.qualified_name:
        raise ValueError("Cannot compare conditions of different classes!")

    result = evaluate_class(expected_clsm, generated_clsm,evaluation_config["normalise_incomplete_java"])

    path_outputfile = path_result if path_result is not None else Path(path_output) / f"llmedico-evaluation-{expected_clsm.qualified_name}.csv"
    with EvaluationCSVWriter(path_outputfile) as writer:
        for row in result:
            writer.write(row)

    return result


if __name__ == '__main__':
    PATH_EXPECTED = Path(__file__).parent.parent.parent.parent / "storage" / "goal-output-groundtruth" / "freecol-0.11.6" / "net.sf.freecol.common.model.Player$ActivePredicate_goal.json"
    TYPE_EXPECTED = InputFormat.JDOCTOR
    PATH_GENERATED = Path("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/llmedico-condition_translator.json")
    TYPE_GENERATED = InputFormat.LLMEDICO
    PATH_OUT_DIR = Path(__file__).parent.parent.parent.parent / "data" / "output"
    PATH_RESULT = None #Path(__file__).parent.parent.parent.parent / "data" / "output" / "llmedico-evaluation-org.project.MyClass.csv"
    DEBUG = True
    SILENT = False
    os.environ["LLMEDICO_CONFIG"] = (Path(__file__).parent.parent.parent.parent / "config.toml").as_posix()
    evaluate(path_expected=PATH_EXPECTED,
             type_expected=TYPE_EXPECTED,
             path_generated=PATH_GENERATED,
             type_generated=TYPE_GENERATED,
             path_result=PATH_RESULT,
             path_output=PATH_OUT_DIR,
             debug=DEBUG,
             silent=SILENT)