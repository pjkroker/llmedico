import logging
from pathlib import Path
import re
import copy
from typing import Iterable, Dict, List

from llm_caller.models.ollama import Ollama
from llm_caller.prompts import PRE_CONDITION_PROMPT, RETURN_CONDITION_PROMPT, THROWS_CONDITION_PROMPT
from llm_caller.utils.processing import extract_java_assertions


ConditionOutput = Dict[str, List[str]]
class Translator():
    PATH_JSON = Path("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/result.json")
    MODE_TO_PROMPT = {
        "param": PRE_CONDITION_PROMPT,
        "return": RETURN_CONDITION_PROMPT,
        "throws": THROWS_CONDITION_PROMPT,
    }
    def __init__(self):
        pass
        #self.data = load_json(self.PATH_JSON)

    def translate_javadoc(self, javadoc:str,modes:Iterable[str]) -> ConditionOutput:
        """
        Generates for a given Java Docstring meaningful Java assertions.
        :param javadoc:
        :return:
        """
        llm = Ollama("llama3.1")
        output: ConditionOutput = {mode: [] for mode in modes}

        for mode in modes:
            if mode not in self.MODE_TO_PROMPT:
                raise ValueError(f"Unsupported mode: {mode}")

            logging.debug(f"translating for current mode: {mode}")
            prompt = self.MODE_TO_PROMPT[mode].format(javadoc=javadoc)
            result = llm.generate(prompt)
            logging.debug(f"llm generated the following response: {result}")
            extracted_assertion = extract_java_assertions(result)
            logging.debug(f"extracted the following assertions: {extracted_assertion}")
            output[mode].append(extracted_assertion[0])
        logging.debug(f"final Conditions: {output}")
        return output

    @staticmethod
    def _get_modes():
        pass

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
