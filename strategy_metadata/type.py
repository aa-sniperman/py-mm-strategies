from pydantic import BaseModel

class StrategyMetadata(BaseModel):
    name: str
    type: str
    key: str


class VolMakerMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str


class SinglePairMMMetadata(StrategyMetadata):
    chain: str
    protocol: str
    quote: str
    base: str

class Arbitrageur1DexMetadata:
    chain: str
    protocol: str
    quote: str
    base: str

class ArbitrageurDex2DexMetadata(StrategyMetadata):
    dex_1_metadata: Arbitrageur1DexMetadata
    dex_2_metadata: Arbitrageur1DexMetadata