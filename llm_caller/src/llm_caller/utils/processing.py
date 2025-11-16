import re
from typing import List, Optional

def extract_code_by_language(llm_response: str, language: str) -> List[str]:
    """
    Extracts code snippets for a specific programming language from an LLM response.

    Args:
        llm_response (str): The raw response from the LLM.
        language (str): The programming language to filter by (e.g., 'java', 'python').

    Returns:
        List[str]: A list of code snippets for the requested language.
    """
    # Regex to find fenced code blocks with language specification
    pattern = rf"```{language}\n(.*?)```"

    # re.DOTALL allows newlines inside the match
    code_blocks = re.findall(pattern, llm_response, re.DOTALL)

    # Strip extra whitespace from each block
    return [block.strip() for block in code_blocks]