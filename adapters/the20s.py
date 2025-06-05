import time
import hashlib
import json
from typing import Dict, Any
import requests
import urllib3
from settings import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def hash_with_sha256(input_string: str) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode("utf-8"))
    return sha256_hash.hexdigest()


def create_sign_mess(mess_json: Dict[str, Any], key: str, loop: int = 1) -> str:
    job_sign = key
    mess_json_copy = dict(mess_json)

    for _ in range(loop):
        mess_json_copy["key_private"] = job_sign
        input_string = json.dumps(mess_json_copy, sort_keys=True, separators=(",", ":"))
        print("Input string for signing:", input_string)
        job_sign = hash_with_sha256(input_string)

    return job_sign


class The20sAdapter:
    @staticmethod
    def get_order_details(order_id: str, exchange_name: str, base_symbol: str) -> Any:
        ts = str(int(time.time()))
        order_data = {
            "ts": ts,
            "exchange_name": exchange_name,
            "base_symbol": base_symbol,
            "orderID": order_id,
        }

        sign = create_sign_mess(order_data, settings.the20s.key)
        request_payload = {**order_data, "sign": sign}

        response = requests.get(
            f'{settings.the20s.endpoint}/api/get_order_details',
            params=request_payload,
            verify=False,
        )
        return response.json()

    @staticmethod
    def get_current_price(base_symbol: str, exchange_name: str) -> Any:
        ts = str(int(time.time()))
        ticker_data = {
            "ts": ts,
            "exchange_name": exchange_name,
            "base_symbol": base_symbol,
        }

        sign = create_sign_mess(ticker_data, settings.the20s.key)
        request_payload = {**ticker_data, "sign": sign}

        response = requests.get(
            f'{settings.the20s.endpoint}/api/ticker',
            params=request_payload,
            verify=False,
        )
        return response.json()

    @staticmethod
    def make_order(
        base_symbol: str,
        side: str,
        size: str,
        price: float,
        filled_price: float,
        exchange_name: str,
    ) -> Any:
        ts = str(int(time.time()))
        order_params = {
            "base_symbol": base_symbol,
            "exchange_name": exchange_name,
            "order_side": side,
            "quantity": size,
            "order_type": "limit",
            "price": price,
            "filled_price": filled_price,
            "force": "ioc",
        }

        sign = create_sign_mess({**order_params, "ts": ts}, settings.the20s.key)
        request_payload = {"ts": ts, **order_params, "sign": sign}

        response = requests.post(
            f'{settings.the20s.endpoint}/api/send_order',
            json=request_payload,
            verify=False,
        )
        return response.json()

    @staticmethod
    def get_order_books(base_symbol: str, exchange_name: str) -> Any:
        ts = str(int(time.time()))
        ticker_data = {
            "ts": ts,
            "exchange_name": exchange_name,
            "base_symbol": base_symbol,
        }

        sign = create_sign_mess(ticker_data, settings.the20s.key)
        request_payload = {**ticker_data, "sign": sign}

        response = requests.get(
            f'{settings.the20s.endpoint}/api/order_book',
            params=request_payload,
            verify=False,
        )
        return response.json().get("data")
