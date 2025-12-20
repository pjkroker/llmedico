import json
import logging
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
    if not code_blocks:
        raise RuntimeError(f"No code snippets found for language {language}. \nMake sure the code blocks are wrapped exactly like shown in the provided example!\nInclude the code inbetween ```{language} and ```")
    # Strip extra whitespace from each block
    return [block.strip() for block in code_blocks]

def extract_java_assertions(llm_response: str) -> List[str]:
    """
        Extracts individual Java assertion statements from Java code blocks
        in the LLM response.

        Returns:
            List[str]: A list where each entry is a single Java assertion line.
        """
    code_blocks = extract_code_by_language(llm_response, "java")
    assertions: List[str] = []

    for block in code_blocks:
        # Split the block by lines
        for line in block.splitlines():
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Only keep actual Java assert statements
            # Example line: assert args[0] != null; //description: a must not be null
            if line.startswith("assert "):
                assertions.append(line)

    return assertions

def extract_conditions(llm_response: str) -> list:
    raw_json = extract_code_by_language(llm_response, "json")
    conditions = json.loads(raw_json[0])
    return conditions
