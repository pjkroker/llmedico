import json
import os
from pathlib import Path

import llmedico
from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.builder.class_model_builder_jdoctor import ClassModelBuilderJdoctor
from llmedico.evaluation.evaluation_csv_writer import EvaluationCSVWriter
from llmedico.evaluation.evaluator import evaluate_class
from llmedico.main import main

path = Path(__file__).parent.parent / "storage" / "jgrapht-core-0.9.2.txt"

with path.open("r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

path_goals = Path(__file__).parent.parent / "storage" / "goal-output-groundtruth" / "jgrapht-core-0.9.2"
path_llmedico = Path(__file__).parent / "results" / "jgrapht-core-0.9.2"


print(len(lines))
print(lines)
done = []
for fqn in lines:
    if fqn not in done:
        base = Path(__file__).parent / "results-evalutation" / "jgrapht-core-0.9.2"
        path_out_dir = base
        if not path_out_dir.exists():
            os.makedirs(path_out_dir)


        builder = ClassModelBuilder()
        input_path = path_llmedico / fqn / "llmedico-condition_translator.json"
        with open(input_path, "r", encoding="utf-8") as f:
            extracted_conditions = json.load(f)
        generated_cls = builder.build_class(extracted_conditions[0])

        builder = ClassModelBuilderJdoctor()
        input_path = path_goals / (fqn + "_goal.json")
        with open(input_path, "r", encoding="utf-8") as f:
            extracted_conditions = json.load(f)
        expected_cls = builder.build_class(extracted_conditions)
        result = evaluate_class(expected_cls, generated_cls)

        path_outputfile = base / f"result_{fqn}.csv"
        with EvaluationCSVWriter(path_outputfile) as writer:
            for row in result:
                writer.write(row)