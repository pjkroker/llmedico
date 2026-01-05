from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AssertionRelation(Enum):
    IDENTICAL = "identical"
    EMPTY = "empty"
    EQUIVALENT = "equivalent"
    DUAL = "dual"
    STRONGER = "stronger"
    WEAKER = "weaker"
    INCOMPARABLE = "incomparable"
    UNSUPPORTED = "unsupported"
    MISSING = "missing"
    UNEXPECTED = "unexpected"


@dataclass
class EvaluationResult:
    relation: AssertionRelation
    counterexample: Optional[dict] = None
    reason: Optional[str] = None
