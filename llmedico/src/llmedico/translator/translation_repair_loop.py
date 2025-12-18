import logging
logger = logging.getLogger(__name__)

class TranslationRepairLoop:
    def __init__(self, translator, validator, max_iters=5):
        self.translator = translator
        self.validator = validator
        self.max_iters = max_iters

    def translate_with_repair(self, javadoc: str,parameters: list[str], mode: str, errors, expected_len: int, previous_output: str) -> str:
        i = 1
        result = ""
        while errors and i < self.max_iters:
            logger.info("Repair loop iteration %d", i)
            result = self.translator._translate_once(javadoc, parameters, mode, errors, previous_output)
            errors = self.validator.validate(result, expected_len)
            i += 1

        if not errors:
            logger.info(f"Repair successful, after {i} out of a maximum of {self.max_iters} iterations.")
            return result
        else:
            logger.warning(f"Repair failed, after {i} out of a maximum of {self.max_iters} iterations.")
            return """```json 
                    [] 
                    ```"""