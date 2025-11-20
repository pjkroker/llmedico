import click
from pathlib import Path
from llmedico.main import main as run_pipeline

@click.command(name="analyze")
@click.option(
    "--target-class",
    "fq_class_name",
    required=True,
    help="Fully qualified class name, e.g. 'org.apache.commons.lang3.StringUtils'",
)
@click.option(
    "--target-method",
    "target_method",
    default="",
    help="Target method to analyze (optional)",
)
@click.option(
    "--data-dir",
    "path_data_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory containing input/output data",
)
@click.option(
    "--out-dir",
    "path_output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Output directory for generated artifacts",
)

def analyze_command(fq_class_name, target_method, path_data_dir, path_output_dir):
    """
    Analyze a Java class and generate method assertions / data.
    """

    click.echo("=== LLMedico: analyze ===")
    click.echo(f"Target class:   {fq_class_name}")
    click.echo(f"Target method:  {target_method}")
    click.echo(f"Data dir:       {path_data_dir}")
    click.echo(f"Output dir:     {path_output_dir}")

    run_pipeline(fq_class_name, target_method, path_data_dir, path_output_dir)

