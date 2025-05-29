from fastapi import APIRouter, HTTPException
from typing import List
from pathlib import Path
from pydantic import BaseModel
from parameters.client import get_strategy_params, set_strategy_params
from strategy_metadata.type import load_strategy_metadata
import subprocess
import concurrent.futures
import json
from adapters.data_layer import DataLayerAdapter
from token_configs import TokenConfig


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STRATEGY_DIR = PROJECT_ROOT / "strategy_metadata"

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    responses={404: {"description": "Not found"}},
)


@router.post("/{key}", response_model=dict)
def edit_strategy_parameters(key: str, new_set: dict):
    """
    Edit parameter of the specified strategy
    """
    try:
        metadata = load_strategy_metadata(key)
        strat_key = metadata["key"]
        return set_strategy_params(strat_key, new_set)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StrategyStatus(BaseModel):
    key: str
    status: str
    metadata: dict


def get_status(name: str) -> str:
    try:
        result = subprocess.run(
            ["circusctl", "status", name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            status_line = result.stdout.strip()
            return status_line.split(": ")[1] if ": " in status_line else "unknown"
        else:
            return "unknown"
    except Exception:
        return "error"


@router.get("", response_model=List[StrategyStatus])
def get_all_strategies():
    try:
        strategies = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Prepare futures for status calls
            futures = {}
            for file in STRATEGY_DIR.glob("*.json"):
                name = file.stem
                futures[executor.submit(get_status, name)] = file

            for future in concurrent.futures.as_completed(futures):
                file = futures[future]
                name = file.stem

                # Load metadata
                try:
                    with open(file, "r") as f:
                        metadata = json.load(f)
                except Exception as e:
                    metadata = {"error": f"Could not read JSON: {str(e)}"}

                status = future.result()

                strategies.append(
                    {"key": name, "status": status, "metadata": metadata}
                )

        return strategies

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{key}", response_model=dict)
async def get_strategy_parameters(key: str):
    """
    Return the strategy parameters
    """
    try:
        metadata = load_strategy_metadata(key)
        strategy_key = metadata["key"]
        chain = metadata["chain"]
        base_config = TokenConfig[metadata["base"]]
        pair = base_config.pair
        strategy_params = get_strategy_params(strategy_key)
        pair_data = DataLayerAdapter.get_pair(chain=chain, pair=pair)

        return {
            "key": strategy_key,
            "metadata": metadata,
            "strategyParams": strategy_params,
            "pairData": pair_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
