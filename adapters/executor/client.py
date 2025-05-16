import httpx
from settings import settings

print(settings.executor)
client = httpx.AsyncClient(
    base_url=settings.executor.endpoint,
    timeout=10.0,
    headers={
        "username": settings.executor.username,
        "x-api-secret": settings.executor.api_secret,
    },
)
