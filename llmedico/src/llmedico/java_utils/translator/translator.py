import logging
logger = logging.getLogger(__name__)
from pathlib import Path
import re
import copy
from typing import Iterable, Dict, List

from llm_caller.models.ollama import Ollama
from llm_caller.prompts import PRE_CONDITION_PROMPT, RETURN_CONDITION_PROMPT, THROWS_CONDITION_PROMPT
from llm_caller.utils.processing import extract_java_assertions


ConditionOutput = Dict[str, List[str]]

class ToradocuCondition:
    def __init__(self, java_assertion: str, kind: str = "PRE"):
        self.java_assertion = java_assertion.strip()
        self.kind = kind
        self.comment = self._extract_comment()
        self.condition = self._extract_condition()

    def _extract_condition(self) -> str:
        """
        Extracts the logical condition from:
        assert <condition>; // comment
        """
        # Remove leading 'assert'
        assertion = self.java_assertion
        if not assertion.startswith("assert"):
            raise ValueError(f"Not a valid Java assert: {assertion}")

        # Remove 'assert' and everything after ';'
        without_assert = assertion[len("assert"):].strip()
        condition_part = without_assert.split(";", 1)[0].strip()

        if not condition_part:
            raise ValueError("Empty assertion condition")

        return condition_part

    def _extract_comment(self) -> str:
        """
        Extracts the human-readable comment from:
        //description: ...
        """
        if "//" not in self.java_assertion:
            return ""

        comment_part = self.java_assertion.split("//", 1)[1].strip()

        # Remove optional prefixes like 'description:'
        comment_part = re.sub(
            r"^(description|desc|comment)\s*:\s*",
            "",
            comment_part,
            flags=re.IGNORECASE,
        )

        return comment_part

    def to_dict(self) -> dict:
        """
        Converts to Toradocu-style JSON representation.
        """
        return {
            "comment": self.comment,
            "kind": self.kind,
            "condition": self.condition,
        }

    def get_comment(self):
        return self.comment
    def get_kind(self):
        return self.kind
    def get_condition(self):
        return self.condition




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

            logger.debug(f"translating for current mode: {mode}")
            prompt = self.MODE_TO_PROMPT[mode].format(javadoc=javadoc)
            result = llm.generate(prompt)
            logger.debug(f"llm generated the following response: {result}")
            extracted_assertion = extract_java_assertions(result)
            logger.debug(f"extracted the following assertions: {extracted_assertion}")
            output[mode].append(extracted_assertion[0])
        logger.debug(f"final Conditions: {output}")
        return output


    @staticmethod
    def assertion_to_json(assertion: str) -> dict:
        """
        Convert a Java assertion statement into the Randoop JSON structure.

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
