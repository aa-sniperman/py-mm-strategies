from strategies.makers_union import MakersUnion
from strategies.force_trade.base import get_makers_and_tokens, ForceTradeBaseParams
from adapters.data_layer import DataLayerAdapter
from token_configs import TokenConfigInfo
from bot import send_message
import random

class ForceTradeMCParams(ForceTradeBaseParams):
    max_trade_size: float
    min_trade_size: float
    max_total_trade_size: float
    target_mc: float

async def force_trade_mc(
    params: ForceTradeMCParams
):
    send_message("Open force trade by MC")
    extracted = get_makers_and_tokens(params)
    base_config: TokenConfigInfo = extracted["base"]
    quote_config: TokenConfigInfo = extracted["quote"]
    union: MakersUnion = extracted["union"]
    
    base_market_data = DataLayerAdapter.get_market_data(base_config.chain, base_config.pair)
    quote_market_data = DataLayerAdapter.get_market_data(quote_config.chain, quote_config.pair)

    mc = base_market_data["mc"]
    is_buy = mc < params.target_mc

    total_trade_size = 0


    while is_buy == (mc < params.target_mc) and total_trade_size < params.max_total_trade_size:
        trade_size = random.uniform(params.min_trade_size, params.max_trade_size)
        trade_value = trade_size / (quote_market_data["price"] if is_buy else base_market_data["price"])

        await union.execute_swap(
            quote_config.address if is_buy else base_config.address,
            base_config.address if is_buy else quote_config.address,
            params.protocol,
            trade_value,
            0 # to-do: calculate min amount out based on slippage
        )

        total_trade_size += trade_size

        base_market_data = DataLayerAdapter.get_market_data(base_config.chain, base_config.pair)
        quote_market_data = DataLayerAdapter.get_market_data(quote_config.chain, quote_config.pair)

    send_message("Done force trade by MC")

