import logging
logger = logging.getLogger(__name__)
from .model import Model
import ollama

class Ollama(Model):
    """Implementation of BaseModel for local Ollama models."""

    def __init__(self, model_name: str, temperature: float = 0.7, **kwargs):
        """
        model_name: the name of the model installed in Ollama (e.g. 'llama3')
        """
        super().__init__(model_name)

        # Default generation options
        self.options = {
            "temperature": temperature,
            **kwargs,
        }

    def generate(self, prompt: str, system_prompt: str="Rules and behavior", temperature: float = 0.7, **kwargs) -> str:
        logger.debug("Ollama: system prompt is: %s", system_prompt)
        logger.info("Ollama: user prompt: %s", prompt)
        response = ollama.chat(
            model=self.model_name,
            messages=[{ "role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}],
            options=self.options,
        )
        striped_response = response["message"]["content"].strip()
        logger.debug(f"raw response from {self.model_name}: {str(striped_response)}")
        return striped_response
