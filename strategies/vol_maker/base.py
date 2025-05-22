from abc import abstractmethod
from typing import TypedDict
from pydantic import BaseModel
from strategies.base import BaseStrategy

class BaseVolMakerConfig(BaseModel):
    min_trade_size: float
    max_trade_size: float
    timescale: float
    max_wallets_num: int

class SenderRecipientInfo(TypedDict):
    sender: str
    recipient: str
    fund_destination: str

class BaseVolMaker(BaseStrategy):
    @abstractmethod
    def _check_vol(self) -> bool:
        pass

    @abstractmethod
    def _pick_sender_and_recipient(self) -> SenderRecipientInfo:
        pass

    @abstractmethod
    async def _make_trade(self, sender: str, recipient: str, fund_des: str):
        pass
