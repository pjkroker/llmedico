import os
from pathlib import Path

from click.testing import CliRunner
from llmedico.cli import main as cli
from ..test_with_llm import LLM_TESTS

def test_cli_help_shows_commands():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "translate" in result.output
    assert "evaluate" in result.output

def test_cli_evaluate():
    runner = CliRunner()
    path_exp = Path(__file__).parent.parent / "data" / "input" / "cli" / "org.jgrapht.alg.KShortestPaths_goal.json"
    path_gen = Path(__file__).parent.parent / "data" / "input" / "cli" / "llmedico-condition_translator.json"
    path_out = Path(__file__).parent.parent / "data" / "output" / "cli"
    path_out_file = path_out / "llmedico-evaluation-org.jgrapht.alg.KShortestPaths.csv"
    if path_out_file.exists():
        os.remove(path_out_file)
    result = runner.invoke(cli, ["evaluate",
                                 "--expected", path_exp,
                                 "--expected-type", "jdoctor",
                                 "--generated", path_gen,
                                 "--generated-type", "llmedico",
                                 "--out", path_out])

    assert path_out_file.exists()

def test_cli_translate():
    if LLM_TESTS:
        runner = CliRunner()
        target_class = "com.example.assertions.TestJavaAssertion"
        path_src = Path(__file__).parent.parent / "data" / "input" / "test-project" / "src" / "main" / "java"
        path_jar = Path(__file__).parent.parent / "data" / "input" / "test-project" / "target" / "assertion-parser-1.0-SNAPSHOT.jar"
        path_out = Path(__file__).parent.parent / "data" / "output" / "cli"

        result = runner.invoke(cli, ["translate",
                                     "--target-class", target_class,
                                     "--src-dir", path_src,
                                     "--jar-dir", path_jar,
                                     "--out-dir", path_out])
        print(result)

