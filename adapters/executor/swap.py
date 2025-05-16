from typing import Optional
from adapters.executor.client import client

class ExecutorSwap:
    @staticmethod
    async def execute_swap(
        chain: str,
        account: str,
        protocol: str,
        token_in: str,
        token_out: str,
        amount_in: float,
        min_amount_out: Optional[float],
        recipeint: Optional[str]
    ): 
        body = {
            "chain": chain,
            "account": account,
            "tokenIn": token_in,
            "tokenOut": token_out,
            "recipient": recipeint if recipeint else account,
            "protocol": protocol,
            "amountIn": str(amount_in),
            "amountOutMin": str(min_amount_out) if min_amount_out else "0"
        }

        response = await client.post('/order/swap', params=body)
        return response.json()