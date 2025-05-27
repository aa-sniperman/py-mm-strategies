from strategies.trading.tp_sl.base import TPSLBaseParams, TPSLBaseStates, BaseTPSLMM
from parameters.client import get_strategy_params
from strategy_metadata.type import SinglePairMMMetadata
from adapters.data_layer import DataLayerAdapter
from bot import send_message
import time


class PChangeTPSLParams(TPSLBaseParams):
    candle_interval: str
    interval: int
    tp_percent: float
    sl_percent: float


class PChangeTPSLStates(TPSLBaseStates):
    p_change: float


class PChangeTPSLMM(BaseTPSLMM):
    def __init__(self, metadata: SinglePairMMMetadata, maker_key: str):
        super().__init__(metadata, maker_key)

    def _update_params(self):
        raw = get_strategy_params(self.metadata.key)

        self.params = PChangeTPSLParams(
            tp_percent=raw["tpPercent"],
            sl_percent=raw["slPercent"],
            sell_on_low=raw["sellOnLow"],
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

            now = int(time.time())

            ohlcvs = DataLayerAdapter.get_ohlcvs(
                self.base_token_config.pair,
                self.params.candle_interval,
                now - self.params.interval,
                now,
            )

            o_price = ohlcvs[len(ohlcvs) - 1]["o"]

            cur_price = base_market_data["price"]

            self.states = PChangeTPSLStates(
                base_price=cur_price,
                quote_price=quote_market_data["price"],
                p_change=100 * (cur_price - o_price) / o_price,
            )

        except Exception as e:
            send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")

    async def run(self):
        while True:
            self._update_params()
            self._update_states()

            if self.states.p_change > self.params.tp_percent:
                send_message(f"🚨 {self.metadata.name}: Price change surged above upper bound. Tping...")
                await self._sell()
            elif self.states.p_change < self.params.sl_percent:
                send_message(f"🚨 {self.metadata.name}: Price change dropped below lower bound. {"Sling" if self.params.sell_on_low else "Buying dip"}...")
                if self.params.sell_on_low:
                    await self._sell()
                else:
                    await self._buy()

            time.sleep(5)
