import redis
from settings import settings

params_redis_client = redis.Redis(
    host=settings.redis.dl_host,
    password=settings.redis.dl_password,
    decode_responses=True,
    db=settings.redis.dl_db,
    username=settings.redis.dl_username,
)
