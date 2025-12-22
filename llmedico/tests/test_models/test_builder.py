from llmedico.builder.class_model_builder import ClassModelBuilder
from llmedico.conditions.model import Condition, ConditionKind


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


