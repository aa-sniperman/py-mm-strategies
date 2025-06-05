from pydantic import BaseModel
from strategies.base import BaseStrategy
from adapters.executor.swap import ExecutorSwap
from strategy_metadata.type import ArbitrageurDex2DexMetadata
from makers.loader import load_makers
from token_configs import TokenConfigInfo, get_token_config
from parameters.client import get_strategy_params
from adapters.data_layer import DataLayerAdapter
from bot import send_message
import math
import time
import asyncio


class ArbitrageurDex2DexConfig(BaseModel):
    min_trade_size: float
    max_trade_size: float
    min_gap_percent: float
    delay_time: int


class SingleDexStates(BaseModel):
    base_price: float
    quote_price: float
    base_balance: float
    quote_balance: float
    base_usd: float
    quote_usd: float


class Trade(BaseModel):
    base_to_quote: bool
    amount_in: float


class DexData(BaseModel):
    chain: str
    protocol: str
    wallet: str
    base_config: TokenConfigInfo
    quote_config: TokenConfigInfo


class ArbitrageurDex2DexStates(BaseModel):
    dex_1_states: SingleDexStates
    dex_2_states: SingleDexStates
    gap_percent: float


class ArbitrageurDex2Dex(BaseStrategy):
    def __init__(self, metadata: ArbitrageurDex2DexMetadata):
        super().__init__(metadata)
        self.dex_1_data = DexData(
            wallet=load_makers(f"{metadata.key}:dex_1_wallet")[0],
            chain=metadata.dex_1_metadata.chain,
            protocol=metadata.dex_1_metadata.protocol,
            base_config=get_token_config(metadata.dex_1_metadata.base),
            quote_config=get_token_config(metadata.dex_1_metadata.quote),
        )
        self.dex_2_data = DexData(
            wallet=load_makers(f"{metadata.key}:dex_2_wallet")[0],
            chain=metadata.dex_2_metadata.chain,
            protocol=metadata.dex_2_metadata.protocol,
            base_config=get_token_config(metadata.dex_2_metadata.base),
            quote_config=get_token_config(metadata.dex_2_metadata.quote),
        )

        self.states = ArbitrageurDex2DexStates(
            dex_1_states=SingleDexStates(
                base_balance=0,
                quote_balance=0,
                base_price=0,
                quote_price=0,
                quote_usd=0,
                base_usd=0,
            ),
            dex_2_states=SingleDexStates(
                base_balance=0,
                quote_balance=0,
                base_price=0,
                quote_price=0,
                quote_usd=0,
                base_usd=0,
            ),
        )

    def _update_params(self):
        raw = get_strategy_params(self.metadata.key)

        self.params = ArbitrageurDex2DexConfig(
            min_trade_size=raw["minSize"],
            max_trade_size=raw["maxSize"],
            min_gap_percent=raw["minGapPercent"],
        )

    def _get_dex_states(self, dex_data: DexData):
        base_market_data = DataLayerAdapter.get_market_data(
            dex_data.chain, dex_data.base_config.pair
        )
        quote_market_data = DataLayerAdapter.get_market_data(
            dex_data.chain, dex_data.quote_config.pair
        )

        base_price = base_market_data["price"]
        quote_price = quote_market_data["price"]

        raw_balances = DataLayerAdapter.get_balances(
            dex_data.chain,
            [dex_data.wallet],
            [dex_data.base_config.address, dex_data.quote_config.address],
            ["base", "quote"],
        )

        base_balance = raw_balances[dex_data.wallet]["base"]
        quote_balance = raw_balances[dex_data.wallet]["quote"]

        base_usd = base_balance * base_price
        quote_usd = quote_balance * quote_price

        return SingleDexStates(
            base_price=base_price,
            quote_price=quote_price,
            base_balance=base_balance,
            quote_balance=quote_balance,
            base_usd=base_usd,
            quote_usd=quote_usd,
        )

    def _update_states(self):
        dex_1_states = self._get_dex_states(self.dex_1_data)
        dex_2_states = self._get_dex_states(self.dex_2_data)
        self.states = ArbitrageurDex2DexStates(
            dex_1_states=dex_1_states,
            dex_2_states=dex_2_states,
            gap_percent=math.floor(
                10000
                * (dex_1_states.base_price - dex_2_states.base_price)
                / dex_2_states.base_price
            )
            / 100,
        )

    def _calculate_trades(self):
        gap_range = abs(self.states.gap_percent)

        if gap_range < self.params.min_gap_percent:
            return None

        max_gap_range = 4

        weight = min(gap_range / max_gap_range, 1)

        trade_size = self.params.min_trade_size + weight * (
            self.params.max_trade_size - self.params.min_trade_size
        )

        base_to_quote_dex_1 = self.states.gap_percent > 0

        trade_size = min(
            trade_size,
            (
                self.states.dex_1_states.base_balance
                if base_to_quote_dex_1
                else (
                    self.states.dex_1_states.quote_usd
                    / self.states.dex_1_states.base_price
                )
            )
            - 0.0001,
        )

        base_to_quote_dex_2 = self.states.gap_percent < 0

        trade_size = min(
            trade_size,
            (
                self.states.dex_2_states.base_balance
                if base_to_quote_dex_2
                else (
                    self.states.dex_2_states.quote_usd
                    / self.states.dex_2_states.base_price
                )
            )
            - 0.0001,
        )

        amount_in_dex_1 = min(
            trade_size
            / (
                1
                if base_to_quote_dex_1
                else self.states.dex_1_states.quote_price
                / self.states.dex_1_states.base_price
            ),
            (
                self.states.dex_1_states.base_balance
                if base_to_quote_dex_1
                else self.states.dex_1_states.quote_balance
            )
            - 0.0001,
        )

        amount_in_dex_2 = min(
            trade_size
            / (
                1
                if base_to_quote_dex_2
                else self.states.dex_2_states.quote_price
                / self.states.dex_2_states.base_price
            ),
            (
                self.states.dex_2_states.base_balance
                if base_to_quote_dex_2
                else self.states.dex_2_states.quote_balance
            )
            - 0.0001,
        )

        trade_dex_1 = Trade(
            base_to_quote=base_to_quote_dex_1,
            amount_in=math.floor(amount_in_dex_1 * 1e9) / 1e9,
        )

        trade_dex_2 = Trade(
            base_to_quote=base_to_quote_dex_2,
            amount_in=math.floor(amount_in_dex_2 * 1e9) / 1e9,
        )

        return {"trade_dex_1": trade_dex_1, "trade_dex_2": trade_dex_2}

    async def _make_trade(self, dex_data: DexData, trade: Trade):
        if trade is None:
            return
        if trade.amount_in <= 0:
            return

        print(f"Executing trade: {trade.model_dump_json()} on Dex {dex_data.protocol}...")
        res = await ExecutorSwap.execute_swap(
            chain=dex_data.chain,
            account=dex_data.wallet,
            token_in=(
                dex_data.base_config.address
                if trade.base_to_quote
                else dex_data.quote_config.address
            ),
            token_out=(
                dex_data.quote_config.address
                if trade.base_to_quote
                else dex_data.base_config.address
            ),
            amount_in=trade.amount_in,
            protocol=dex_data.protocol,
        )

        self._noti_trade(dex_data, res)

    def _noti_trade(self, dex_data: DexData, res: dict):
        base_to_quote = res["token_in"] == dex_data.base_config.address
        message = f"""
✅ **Trade executed** ✅

🔄 **Direction**: {'🔻 Sell' if base_to_quote else '🔺 Buy'}
💼 **Account**: {res["account"]}
🚉 **Dex**: ${res["protocol"]}
📝 **TX Hash**: {res["txHash"]}
💰 **Amount In**: {res["amountIn"]} ${dex_data.base_config.symbol if base_to_quote else dex_data.quote_config.symbol}
📊 **Dex1 Price**: 💵 ${self.states.dex_1_states.base_price}
🔗 **Dex2 Price**: 💵 ${self.states.dex_2_states.base_price}
📉 **Price Gap**: ${self.states.gap_percent}% 
---------------------------------------------
            """

        print(message)

    async def _make_trade_on_2_dexes(self, trade_dex_1: Trade, trade_dex_2: Trade):
        try:
            await asyncio.gather(
                self._make_trade(self.dex_1_data, trade_dex_1),
                self._make_trade(self.dex_2_data, trade_dex_2),
            )
            time.sleep(self.params.delay_time / 1000)
        except Exception as e:
            send_message(
                f"🚨 {self.metadata.name}: Failed when executing arb trades: {str(e)}"
            )

    async def run(self):
        while(True):
            self._update_params()
            self._update_states()

            trades = self._calculate_trades()

            if trades is not None:
                await self._make_trade_on_2_dexes(trades["trade_dex_1"], trades["trade_dex_2"])

            time.sleep(5)