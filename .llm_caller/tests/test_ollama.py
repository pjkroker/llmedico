from llm_caller.models.ollama import Ollama


def test_ollama_model_connection():
    llama2 = Ollama("llama2")
    prompt = "Hello"
    result = llama2.generate(prompt, system_prompt="You are a Java Assistant")

    # Assert that the result contains expected parts
    assert isinstance(result, str)
    assert "Hello" in result

