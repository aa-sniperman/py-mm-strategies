from strategies.base import BaseStrategy
from strategies.makers_union import MakersUnion
from makers.loader import load_makers
from pydantic import BaseModel
from strategy_metadata.type import SinglePairMMMetadata
from token_configs import TokenConfig
from adapters.data_layer import DataLayerAdapter
import math
import time
import random


class LossControlBaseConfig(BaseModel):
    max_base_loss: float
    max_quote_loss: float
    max_base_loss_1h: float
    max_quote_loss_1h: float
    avg_refresh_time: float
    min_trade_size: float
    max_trade_size: float
    slippage: float


class LossControlBaseStates(BaseModel):
    quote_price: float
    base_price: float
    base_snapshot: float
    quote_snapshot: float
    base_snapshot_1h: float
    quote_snapshot_1h: float
    checkpoint: int


class LossControlBaseMM(BaseStrategy):
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
        self.params = LossControlBaseConfig(
            max_base_loss=0,
            max_base_loss_1h=0,
            max_quote_loss=0,
            max_quote_loss_1h=0,
            avg_refresh_time=0,
            min_trade_size=0,
            max_trade_size=0,
            slippage=0,
        )
        self.states = LossControlBaseStates(
            base_snapshot=0,
            quote_snapshot=0,
            base_snapshot_1h=0,
            quote_snapshot_1h=0,
            checkpoint=0,
        )

    def _update_states(self):
        now = int(time.time())

        self.union.sync_balances()

        if self.states.checkpoint == 0:
            self.states.checkpoint = now
            self.states.base_snapshot = self.union.balances["total"][
                self.base_token_config.address
            ]
            self.states.quote_snapshot = self.union.balances["total"][
                self.quote_token_config.address
            ]
            self.states.base_snapshot_1h = (self.states.base_snapshot,)
            self.states.quote_snapshot_1h = self.states.quote_snapshot

        else:
            next_checkpoint = self.states.checkpoint + 3600
            if next_checkpoint < now:
                self.states.checkpoint = now
                self.states.base_snapshot_1h = self.union.balances["total"][
                    self.base_token_config.address
                ]
                self.states.quote_snapshot_1h = self.union.balances["total"][
                    self.quote_token_config.address
                ]
        base_market_data = DataLayerAdapter.get_market_data(
            self.metadata["chain"], self.base_token_config.pair
        )
        quote_market_data = DataLayerAdapter.get_market_data(
            self.metadata["chain"], self.quote_token_config.pair
        )

        self.states.base_price = base_market_data["price"]
        self.states.quote_price = quote_market_data["price"]

    async def _buy(self):
        min_size = self.params.min_trade_size / self.states.quote_price

        current_quote_bal = self.union.balances["total"][
            self.quote_token_config.address
        ]
        current_loss = self.states.quote_snapshot - current_quote_bal
        current_loss_1h = self.states.quote_snapshot_1h - current_quote_bal

        max_size = min(
            self.params.max_trade_size / self.states.quote_price,
            current_quote_bal,
            self.params.max_quote_loss - current_loss,
            self.params.max_quote_loss_1h - current_loss_1h,
        )

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

        current_base_bal = self.union.balances["total"][self.base_token_config.address]
        current_loss = self.states.base_snapshot - current_base_bal
        current_loss_1h = self.states.base_snapshot_1h - current_base_bal

        max_size = min(
            self.params.max_trade_size / self.states.base_price,
            current_base_bal,
            self.params.max_base_loss - current_loss,
            self.params.max_base_loss_1h - current_loss_1h,
        )

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