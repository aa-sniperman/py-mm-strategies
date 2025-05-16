from strategies.vol_maker.base import (
    BaseVolMaker,
    BaseVolMakerConfig,
    SenderRecipientInfo,
)
from parameters.client import get_strategy_params
from makers.loader import load_makers
from pydantic import BaseModel
from strategy_metadata.type import VolMakerMetadata
from token_configs import TokenConfig
from adapters.data_layer import DataLayerAdapter
from adapters.executor.swap import ExecutorSwap
from adapters.executor.token import ExecutorTokenHelper
from telebot import send_message
from utils.array import weighted_random_choice
import math
import time
import random


class VolMakerV1Config(BaseVolMakerConfig):
    target_vol_1h: float


class VolMakerV1States(BaseModel):
    balances: list[float]
    quote_price: float
    base_price: float
    cur_1h_vol: float
    cur_24h_vol: float


class VolMakerV1(BaseVolMaker):
    def __init__(self, metadata: VolMakerMetadata):
        super.__init__(metadata)
        self.original_makers = load_makers(metadata.key)
        self.makers = []
        self.base_token_config = TokenConfig[metadata.base]
        self.quote_token_config = TokenConfig[metadata.quote]

    def _update_params(self):
        raw = get_strategy_params(self.metadata.key)
        self.params = VolMakerV1Config(
            target_vol_1h=float(raw["targetVol1h"]),
            min_trade_size=float(raw["minSize"]),
            max_trade_size=float(raw["maxSize"]),
            timescale=float(raw["timescale"]),
            max_wallets_num=int(raw["makersNumber"]),
        )

    def _update_states(self):
        try:
            base_market_data = DataLayerAdapter.get_market_data(
                self.metadata.chain, self.base_token_config.pair
            )
            quote_market_data = DataLayerAdapter.get_market_data(
                self.metadata.chain, self.quote_token_config.pair
            )
            raw_balances = DataLayerAdapter.get_balances(
                self.metadata.chain,
                self.original_makers,
                [self.base_token_config.address, self.quote_token_config.address],
                ["base", "quote"],
            )
            balances: list[float] = []
            for maker in self.original_makers:
                balances.append(
                    raw_balances[maker]["base"] * base_market_data["price"]
                    + raw_balances[maker]["quote"] * quote_market_data["price"]
                )

            paired = [
                {"maker": maker, "balance": balances[index]}
                for index, maker in enumerate(self.original_makers)
            ]

            paired.sort(key=lambda x: x["balance"], reverse=True)

            self.makers = [p["maker"] for p in paired[: self.params.max_wallets_num]]

            self.states = VolMakerV1States(
                quote_price=quote_market_data["price"],
                base_price=base_market_data["price"],
                cur_1h_vol=base_market_data["volume_1h"],
                cur_24h_vol=base_market_data["volume_24h"],
                balances=[p["balance"] for p in paired[: self.params.max_wallets_num]],
            )
        except Exception as e:
            send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")

    def _pick_sender_and_recipient(self):
        min_trade_size = self.params.min_trade_size

        eligible_senders = [
            maker
            for i, maker in enumerate(self.makers)
            if self.states.balances[i] >= min_trade_size
        ]

        eligible_recipients = self.makers

        if len(eligible_senders) == 0 or len(eligible_recipients) == 0:
            send_message(
                f"🚨 {self.metadata.name}: There is no wallet with enough money to trade"
            )
            return None

        sender_weights = [
            self.states.balances[self.makers.index(sender)]
            for sender in eligible_senders
        ]

        total_balance = sum(self.states.balances)

        fund_destination_weights = [
            self.states.balances[self.makers.index(recipient)]
            for recipient in eligible_recipients
        ]

        recipient_weights = [
            total_balance - self.states.balances[self.makers.index(recipient)]
            for recipient in eligible_recipients
        ]

        sender = weighted_random_choice(eligible_senders, sender_weights)
        recipient = weighted_random_choice(eligible_recipients, recipient_weights)
        fund_destination = weighted_random_choice(
            eligible_recipients, fund_destination_weights
        )

        return SenderRecipientInfo(
            sender=sender, recipient=recipient, fund_destination=fund_destination
        )

    async def _make_trade(self, sender, recipient, fund_des):

        sender_quote_bal = DataLayerAdapter.get_balance(
            self.metadata.chain, sender, self.base_token_config.address
        )
        sender_quote_value = sender_quote_bal * self.states.quote_price

        sender_base_bal = DataLayerAdapter.get_balance(
            self.metadata.chain, sender, self.quote_token_config.address
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
                        self.metadata.chain,
                        sender,
                        self.quote_token_config.address,
                        math.floor((sender_quote_bal - 0.001) * 1e9) / 1e9,
                        fund_des,
                    )
                    time.sleep(10)
                except Exception as e:
                    send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")
            if sender_base_bal > 0.001:
                try:
                    await ExecutorTokenHelper.transfer_token(
                        self.metadata.chain,
                        sender,
                        self.base_token_config.address,
                        math.floor((sender_base_bal - 0.001) * 1e9) / 1e9,
                        fund_des,
                    )
                except Exception as e:
                    send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")
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
            balance,
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
                    f"Wallet {sender} {"buying" if is_buy else "selling"} with {trade_amount}, recipient: {recipient}"
                )

                res = await ExecutorSwap.execute_swap(
                    chain=self.metadata.chain,
                    account=sender,
                    protocol=self.metadata.protocol,
                    token_in=(
                        self.quote_token_config.address
                        if is_buy
                        else self.base_token_config.address
                    ),
                    token_out=self.base_token_config.address,
                    amount_in=trade_amount,
                    recipeint=recipient,
                )

                print(res)

                success = True
            except Exception as e:
                send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")
                attempts += 1
                time.sleep(5)

        time.sleep(random.randint(10, 50) * self.params.timescale / 1000)

    def _check_vol(self) -> bool:
        if self.states.cur_1h_vol >= self.params.target_vol_1h:
            return True
        target_vol_24h = self.params.target_vol_1h * 24
        if self.states.cur_24h_vol * 2 < target_vol_24h:
            send_message(
                f"🚨 {self.metadata.name}: Low vol 24h. Expected: ${target_vol_24h}. Current: ${self.states.cur_24h_vol}"
            )

    async def run(self):
        while(True):
            self._update_params()
            self._update_states()

            vol_ok = self._check_vol()
            if vol_ok:
                time.sleep(30)
                continue

            number_of_trades = random.randint(2, 4)

            print(f"Making vol with {number_of_trades} random trades...")
            for i in 0..number_of_trades:
                self._update_states()
                wallets = self._pick_sender_and_recipient()
                if wallets is not None:
                    print(f"Picked sender: {wallets.sender}. Picked recipient: {wallets.recipient}")
                    await self._make_trade(wallets.sender, wallets.recipient, wallets.fund_destination)

            time.sleep(5)
