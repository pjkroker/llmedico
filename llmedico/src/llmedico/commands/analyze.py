import click

@click.command(name="analyze")
@click.argument("path")
@click.option("--method", help="Method name to analyze")
def analyze_command(path, method):
    """Analyze a JSON file."""
    click.echo(f"Analyzing {path}, method={method}")
