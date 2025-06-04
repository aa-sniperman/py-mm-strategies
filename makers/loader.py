from pathlib import Path
from parameters.client import params_redis_client

PROJECT_ROOT = Path(__file__).resolve().parents[0]


def set_makers(strat_key: str, makers: list[str]):
    redis_key = f"maker:{strat_key}"
    params_redis_client.delete(redis_key)
    params_redis_client.sadd(redis_key, *makers)


def load_makers(strat_key: str):
    redis_key = f"maker:{strat_key}"
    members = params_redis_client.smembers(redis_key)
    return [m for m in members]
