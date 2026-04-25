"""
Generates the evaluate/ example outputs by comparing LLMedico-generated conditions
against the JDoctor reference conditions in reference/.

Run generate_translate.py first, then run this script from the repo root:

    python llmedico/examples/generate_evaluate.py
"""
import os
from pathlib import Path

from llmedico.evaluation.evaluation import evaluate, InputFormat

os.environ["LLMEDICO_CONFIG"] = (Path(__file__).parent.parent / "config.toml").as_posix()

EXAMPLES = Path(__file__).parent

TARGET_CLASSES = [
    "org.apache.commons.collections4.ArrayStack",
    "org.apache.commons.collections4.BagUtils",
]

out_dir = EXAMPLES / "evaluate"
out_dir.mkdir(parents=True, exist_ok=True)

for target_class in TARGET_CLASSES:
    reference = EXAMPLES / "reference" / f"{target_class}-jdoctor.json"
    generated = EXAMPLES / "translate" / target_class / "llmedico-condition_translator.json"

    evaluate(
        reference,
        InputFormat.JDOCTOR,
        generated,
        InputFormat.LLMEDICO,
        out_dir,
    )
