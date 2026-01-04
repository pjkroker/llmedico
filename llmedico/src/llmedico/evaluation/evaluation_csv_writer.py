import csv
from pathlib import Path

from llmedico.evaluation.evaluation_row import EvaluationRow


class EvaluationCSVWriter:
    def __init__(self, path: Path):
        self.path = path
        self._file = None
        self._writer = None

    def __enter__(self):
        self._file = open(self.path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._file,
            fieldnames=[
                "class",
                "method",
                "expected",
                "generated",
                "relation",
                "reason",
            ],
        )
        self._writer.writeheader()
        return self

    def write(self, row):
        self._writer.writerow({
            "class": row.class_name,
            "method": row.method_signature,
            "expected": row.expected,
            "generated": row.generated,
            "relation": row.relation,
            "reason": row.reason or "",
        })

    def __exit__(self, exc_type, exc, tb):
        # Always close the file, even if an exception occurred
        if self._file:
            self._file.close()
        # Returning False means exceptions (if any) are re-raised
        return False