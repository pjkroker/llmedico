import json
from pathlib import Path

from llmedico.builder.class_model_builder import ClassModelBuilder


def test_build_complete_graph_generator():
    file = Path(__file__).parent.parent / 'data' / 'input' / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.generate.CompleteGraphGenerator.json"
    with open(file) as f:
        llmedico_trans_conditions = json.load(f)
    print(llmedico_trans_conditions)
    builder = ClassModelBuilder()
    cls = builder.build_class(llmedico_trans_conditions[0])
    assert cls is not None

def test_build_graph():
    file = Path(__file__).parent.parent / 'data' / 'input' / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.Graph.json"
    with open(file) as f:
        llmedico_trans_conditions = json.load(f)
    print(llmedico_trans_conditions)
    builder = ClassModelBuilder()
    cls = builder.build_class(llmedico_trans_conditions[0])
    assert cls is not None

