from pydantic import BaseModel
from pathlib import Path
import json

class StrategyMetadata(BaseModel):
    name: str
    type: str

class VolMakerMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str

# Get the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parents[0]
dotenv_path = PROJECT_ROOT / ".env"
def load_strategy_metadata(file_name: str):
    # read the json file
    file_path = PROJECT_ROOT / f"{file_name}"
    with open(file_path, "r") as f:
        data = json.load(f)
