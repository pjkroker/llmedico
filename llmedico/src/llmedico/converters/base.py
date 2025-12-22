from abc import ABC, abstractmethod

from llmedico.conditions.model import ClassModel, MethodModel


class ConditionConverter(ABC):

    @abstractmethod
    def convert_class(self, cls: ClassModel):
        pass

    @abstractmethod
    def convert_method(self, method: MethodModel):
        pass

