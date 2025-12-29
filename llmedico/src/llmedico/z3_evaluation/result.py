from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AssertionRelation(Enum):
    EQUIVALENT = "equivalent"
    STRONGER = "stronger"
    WEAKER = "weaker"
    INCOMPARABLE = "incomparable"
    UNSUPPORTED = "unsupported"


@dataclass
class EvaluationResult:
    relation: AssertionRelation
    counterexample: Optional[dict] = None
    reason: Optional[str] = None
