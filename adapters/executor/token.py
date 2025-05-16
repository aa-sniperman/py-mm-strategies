from typing import List
from adapters.executor.client import client


class ExecutorTokenHelper:
    @staticmethod
    async def unwrap(chain: str, account: str, amount: float):
        body = {
            "chain": chain,
            "account": account,
            "amount": str(amount)
        }
        response = await client.post('/order/unwrap', params=body)
        return response.json()

    @staticmethod
    async def wrap(chain: str, account: str, amount: float):
        body = {
            "chain": chain,
            "account": account,
            "amount": str(amount)
        }
        response = await client.post('/order/wrap', params=body)
        return response.json()

    @staticmethod
    async def transfer_token(chain: str, account: str, token: str, amount: float, recipient: str):
        body = {
            "chain": chain,
            "account": account,
            "token": token,
            "recipient": recipient,
            "amount": str(amount)
        }
        response = await client.post('/order/transfer', params=body)
        return response.json()

    @staticmethod
    async def batch_transfer_token(chain: str, account: str, token: str, amounts: List[float], recipients: List[str]):
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
            "recipients": {
                "accounts": filter_recipients
            },
            "amounts": filter_amounts
        }

        response = await client.post('/order/batch-transfer', params=body)
        return response.json()
