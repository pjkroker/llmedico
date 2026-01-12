import json
from pathlib import Path

from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.converters.jdoctor import JDoctorConditionConverter
from llmedico.translator.method_selector import MethodSelector

def test_method_selector():
    # using class model
    builder = ClassModelBuilder()
    input_path = Path(__file__).parent.parent / "data" / "input" / "llmedico-javadoc_extractor.json"

    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    cls = builder.build_class(extracted_conditions[0])

    selector = MethodSelector(cls)
    selection = selector.get_methods_to_str()
    print(selection)
    assert selection.endswith("double getEdgeWeight(java.lang.Object e)\n")



