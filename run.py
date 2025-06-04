import sys
from strategy_metadata.type import (
    StrategyMetadata,
    VolMakerMetadata,
)
from strategy_metadata.client import get_strategy_metadata
from strategies.base import BaseStrategy
from strategies.vol_maker.v1 import VolMakerV1
from strategies.vol_maker.sol_bundle import VolMakerSolBundle
from strategies.vol_maker.tron import VolMakerTron
import asyncio


async def main(strat_key: str):
    metadata = get_strategy_metadata(strat_key, StrategyMetadata)
    runner: BaseStrategy
    if metadata.type == "vol-v1":
        runner = VolMakerV1(get_strategy_metadata(strat_key, VolMakerMetadata))
    if metadata.type == "vol-sol-bundle":
        runner = VolMakerSolBundle(
            get_strategy_metadata(strat_key, VolMakerMetadata)
        )
    if metadata.type == "tron-vol":
        runner = VolMakerTron(
            get_strategy_metadata(strat_key, VolMakerMetadata)
        )

    if runner is not None:
        await runner.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <strat_key>")
        sys.exit(1)

    strat_key = sys.argv[1]
    asyncio.run(main(strat_key))
