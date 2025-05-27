import sys
from strategy_metadata.type import SinglePairMMMetadata
from strategies.trading.rsi_range import RSIRangeConfig, RSIRangeMM
from parameters.client import set_strategy_params
from strategies.base import BaseStrategy
from strategies.vol_maker.v1 import VolMakerV1
import asyncio


async def main():
    metadata = SinglePairMMMetadata(
        name="EQB RSI Range MM",
        type="rsi-mm",
        key="eqb-rsi",
        chain="arbitrum",
        protocol="camelot-v2",
        quote="WETH_ARB",
        base="EQB",
    )

    set_strategy_params(
        metadata.key,
        {
            "maxBaseLoss": 1000,
            "maxQuoteLoss": 0.15,
            "maxBaseLoss1h": 300,
            "maxQuoteLoss1h": 0.05,
            "avgRefreshTime": 60,
            "minSize": 50,
            "maxSize": 200,
            "slippage": 0,
            "candleInterval": "15m",
            "rsiWindow": 14,
            "upperRsi": 70,
            "lowerRsi": 30,
        },
    )
    runner = RSIRangeMM(metadata=metadata, maker_key="eqb")
    await runner.run()


if __name__ == "__main__":

    asyncio.run(main())
