from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from parameters.client import get_strategy_params, set_strategy_params, params_redis_client
from strategy_metadata.type import StrategyMetadata, VolMakerMetadata
from strategy_metadata.client import get_strategy_metadata, set_strategy_metadata
from makers.loader import set_makers
import concurrent.futures
from adapters.data_layer import DataLayerAdapter
from token_configs import TokenConfig
from circus.client import CircusClient
from strategies.vol_maker.v1 import VolMakerV1Config
from typing import List, Dict, Any
from fastapi import Body

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

def spawn_circus_watcher(name: str, flag: str = "value"):
    try:
        cmd = f"./venv/bin/python -u run.py {name} --flag={flag}"

        stdout_log = f"logs/{name}-vol.stdout.log"
        stderr_log = f"logs/{name}-vol.stderr.log"

        options = {
            "cmd": cmd,
            "working_dir": ".",
            "name": name,
            "autostart": True,
            "start": True,
            "stdout_stream.class": "TimedRotatingFileStream",
            "stdout_stream.filename": stdout_log,
            "stdout_stream.time_format": "%Y-%m-%d %H:%M:%S",
            "stdout_stream.utc": True,
            "stdout_stream.rotate_when": "H",
            "stdout_stream.rotate_interval": 1,
            "stderr_stream.class": "TimedRotatingFileStream",
            "stderr_stream.filename": stderr_log,
            "stderr_stream.time_format": "%Y-%m-%d %H:%M:%S",
            "stderr_stream.utc": True,
            "stderr_stream.rotate_when": "H",
            "stderr_stream.rotate_interval": 1,
        }

        client = CircusClient(endpoint="tcp://127.0.0.1:5555")
        result = client.call("add", **options)
        print(f"Spawned watcher '{name}':", result)
        return result
    except Exception as e:
        print(f"Failed to spawn watcher '{name}': {e}")
        return {"status": "error", "reason": str(e)}

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

class NewStrategyRequest(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="Strategy metadata")
    params: Dict[str, Any] = Field(..., description="Strategy parameters")
    makers: List[str] = Field(..., description="List of maker wallet addresses")

@router.post("/new-strategy")
async def create_new_strategy(request: NewStrategyRequest = Body(...)):
    metadata = request.metadata
    params = request.params
    makers = request.makers

    strat_key = metadata["key"]
    existing = params_redis_client.hexists(f"metadata:{strat_key}", "key")

    if existing:
        raise HTTPException(status_code=400, detail=f"Strategy with key {strat_key} already exists")
    
    type = metadata["type"]

    if type in ["vol-v1", "vol-sol-bundle", "tron-vol"]:
        VolMakerMetadata.model_validate(metadata)
        VolMakerV1Config.model_validate(params)
    else:
        raise HTTPException(status_code=400, detail=f"Strategy type {type} is not supported")

    set_strategy_metadata(strat_key, metadata)
    set_strategy_params(strat_key, params)
    set_makers(strat_key, makers)
    try:
        spawn_circus_watcher(strat_key, metadata.get("flag", "value"))
    except Exception as e:
        # Rollback Redis state
        params_redis_client.delete(f"metadata:{strat_key}")
        params_redis_client.delete(f"params:{strat_key}")
        params_redis_client.delete(f"makers:{strat_key}")
        raise HTTPException(status_code=500, detail=f"Failed to spawn process: {str(e)}")
    return {"status": "ok", "strategy": strat_key}