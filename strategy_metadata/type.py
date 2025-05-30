from pydantic import BaseModel
from pathlib import Path
import json
from typing import Type, TypeVar


class StrategyMetadata(BaseModel):
    name: str
    type: str
    key: str


class VolMakerMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str


class SinglePairMMMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str


# Get the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parents[0]

T = TypeVar("T", bound=BaseModel)  # Ensures only Pydantic models can be passed

def load_strategy_metadata(file_name: str, model_class: Type[T]) -> T:
    file_path = PROJECT_ROOT / f"{file_name}.json"
    with open(file_path, "r") as f:
        raw_data = json.load(f)
    return model_class(**raw_data)
