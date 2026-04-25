import datetime
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import logging

from llmedico.evaluation.evaluation import evaluate, InputFormat, _write_evaluation_rows_by_type
from llmedico.evaluation.result import AssertionRelation
from llmedico.evaluation_metrics.evaluator_metrics import (
    compute_metrics_project,
    MetricMode,
)

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR.parent / "storage"
INPUT_DIR = BASE_DIR.parent.parent / "pyjdoctor" / "data" / "input"

DATE_DEFAULT = "2026-01-21"

path_ground_truth_base = STORAGE_DIR / "goal-output-groundtruth"
path_llmedico_base = BASE_DIR / "results-translation"
path_jdoctor_base = BASE_DIR / "results-translation-jdoctor"
path_output_base = BASE_DIR / "results-evaluation"


projects = [
    "commons-collections4-4.1",
    "commons-math3-3.6.1",
    "freecol-0.11.6",
    "gs-core-1.3",
    "guava-19.0",
    "jgrapht-core-0.9.2",
    "plume-lib-1.1.0",
    #"commons-lang-rel-commons-lang-3.20.0",
]


# ============================================================
# SCENARIO DEFINITION
# ============================================================

@dataclass
class EvaluationScenario:
    name: str
    left_provider: str   # "ground_truth" | "jdoctor"
    right_provider: str  # "llmedico"
    date_left: str | None
    date_right: str
    metric_mode: str


SCENARIOS = [

    # # 1. Ground Truth vs LLMedico
    # EvaluationScenario(
    #     name="groundtruth_vs_llmedico",
    #     left_provider="ground_truth",
    #     right_provider="llmedico",
    #     date_left=None,
    #     date_right=DATE_DEFAULT,
    #     metric_mode="llmedico",
    # ),

    # # 2. JDoctor vs LLMedico
    # EvaluationScenario(
    #     name="jdoctor_vs_llmedico",
    #     left_provider="jdoctor",
    #     right_provider="llmedico",
    #     date_left=DATE_DEFAULT,
    #     date_right=DATE_DEFAULT,
    #     metric_mode="jdoctor",
    # ),

    # # 3. JDoctor NEW vs LLMedico NEW
    # EvaluationScenario(
    #     name="jdoctor_new_vs_llmedico_new",
    #     left_provider="jdoctor",
    #     right_provider="llmedico",
    #     date_left="2026-02-01",
    #     date_right="2026-02-01",
    #     metric_mode="jdoctor",
    # ),

    # 4. Ground Truth vs JDoctor
    EvaluationScenario(
        name="groundtruth_vs_jdoctor",
        left_provider="ground_truth",
        right_provider="jdoctor",
        date_left=None,
        date_right=DATE_DEFAULT,
        metric_mode="jdoctor",
    ),

]

def resolve_format(provider: str) -> InputFormat:
    if provider == "llmedico":
        return InputFormat.LLMEDICO
    else:
        # ground_truth and jdoctor both use JDOCTOR format
        return InputFormat.JDOCTOR

# ============================================================
# PATH RESOLUTION
# ============================================================

def ground_truth_file(project: str, class_: str) -> Path:
    return path_ground_truth_base / project / f"{class_}_goal.json"


def llmedico_file(project: str, class_: str, date: str) -> Path:
    return (
        path_llmedico_base
        / date
        / f"{project}-{date}"
        / class_
        / "llmedico-condition_translator.json"
    )


def jdoctor_file(project: str, class_: str, date: str) -> Path:
    return (
        path_jdoctor_base
        / date
        / f"{project}-{date}"
        / class_
        / "toradocu-condition_translator.json"
    )


def resolve_file(provider: str, project: str, class_: str, date: str | None) -> Path:
    if provider == "ground_truth":
        return ground_truth_file(project, class_)
    elif provider == "jdoctor":
        return jdoctor_file(project, class_, date)
    elif provider == "llmedico":
        return llmedico_file(project, class_, date)
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ============================================================
# EVALUATION LOGIC
# ============================================================

def load_classes(project: str) -> list[str]:
    path_classes = STORAGE_DIR / "projects_txt" / "jdoctor" / f"{project}.txt"
    with path_classes.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run_scenario(scenario: EvaluationScenario):

    print(f"\n==============================")
    print(f"Running scenario: {scenario.name}")
    print(f"==============================")

    output_root = path_output_base / scenario.name
    output_root.mkdir(parents=True, exist_ok=True)

    #all_rows = []
    all_rows_nested = []  # <- list of class lists
    for project in projects:

        print(f"\nProject: {project}")
        classes_ = load_classes(project)

        project_rows = []

        for class_ in classes_:

            left_file = resolve_file(
                scenario.left_provider,
                project,
                class_,
                scenario.date_left,
            )

            right_file = resolve_file(
                scenario.right_provider,
                project,
                class_,
                scenario.date_right,
            )

            rows = evaluate(
                left_file,
                resolve_format(scenario.left_provider),
                right_file,
                resolve_format(scenario.right_provider),
                output_root / project,
            )

            project_rows.append(rows)

        compute_metrics_project(
            project_rows,  # keep nested structure
            project,
            output_root,
            MetricMode(scenario.metric_mode),
        )

        all_rows_nested.extend(project_rows)

    compute_metrics_project(
        all_rows_nested,  # must stay nested
        "all_projects",
        output_root,
        MetricMode(scenario.metric_mode),
    )

    flat_rows = [
        row for rows_class in all_rows_nested for row in rows_class
    ]

    # relation breakdown
    relation_counts = Counter(row.relation for row in flat_rows)
    logger.warning(relation_counts)

    # write relation-specific CSV
    types = [
        AssertionRelation("equivalent"),
        # AssertionRelation("stronger"),
        # AssertionRelation("identical"),
        # AssertionRelation("equivalent"),
        # AssertionRelation("unexpected"),
        # AssertionRelation("unsupported"),
        # AssertionRelation("incomparable"),
    ]

    _write_evaluation_rows_by_type(
        flat_rows,
        types,
        output_root / "relevant_assertion_relations-all_projects.csv",
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    for scenario in SCENARIOS:
        run_scenario(scenario)
