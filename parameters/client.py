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
    