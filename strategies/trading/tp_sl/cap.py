from strategies.trading.tp_sl.base import TPSLBaseParams, TPSLBaseStates, BaseTPSLMM
from parameters.client import get_strategy_params
from strategy_metadata.type import SinglePairMMMetadata
from adapters.data_layer import DataLayerAdapter
from bot import send_message
import math
import time
import random


class CapTPSLParams(TPSLBaseParams):
    hard_TP_cap: float
    soft_TP_cap: float
    hard_SL_cap: float
    soft_SL_cap: float


class CapTPSLStates(TPSLBaseStates):
    cap: float


class CapTPSLMM(BaseTPSLMM):
    def __init__(self, metadata: SinglePairMMMetadata):
        super().__init__(metadata)

    def _update_params(self):
        raw = get_strategy_params(self.metadata["key"])

        self.params = CapTPSLParams(
            hard_TP_cap=raw["hardTPCap"],
            soft_TP_cap=raw["softTPCap"],
            hard_SL_cap=raw["hardSLCap"],
            soft_SL_cap=raw["softSLCap"],
            sell_on_low=raw["sellOnLow"],
            avg_refresh_time=raw["avgRefreshTime"],
            min_trade_size=float(raw["minSize"]),
            max_trade_size=float(raw["maxSize"]),
            slippage=float(raw["slippage"]),
        )

    def _update_states(self):
        try:
            base_market_data = DataLayerAdapter.get_market_data(
                self.metadata["chain"], self.base_token_config.pair
            )
            quote_market_data = DataLayerAdapter.get_market_data(
                self.metadata["chain"], self.quote_token_config.pair
            )

            self.states = CapTPSLStates(
                base_price=base_market_data["price"],
                quote_price=quote_market_data["price"],
                cap=base_market_data["mc"],
            )

        except Exception as e:
            send_message(f"🚨 Error at {self.metadata['name']}: {str(e)}")

    async def _buy_soft(self):
        min_size = 0.5 * self.params.min_trade_size / self.states.quote_price

        max_size = 0.5 * self.params.max_trade_size / self.states.quote_price

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

    async def _sell_soft(self):
        min_size = 0.5 * self.params.min_trade_size / self.states.base_price

        max_size = 0.5 * self.params.max_trade_size / self.states.base_price

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

            cap = self.states.cap
            if cap > self.params.hard_TP_cap:
                await self._sell()
            elif cap > self.params.soft_TP_cap:
                await self._sell_soft()
            elif cap < self.params.hard_SL_cap:
                if self.params.sell_on_low:
                    await self._sell()
                else:
                    await self._buy()
            elif cap < self.params.soft_SL_cap:
                if self.params.sell_on_low:
                    await self._sell_soft()
                else:
                    await self._buy_soft()

            time.sleep(5)
