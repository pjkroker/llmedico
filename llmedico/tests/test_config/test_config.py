from llmedico.config.config import Config

def test_config():
    llm_config = Config().section("config")
    assert llm_config["model"] == "provider/model"
    config = Config()
    translation_config = config.section("translation")
    assert translation_config.get("iteration_repairloop") == 5
