import logging
logger = logging.getLogger(__name__)
from .model import Model
import ollama

class Ollama(Model):
    """Implementation of BaseModel for local Ollama models."""

    def __init__(self, model_name):
        """
        model_name: the name of the model installed in Ollama (e.g. 'llama3')
        """
        super().__init__(model_name)

    def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
        logger.debug("Ollama: generating prompt: %s", prompt)
        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature, **kwargs}
        )
        striped_response = response["message"]["content"].strip()
        logger.debug(f"raw response from {self.model_name}: {str(striped_response)}")
        return striped_response
