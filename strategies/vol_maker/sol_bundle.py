from strategies.vol_maker.v1 import VolMakerV1States, VolMakerV1
from makers.loader import load_makers
from strategy_metadata.type import VolMakerMetadata
from token_configs import TokenConfig
from adapters.data_layer import DataLayerAdapter
from adapters.executor.swap import ExecutorSwap
from adapters.executor.token import ExecutorTokenHelper
from bot import send_message
import math
import time
import random


class VolMakerSolBundle(VolMakerV1):
    # xy = (x + dx)(y - dy)
    # 0 = ydx - xdy - dxdy
    # dy(x + dx) = ydx
    # dy = ydx / (x + dx)

    def __init__(self, metadata: VolMakerMetadata):
        super().__init__(metadata)
        self.original_makers = load_makers(metadata["key"])
        self.makers = []
        self.base_token_config = TokenConfig[metadata["base"]]
        self.quote_token_config = TokenConfig[metadata["quote"]]
        self.states = VolMakerV1States(
            quote_price=0,
            base_price=0,
            cur_1h_vol=0,
            cur_24h_vol=0,
            balances=[],
        )

    async def _get_amount_out(self, token_in: str, token_out, amount_in: str):
        pool_holding_info = DataLayerAdapter.get_pool_holdings(
            self.base_token_config.pair
        )

        holding_in = pool_holding_info[token_in]
        holding_out = pool_holding_info[token_out]
        expect_amount_out = holding_out * amount_in / (holding_in + amount_in)
        slippage = 0.1
        min_amount_out = expect_amount_out * slippage

        return min_amount_out

    async def _make_trade(self, sender, recipient, fund_des):

        sender_quote_bal = DataLayerAdapter.get_balance(
            self.metadata["chain"], sender, self.quote_token_config.address
        )
        sender_quote_value = sender_quote_bal * self.states.quote_price

        sender_base_bal = DataLayerAdapter.get_balance(
            self.metadata["chain"], sender, self.base_token_config.address
        )
        sender_base_value = sender_base_bal * self.states.base_price

        if (
            sender_quote_value < self.params.min_trade_size
            and sender_base_value < self.params.min_trade_size
        ):
            if sender == fund_des:
                return
            print(
                f"Not enough money to trade, gathering funds from ${sender} to ${fund_des}..."
            )
            if sender_quote_bal > 0.001:
                try:
                    await ExecutorTokenHelper.transfer_token(
                        self.metadata["chain"],
                        sender,
                        self.quote_token_config.address,
                        math.floor((sender_quote_bal - 0.001) * 1e9) / 1e9,
                        fund_des,
                    )
                    time.sleep(10)
                except Exception as e:
                    send_message(f"🚨 Error at {self.metadata['name']}: {str(e)}")
            if sender_base_bal > 0.001:
                try:
                    await ExecutorTokenHelper.transfer_token(
                        self.metadata["chain"],
                        sender,
                        self.base_token_config.address,
                        math.floor((sender_base_bal - 0.001) * 1e9) / 1e9,
                        fund_des,
                    )
                except Exception as e:
                    send_message(f"🚨 Error at {self.metadata['name']}: {str(e)}")
            return

        is_buy: bool

        if sender_quote_value < self.params.min_trade_size:
            is_buy = False
        elif sender_base_value < self.params.min_trade_size:
            is_buy = True
        else:
            total_value = sender_quote_value + sender_base_value
            buy_prob = sender_quote_value / total_value
            is_buy = random.random() < buy_prob

        balance = sender_quote_bal if is_buy else sender_base_bal

        min_trade = self.params.min_trade_size / (
            self.states.quote_price if is_buy else self.states.base_price
        )

        max_trade = min(
            self.params.max_trade_size
            / (self.states.quote_price if is_buy else self.states.base_price),
            balance - 0.0002,
        )

        percent = random.randint(0, 100)
        trade_amount = ((max_trade - min_trade) * percent) / 100 + min_trade
        if trade_amount <= 0:
            return

        trade_amount = math.floor(1e9 * trade_amount) / 1e9

        attempts = 0
        success = False

        while attempts < 3 and success is False:
            try:
                print(
                    f"Wallet {sender} {'buying' if is_buy else 'selling'} with {trade_amount}, recipient: {recipient}"
                )

                token_in = (
                    self.quote_token_config.address
                    if is_buy
                    else self.base_token_config.address
                )
                token_out = (
                    self.quote_token_config.address
                    if not is_buy
                    else self.base_token_config.address
                )
                protocol = self.metadata["protocol"]

                min_amount_out = self._get_amount_out(
                    token_in=token_in, token_out=token_out, amount_in=trade_amount
                )

                res = await ExecutorSwap.execute_multi_swaps(
                    chain=self.metadata["chain"],
                    items=[
                        {
                            "tokenIn": token_in,
                            "tokenOut": token_out,
                            "protocol": protocol,
                            "account": sender,
                            "recipient": recipient,
                            "amountIn": str(math.floor(1e9 * trade_amount) / 1e9),
                            "amountOutMin": str(math.floor(1e9 * min_amount_out) / 1e9),
                        },
                        {
                            "tokenIn": token_out,
                            "tokenOut": token_in,
                            "protocol": protocol,
                            "account": recipient,
                            "recipient": sender,
                            "amountIn": str(math.floor(1e9 * min_amount_out) / 1e9),
                            "amountOutMin": str(0),
                        },
                    ],
                )

                print(res)

                success = True
            except Exception as e:
                send_message(f"🚨 Error at {self.metadata['name']}: {str(e)}")
                attempts += 1
                time.sleep(5)

        time.sleep(random.randint(10, 50) * self.params.timescale / 1000)
