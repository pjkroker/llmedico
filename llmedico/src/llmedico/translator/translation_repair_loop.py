import logging
from typing import Optional

from llm_caller.utils.processing import extract_code_by_language, extract_list_raw

logger = logging.getLogger(__name__)

class TranslationRepairLoop:
    def __init__(self, translator, validator, max_iters=5):
        self.translator = translator
        self.validator = validator
        self.max_iters = max_iters

    def _first_aid_repair(self, raw_response: str, errors: list[str], expected_len: int) -> Optional[str]:
        if errors[0].startswith("No code snippets found for language"):
            logger.debug("Trying to fix output format")
            try:
                broken_response = extract_code_by_language(raw_response, "")
                fixed_response = "```json\n" + broken_response[0] + "\n```"
            except RuntimeError as e:
                broken_response = extract_list_raw(raw_response)
                if broken_response is not None:
                    fixed_response = "```json\n" + broken_response + "\n```"

                else: return None

            errors = self.validator.validate(fixed_response, expected_len)
            if errors:
                self._first_aid_repair(fixed_response, errors, expected_len)
            else: return fixed_response
        logger.debug("Could not manually fix llm response!")
        return None

    def translate_with_repair(self, javadoc: str, method_name: str, output_template: str, parameters: list[str], return_type:str, method_selection:str, mode: str, errors: list[str], expected_len: int, previous_output: str) -> str:
        logger.debug('Trying to fix initial solution with repair loop.')
        i = 0
        result = ""
        while errors and i < self.max_iters:
            i += 1
            logger.info("Repair loop iteration %d", i)
            result = self.translator._translate_once(javadoc, method_name, output_template, parameters,return_type, method_selection, mode, errors, previous_output)
            errors = self.validator.validate(result, expected_len)
            previous_output = result

        if not errors:
            logger.info(f"Repair successful, after {i} out of a maximum of {self.max_iters} iterations.")
            return result
        else:
            logger.debug("Repair loop failed. Try to fix it manually.")
            repair = self._first_aid_repair(result, errors, expected_len)
            if repair:
                logger.warning(f"Could fix manually but repair loop failed, after {i} out of a maximum of {self.max_iters} iterations.")
                return repair

            logger.warning(f"Repair failed, after {i} out of a maximum of {self.max_iters} iterations.")
            return "```json\n[]\n```"