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
        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature, **kwargs}
        )
        return response["message"]["content"].strip()
