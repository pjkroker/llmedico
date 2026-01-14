import click

# Import commands from the submodule
from llmedico.commands.translate import translate_command
from llmedico.commands.evaluate import evaluate_command

@click.group()
def main():
    """LLMedico: Translate and Evaluate Conditions - command-line tool."""
    pass

# Register your commands
main.add_command(translate_command)
main.add_command(evaluate_command)
