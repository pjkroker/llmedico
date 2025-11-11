from llm_caller.models.ollama import Ollama


def test_ollama_model_connection():
    llama2 = Ollama("llama2")
    prompt = "Hello"
    result = llama2.generate(prompt)

    # Assert that the result contains expected parts
    assert isinstance(result, str)
    assert "Hello" in result

