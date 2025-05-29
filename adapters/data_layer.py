import redis
import clickhouse_connect
from settings import settings
from typing import List, Dict, TypedDict
import json
from schema.pair_schema import DexScreenerPair


class MarketDataInfo(TypedDict):
    mc: float
    price: float
    price_by_quote: float
    volume_1h: float
    volume_24h: str


class OHLCV(TypedDict):
    ts: int
    o: float
    h: float
    l: float
    c: float
    v: float


def get_dl_ch_client():
    return clickhouse_connect.get_client(
        host=settings.clickhouse.host,
        username=settings.clickhouse.username,
        port=settings.clickhouse.port,
        password=settings.clickhouse.password,
        database=settings.clickhouse.database,
    )


dl_redis_client = redis.Redis(
    host=settings.redis.dl_host,
    password=settings.redis.dl_password,
    port=settings.redis.dl_port,
    decode_responses=True,
    db=settings.redis.dl_db,
    username=settings.redis.dl_username,
)


class DataLayerAdapter:

    @staticmethod
    def get_pair(chain: str, pair: str) -> MarketDataInfo:
        key = f"pair:{chain}:dexscreener"
        pair_data: DexScreenerPair = json.loads(dl_redis_client.hget(key, pair))
        return pair_data

    @staticmethod
    def get_market_data(chain: str, pair: str) -> MarketDataInfo:
        key = f"pair:{chain}:dexscreener"
        pair_data = json.loads(dl_redis_client.hget(key, pair))
        return {
            "mc": float(pair_data["marketCap"]),
            "price": float(pair_data["priceUsd"]),
            "price_by_quote": float(pair_data["priceNative"]),
            "volume_1h": float(pair_data["volume"]["h1"]),
            "volume_24h": float(pair_data["volume"]["h24"]),
        }

    @staticmethod
    def get_balance(chain: str, account: str, token: str):
        key = f"balance:{chain}:{account}"
        cached = dl_redis_client.hget(key, token)
        return float(cached)

    @staticmethod
    def get_balances(
        chain: str, accounts: List[str], tokens: List[str], symbols: List[str]
    ) -> Dict[str, Dict[str, float]]:
        result: Dict[str, Dict[str, float]] = {}
        total: Dict[str, float] = {symbol: 0 for symbol in symbols}

        for account in accounts:
            key = f"balance:{chain}:{account}"
            symbol_to_balance = {}

            for token, symbol in zip(tokens, symbols):
                raw_balance = dl_redis_client.hget(name=key, key=token)
                if raw_balance is not None:
                    formatted = float(raw_balance)
                    symbol_to_balance[symbol] = formatted
                    total[symbol] += formatted
                else:
                    symbol_to_balance[symbol] = 0

            result[account] = symbol_to_balance

        # Add total to result
        result["total"] = {symbol: float(total[symbol]) for symbol in symbols}

        return result

    @staticmethod
    def get_ohlcvs(pair: str, interval: str, from_ts: int, to_ts: int):
        query = """
        SELECT ts, o, h, l, c, v
        from %(db)s
        WHERE pair = %(pair)s
        and ts BETWEEN %(from_ts)s and %(to_ts)s
        order by ts desc 
        """

        results = get_dl_ch_client().query(
            query=query,
            parameters={
                "db": "ohlcv_15m" if interval == "15m" else "ohlcv_1h",
                "pair": pair,
                "from_ts": from_ts,
                "to_ts": to_ts,
            },
        )

        rows = results.result_rows

        columns = ["ts", "o", "h", "l", "c", "v"]

        return [OHLCV(dict(zip(columns, row))) for row in rows]

    @staticmethod
    def get_pool_holdings(pair: str):
        key = f"solana_pool_holding:{pair}"
        pair_data = dl_redis_client.hgetall(key)

        return pair_data
