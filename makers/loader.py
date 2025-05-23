from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[0]


def load_makers(file_name: str):
    # read the json file
    file_path = PROJECT_ROOT / f"{file_name}.json"
    with open(file_path, "r") as f:
        data = json.load(f)
        return data
