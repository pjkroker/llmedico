"""
Generates the translate/ example outputs by running LLMedico on two classes
from Apache Commons Collections 4.1.

Run from the repo root with the virtual environment activated:

    python llmedico/examples/generate_translate.py

Set INPUT_DIR to the directory containing your Java project sources and JARs.
"""
import os
from pathlib import Path

from llmedico.main import main

os.environ["LLMEDICO_CONFIG"] = (Path(__file__).parent.parent / "config.toml").as_posix()

# --- configure these paths -----------------------------------------------
INPUT_DIR = Path(__file__).parent.parent.parent / ".pyjdoctor" / "data" / "input"
SRC_DIR   = INPUT_DIR / "commons-collections4-4.1-src" / "src" / "main" / "java"
JAR       = INPUT_DIR / "commons-collections4-4.1-src" / "target" / "commons-collections4-4.1.jar"
# -------------------------------------------------------------------------

TARGET_CLASSES = [
    "org.apache.commons.collections4.ArrayStack",
    "org.apache.commons.collections4.BagUtils",
]

for target_class in TARGET_CLASSES:
    out_dir = Path(__file__).parent / "translate" / target_class
    out_dir.mkdir(parents=True, exist_ok=True)

    main(
        fq_class_name=target_class,
        target_method=None,
        path_source_dir=SRC_DIR,
        path_jar=JAR,
        path_output_dir=out_dir,
    )
