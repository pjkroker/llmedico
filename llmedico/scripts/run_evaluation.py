import os
from pathlib import Path

from llmedico.evaluation.evaluation import evaluate, InputFormat
from llmedico.evaluation.evaluator import evaluate_class
from llmedico.evaluation_metrics.evaluation_metrics_writer import EvaluationMetricsCSVWriter
from llmedico.evaluation_metrics.evaluator_metrics import _compute_metrics_class, MetricMode, \
    compute_metrics_all_classes, compute_metrics_project

path = Path(__file__).parent.parent / "storage" / "jgrapht-core-0.9.2.txt"

with path.open("r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

path_goals = Path(__file__).parent.parent / "storage" / "goal-output-groundtruth" / "jgrapht-core-0.9.2"
path_llmedico = Path(__file__).parent / "results-translation" / "jgrapht-core-0.9.2"


print(len(lines))
print(lines)
done = []
evaluation_rows = []
for fqn in lines:
    if fqn not in done:
        base = Path(__file__).parent / "results-evalutation" / "jgrapht-core-0.9.2"
        path_out_dir = base
        if not path_out_dir.exists():
            os.makedirs(path_out_dir)

        evaluation_rows.append(evaluate(path_goals / (fqn + "_goal.json"),
                 InputFormat.JDOCTOR,
                 path_llmedico / fqn / "llmedico-condition_translator.json",
                 InputFormat.LLMEDICO,
                 path_out_dir))

# for every class
path_outputfile = base = Path(__file__).parent / "results-evalutation" / "jgrapht-core-0.9.2"
compute_metrics_all_classes(evaluation_rows, "org.jgrapht", path_outputfile, MetricMode("llmedico"))
#for project
compute_metrics_project(evaluation_rows, "org.jgrapht", path_outputfile, MetricMode("llmedico"))




