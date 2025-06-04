import asyncio
from parameters.client import get_strategy_params, set_strategy_params
from strategy_metadata.client import set_strategy_metadata
from pathlib import Path
import json



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

    strat_keys = [
        "eqb",
        "pumpe",
        "sunana",
        "torch",
        "txbt"
    ]
    PROJECT_ROOT = Path(__file__).resolve().parents[0]

    for strategy_key in strat_keys:
        file_path = PROJECT_ROOT / f"strategy_metadata/{strategy_key}.json"
        with open(file_path, "r") as f:
            metadata = json.load(f)
            set_strategy_metadata(strategy_key, metadata)
        params = get_strategy_params(strategy_key)
        set_strategy_params(strategy_key, params)


if __name__ == "__main__":

    asyncio.run(main())
