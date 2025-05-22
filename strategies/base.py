from abc import ABC, abstractmethod
from strategy_metadata.type import StrategyMetadata

class BaseStrategy(ABC):
    def __init__(self, metadata: StrategyMetadata):
        self.metadata = metadata

    @abstractmethod
    def _update_params(self) -> None:
        pass

    @abstractmethod
    def _update_states(self) -> None:
        pass

    @abstractmethod
    async def run(self):
        pass