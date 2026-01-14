from pathlib import Path

import click

from llmedico.evaluation.evaluation import evaluate as run_pipeline, InputFormat

CONDITION_TYPES = ["llmedico", "jdoctor"]

@click.command(name="evaluate")

@click.option(
    "--expected",
    "--expected-conditions",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to the expected conditions JSON file"
)
@click.option(
    "--expected-type",
    type=click.Choice(CONDITION_TYPES, case_sensitive=False),
    required=True,
    help="Type of expected conditions (llmedico or jdoctor)"
)
@click.option(
    "--generated",
    "--generated-conditions",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to the generated conditions JSON file"
)
@click.option(
    "--generated-type",
    type=click.Choice(CONDITION_TYPES, case_sensitive=False),
    required=True,
    help="Type of generated conditions (llmedico or jdoctor)"
)
@click.option(
    "--out",
    "--out-dir",
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    required=True,
    help="Path to the generated conditions JSON file"
)

def evaluate_command(expected, expected_type, generated, generated_type, out):
    """Evaluate Conditions. Compare generated conditions against expected conditions."""
    click.echo(f"Expected conditions:")
    click.echo(f"  path = {expected}")
    click.echo(f"  type = {expected_type}")

    click.echo(f"\nGenerated conditions:")
    click.echo(f"  path = {generated}")
    click.echo(f"  type = {generated_type}")

    click.echo(f"output directory: {out}")
    run_pipeline(path_expected=expected,
                 type_expected=InputFormat(expected_type),
                 path_generated=generated,
                 type_generated=InputFormat(generated_type),
                 path_output=out)