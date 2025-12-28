import logging
logger = logging.getLogger(__name__)
from typing import Any
from llm_caller.models.model import  Model
import litellm

class LiteLLMModel(Model):

    def __init__(self, model_name: str, **default_kwargs: Any):
        super().__init__(model_name)
        self.default_kwargs = default_kwargs

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using LiteLLM.
        """
        call_kwargs = { #overwrite internal attributes
            **self.default_kwargs,
            **kwargs,
        }

        response = litellm.completion(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **call_kwargs,
        )
        raw_response = response.choices[0].message["content"]
        logger.debug(f"raw response from {self.model_name}: {str(raw_response)}")
        return raw_response