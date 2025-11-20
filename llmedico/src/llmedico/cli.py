import click

# Import commands from the submodule
from .commands.analyze import analyze_command
from .commands.generate import generate_command

@click.group()
def main():
    """jdoctor command-line tool."""
    pass

# Register your commands
main.add_command(analyze_command)
main.add_command(generate_command)
