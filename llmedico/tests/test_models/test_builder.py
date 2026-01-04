import json
from pathlib import Path

from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.conditions.model import Condition, ConditionKind, TypeModel


def test_condition_kind():
    kind = "PARAM"

    c = Condition(
        kind=ConditionKind(kind),
        name="n",
        expression="assert 0==0;",
        content="number to test.",
        description="number to test."
    )

    assert c.kind == ConditionKind.PARAM

def test_is_condition_kind():
    tag = "param"
    assert ConditionKind.is_condition_kind(tag) is True
    tag = "see"
    assert ConditionKind.is_condition_kind(tag) is False

def test_build_condition():
    null = None
    tags = {"tags":[
        {
            "tag": "param",
            "name": "maxSize",
            "content": "maximum number of paths the list is able to store.",
            "assertion": "assert args[1] >= 0;",
            "description": "maxSize must be non-negative"
          },
          {
            "tag": "return",
            "name": 5,
            "content": "true if n is prime. (All numbers < 2 return false).",
            "assertion": "assert args[0]<2 ? methodResultID==false;",
            "description": "true if n is prime. (All numbers < 2 return false)."
          }]
    }
    return_condition = Condition(
            kind=ConditionKind.RETURN,
            expression="assert args[0]<2 ? methodResultID==false;",
            content="true if n is prime. (All numbers < 2 return false).",
            description="true if n is prime. (All numbers < 2 return false)."
        )
    builder = ClassModelBuilder()
    conditions = builder._build_conditions(tags)
    print(conditions)
    assert len(conditions) == 2
    assert conditions[0].name == "maxSize"
    assert conditions[1] == return_condition
    assert conditions[1].name == None

def test_build_type():
    parameter_data_str = """{
            "type": {
              "qualified_name": "org.jgrapht.Graph",
              "simple_name": "Graph",
              "is_array": false
            },
            "name": "graph"
          }"""
    parameter_data = json.loads(parameter_data_str)
    builder = ClassModelBuilder()
    assert builder._build_type(parameter_data) == TypeModel(qualified_name="org.jgrapht.Graph", simple_name="Graph", is_array=False)

    parameter_data_str = """{
                "type": {
                  "qualified_name": "org.jgrapht.Graph",
                  "simple_name": "Graph",
                  "is_array": true
                },
                "name": "graph"
              }"""
    parameter_data = json.loads(parameter_data_str)
    assert builder._build_type(parameter_data) == TypeModel(qualified_name="org.jgrapht.Graph", simple_name="Graph",
                                                            is_array=True)

def test_build_return_type():
    builder = ClassModelBuilder()
    method_data_str = """{
        "type": "method",
        "name": "getVertex",
        "return_type": {
          "qualified_name": "java.lang.Object",
          "simple_name": "Object",
          "is_array": false
        },
        "parameters": [],
        "javadoc": "/** * Returns target vertex. */",
        "tags": [],
        "code": "/** * Returns target vertex. */public V getVertex() {  return this.vertex;}"
      }"""

    method_data = json.loads(method_data_str)
    assert builder._build_return_type(method_data) == TypeModel(qualified_name="java.lang.Object", simple_name="Object", is_array=False)

def test_build_class():
    builder = ClassModelBuilder()
    input_path = Path(__file__).parent.parent / "data" / "input" / "llmedico-condition_translator.json"
    with open(input_path, "r", encoding="utf-8") as f:
        extracted_conditions = json.load(f)
    cls = builder.build_class(extracted_conditions[0])
    assert len(cls.methods) == len(extracted_conditions[0]["members"])

