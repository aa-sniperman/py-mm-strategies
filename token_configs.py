from pydantic import BaseModel
from typing import Dict
from parameters.client import params_redis_client

NATIVE = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"


class TokenConfigInfo(BaseModel):
    chain: str
    address: str
    pair: str
    symbol: str
    quote: str
    protocol: str


def get_token_config(key: str):
    redis_key = f"token_config:{key}"
    raw_data = params_redis_client.hgetall(redis_key)

    return TokenConfigInfo(**raw_data)


def set_token_config(key: str, new_set: dict):
    redis_key = f"token_config:{key}"
    current_set = params_redis_client.hgetall(redis_key)

    updated_set = {**current_set, **new_set}

    updated_set = {k: str(v) for k, v in updated_set.items()}

    if updated_set:
        params_redis_client.hset(redis_key, mapping=updated_set)

    return updated_set


TokenConfig: Dict[str, TokenConfigInfo] = {
    "EQB": TokenConfigInfo(
        chain="arbitrum",
        address="0xBfbCFe8873fE28Dfa25f1099282b088D52bbAD9C",
        pair="0x69B545997BD6aBC81CaE39Fe9bdC94d2242a0f92",
        symbol="EQB",
        quote="WETH_ARB",
        protocol="camelot-v2",
    ),
    "HOLD_SYNCSWAP": TokenConfigInfo(
        chain="zksync",
        address="0xed4040fD47629e7c8FBB7DA76bb50B3e7695F0f2",
        pair="0x9bec30fd825f5e8e9bc6a84914b8a3ab31742103",
        symbol="HOLD",
        quote="",
        protocol="syncswap",
    ),
    "HOLD": TokenConfigInfo(
        chain="berachain",
        address="0xFF0a636Dfc44Bb0129b631cDd38D21B613290c98",
        pair="0xAD28e28d64Fb46c785246d0468dEc1c89C1774bA",
        symbol="HOLD",
        quote="",
        protocol="holdso",
    ),
    "HOLD_KODIAK": TokenConfigInfo(
        chain="berachain",
        address="0xFF0a636Dfc44Bb0129b631cDd38D21B613290c98",
        pair="0xdcA120bd3A13250B67f6FAA5c29c1F38eC6EBeCE",
        symbol="HOLD",
        quote="",
        protocol="kodiak-v2",
    ),
    "MEDAL": TokenConfigInfo(
        chain="ancient8",
        address="0x300a495ad18b33cb82f38add2519f3e3c5c147d3",
        pair="0x1888bbbb58e2b89e0be01fe50d9b4883ee419793",
        symbol="MEDAL",
        quote="",
        protocol="dojo-v2",
    ),
    "A8": TokenConfigInfo(
        chain="ancient8",
        address="0xD812d616A7C54ee1C8e9c9CD20D72090bDf0d424",
        pair="0xd907efdb8d52edd6917263f24db230b525a3ef0b",
        symbol="A8",
        quote="",
        protocol="dojo-v2",
    ),
    "PUMPE": TokenConfigInfo(
        chain="metis",
        address="0xCb36d532a9995F4471C99868F8DA775B7a23eBB8",
        pair="0x8d57Aa133B98cf9F13bF7CDaE269fC4d29ADcC55",
        symbol="PUMPE",
        quote="",
        protocol="hercules-v2",
    ),
    "SUNANA": TokenConfigInfo(
        chain="tron",
        address="TXme8qsGdorboWFTX3E2XBWkmLNq4h7Kbx",
        pair="TJ9g2SzMSH7yV71AtpEjLa4HQyRkSGYHW4",
        symbol="SUNANA",
        quote="TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR",
        protocol="sunswap-v2",
    ),
    "WTRX": TokenConfigInfo(
        chain="tron",
        address="TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR",
        pair="TFGDbUyP8xez44C76fin3bn3Ss6jugoUwJ",
        symbol="WTRX",
        quote="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        protocol="sunswap-v2",
    ),
    "TORCH": TokenConfigInfo(
        chain="metis",
        address="0xbB1676046C36BCd2F6fD08d8f60672c7087d9aDF",
        pair="0x6eeAC91f1Bd77e1aD9a25C12c6A9577b4c185D94",
        symbol="TORCH",
        quote="",
        protocol="hercules-v3",
    ),
    "WETH_ARB": TokenConfigInfo(
        chain="arbitrum",
        address="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        pair="0x389938CF14Be379217570D8e4619E51fBDafaa21",
        symbol="WETH",
        quote="",
        protocol="",
    ),
    "TXBT": TokenConfigInfo(
        chain="solana",
        address="9KweAdQhYk7HYz8VKDjX1VxofFjkkTPEfdvQz2N7s4G4",
        pair="967p57PHxv4xaPUFEhbu6aGaxVGEsXHJXNtYg96fbyT",
        symbol="TXBT",
        quote="F9NkJfxAqKBB6rqiRdXcTGyYVKgttSY8x3FsZtxadcVg",
        protocol="dex-labs",
    ),
    "BSOL": TokenConfigInfo(
        chain="solana",
        address="F9NkJfxAqKBB6rqiRdXcTGyYVKgttSY8x3FsZtxadcVg",
        pair="B34gLwtw1EpdaUvC8rE574zfvYXfYKb8Vw6DttS2hEfF",
        symbol="BSOL",
        quote="So11111111111111111111111111111111111111112",
        protocol="dex-labs",
    ),
    "WMETIS": TokenConfigInfo(
        chain="metis",
        address="0x75cb093E4D61d2A2e65D8e0BBb01DE8d89b53481",
        pair="0xA4E4949e0cccd8282f30e7E113D8A551A1eD1aeb",
        symbol="WMETIS",
        quote="0xEA32A96608495e54156Ae48931A7c20f0dcc1a21",
        protocol="hercules-v3",
    ),
    "WBERA": TokenConfigInfo(
        chain="berachain",
        address="0x6969696969696969696969696969696969696969",
        pair="0x2c4a603A2aA5596287A06886862dc29d56DbC354",
        symbol="WBERA",
        quote="0xFCBD14DC51f0A4d49d5E53C2E0950e0bC26d0Dce",
        protocol="kodiak-v2",
    ),
}
