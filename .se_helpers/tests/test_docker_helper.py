import json
import logging
from pathlib import Path

from se_helpers.docker_helper import DockerHelper


def test_docker_builder_with_logging():
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename=Path(__file__).parent / "data" / "output" / "test_docker_helper.log", filemode='w', force=True)
    container = DockerHelper()
    path_docker_build_log = Path(__file__).parent / "data" / "output" / "build.log"
    container.build_container(context_path=".",
                              dockerfile=Path(__file__).parent / "data" / "dockerfile",
                              tag="my_dockerfile_test",
                              log_path=path_docker_build_log,)
    assert path_docker_build_log.is_file()
    with open(path_docker_build_log, "r") as file:
        data = file.read()
    assert "Successfully built" in data