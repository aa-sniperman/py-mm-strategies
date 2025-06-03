from strategies.vol_maker.base import (
    SenderRecipientInfo,
)
from strategies.vol_maker.v1 import VolMakerV1
from adapters.data_layer import DataLayerAdapter
from adapters.executor.swap import ExecutorSwap
from bot import send_message
from utils.array import weighted_random_choice
import math
import time
import random


class VolMakerTron(VolMakerV1):
    def _pick_sender_and_recipient(self, is_accumulating: bool):
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

        biggest_wallet = max(
            eligible_recipients,
            key=lambda wallet: self.states.balances[self.makers.index(wallet)],
        )

        if is_accumulating:
            eligible_recipients = [
                sender for sender in eligible_senders if sender != biggest_wallet
            ]

        sender_weights = [
            self.states.balances[self.makers.index(sender)]
            for sender in eligible_senders
        ]

        total_balance = sum(self.states.balances)

        recipient_weights = [
            total_balance - self.states.balances[self.makers.index(recipient)]
            for recipient in eligible_recipients
        ]

        sender = weighted_random_choice(eligible_senders, sender_weights)
        if is_accumulating:
            sender = biggest_wallet

        recipient = biggest_wallet
        if not is_accumulating:
            recipient = weighted_random_choice(eligible_recipients, recipient_weights)

        return SenderRecipientInfo(
            sender=sender, recipient=recipient, fund_destination=""
        )

    async def _make_trade(self, sender, recipient):

        sender_quote_bal = DataLayerAdapter.get_balance(
            self.metadata.chain, sender, self.quote_token_config.address
        )
        sender_quote_value = sender_quote_bal * self.states.quote_price

        sender_base_bal = DataLayerAdapter.get_balance(
            self.metadata.chain, sender, self.base_token_config.address
        )
        sender_base_value = sender_base_bal * self.states.base_price

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
            balance - 10,
        )

        percent = random.randint(0, 100)
        trade_amount = ((max_trade - min_trade) * percent) / 100 + min_trade
        if trade_amount <= 0:
            return

        trade_amount = math.floor(1e9 * trade_amount) / 1e9

        try:
            print(
                f"Wallet {sender} {'buying' if is_buy else 'selling'} with {trade_amount}, recipient: {recipient}"
            )

            await ExecutorSwap.execute_swap(
                chain=self.metadata.chain,
                account=sender,
                protocol=self.metadata.protocol,
                token_in=(
                    self.quote_token_config.address
                    if is_buy
                    else self.base_token_config.address
                ),
                token_out=(
                    self.quote_token_config.address
                    if not is_buy
                    else self.base_token_config.address
                ),
                amount_in=trade_amount,
                recipient=recipient,
            )

        except Exception as e:
            if e is not None and len(str(e)) > 0:
                send_message(f"🚨 Error at {self.metadata.name}: {str(e)}")

        time.sleep(random.randint(10, 50) * self.params.timescale / 1000)

    async def run(self):
        while True:
            self._update_params()
            self._update_states()

            vol_ok = self._check_vol()
            print(
                f"Current vol: ${self.states.cur_1h_vol}. Target vol: ${self.params.target_vol_1h}"
            )
            if vol_ok:
                print("Done")
                time.sleep(30)
                continue

            number_of_trades = random.randint(1, 2)

            print(f"Making vol with {number_of_trades} random trades...")
            for i in range(number_of_trades):
                self._update_states()
                wallets = self._pick_sender_and_recipient()
                if wallets is not None:
                    print(
                        f"Picked sender: {wallets['sender']}. Picked recipient: {wallets['recipient']}"
                    )
                    await self._make_trade(
                        wallets["sender"],
                        wallets["recipient"],
                    )

            time.sleep(5)
