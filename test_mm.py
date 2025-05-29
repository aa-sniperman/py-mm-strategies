import sys
from strategy_metadata.type import SinglePairMMMetadata
from strategies.trading.rsi_range import RSIRangeConfig, RSIRangeMM
from parameters.client import set_strategy_params
from strategies.base import BaseStrategy
from strategies.vol_maker.v1 import VolMakerV1
from adapters.data_layer import DataLayerAdapter
import asyncio


async def main():
    # metadata = SinglePairMMMetadata(
    #     name="EQB RSI Range MM",
    #     type="rsi-mm",
    #     key="eqb-rsi",
    #     chain="arbitrum",
    #     protocol="camelot-v2",
    #     quote="WETH_ARB",
    #     base="EQB",
    # )

    # set_strategy_params(
    #     metadata.key,
    #     {
    #         "maxBaseLoss": 1000,
    #         "maxQuoteLoss": 0.15,
    #         "maxBaseLoss1h": 300,
    #         "maxQuoteLoss1h": 0.05,
    #         "avgRefreshTime": 60,
    #         "minSize": 50,
    #         "maxSize": 200,
    #         "slippage": 0,
    #         "candleInterval": "15m",
    #         "rsiWindow": 14,
    #         "upperRsi": 70,
    #         "lowerRsi": 30,
    #     },
    # )
    # runner = RSIRangeMM(metadata=metadata, maker_key="eqb")
    # await runner.run()

    data = DataLayerAdapter.get_pool_holdings(
        "967p57PHxv4xaPUFEhbu6aGaxVGEsXHJXNtYg96fbyT"
    )
    print(data["9KweAdQhYk7HYz8VKDjX1VxofFjkkTPEfdvQz2N7s4G4"])


if __name__ == "__main__":

    asyncio.run(main())
