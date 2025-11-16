from pathlib import Path

def save_json_to_file(json_string: str, out_path: str | Path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf8") as f:
        f.write(json_string)
