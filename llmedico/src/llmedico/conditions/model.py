from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class ConditionKind(Enum):
    PARAM = "PARAM"
    RETURN = "RETURN"
    THROWS = "THROWS"

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
    declaring_class: "ClassModel" #his is a type hint referring to a class that will exist later.
    conditions: list[Condition]
    is_constructor: bool = False

@dataclass
class ClassModel:
    package: str
    name: str
    methods: list[MethodModel] = field(default_factory=list)



