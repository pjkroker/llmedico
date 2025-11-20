import click

@click.command(name="generate")
def generate_command():
    """Generate something."""
    click.echo("Generating output...")
