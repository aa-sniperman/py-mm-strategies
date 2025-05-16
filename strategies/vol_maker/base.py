from abc import ABC, abstractmethod
from strategy_metadata.type import VolMakerMetadata
from typing import TypedDict
from pydantic import BaseModel

class BaseVolMakerConfig(BaseModel):
    min_trade_size: float
    max_trade_size: float
    timescale: float
    max_wallets_num: int

class SenderRecipientInfo(TypedDict):
    sender: str
    recipient: str
    fund_destination: str

class BaseVolMaker(ABC):

    def __init__(self, metadata: VolMakerMetadata):
        self.metadata = metadata

    @abstractmethod
    def _update_params(self) -> None:
        pass

    @abstractmethod
    def _update_states(self) -> None:
        pass

    @abstractmethod
    def _check_vol(self) -> bool:
        pass

    @abstractmethod
    def _pick_sender_and_recipient(self) -> SenderRecipientInfo:
        pass

    @abstractmethod
    async def _make_trade(self, sender: str, recipient: str, fund_des: str):
        pass

    @abstractmethod
    async def run(self):
        pass