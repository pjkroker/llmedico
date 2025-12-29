from pathlib import Path

from llmedico.config.config import Config

def test_config():
    llm_config = Config(Path(__file__).parent / "config.toml").section("config")
    assert llm_config["model"] == "provider/model"
    config = Config(Path(__file__).parent / "config.toml")
    translation_config = config.section("translation")
    assert translation_config.get("iteration_repairloop") == 5
