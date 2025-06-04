from fastapi import APIRouter, HTTPException
from typing import List
from pathlib import Path
from pydantic import BaseModel
from parameters.client import get_strategy_params, set_strategy_params, params_redis_client
from strategy_metadata.type import StrategyMetadata, VolMakerMetadata
from strategy_metadata.client import get_strategy_metadata
import concurrent.futures
from adapters.data_layer import DataLayerAdapter
from token_configs import TokenConfig
from circus.client import CircusClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
        metadata = get_strategy_metadata(key, StrategyMetadata)
        strat_key = metadata.key
        return set_strategy_params(strat_key, new_set)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StrategyStatus(BaseModel):
    key: str
    status: str
    metadata: StrategyMetadata


def get_status(name: str) -> str:
    client = CircusClient(endpoint="tcp://127.0.0.1:5555")
    try:
        res = client.send_message("status", name=name)
        return res.get("status", "unknown")
    except Exception as e:
        print(f"Error getting status: {e}")
        return "error"

@router.get("", response_model=List[StrategyStatus])
def get_all_strategies():
    try:
        cursor = 0
        strategy_keys = []

        while True:
            cursor, keys = params_redis_client.scan(cursor=cursor, match='metadata:*', count=100)
            strategy_keys.extend(keys)
            if cursor == 0:
                break

        strategy_keys = [key.replace('metadata:', '') for key in strategy_keys]

        strategies = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Prepare futures for status calls
            futures = {}
            for strat_key in strategy_keys:
                futures[executor.submit(get_status, strat_key)] = strat_key

            for future in concurrent.futures.as_completed(futures):
                strat_key = futures[future]
                metadata = get_strategy_metadata(strat_key, StrategyMetadata)

                status = future.result()

                strategies.append(
                    {"key": strat_key, "status": status, "metadata": metadata}
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
        metadata = get_strategy_metadata(key, VolMakerMetadata)
        strategy_key = metadata.key
        chain = metadata.chain
        base_config = TokenConfig[metadata.base]
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
