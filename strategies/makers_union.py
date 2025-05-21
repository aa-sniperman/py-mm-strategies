from typing import Dict, List, Optional
from pydantic import BaseModel
from adapters.data_layer import DataLayerAdapter
from adapters.executor.swap import ExecutorSwap
from bot import send_message
import random
import asyncio
import math


class MakersUnion(BaseModel):
    chain: str
    makers: List[str]
    tokens: List[str]
    balances: Dict[str, Dict[str, float]] = {}

    def __init__(
        self,
        chain: str,
        protocol: str,
        makers: List[str],
        tokens: List[str],
    ):
        super().__init__(chain=chain, protocol=protocol, makers=makers, tokens=tokens)

    def total_balance(self, token: str):
        return self.balances["total"][token]

    def sync_balances(self):
        self.balances = DataLayerAdapter.get_balances(
            chain=self.chain,
            accounts=self.makers,
            tokens=self.tokens,
            symbols=self.tokens,
        )

    async def _execute_swap_for_a_maker(
        self,
        maker: str,
        token_in: str,
        token_out: str,
        protocol: str,
        amount_in: float,
        min_amount_out: float,
        recipient: Optional[str],
    ):
        try:
            print(f"Maker {maker} trading {amount_in} {token_in} for {token_out}...")
            res = await ExecutorSwap.execute_swap(
                chain=self.chain,
                account=maker,
                protocol=protocol,
                token_in=token_in,
                token_out=token_out,
                amount_in=math.floor(amount_in * 1e9) / 1e9,
                min_amount_out=min_amount_out,
                recipient=recipient,
            )

            print(res)
        except Exception as e:
            send_message(f"Failed to execute swap for maker {maker}: {str(e)}")

    def calculate_inputs_for_swaps(
        self, token: str, amount_in: float
    ) -> Dict[str, float]:
        if self.balances["total"][token] * 0.95 < amount_in:
            send_message(
                f"Failed to execute swaps for {amount_in} {token}: Insufficient balance"
            )

        remaining_amount = amount_in

        allocations: Dict[str, float] = {}
        available: Dict[str, float] = {m: self.balances[m][token] for m in self.makers}

        shuffled_makers = self.makers[:]
        random.shuffle(shuffled_makers)

        while remaining_amount > 0:
            for maker in shuffled_makers:
                if remaining_amount <= 0:
                    break

                max_takeable = available[maker] * random.randint(5, 55) / 100

                if max_takeable < 1e-9:
                    continue

                allocation = min(remaining_amount, max_takeable)

                if allocation > 0:
                    allocations[maker] = allocations.get(maker, 0) + allocation
                    available[maker] -= allocation
                    remaining_amount -= allocation

        return allocations

    async def execute_swap(
        self,
        token_in: str,
        token_out: str,
        protocol: str,
        amount_in: float,
        min_amount_out: float,
        recipient: Optional[str],
    ):
        self.sync_balances()
        allocations = self.calculate_inputs_for_swaps(token_in, amount_in)

        await asyncio.gather(
            *(
                self._execute_swap_for_a_maker(
                    maker,
                    token_in,
                    token_out,
                    protocol,
                    amount,
                    min_amount_out,
                    recipient,
                )
                for (maker, amount) in allocations.items()
            )
        )
