import json
from pathlib import Path

from llmedico.builder.class_model_builder_jdoctor import ClassModelBuilderJdoctor


def test_builder_jdoctor():
    builder = ClassModelBuilderJdoctor()
    input_path = Path(__file__).parent.parent / "data" / "input" / "org.jgrapht.alg.AbstractPathElementList_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_jdoctor_conditions = json.load(f)
    cls = builder.build_class(extracted_jdoctor_conditions)

    assert cls.package == "org.jgrapht.alg"

    input_path = Path(__file__).parent.parent / "data" / "input" / "org.jgrapht.graph.GraphDelegator_goal.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_jdoctor_conditions = json.load(f)
    cls = builder.build_class(extracted_jdoctor_conditions)

    assert cls.qualified_name == "org.jgrapht.graph.GraphDelegator"