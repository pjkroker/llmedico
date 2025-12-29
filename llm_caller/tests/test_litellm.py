from llm_caller.models.litellm import LiteLLMModel


def test_litellm_model_connection():
    llama2 = LiteLLMModel("ollama/llama3.2")
    prompt = "Hello"
    result = llama2.generate(prompt)

    # Assert that the result contains expected parts
    assert isinstance(result, str)
    assert "Hello" in result

def test_litellm_openai_endpoint():
    llama3 = LiteLLMModel(model_name="openai/llama3.2", api_base="http://localhost:11434/v1", api_key="dummy")

    prompt = " Say Hello!"
    result = llama3.generate(prompt)

    # Assert that the result contains expected parts
    assert isinstance(result, str)
    assert "Hello" in result