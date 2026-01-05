import json
from pathlib import Path


def test_get_methods():
    p = Path(__file__).parent / "data" / "input" / "generated_conditions" / "llmedico-condition_translator-org.jgrapht.Graph.json"

    with open(p) as f:
        d = json.load(f)
    members = set()
    for member in d[0]["members"]:
        if member["type"] == "method":
            members.add(member["name"])

    print(members)
    print(len(members))

