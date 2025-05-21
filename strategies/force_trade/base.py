from pydantic import BaseModel
from makers.loader import load_makers
from strategies.makers_union import MakersUnion
from token_configs import TokenConfig

class ForceTradeBaseParams(BaseModel):
    protocol: str
    cluster_key: str
    token_key: str
    slippage: float

def get_makers_and_tokens(params: ForceTradeBaseParams):
    makers = load_makers(params.cluster_key)
    base_config = TokenConfig[params.token_key]
    quote_config = TokenConfig[base_config.quote]

    union = MakersUnion(base_config.chain, params.protocol, makers=makers, tokens=[base_config.address, quote_config.address])
    return {
        "union": union,
        "base": base_config,
        "quote": quote_config
    }
