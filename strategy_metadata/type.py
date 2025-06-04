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