import json
from pathlib import Path


def analyze_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    methods = len(data)
    return_tags = 0
    param_tags = 0
    throws_tags = 0

    for method in data:
        if method.get("returnTag"):
            return_tags += 1
        param_tags += len(method.get("paramTags", []))
        throws_tags += len(method.get("throwsTags", []))

    return methods, return_tags, param_tags, throws_tags


def analyze_directory_flat(directory_path):
    """For ground truth: JSON files directly inside project folder"""
    total_methods = 0
    total_return_tags = 0
    total_param_tags = 0
    total_throws_tags = 0
    total_num_class = 0

    for filepath in Path(directory_path).glob("*.json"):
        if "$" in filepath.name:
            continue

        total_num_class += 1
        m, r, p, t = analyze_json_file(filepath)

        total_methods += m
        total_return_tags += r
        total_param_tags += p
        total_throws_tags += t

    return {
        "methods": total_methods,
        "return_tags": total_return_tags,
        "param_tags": total_param_tags,
        "throws_tags": total_throws_tags,
        "num_class": total_num_class,
    }


def analyze_directory_recursive(directory_path):
    """For Jdoctor: JSON files nested in class subdirectories"""
    total_methods = 0
    total_return_tags = 0
    total_param_tags = 0
    total_throws_tags = 0
    total_num_class = 0

    for filepath in Path(directory_path).rglob("toradocu-condition_translator.json"):
        if "$" in str(filepath):
            continue

        total_num_class += 1
        m, r, p, t = analyze_json_file(filepath)

        total_methods += m
        total_return_tags += r
        total_param_tags += p
        total_throws_tags += t

    return {
        "methods": total_methods,
        "return_tags": total_return_tags,
        "param_tags": total_param_tags,
        "throws_tags": total_throws_tags,
        "num_class": total_num_class,
    }


if __name__ == "__main__":
    path_ground_truth_base = Path(__file__).parent.parent / "storage" / "goal-output-groundtruth"
    path_jdoc_results_base = Path(__file__).parent / "results-translation-jdoctor" / "2026-01-21"

    projects = [
        "commons-collections4-4.1",
        "commons-math3-3.6.1",
        "freecol-0.11.6",
        "gs-core-1.3",
        "guava-19.0",
        "jgrapht-core-0.9.2",
        "plume-lib-1.1.0"
    ]

    for project in projects:
        print(f"\nAnalyzing {project} (Ground Truth)")
        totals = analyze_directory_flat(path_ground_truth_base / project)

        print("=== OVERALL TOTALS ===")
        print(f"Total classes:     {totals['num_class']}")
        print(f"Total methods:     {totals['methods']}")
        print(f"Total return tags: {totals['return_tags']}")
        print(f"Total param tags:  {totals['param_tags']}")
        print(f"Total throws tags: {totals['throws_tags']}")

        # print(f"\nAnalyzing {project} (Jdoctor)")
        # totals = analyze_directory_recursive(
        #     path_jdoc_results_base / f"{project}-2026-01-21"
        # )
        #
        # print("=== OVERALL TOTALS ===")
        # print(f"Total classes:     {totals['num_class']}")
        # print(f"Total methods:     {totals['methods']}")
        # print(f"Total return tags: {totals['return_tags']}")
        # print(f"Total param tags:  {totals['param_tags']}")
        # print(f"Total throws tags: {totals['throws_tags']}")
