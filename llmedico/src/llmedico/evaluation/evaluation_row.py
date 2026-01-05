from dataclasses import dataclass
from typing import Optional

from llmedico.conditions.model import ConditionKind
from llmedico.evaluation.result import AssertionRelation


@dataclass
class EvaluationRow:
    class_name: str
    method_signature: str
    kind_exp: ConditionKind
    name_exp: str
    kind_gen: ConditionKind
    name_gen: str
    expected: str
    generated: str
    relation: AssertionRelation
    reason: Optional[str] = None
