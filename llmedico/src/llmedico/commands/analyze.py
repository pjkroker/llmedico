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
    required=True,
    default="",
    help="Target method to analyze (optional)",
)
@click.option(
    "--data-dir",
    "path_data_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=False,
    help="Directory containing input data. Implies standard layout.",
)
@click.option("--source-dir", "path_source_dir", type=click.Path(), help="Directory with Java source files.")
@click.option("--class-dir", "path_class_dir", type=click.Path(), help="Directory with compiled .class files.")
@click.option(
    "--out-dir",
    "path_output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Output directory for generated artifacts",
)

def analyze_command(fq_class_name, target_method, path_data_dir, path_source_dir, path_class_dir, path_output_dir):
    """
    Analyze a Java class and generate method assertions / data.
    """
    # -------------------------------
    # 1. Validate + derive directories
    # -------------------------------
    if path_source_dir and path_class_dir:
        # User explicitly provided both → trust them
        path_source_dir = Path(path_source_dir)
        path_class_dir = Path(path_class_dir)
    elif path_data_dir:
        # Derive from data dir
        base = Path(path_data_dir)
        path_source_dir = base / "/src/main/java"
        path_class_dir = base / "/target/classes"
    else:
        raise click.UsageError(
            "You must specify either (--data-dir) OR both (--source-dir and --class-dir)"
        )



    click.echo("=== LLMedico: analyze ===")
    click.echo(f"Target class:   {fq_class_name}")
    click.echo(f"Target method:  {target_method}")
    click.echo(f"Data dir:       {path_data_dir}")
    click.echo(f"Source dir:     {path_source_dir}")
    click.echo(f"Class dir:      {path_class_dir}")
    click.echo(f"Output dir:     {path_output_dir}")

    run_pipeline(fq_class_name, target_method, path_data_dir if path_data_dir else None,path_source_dir, path_class_dir, path_output_dir)

