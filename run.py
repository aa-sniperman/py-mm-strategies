import sys
from strategy_metadata.type import (
    load_strategy_metadata,
    StrategyMetadata,
    VolMakerMetadata,
)
from strategies.base import BaseStrategy
from strategies.vol_maker.v1 import VolMakerV1
from strategies.vol_maker.sol_bundle import VolMakerSolBundle
from strategies.vol_maker.tron import VolMakerTron
import asyncio


async def main(metadata_filename: str):
    metadata = load_strategy_metadata(metadata_filename, StrategyMetadata)
    runner: BaseStrategy
    if metadata.type == "vol-v1":
        runner = VolMakerV1(load_strategy_metadata(metadata_filename, VolMakerMetadata))
    if metadata.type == "vol-sol-bundle":
        runner = VolMakerSolBundle(
            load_strategy_metadata(metadata_filename, VolMakerMetadata)
        )
    if metadata.type == "tron-vol":
        runner = VolMakerTron(
            load_strategy_metadata(metadata_filename, VolMakerMetadata)
        )

    if runner is not None:
        await runner.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <metadata_filename>")
        sys.exit(1)

    metadata_filename = sys.argv[1]
    asyncio.run(main(metadata_filename))
