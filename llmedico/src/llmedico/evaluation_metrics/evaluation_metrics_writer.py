import csv
from pathlib import Path


class EvaluationMetricsCSVWriter:
    def __init__(self, path: Path):
        self.path = path
        self._file = None
        self._writer = None

    def __enter__(self):
        self._file = open(self.path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._file,
            fieldnames=[
                "class_fqn",
                "param_precision",
                "param_recall",
                "return_precision",
                "return_recall",
                "throws_precision",
                "throws_recall",
                "overall_precision",
                "overall_recall",
                "overall_f1",
            ],
        )
        self._writer.writeheader()
        return self

    def write(self, row):
        """
        row is an EvaluationRow
        """
        self._writer.writerow({
            "class_fqn": row.class_fqn,
            "param_precision": row.param_precision,
            "param_recall": row.param_recall,
            "return_precision": row.return_precision,
            "return_recall": row.return_recall,
            "throws_precision": row.throws_precision,
            "throws_recall": row.throws_recall,
            "overall_precision": row.overall_precision,
            "overall_recall": row.overall_recall,
            "overall_f1": row.overall_f1,
        })

    def __exit__(self, exc_type, exc, tb):
        if self._file:
            self._file.close()
        return False
