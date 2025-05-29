from typing import TypedDict, Optional


class Token(TypedDict):
    address: str
    name: str
    symbol: str


class TxnStats(TypedDict):
    buys: int
    sells: int


class Txns(TypedDict):
    m5: TxnStats
    h1: TxnStats
    h6: TxnStats
    h24: TxnStats


class Volume(TypedDict):
    m5: float
    h1: float
    h6: float
    h24: float


class PriceChange(TypedDict):
    m5: float
    h1: float
    h6: float
    h24: float


class Liquidity(TypedDict):
    usd: float
    base: float
    quote: float


class Boosts(TypedDict):
    active: int


class DexScreenerPair(TypedDict, total=False):
    chainId: str
    dexId: str
    url: str
    pairAddress: str
    baseToken: Token
    quoteToken: Token
    priceNative: str
    marketCap: str
    priceUsd: str
    txns: Txns
    volume: Volume
    priceChange: PriceChange
    liquidity: Liquidity
    fdv: Optional[float]
    pairCreatedAt: Optional[int]
    boosts: Optional[Boosts]
