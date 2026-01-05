import json
import logging

from llm_caller.models.model import Model
from llmedico.translator.condition_validator import ConditionValidator
from llmedico.translator.translation_repair_loop import TranslationRepairLoop

logger = logging.getLogger(__name__)
from pathlib import Path
import re
import copy
from typing import Iterable, Dict, List

from llm_caller.models.ollama import Ollama
from llm_caller.prompts import PRE_CONDITION_PROMPT_JSON, THROWS_CONDITION_PROMPT_JSON, PRE_CONDITION_PROMPT_JSON_FEEDBACK, \
    RETURN_CONDITION_PROMPT_JSON_FEEDBACK, THROWS_CONDITION_PROMPT_JSON_FEEDBACK, RETURN_CONDITION_PROMPT_JSON
from llm_caller.utils.processing import extract_java_assertions, extract_conditions

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
        "PARAM": PRE_CONDITION_PROMPT_JSON,
        "RETURN": RETURN_CONDITION_PROMPT_JSON,
        "THROWS": THROWS_CONDITION_PROMPT_JSON,
    }
    MODE_TO_PROMPT_REPAIR = {
        "PARAM": PRE_CONDITION_PROMPT_JSON_FEEDBACK,
        "RETURN": RETURN_CONDITION_PROMPT_JSON_FEEDBACK,
        "THROWS": THROWS_CONDITION_PROMPT_JSON_FEEDBACK,
    }
    def __init__(self, llm: Model, max_iters_repair: int = 5):
        self.llm = llm
        self.max_iters_repair = max_iters_repair
        #self.data = load_json(self.PATH_JSON)

    def translate_javadoc(self, javadoc:str, parameters: list[str], return_type: str, tags,  modes) -> ConditionOutput:
        """
        Generates for a given Java Docstring meaningful Java assertions.
        :param javadoc:
        :return:
        """
        output: ConditionOutput = {mode: [] for mode in modes}

        for mode in modes:
            if mode not in self.MODE_TO_PROMPT:
                raise ValueError(f"Unsupported mode: {mode}")

            current_tags = [tag for tag in tags if tag["tag"] == mode.lower()]
            logger.debug(f"translating for current mode: {mode} with the following tags: \n{tags}")
            expected_len = modes[mode]
            result = self._translate_once(javadoc, parameters, return_type, mode, [], "")
            validator = ConditionValidator("json")
            errors = validator.validate(result, expected_len)
            if errors:
                logger.warning(f"Found the following errors while validating the response: {errors}")
                logger.debug("Start feedback repair loop")
                repair = TranslationRepairLoop(self, validator, self.max_iters_repair)
                result = repair.translate_with_repair(javadoc, parameters, return_type, mode, errors, expected_len, result)
                if result == "```json\n[]\n```": #Provide an empty result if Repair Loop failed
                    logger.warning(f"Could not repair llm response, constructing an empty response!!")
                    for i in range(len(current_tags)):
                        current_tags[i]["assertion"] = ""
                        current_tags[i]["description"] = current_tags[i]["content"]
                    empty_response = ",".join(json.dumps(current_tag) for current_tag in current_tags)
                    result = f"```json\n[{empty_response}]\n```"
            extracted_conditions = extract_conditions(result)
            logger.debug(f"extracted the following assertions: {extracted_conditions}")
            output[mode] = extracted_conditions
        return output

    def _translate_once(self,javadoc: str, parameters: list[str], return_type:str, mode, feedback: [],previous_output: str="") -> str:
        if feedback == [] and previous_output=="":#TODO make better
            prompt = self.MODE_TO_PROMPT[mode].format(javadoc=javadoc, parameters=parameters, return_type=return_type)
        else:
            prompt = self.MODE_TO_PROMPT_REPAIR[mode].format(javadoc=javadoc, parameters=parameters, return_type=return_type, errors=feedback, previous_output=previous_output)
        result = self.llm.generate(prompt)
        return result

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
