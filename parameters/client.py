import redis
import json
from settings import settings

params_redis_client = redis.Redis(
    host=settings.redis.dl_host,
    port=settings.redis.dl_port,
    password=settings.redis.dl_password,
    decode_responses=True,
    db=settings.redis.dl_db,
    username=settings.redis.dl_username,
    socket_timeout=5,         # seconds
    socket_connect_timeout=5  # connection timeout
)

def get_strategy_params(strategy_key: str):
    return params_redis_client.hgetall(strategy_key)
    
def set_strategy_params(strategy_key: str, new_set: dict):
    current_set = params_redis_client.hgetall(strategy_key)
    
    # Merge the current set with the new set
    updated_set = {**current_set, **new_set}

    # Redis expects a flat dict of strings
    updated_set = {k: str(v) for k, v in updated_set.items()}

    # Update Redis
    if updated_set:
        params_redis_client.hset(strategy_key, mapping=updated_set)
    
    return updated_set
