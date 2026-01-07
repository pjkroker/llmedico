import os
from pathlib import Path

from llmedico.main import main

path = Path(__file__).parent.parent / "storage" / "jgrapht-core-0.9.2.txt"

with path.open("r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

print(len(lines))
print(lines)
done = []
for fqn in lines:
    if fqn not in done:
        base = Path(__file__).parent / "results-translation" / "jgrapht-core-0.9.2"
        path_out_dir = base / fqn
        if not path_out_dir.exists():
            os.makedirs(path_out_dir)
        main(fq_class_name=fqn,
             target_method="dummy",
             path_data_dir=Path("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/jgrapht-jgrapht-0.9.2/jgrapht-core"),
             path_source_dir=None,
             path_class_dir=None,
             path_output_dir=path_out_dir,
             path_jar=Path("/Users/paul/paul_data/projects_cs/ba_versuch1/pyjdoctor/data/input/jgrapht-jgrapht-0.9.2/jgrapht-core/target/jgrapht-core-0.9.2.jar"))