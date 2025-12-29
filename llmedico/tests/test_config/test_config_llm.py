from llmedico.config.config_llm import *

def test_config_llm():
    load_dotenv_if_present(Path(__file__).parent / '.env')
    assert get_api_key("openai") == "hello_world"

