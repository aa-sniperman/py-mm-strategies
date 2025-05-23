from strategies.base import BaseStrategy
from strategies.makers_union import MakersUnion
from makers.loader import load_makers
from pydantic import BaseModel
from strategy_metadata.type import SinglePairMMMetadata
from token_configs import TokenConfig
import math
import time
import random


class TPSLBaseParams(BaseModel):
    sell_on_low: bool # determine stop loss or buy dip
    avg_refresh_time: float
    min_trade_size: float
    max_trade_size: float
    slippage: float


class TPSLBaseStates(BaseModel):
    quote_price: float
    base_price: float


class BaseTPSLMM(BaseStrategy):
    def __init__(self, metadata: SinglePairMMMetadata):
        super().__init__(metadata)
        makers = load_makers(metadata["key"])

        self.base_token_config = TokenConfig[metadata["base"]]
        self.quote_token_config = TokenConfig[metadata["quote"]]

        self.union = MakersUnion(
            metadata.chain,
            metadata.protocol,
            makers,
            [self.base_token_config.address, self.quote_token_config.address],
        )

        self.params = TPSLBaseParams(
            avg_refresh_time=0,
            min_trade_size=0,
            max_trade_size=0,
            slippage=0
        )

        self.states = TPSLBaseStates(
            quote_price=0,
            base_price=0
        )

    async def _buy(self):
        min_size = self.params.min_trade_size / self.states.quote_price

        max_size = self.params.max_trade_size / self.states.quote_price

        if max_size <= min_size:
            return

        trade_size = random.uniform(min_size, max_size)

        if trade_size > 1e-4:
            await self.union.execute_swap(
                self.quote_token_config.address,
                self.base_token_config.address,
                self.metadata.protocol,
                math.floor(trade_size * 1e9) / 1e9,
                0,  # todo: add slippage
                None,
            )

        time.sleep(self.params.avg_refresh_time)

    async def _sell(self):
        min_size = self.params.min_trade_size / self.states.base_price

        max_size = self.params.max_trade_size / self.states.base_price

        if max_size <= min_size:
            return

        trade_size = random.uniform(min_size, max_size)

        if trade_size > 1e-4:
            await self.union.execute_swap(
                self.base_token_config.address,
                self.quote_token_config.address,
                self.metadata.protocol,
                math.floor(trade_size * 1e9) / 1e9,
                0,  # todo: add slippage
                None,
            )

        time.sleep(self.params.avg_refresh_time)