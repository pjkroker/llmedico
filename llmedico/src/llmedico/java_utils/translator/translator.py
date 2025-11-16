from se_helpers.files import*
from se_helpers.files.files import load_json
from llm_caller.models.ollama import Ollama
from llm_caller.prompts import GEN_JAVA_ASSERTION_PROMPT
from llm_caller.utils.processing import extract_code_by_language
from llmedico.java_utils.javapy import JavaParser

class Translator():
    PATH_JSON = "/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/result.json"

    def __init__(self):
        self.data = load_json(self.PATH_JSON)

    def translate(self):
        java_doc = self.data[0]["methods"][0]["javadoc"]
        llama2 = Ollama("llama2")
        prompt = GEN_JAVA_ASSERTION_PROMPT.format(javadoc=java_doc)
        result = llama2.generate(prompt)
        print(result)
        extraceted_code = extract_code_by_language(result, "java")
        print(extraceted_code)
        jp = JavaParser()
        # Split each string at \n and flatten
        separated_lines = [line for code in extraceted_code for line in code.split('\n')]
        print(separated_lines)
        for assertion in separated_lines:
            print(jp.is_valid_java_assert(assertion))