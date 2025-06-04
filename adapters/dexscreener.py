import httpx
from schema.pair_schema import DexScreenerPair
from typing import cast

client = httpx.AsyncClient(
    base_url="https://api.dexscreener.com",
    timeout=10.0,
)


class DexScreenerAdapter:
    @staticmethod
    async def fetch_pair(
        chain: str,
        pair: str,
    ) -> DexScreenerPair:
        response = await client.post(f"/latest/dex/pairs/{chain}/{pair}")
        data = response.json()
        return cast(DexScreenerPair, data["pair"])
