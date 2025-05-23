import sys
from strategy_metadata.type import load_strategy_metadata
from strategies.base import BaseStrategy
from strategies.vol_maker.v1 import VolMakerV1
import asyncio


async def main(metadata_filename: str):
    metadata = load_strategy_metadata(metadata_filename)
    runner: BaseStrategy
    if metadata is not None:
        if metadata["type"] == "vol-v1":
            runner = VolMakerV1(metadata)

    if runner is not None:
        await runner.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <metadata_filename>")
        sys.exit(1)

    metadata_filename = sys.argv[1]
    asyncio.run(main(metadata_filename))
