import json
from pathlib import Path

from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.converters.jdoctor import JDoctorConditionConverter


def test_builder_llmedico_broken_class():
    builder = ClassModelBuilder()
    input_path = Path(__file__).parent.parent / "data" / "input" / "llmedico-condition_translator-org.apache.commons.collections4.bag.json"
    with open(input_path, "r", encoding="utf-8") as f:
        llmedico_conditions = json.load(f)
    cls = builder.build_class(llmedico_conditions[0])

    with open("/Users/paul/paul_data/projects_cs/ba_versuch1/llmedico/data/output/llmedico-condition_translator.json", "r", encoding="utf-8") as f:
        llmedico_trans_conditions = json.load(f)
    builder = ClassModelBuilder()
    cls = builder.build_class(llmedico_trans_conditions[0])

    jdoc_converter = JDoctorConditionConverter()
    jdoc_trans_conditions = jdoc_converter.convert_class(cls)
    print(json.dumps(jdoc_trans_conditions, indent=4))