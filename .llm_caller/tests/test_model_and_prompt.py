from llm_caller.models import *
from llm_caller.models.ollama import Ollama
from llm_caller.prompts import SUMMARIZATION_PROMPT

def test_SUMMARIZATION_PROMPT():
    llama2 = Ollama("llama2")
    text = """
        Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.[34] Python is dynamically type-checked and garbage-collected. It supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming.
        Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language. Python 3.0, released in 2008, was a major revision and not completely backward-compatible with earlier versions. Beginning with Python 3.5,[35] capabilities and keywords for typing were added to language, allowing optional static typing.[36] Currently only versions in the 3.x series are supported.
        Python has gained widespread use in the machine learning community.[37][38][39][40] It is widely taught as an introductory programming language.[41] Since 2003, Python has consistently ranked in the top ten of the most popular programming languages in the TIOBE Programming Community Index, which ranks based on searches in 24 platforms.[42]
        """
    prompt = SUMMARIZATION_PROMPT.format(text=text)
    result = llama2.generate(prompt)
    assert len(result) < len(text)