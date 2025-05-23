from pydantic import BaseModel
from pathlib import Path
import json

class StrategyMetadata(BaseModel):
    name: str
    type: str
    key: str

class VolMakerMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str

class RSIRangeMMMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str

class BaseTPSLMMMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str

# Get the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parents[0]
def load_strategy_metadata(file_name: str):
    # read the json file
    file_path = PROJECT_ROOT / f"{file_name}.json"
    with open(file_path, "r") as f:
        data = json.load(f)
        return data
