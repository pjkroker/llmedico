import json
from pathlib import Path

def save_json_to_file(json_string: str, out_path: str | Path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf8") as f:
        f.write(json_string)


def save_realy_json_to_file(data:list | dict, out_path: str | Path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(file_path: Path) -> dict:
    # Open the file and load its contents
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check type
    # if isinstance(data, list) and len(data) == 1:
    #     data = data[0] #convert from array to dict
    return data

