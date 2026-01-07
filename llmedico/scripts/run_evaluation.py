import os
from pathlib import Path

from llmedico.evaluation.evaluation import evaluate, InputFormat

path = Path(__file__).parent.parent / "storage" / "jgrapht-core-0.9.2.txt"

with path.open("r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

path_goals = Path(__file__).parent.parent / "storage" / "goal-output-groundtruth" / "jgrapht-core-0.9.2"
path_llmedico = Path(__file__).parent / "results-translation" / "jgrapht-core-0.9.2"


print(len(lines))
print(lines)
done = []
for fqn in lines:
    if fqn not in done:
        base = Path(__file__).parent / "results-evalutation" / "jgrapht-core-0.9.2"
        path_out_dir = base
        if not path_out_dir.exists():
            os.makedirs(path_out_dir)

        evaluate(path_goals / (fqn + "_goal.json"),
                 InputFormat.JDOCTOR,
                 path_llmedico / fqn / "llmedico-condition_translator.json",
                 InputFormat.LLMEDICO,
                 path_out_dir)