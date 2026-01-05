import subprocess
import tempfile
from pathlib import Path

MY_JAVA_CLASS_TEMPLATE = """public class MyClass {{
  public static void main(String args[]) {{
    {assertion}
  }}
}}"""

def get_compile_errors(assertion: str):
    """
    Create a temporary directory and compile the java code. Then return the error message.
    Args:
        assertion(str): The Java code to compile.
    Returns:
        str: The error message. If there is no error message, return "" (empty string).
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        p = Path(temp_dir)

        file_path = p / "MyClass.java"

        with open(file_path, "w") as file:
            file.write(MY_JAVA_CLASS_TEMPLATE.format(assertion=assertion))

        result = subprocess.run(
            ["javac", file_path],  # Command to compile
            capture_output=True,  # Capture stdout and stderr
            text=True  # Output as text
        )

        # If compilation fails, return the error message
        if result.returncode != 0:
            return result.stderr

        # If no errors, return an empty string
        return ""

