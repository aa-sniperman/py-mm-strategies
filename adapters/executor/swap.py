from typing import Optional
from typing import List, TypedDict
from adapters.executor.client import client


class SwapItem(TypedDict):
    tokenIn: str
    tokenOut: str
    protocol: str
    account: str
    recipient: str
    amountIn: str
    amountOutMin: str


class ExecutorSwap:
    @staticmethod
    async def execute_swap(
        chain: str,
        account: str,
        protocol: str,
        token_in: str,
        token_out: str,
        amount_in: float,
        min_amount_out: Optional[float] = None,
        recipient: Optional[str] = None,
    ):
        body = {
            "chain": chain,
            "account": account,
            "tokenIn": token_in,
            "tokenOut": token_out,
            "recipient": recipient if recipient else account,
            "protocol": protocol,
            "amountIn": str(amount_in),
            "amountOutMin": str(min_amount_out) if min_amount_out else "0",
        }

        print(body)
        response = await client.post("/order/swap", data=body)
        return response.json()

    @staticmethod
    async def execute_multi_swaps(chain: str, items: List[SwapItem]):
        body = {
            "chain": chain,
            "items": items,
        }

        print(body)

        response = await client.post("/order/multi-swap", json=body)
        return response.json()
