from abc import ABC, abstractmethod
from typing import Dict, Any

from abc import ABC, abstractmethod

class Model(ABC):
    """Abstract base class for all LLM model implementations."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model given a prompt."""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} model={self.model_name}>"