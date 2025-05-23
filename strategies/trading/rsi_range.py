from strategies.base import BaseStrategy
from strategies.makers_union import MakersUnion
from parameters.client import get_strategy_params
from makers.loader import load_makers
from pydantic import BaseModel
from strategy_metadata.type import RSIRangeMMMetadata
from token_configs import TokenConfig
from adapters.data_layer import DataLayerAdapter
from bot import send_message
from utils.chart import cal_rsi
from pandas import DataFrame
import math
import time
import random


class RSIRangeConfig(BaseModel):
    candle_interval: str  # 15m or 1h
    rsi_window: int
    upper_rsi: float
    lower_rsi: float
    max_base_loss: float
    max_quote_loss: float
    max_base_loss_1h: float
    max_quote_loss_1h: float
    avg_refresh_time: float
    min_trade_size: float
    max_trade_size: float
    slippage: float


class RSIRangeStates(BaseModel):
    rsi: DataFrame
    quote_price: float
    base_price: float
    base_snapshot: float
    quote_snapshot: float
    base_snapshot_1h: float
    quote_snapshot_1h: float
    checkpoint: int


class RSIRangeMM(BaseStrategy):
    def __init__(self, metadata: RSIRangeMMMetadata):
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
        self.states = RSIRangeStates(
            quote_price=0,
            base_price=0,
            rsi=[],
            base_snapshot=0,
            quote_snapshot=0,
            base_snapshot_1h=0,
            quote_snapshot_1h=0,
            checkpoint=0,
        )

    def _update_params(self):
        raw = get_strategy_params(self.metadata["key"])

        self.params = RSIRangeConfig(
            rsi_window=raw["rsiWindow"],
            candle_interval=raw["rsiInterval"],
            upper_rsi=raw["upperRSI"],
            lower_rsi=raw["lowerRSI"],
            max_base_loss=raw["maxBaseLoss"],
            max_quote_loss=raw["maxQuoteLoss"],
            max_base_loss_1h=raw["maxBaseLoss1h"],
            max_quote_loss_1h=raw["maxQuoteLoss1h"],
            avg_refresh_time=raw["avgRefreshTime"],
            min_trade_size=float(raw["minSize"]),
            max_trade_size=float(raw["maxSize"]),
            slippage=float(raw["slippage"]),
        )

    def _update_states(self):
        try:
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

            ohlcvs = DataLayerAdapter.get_ohlcvs(
                self.base_token_config.pair, self.params.candle_interval, now - 21600, now
            )
            self.states.rsi = cal_rsi(
                ohlcvs=ohlcvs, num_of_periods=self.params.rsi_window
            )

            base_market_data = DataLayerAdapter.get_market_data(
                self.metadata["chain"], self.base_token_config.pair
            )
            quote_market_data = DataLayerAdapter.get_market_data(
                self.metadata["chain"], self.quote_token_config.pair
            )

            self.states.base_price = base_market_data["price"]
            self.states.quote_price = quote_market_data["price"]

        except Exception as e:
            send_message(f"🚨 Error at {self.metadata['name']}: {str(e)}")

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

    async def run(self):
        while True:
            self._update_params()
            self._update_states()

            df = self.states.rsi
            if len(df) == 0:
                continue

            # Drop rows where RSI is NaN
            first_valid = df.dropna(subset=["rsi"]).iloc[0]

            # Extract ts and rsi
            ts = first_valid["ts"]
            rsi = first_valid["rsi"]

            now = int(time.time())

            max_lag = 16 * 60 if self.params.candle_interval == "15m" else 61 * 60
            if ts + max_lag < now:
                print(f"{self.metadata['name']}: RSI data lagging")
                continue

            if rsi < self.params.lower_rsi:
                await self._buy()

            elif rsi > self.params.upper_rsi:
                await self._sell()

            time.sleep(5)
