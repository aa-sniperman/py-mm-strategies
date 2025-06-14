from strategies.trading.tp_sl.base import TPSLBaseParams, TPSLBaseStates, BaseTPSLMM
from parameters.client import get_strategy_params
from strategy_metadata.type import SinglePairMMMetadata
from adapters.data_layer import DataLayerAdapter
from utils.chart import cal_rolling_twap
from bot import send_message
import time


class TWAPTPSLParams(TPSLBaseParams):
    candle_interval: str
    rolling_window: int
    tp_price: float
    sl_price: float


class TWAPTPSLStates(TPSLBaseStates):
    _: int = 0


class TWAPTPSLMM(BaseTPSLMM):
    def __init__(self, metadata: SinglePairMMMetadata, maker_key: str):
        super().__init__(metadata, maker_key)

    def _update_params(self):
        raw = get_strategy_params(self.metadata.key)

        self.params = TWAPTPSLParams(
            tp_price=raw["tpPrice"],
            sl_price=raw["slPrice"],
            sell_on_low=raw["sellOnLow"],
            rolling_window=raw["rollingWindow"],
            avg_refresh_time=raw["avgRefreshTime"],
            min_trade_size=float(raw["minSize"]),
            max_trade_size=float(raw["maxSize"]),
            slippage=float(raw["slippage"]),
        )

    def _update_states(self):
        try:
            base_market_data = DataLayerAdapter.get_market_data(
                self.metadata.chain, self.base_token_config.pair
            )
            quote_market_data = DataLayerAdapter.get_market_data(
                self.metadata.chain, self.quote_token_config.pair
            )   

            self.states = TWAPTPSLStates(
                base_price=base_market_data["price"],
                quote_price=quote_market_data["price"],
            )

        except Exception as e:
            send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")

    async def run(self):
        while True:
            self._update_params()
            self._update_states()

            now = int(time.time())

            ohlcvs = DataLayerAdapter.get_ohlcvs(
                self.base_token_config.pair,
                self.params.candle_interval,
                now - 24 * 3600,
                now,
            )

            df = cal_rolling_twap(ohlcvs, self.params.rolling_window)

            # Drop rows where RSI is NaN
            first_valid = df.dropna(subset=["twap"]).iloc[-1]

            # Extract ts and rsi
            ts = first_valid["ts"]
            twap = first_valid["twap"]

            max_lag = 16 * 60 if self.params.candle_interval == "15m" else 61 * 60
            if ts + max_lag < now:
                print(f"{self.metadata.name}: TWAP data lagging")
                continue

            if twap > self.params.tp_price:
                send_message(f"🚨 {self.metadata.name}: TWAP surged above TP price. Tping...")
                await self._sell()
            elif twap < self.params.sl_price:
                send_message(f"🚨 {self.metadata.name}: Price change dropped below lower bound. {"Sling" if self.params.sell_on_low else "Buying dip"}...")
                if self.params.sell_on_low:
                    await self._sell()
                else:
                    await self._buy()

            time.sleep(5)
