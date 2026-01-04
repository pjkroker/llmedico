from abc import ABC, abstractmethod
from typing import Any

from llmedico.conditions.model import ClassModel


class ClassModelBuilderBase(ABC):

    @abstractmethod
    def build_class(self, data: Any) -> ClassModel:
        pass