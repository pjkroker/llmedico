import os
import datetime
from pathlib import Path

from llmedico.evaluation.evaluation import evaluate, InputFormat
from llmedico.evaluation.evaluator import evaluate_class
from llmedico.evaluation_metrics.evaluation_metrics_writer import EvaluationMetricsCSVWriter
from llmedico.evaluation_metrics.evaluator_metrics import _compute_metrics_class, MetricMode, \
    compute_metrics_all_classes, compute_metrics_project

input_ = Path(__file__).parent.parent.parent / "pyjdoctor" / "data" / "input"
projects = {"commons-collections4-4.1":
                {"data_dir": input_ / "commons-collections4-4.1-src" / "src",
                 "jar_dir": input_ / "commons-collections4-4.1-src" / "target" / "commons-collections4-4.1.jar",
                 "jdoc_data_dir_a": input_ / "commons-collections4-4.1-src",
                 "jdoc_source_dir_r": "/input/src/main/java",
                 "jdoc_class_dir_r": "/input/target/classes"},
            "commons-math3-3.6.1":{
                "data_dir": input_ / "commons-math3-3.6.1-src" / "src",
                "jar_dir": input_ / "commons-math3-3.6.1-src" / "target" / "commons-math3-3.6.1.jar",
                "jdoc_data_dir_a": input_ / "commons-math3-3.6.1-src",
                "jdoc_source_dir_r": "/input/src/main/java",
                "jdoc_class_dir_r": "/input/target/classes"},
            "freecol-0.11.6":{
                "data_dir": input_ / "freecol-0.11.6" / "src",
                "jar_dir": input_ / "freecol-0.11.6" / "FreeCol.jar",
                "jdoc_data_dir_a": input_ / "freecol-0.11.6",
                "jdoc_source_dir_r": "/input/src/",
                "jdoc_class_dir_r": "/input/build"},
            "gs-core-1.3": {
                "data_dir": input_ / "gs-core-1.3" / "gs-core-1.3-sources",
                "jar_dir": input_ / "gs-core-1.3" / "gs-core-1.3.jar",
                "jdoc_data_dir_a": input_ / "gs-core-1.3",
                "jdoc_source_dir_r": "/input/gs-core-1.3-sources/",
                "jdoc_class_dir_r": "/input/gs-core-1.3"},
            "guava-19.0": {
                "data_dir": input_ / "guava-19.0" / "guava" / "src",
                "jar_dir": input_ / "guava-19.0" / "guava" / "target" / "guava-19.0.jar",
                "jdoc_data_dir_a": input_ / "guava-19.0",
                "jdoc_source_dir_r": "/input/guava/src",
                "jdoc_class_dir_r": "/input/guava/target/classes"},
            "jgrapht-core-0.9.2": {
                "data_dir": input_ / "jgrapht-0.9.2" / "jgrapht-core" / "src",
                "jdoc_data_dir_a": input_ / "jgrapht-0.9.2" / "jgrapht-core",
                "jdoc_source_dir_r": "/input/src/main/java",
                "jdoc_class_dir_r" : "/input/target/classes",
                "jar_dir": input_ / "jgrapht-0.9.2" / "jgrapht-core" / "target" / "jgrapht-core-0.9.2.jar",
                "class_dir": input_ / "jgrapht-0.9.2" / "jgrapht-core" / "target" / "classes"},
            "plume-lib-1.1.0": {
                "data_dir": input_ / "plume-lib-1.1.0" / "java" / "src",
                "jar_dir": input_ / "plume-lib-1.1.0" / "java" / "plume.jar",
                "jdoc_data_dir_a": input_ / "plume-lib-1.1.0" / "java" / "src",
                "jdoc_source_dir_r": "/input/",
                "jdoc_class_dir_r": "/input/"
            }
            }

