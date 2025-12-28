from llm_caller.models.litellm import LiteLLMModel


def test_litellm_model_connection():
    llama2 = LiteLLMModel("ollama/llama3.2")
    prompt = "Hello"
    result = llama2.generate(prompt)

    # Assert that the result contains expected parts
    assert isinstance(result, str)
    assert "Hello" in result

