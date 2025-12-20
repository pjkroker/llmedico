from abc import ABC, abstractmethod
from typing import List
from conditions.model import Condition

class ConditionConverter(ABC):

    @abstractmethod
    def convert(self, conditions: List[Condition]):
        pass
