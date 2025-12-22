import json
from pathlib import Path
from pprint import pprint

from llmedico.conditions.model import Condition, ConditionKind, TypeModel, ParameterModel, MethodSignature, MethodModel, ClassModel
from llmedico.converters.jdoctor import JDoctorConditionConverter


def test_jdoctor_adapter_constructor():
    # --- class ---
    cls = ClassModel(
        package="org.jgrapht.alg",
        name="AbstractPathElementList",
        qualified_name="org.jgrapht.alg.AbstractPathElementList"
    )

    # --- parameters ---
    p1 = ParameterModel(
        name="graph",
        type=TypeModel(
            qualified_name="org.jgrapht.Graph",
            simple_name="Graph"
        )
    )

    p2 = ParameterModel(
        name="maxSize",
        type=TypeModel(
            qualified_name="int",
            simple_name="int"
        )
    )

    p3 = ParameterModel(
        name="elementList",
        type=TypeModel(
            qualified_name="org.jgrapht.alg.AbstractPathElementList",
            simple_name="AbstractPathElementList"
        )
    )

    p4 = ParameterModel(
        name="edge",
        type=TypeModel(
            qualified_name="java.lang.Object",
            simple_name="Object"
        )
    )

    # --- signature ---
    sig = MethodSignature(
        name="AbstractPathElementList",
        return_type=None,
        parameters=[p1, p2, p3, p4]
    )

    # --- conditions ---
    conditions = [
        Condition(
            kind=ConditionKind.PARAM,
            name="maxSize",
            expression="assert args[1] >= 0;",
            content="maximum number of paths the list is able to store.",
            description="maxSize must be non-negative"
        ),
        Condition(
            kind=ConditionKind.PARAM,
            name="elementList",
            expression="assert args[2] != null;",
            content="paths, list of <code>AbstractPathElement</code>.",
            description="elementList cannot be null"
        ),
        Condition(
            kind=ConditionKind.PARAM,
            name="edge",
            expression="assert args[3] != null;",
            content="edge reaching the end vertex of the created paths.",
            description="edge cannot be null"
        ),

        Condition(
            kind=ConditionKind.THROWS,
            name="NullPointerException",
            expression="assert args[2]==null || args[3]==null;",
            content="if the specified prevPathElementList or edge\nis <code>null</code>.",
            description="if the specified prevPathElementList or edge is null."
        ),
        Condition(
            kind=ConditionKind.THROWS,
            name="IllegalArgumentException",
            expression="assert args[1]<0 || args[1]==0;",
            content="if <code>maxSize</code> is negative or\n0.",
            description="if maxSize is negative or 0."
        )
    ]

    # --- method ---
    method = MethodModel(
        signature=sig,
        declaring_class=cls,
        conditions=conditions,
        is_constructor=True
    )

    cls.methods.append(method)

    # --- run adapter ---
    jdoctor_converter = JDoctorConditionConverter()
    output = jdoctor_converter.convert_method(method)

    path_output_dir = Path(__file__).parent.parent / "data" / "output"
    with open(path_output_dir / "test_constructor.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


    # --- assertions ---
    assert output["name"] == "AbstractPathElementList"
    assert "paramTags" in output
    assert "throwsTags" in output
    assert output["isVarArgs"] is False


def test_jdoctor_adapter_method_with_return_type():
    # --- class ---
    cls = ClassModel(
        package="org.apache.commons.math3.primes",
        name="Primes",
        qualified_name="org.apache.commons.math3.primes.Primes"
    )

    # --- parameters ---
    p1 = ParameterModel(
        name="n",
        type=TypeModel(
            qualified_name="int",
            simple_name="int"
        )
    )

    # --- signature ---
    sig = MethodSignature(
        name="isPrime",
        return_type=TypeModel("boolean", "boolean"),
        parameters=[p1]
    )

    # --- conditions ---
    conditions = [
        Condition(
            kind=ConditionKind.PARAM,
            name="n",
            expression="assert 0==0;",
            content="number to test.",
            description="number to test."
        ),

        Condition(
            kind=ConditionKind.RETURN,
            expression="assert args[0]<2 ? methodResultID==false;",
            content="true if n is prime. (All numbers < 2 return false).",
            description="true if n is prime. (All numbers < 2 return false)."
        )
    ]

    # --- method ---
    method = MethodModel(
        signature=sig,
        declaring_class=cls,
        conditions=conditions,
        is_constructor=False
    )

    cls.methods.append(method)

    # --- run adapter ---
    jdoctor_converter = JDoctorConditionConverter()
    output = jdoctor_converter.convert_method(method)

    path_output_dir = Path(__file__).parent.parent / "data" / "output"
    with open(path_output_dir / "test_method_with_return_type.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # --- assertions ---
    assert output["name"] == "isPrime"
    assert "paramTags" in output
    assert "returnTag" in output
    assert output["isVarArgs"] is False