path_ground_truth_base = Path(__file__).parent.parent / "storage" / "goal-output-groundtruth"
path_llmedico_base = path_llmedico = Path(__file__).parent / "results-translation"
path_jdoctor_base = Path(__file__).parent / "results-translation-jdoctor"
path_out_base = Path(__file__).parent / "results-evalutation"
date_eval = "-2026-01-11"
#TODO fix these for comparison
done_jdoocc = [ "commons-math3-3.6.1", "freecol-0.11.6", "guava-19.0","plume-lib-1.1.0" ] #["commons-collections4-4.1", "commons-math3-3.6.1", "freecol-0.11.6", "gs-core-1.3", "guava-19.0", "plume-lib-1.1.0"]
done = ["commons-math3-3.6.1", "freecol-0.11.6", "gs-core-1.3", "guava-19.0", "jgrapht-core-0.9.2", "plume-lib-1.1.0"]
date = datetime.date.today()
evaluation_rows = []
for project in projects:
    print(project)
    evaluation_rows_project = []
    path_outputfile = path_out_base / (project + date_eval)  # TODO
    if project not in done:
        path_classes = Path(__file__).parent.parent / "storage" / "projects_txt" / (project + ".txt")
        with path_classes.open("r", encoding="utf-8") as f:
            classes_ = [line.strip() for line in f if line.strip()]
        print(classes_)
        for class_ in classes_:
            evaluation_rows_project.append(evaluate( path_jdoctor_base / (project + date_eval) / class_ / "toradocu-condition_translator.json", #path_ground_truth_base / project / (class_ + "_goal.json"),
                                            InputFormat.JDOCTOR,
                                            path_llmedico_base / (project + date_eval) / class_ / "llmedico-condition_translator.json",
                                            InputFormat.LLMEDICO,
                                            path_outputfile))

        compute_metrics_all_classes(evaluation_rows_project, project, path_outputfile, MetricMode("relaxed"))

        compute_metrics_project(evaluation_rows_project, project, path_outputfile, MetricMode("relaxed"))

        evaluation_rows.append([row for rows_class in evaluation_rows_project for row in rows_class])

compute_metrics_project(evaluation_rows, "all_projects", path_out_base, MetricMode("relaxed"))

# # for every class
# path_outputfile = Path(__file__).parent / "results-evalutation" / "commons-math3-3.6.1-2026-01-10"
# compute_metrics_all_classes(evaluation_rows, "org.jgrapht", path_outputfile, MetricMode("llmedico"))
# #for project
# compute_metrics_project(evaluation_rows, "org.jgrapht", path_outputfile, MetricMode("llmedico"))
#

# path = Path(__file__).parent.parent / "storage" / "projects_txt" / "commons-math3-3.6.1.txt"
#
#
# with path.open("r", encoding="utf-8") as f:
#     lines = [line.strip() for line in f if line.strip()]
#
# path_goals = Path(__file__).parent.parent / "storage" / "goal-output-groundtruth" / "commons-math3-3.6.1"
# path_llmedico = Path(__file__).parent / "results-translation" / "commons-math3-3.6.1-2026-01-10"
#
#
# print(len(lines))
# print(lines)
# done = []
# evaluation_rows = []
# for fqn in lines:
#     if fqn not in done:
#         base = Path(__file__).parent / "results-evalutation" / "commons-math3-3.6.1-2026-01-10"
#         path_out_dir = base
#         if not path_out_dir.exists():
#             os.makedirs(path_out_dir)
#
#         evaluation_rows.append(evaluate(path_goals / (fqn + "_goal.json"),
#                  InputFormat.JDOCTOR,
#                  path_llmedico / fqn / "llmedico-condition_translator.json",
#                  InputFormat.LLMEDICO,
#                  path_out_dir))

# for every class
# path_outputfile = Path(__file__).parent / "results-evalutation" / "commons-math3-3.6.1-2026-01-10"
# compute_metrics_all_classes(evaluation_rows, "org.jgrapht", path_outputfile, MetricMode("llmedico"))
# #for project
# compute_metrics_project(evaluation_rows, "org.jgrapht", path_outputfile, MetricMode("llmedico"))




