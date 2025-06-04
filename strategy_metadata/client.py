from parameters.client import params_redis_client
from pydantic import BaseModel
from typing import Type, TypeVar


T = TypeVar("T", bound=BaseModel)  # Ensures only Pydantic models can be passed


def get_strategy_metadata(strategy_key: str, model_class: Type[T]) -> T:
    redis_key = f"metadata:{strategy_key}"
    raw_data = params_redis_client.hgetall(redis_key)
    return model_class(**raw_data)


def set_strategy_metadata(strategy_key: str, new_set: dict):
    redis_key = f"metadata:{strategy_key}"
    current_set = params_redis_client.hgetall(redis_key)

    # Merge the current set with the new set
    updated_set = {**current_set, **new_set}

    # Redis expects a flat dict of strings
    updated_set = {k: str(v) for k, v in updated_set.items()}

    # Update Redis
    if updated_set:
        params_redis_client.hset(redis_key, mapping=updated_set)

    return updated_set
