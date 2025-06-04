import asyncio
from parameters.client import get_strategy_params, set_strategy_params
from makers.loader import set_makers, load_makers
from pathlib import Path
import json
from token_configs import TokenConfig, set_token_config, get_token_config


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

    strat_keys = ["eqb", "pumpe", "sunana", "torch", "txbt"]
    PROJECT_ROOT = Path(__file__).resolve().parents[0]

    for strategy_key in strat_keys:
        makers = load_makers(strategy_key)
        print(makers)


if __name__ == "__main__":

    asyncio.run(main())
