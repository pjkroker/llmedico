"""
Simple Toradocu precision/recall calculator.
This version stays very close to the original Toradocu script,
but exposes the computation as reusable Python functions.
"""

import csv
from pprint import pprint

COLUMNS = [
    'CORRECT PARAM CONDITIONS',
    'WRONG PARAM CONDITIONS',
    'UNEXPECTED PARAM CONDITIONS',
    'MISSING PARAM CONDITIONS',
    'CORRECT THROWS CONDITIONS',
    'WRONG THROWS CONDITIONS',
    'UNEXPECTED THROWS CONDITIONS',
    'MISSING THROWS CONDITIONS',
    'CORRECT RETURN CONDITIONS',
    'WRONG RETURN CONDITIONS',
    'UNEXPECTED RETURN CONDITIONS',
    'MISSING RETURN CONDITIONS',
]


def compute_metrics(csv_path, additional_missing=0):
    results = {column: 0 for column in COLUMNS}

    with open(csv_path) as f:
        reader = csv.reader(f)

        for row in reader:
            results['CORRECT PARAM CONDITIONS'] += int(row[7])
            results['WRONG PARAM CONDITIONS'] += int(row[8])
            results['UNEXPECTED PARAM CONDITIONS'] += int(row[9])
            results['MISSING PARAM CONDITIONS'] += int(row[10])

            results['CORRECT THROWS CONDITIONS'] += int(row[3])
            results['WRONG THROWS CONDITIONS'] += int(row[4])
            results['UNEXPECTED THROWS CONDITIONS'] += int(row[5])
            results['MISSING THROWS CONDITIONS'] += int(row[6])

            results['CORRECT RETURN CONDITIONS'] += int(row[11])
            results['WRONG RETURN CONDITIONS'] += int(row[12])
            results['UNEXPECTED RETURN CONDITIONS'] += int(row[13])
            results['MISSING RETURN CONDITIONS'] += int(row[14])

    pprint(results)

    # Extract counts
    correct_param = results['CORRECT PARAM CONDITIONS']
    wrong_param = results['WRONG PARAM CONDITIONS']
    unexpected_param = results['UNEXPECTED PARAM CONDITIONS']
    missing_param = results['MISSING PARAM CONDITIONS']

    correct_throws = results['CORRECT THROWS CONDITIONS']
    wrong_throws = results['WRONG THROWS CONDITIONS']
    unexpected_throws = results['UNEXPECTED THROWS CONDITIONS']
    missing_throws = results['MISSING THROWS CONDITIONS']

    correct_return = results['CORRECT RETURN CONDITIONS']
    wrong_return = results['WRONG RETURN CONDITIONS']
    unexpected_return = results['UNEXPECTED RETURN CONDITIONS']
    missing_return = results['MISSING RETURN CONDITIONS']

    # Compute per-category precision and recall
    def precision(correct, wrong, unexpected):
        total = correct + wrong + unexpected
        return None if total == 0 else correct / total

    def recall(correct, wrong, missing):
        total = correct + wrong + missing
        return 1.0 if total == 0 else correct / total

    metrics = {
        "param_precision": precision(correct_param, wrong_param, unexpected_param),
        "param_recall": recall(correct_param, wrong_param, missing_param),

        "return_precision": precision(correct_return, wrong_return, unexpected_return),
        "return_recall": recall(correct_return, wrong_return, missing_return),

        "throws_precision": precision(correct_throws, wrong_throws, unexpected_throws),
        "throws_recall": recall(correct_throws, wrong_throws, missing_throws),
    }

    # Overall metrics
    overall_correct = correct_param + correct_return + correct_throws
    overall_wrong = wrong_param + wrong_return + wrong_throws
    overall_unexpected = unexpected_param + unexpected_return + unexpected_throws
    overall_missing = missing_param + missing_return + missing_throws + additional_missing

    if overall_correct + overall_wrong + overall_unexpected == 0:
        overall_precision = 0.0
    else:
        overall_precision = overall_correct / (overall_correct + overall_wrong + overall_unexpected)

    if overall_correct + overall_wrong + overall_missing == 0:
        overall_recall = 0.0
    else:
        overall_recall = overall_correct / (overall_correct + overall_wrong + overall_missing)

    if overall_precision + overall_recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall)

    metrics.update({
        "overall_precision": overall_precision,
        "overall_recall": overall_recall,
        "overall_f1": f1,
    })

    return metrics


# Optional CLI use
if __name__ == "__main__":
    import sys

    if len(sys.argv) not in (2, 3):
        print("Usage: python toradocu_metrics.py stats.csv [additional_missing]")
        sys.exit(1)

    csv_path = sys.argv[1]
    additional_missing = int(sys.argv[2]) if len(sys.argv) == 3 else 0

    metrics = compute_metrics(csv_path, additional_missing)
    print(metrics)
