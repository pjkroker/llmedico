import logging
logger = logging.getLogger(__name__)
from .model import Model
import ollama

class Ollama(Model):
    """Implementation of BaseModel for local Ollama models."""

    def __init__(self, model_name, temperature: float, top_p: float, top_k: int, repeat_penalty: float):
        """
        model_name: the name of the model installed in Ollama (e.g. 'llama3')
        """
        super().__init__(model_name)
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty

    def generate(self, prompt: str, system_prompt: str="Rules and behavior", temperature: float = 0.7, **kwargs) -> str:
        logger.debug("Ollama: system prompt is: %s", system_prompt)
        logger.info("Ollama: user prompt: %s", prompt)
        response = ollama.chat(
            model=self.model_name,
            messages=[{ "role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}],
            options={"temperature": self.temperature, "top_p": self.top_p, "top_k": self.top_k, **kwargs}
        )
        striped_response = response["message"]["content"].strip()
        logger.debug(f"raw response from {self.model_name}: {str(striped_response)}")
        return striped_response
