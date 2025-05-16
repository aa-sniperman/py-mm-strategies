from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    @abstractmethod
    async def run(self):
        pass