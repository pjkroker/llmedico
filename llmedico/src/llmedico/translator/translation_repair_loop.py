import logging
logger = logging.getLogger(__name__)

class TranslationRepairLoop:
    def __init__(self, translator, validator, max_iters=5):
        self.translator = translator
        self.validator = validator
        self.max_iters = max_iters

    def translate_with_repair(self, javadoc: str,parameters: list[str], return_type:str,method_selection:str, mode: str, errors, expected_len: int, previous_output: str) -> str:
        logger.debug('Trying to fix initial solution with repair loop.')
        i = 0
        result = ""
        while errors and i < self.max_iters:
            i += 1
            logger.info("Repair loop iteration %d", i)
            result = self.translator._translate_once(javadoc, parameters,return_type, method_selection, mode, errors, previous_output)
            errors = self.validator.validate(result, expected_len)
            previous_output = result

        if not errors:
            logger.info(f"Repair successful, after {i} out of a maximum of {self.max_iters} iterations.")
            return result
        else:
            logger.warning(f"Repair failed, after {i} out of a maximum of {self.max_iters} iterations.")
            return "```json\n[]\n```"