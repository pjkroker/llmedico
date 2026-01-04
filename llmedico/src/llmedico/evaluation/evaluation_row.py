from dataclasses import dataclass
from typing import Optional

from llmedico.evaluation.result import AssertionRelation


@dataclass
class EvaluationRow:
    class_name: str
    method_signature: str
    expected: str
    generated: str
    relation: AssertionRelation
    reason: Optional[str] = None
