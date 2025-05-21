from pydantic import BaseModel
from typing import Dict

NATIVE = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'


class TokenConfigInfo(BaseModel):
    chain: str
    address: str
    pair: str
    symbol: str
    quote: str


TokenConfig: Dict[str, TokenConfigInfo] = {
    "EQB": TokenConfigInfo(
        chain="arbitrum",
        address="0xBfbCFe8873fE28Dfa25f1099282b088D52bbAD9C",
        pair="0x69B545997BD6aBC81CaE39Fe9bdC94d2242a0f92",
        symbol="EQB",
        quote="WETH_ARB"
    ),
    "HOLD_SYNCSWAP": TokenConfigInfo(
        chain="zksync",
        address="0xed4040fD47629e7c8FBB7DA76bb50B3e7695F0f2",
        pair="0x9bec30fd825f5e8e9bc6a84914b8a3ab31742103",
        symbol="HOLD",
        quote=""
    ),
    "HOLD": TokenConfigInfo(
        chain="berachain",
        address="0xFF0a636Dfc44Bb0129b631cDd38D21B613290c98",
        pair="0xAD28e28d64Fb46c785246d0468dEc1c89C1774bA",
        symbol="HOLD",
        quote=""
    ),
    "HOLD_KODIAK": TokenConfigInfo(
        chain="berachain",
        address="0xFF0a636Dfc44Bb0129b631cDd38D21B613290c98",
        pair="0xdcA120bd3A13250B67f6FAA5c29c1F38eC6EBeCE",
        symbol="HOLD",
        quote=""
    ),
    "MEDAL": TokenConfigInfo(
        chain="ancient8",
        address="0x300a495ad18b33cb82f38add2519f3e3c5c147d3",
        pair="0x1888bbbb58e2b89e0be01fe50d9b4883ee419793",
        symbol="MEDAL",
        quote=""
    ),
    "A8": TokenConfigInfo(
        chain="ancient8",
        address="0xD812d616A7C54ee1C8e9c9CD20D72090bDf0d424",
        pair="0xd907efdb8d52edd6917263f24db230b525a3ef0b",
        symbol="A8",
        quote=""
    ),
    "PUMPE": TokenConfigInfo(
        chain="metis",
        address="0xCb36d532a9995F4471C99868F8DA775B7a23eBB8",
        pair="0x8d57Aa133B98cf9F13bF7CDaE269fC4d29ADcC55",
        symbol="PUMPE",
        quote=""
    ),
    "SUNANA": TokenConfigInfo(
        chain="tron",
        address="TXme8qsGdorboWFTX3E2XBWkmLNq4h7Kbx",
        pair="TJ9g2SzMSH7yV71AtpEjLa4HQyRkSGYHW4",
        symbol="SUNANA",
        quote=""
    ),
    "TORCH": TokenConfigInfo(
        chain="metis",
        address="0xbB1676046C36BCd2F6fD08d8f60672c7087d9aDF",
        pair="0x6eeAC91f1Bd77e1aD9a25C12c6A9577b4c185D94",
        symbol="TORCH",
        quote=""
    ),
    "WETH_ARB": TokenConfigInfo(
        chain="arbitrum",
        address="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        pair="0x389938CF14Be379217570D8e4619E51fBDafaa21",
        symbol="WETH",
        quote=""
    )
}
