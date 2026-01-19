import csv
import logging
import re
from pathlib import Path

from llmedico.evaluation.evaluation_row import EvaluationRow
logger = logging.getLogger(__name__)

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
                "kind_exp",
                "name_exp",
                "kind_gen",
                "name_gen",
                "expected",
                "generated",
                "relation",
                "reason",
            ],
            quoting=csv.QUOTE_ALL,
        )
        self._writer.writeheader()
        return self

    CONTROL_CHARS = re.compile(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\u2028\u2029]"
    )

    def sanitize(self, s: str) -> str:
        sanitzed = self.CONTROL_CHARS.sub("", s)
        if str != sanitzed: logger.debug(f"assertion contained an illegal character: {sanitzed}")
        return sanitzed

    def write(self, row):
        self._writer.writerow({
            "class": row.class_name,
            "method": row.method_signature,
            "kind_exp": row.kind_exp,
            "name_exp": row.name_exp,
            "kind_gen": row.kind_gen,
            "name_gen": row.name_gen,
            "expected": row.expected,
            "generated": self.sanitize(row.generated),
            "relation": row.relation,
            "reason": row.reason,
        })

    def __exit__(self, exc_type, exc, tb):
        # Always close the file, even if an exception occurred
        if self._file:
            self._file.close()
        # Returning False means exceptions (if any) are re-raised
        return False