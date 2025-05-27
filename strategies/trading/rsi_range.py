from strategies.trading.loss_control_base import LossControlBaseMM, LossControlBaseConfig, LossControlBaseStates
from parameters.client import get_strategy_params
from strategy_metadata.type import SinglePairMMMetadata
from adapters.data_layer import DataLayerAdapter
from utils.chart import cal_rsi
from pandas import DataFrame
import time


class RSIRangeConfig(LossControlBaseConfig):
    candle_interval: str  # 15m or 1h
    rsi_window: int
    upper_rsi: float
    lower_rsi: float


class RSIRangeStates(LossControlBaseStates):
    rsi: DataFrame


class RSIRangeMM(LossControlBaseMM):
    def __init__(self, metadata: SinglePairMMMetadata, maker_key: str):
        super().__init__(metadata, maker_key)

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
        raw = get_strategy_params(self.metadata.key)

        self.params = RSIRangeConfig(
            rsi_window=raw["rsiWindow"],
            candle_interval=raw["candleInterval"],
            upper_rsi=raw["upperRsi"],
            lower_rsi=raw["lowerRsi"],
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
        super()._update_states()
        now = int(time.time())
        ohlcvs = DataLayerAdapter.get_ohlcvs(
            self.base_token_config.pair, self.params.candle_interval, now - 7200 * self.params.rsi_window, now
        )
        self.states.rsi = cal_rsi(ohlcvs=ohlcvs, num_of_periods=self.params.rsi_window)

    async def run(self):
        while True:
            self._update_params()
            self._update_states()

            df = self.states.rsi
            if len(df) == 0:
                continue

            # Drop rows where RSI is NaN
            first_valid = df.dropna(subset=["rsi"]).iloc[-1]

            # Extract ts and rsi
            ts = first_valid["ts"]
            rsi = first_valid["rsi"]

            now = int(time.time())

            max_lag = 16 * 60 if self.params.candle_interval == "15m" else 61 * 60

            print(now, ts, ts + max_lag)
            if ts + max_lag < now:
                print(f"{self.metadata.name}: RSI data lagging")
                continue

            if rsi < self.params.lower_rsi:
                await self._buy()

            elif rsi > self.params.upper_rsi:
                await self._sell()

            time.sleep(5)
