from pathlib import Path

from se_helpers.files import*
from se_helpers.files.files import load_json
from llm_caller.models.ollama import Ollama
from llm_caller.prompts import GEN_JAVA_ASSERTION_PROMPT, GEN_JAVA_ASSERTION_PROMPT_WITH_CODE, GEN_RANDOOP_PRE_CONDITION_PROMPT
from llm_caller.utils.processing import extract_code_by_language
from llmedico.java_utils.javapy import JavaParser

class Translator():
    PATH_JSON = Path("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/result.json")

    def __init__(self):
        self.data = load_json(self.PATH_JSON)

    def translate_javadoc(self, javadoc:str) -> list:
        """
        Generates for a given Java Docstring meaningful Java assertions.
        :param javadoc:
        :return:
        """
        #java_doc = self.data[0]["methods"][0]["javadoc"]
        llm = Ollama("llama3.2")
        #prompt = GEN_JAVA_ASSERTION_PROMPT.format(javadoc=javadoc)
        #prompt = GEN_JAVA_ASSERTION_PROMPT_WITH_CODE.format(javacode=javadoc)
        prompt = GEN_RANDOOP_PRE_CONDITION_PROMPT.format(javadoc=javadoc)
        result = llm.generate(prompt)
        extraceted_assertions = extract_code_by_language(result, "java")
        jp = JavaParser()
        # Split each string at \n and flatten
        separated_lines = [line for code in extraceted_assertions for line in code.split('\n')]
        return separated_lines