from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

class ConditionKind(Enum):
    PARAM = "PARAM"
    RETURN = "RETURN"
    THROWS = "THROWS"

    @classmethod
    def is_condition_kind(cls, value: str) -> bool:
        return value.upper() in (e.value for e in cls)

@dataclass
class Condition:
    kind: ConditionKind
    expression: str
    content: str #parsed with \n chars
    description: str #llm generated description
    name: Optional[str] = None #return values have no name

@dataclass
class TypeModel:
    qualified_name: str     # org.jgrapht.Graph
    simple_name: str        # Graph
    is_array: bool = False

@dataclass
class ParameterModel:
    name: str
    type: TypeModel
    is_varargs: bool = False

@dataclass
class MethodSignature:
    name: str
    return_type: Optional[TypeModel]
    parameters: List[ParameterModel]

@dataclass
class MethodModel:
    signature: MethodSignature
    declaring_class: ClassModel #his is a type hint referring to a class that will exist later.
    conditions: list[Condition]
    is_constructor: bool = False #type

    @property
    def param_conditions(self):
        return [c for c in self.conditions if c.kind == ConditionKind.PARAM]

    @property
    def return_conditions(self):
        return [c for c in self.conditions if c.kind == ConditionKind.RETURN]

    @property
    def throws_conditions(self):
        return [c for c in self.conditions if c.kind == ConditionKind.THROWS]

@dataclass
class ClassModel:
    package: str
    name: str
    qualified_name: str
    is_array: bool = False
    methods: list[MethodModel] = field(default_factory=list)



