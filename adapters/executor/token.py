from typing import List
from adapters.executor.client import client


class ExecutorTokenHelper:
    @staticmethod
    async def fetch_token(chain: str, token: str):
        params = {"address": token, "chain": chain}
        response = await client.get("/token", params=params)
        if not response.content or response.content is None:
            return None
        return response.json()

    async def fetch_pair(chain: str, pair: str):
        params = {"pair": pair, "chain": chain}
        response = await client.get("/pair", params=params)
        if not response.content or response.content is None:
            return None
        return response.json()

    @staticmethod
    async def unwrap(chain: str, account: str, amount: float):
        body = {"chain": chain, "account": account, "amount": str(amount)}
        response = await client.post("/order/unwrap", data=body)
        return response.json()

    @staticmethod
    async def wrap(chain: str, account: str, amount: float):
        body = {"chain": chain, "account": account, "amount": str(amount)}
        response = await client.post("/order/wrap", data=body)
        return response.json()

    @staticmethod
    async def transfer_token(
        chain: str, account: str, token: str, amount: float, recipient: str
    ):
        body = {
            "chain": chain,
            "account": account,
            "token": token,
            "recipient": recipient,
            "amount": str(amount),
        }
        response = await client.post("/order/transfer", data=body)
        return response.json()

    @staticmethod
    async def batch_transfer_token(
        chain: str,
        account: str,
        token: str,
        amounts: List[float],
        recipients: List[str],
    ):
        filter_amounts = []
        filter_recipients = []

        for amount, recipient in zip(amounts, recipients):
            if amount > 0:
                filter_amounts.append(str(amount))
                filter_recipients.append(recipient)

        if not filter_amounts:
            return None  # or return an appropriate message/object

        body = {
            "chain": chain,
            "account": account,
            "token": token,
            "recipients": {"accounts": filter_recipients},
            "amounts": filter_amounts,
        }

        response = await client.post("/order/batch-transfer", data=body)
        return response.json()
