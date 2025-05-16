import redis
import json
from settings import settings
from typing import List, Dict

dl_redis_client = redis.Redis(
    host=settings.redis.dl_host,
    password=settings.redis.dl_password,
    decode_responses=True,
    db=settings.redis.dl_db,
    username=settings.redis.dl_username,
)


class DataLayerAdapter:
    @staticmethod
    def get_market_data(chain: str, pair: str):
        key = f"pair:{chain}:dexscreener"
        cached = dl_redis_client.get(key)
        parsed = json.loads(cached)
        pair_data = parsed[pair]
        return {
            "price": pair_data["priceUSD"],
            "volume_1h": pair_data["volume"]["h1"],
            "volume_24h": pair_data["volume"]["h24"],
        }

    @staticmethod
    def get_balance(chain: str, account: str, token: str):
        key = f"balance:{chain}:{account}"
        cached = dl_redis_client.get(key)
        parsed = json.loads(cached)
        return float(parsed[token])

    @staticmethod
    def get_balances(
        chain: str,
        accounts: List[str],
        tokens: List[str],
        symbols: List[str]
    ) -> Dict[str, Dict[str, float]]:
        result: Dict[str, Dict[str, float]] = {}
        total: Dict[str, float] = {symbol: 0 for symbol in symbols}

        for account in accounts:
            key = f"balance:{chain}:{account}"
            cached = dl_redis_client.get(key)
            if not cached:
                continue
            parsed = json.loads(cached)
            symbol_to_balance = {}

            for token, symbol in zip(tokens, symbols):
                raw_balance = parsed.get(token)
                if raw_balance is not None:
                    formatted = float(raw_balance)
                    symbol_to_balance[symbol] = formatted
                    total[symbol] += formatted
                else:
                    symbol_to_balance[symbol] = 0

            result[account] = symbol_to_balance

        # Add total to result
        result["total"] = {symbol: str(total[symbol]) for symbol in symbols}

        return result
