from pathlib import Path
import re
import copy

from se_helpers.files import*
from se_helpers.files.files import load_json
from llm_caller.models.ollama import Ollama
from llm_caller.prompts import GEN_JAVA_ASSERTION_PROMPT, GEN_JAVA_ASSERTION_PROMPT_WITH_CODE, \
    GEN_RANDOOP_PRE_CONDITION_PROMPT, PRE_CONDITION_PROMPT, RETURN_CONDITION_PROMPT
from llm_caller.utils.processing import extract_code_by_language
from llmedico.java_utils.javapy import JavaParser

class Translator():
    PATH_JSON = Path("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/result.json")

    def __init__(self):
        self.data = load_json(self.PATH_JSON)

    def translate_javadoc(self, javadoc:str,mode) -> list:
        """
        Generates for a given Java Docstring meaningful Java assertions.
        :param javadoc:
        :return:
        """
        #java_doc = self.data[0]["methods"][0]["javadoc"]
        llm = Ollama("llama3.2")
        #prompt = GEN_JAVA_ASSERTION_PROMPT.format(javadoc=javadoc)
        #prompt = GEN_JAVA_ASSERTION_PROMPT_WITH_CODE.format(javacode=javadoc)
        #prompt = GEN_RANDOOP_PRE_CONDITION_PROMPT.format(javadoc=javadoc)
        if mode == "pre":
            prompt = PRE_CONDITION_PROMPT.format(javadoc=javadoc)
        elif mode == "return":
            prompt = RETURN_CONDITION_PROMPT.format(javadoc=javadoc)
        elif mode == "throws":
            raise NotImplementedError
        else:
            raise ValueError(mode)
        result = llm.generate(prompt)
        extraceted_assertions = extract_code_by_language(result, "java")
        # Split each string at \n and flatten
        separated_lines = [line for code in extraceted_assertions for line in code.split('\n')]
        return separated_lines

    @staticmethod
    def assertion_to_json(assertion: str) -> dict:
        """
        Convert a Java assertion statement into the JDoctor JSON structure.

        Expected input format:
            assert <condition>; // <description>

        Returns a dict:
            {
              "description": "...",
              "guard": {
                "condition": "...",
                "description": "..."
              }
            }
        """

        assertion = assertion.strip()

        # Regex to capture condition + description
        pattern = r"assert\s+(.*?);(?:\s*//\s*(.*))?$"
        match = re.match(pattern, assertion)

        if not match:
            raise ValueError(f"Invalid assertion format: {assertion}")

        condition = match.group(1).strip()
        raw_description = (match.group(2) or "").strip()

        # Remove "description:" or variations
        cleaned_description = re.sub(r'^\s*(description|desc)\s*:\s*', '', raw_description, flags=re.IGNORECASE)

        return {
            "description": cleaned_description,
            "guard": {
                "condition": condition,
                "description": cleaned_description
            }
        }


    @staticmethod
    def copy_entry_by_method(data, method_name):
        """
        Given a list of JDoctor entries, return a deep copy of the entry
        whose operation.name matches method_name.

        Example:
            copy_entry_by_method(data, "isNotEmpty")
        """

        for entry in data:
            if entry.get("operation", {}).get("name") == method_name:
                return copy.deepcopy(entry)

        raise ValueError(f"No entry found for method name '{method_name}'")
