from strategies.makers_union import MakersUnion
from strategies.force_trade.base import get_makers_and_tokens, ForceTradeBaseParams
from adapters.data_layer import DataLayerAdapter
from token_configs import TokenConfigInfo
from bot import send_message
from utils.random import random_array_with_sum
import time


class ForceTradeVolParams(ForceTradeBaseParams):
    vol: float
    is_buy: bool
    duration: int
    num_of_trades: int

async def force_trade_vol(
    params: ForceTradeVolParams
):
    send_message("Open force trade by Vol")

    extracted = get_makers_and_tokens(params)
    base_config: TokenConfigInfo = extracted["base"]
    quote_config: TokenConfigInfo = extracted["quote"]
    union: MakersUnion = extracted["union"]

    avg_interval = params.duration / (params.num_of_trades - 1)

    time_gaps = random_array_with_sum(params.num_of_trades - 1, params.duration, avg_interval * 0.8, avg_interval * 1.2)
    trade_vols = random_array_with_sum(params.num_of_trades, params.vol, params.vol * 0.5, params.vol * 1.5)
    
    for i in range(0, params.num_of_trades):
        trade_vol = trade_vols[i]

        await union.execute_swap(
            quote_config.address if params.is_buy else base_config.address,
            base_config.address if params.is_buy else quote_config.address,
            params.protocol,
            trade_vol,
            0 # to-do: calculate min amount out based on slippage
        )

        if i < len(time_gaps):
            time.sleep(time_gaps[i])


    send_message("Done force trade by vol")

