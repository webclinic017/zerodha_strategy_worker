import os
import time
import requests
import json
import time
import datetime
from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB
from entities.bot import TradeBot
from threading import Thread
from kiteconnect import KiteConnect
from talib import abstract
import pandas as pd

API_KEY = os.environ["API_KEY"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
BITTRADE_HOST = os.environ["BITTRADE_HOST"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]

db = DB()
ticker = KiteLiveDataServer(api_key=API_KEY, access_token=ACCESS_TOKEN, db=db)

kite = KiteConnect(api_key=API_KEY, access_token=ACCESS_TOKEN)

ticker.start()
time.sleep(5)

strategies = requests.get(
    BITTRADE_HOST + "/strategy_builder/get_strategies",
    headers={"Authorization": f"Token {AUTH_TOKEN}"},
).json()

token_set = set()
tickers = {}

for strategy in strategies:
    for _ticker in strategy["strategy_tickers"]:
        token_set.add(_ticker["instrument_token"])

        tickers[_ticker["ticker"]] = _ticker

if len(token_set) > 0:
    ticker.subscribe(list(token_set))
    ticker.set_mode(ticker.MODE_FULL, list(token_set))


print(json.dumps(strategies, indent=2))

bot = TradeBot()


def entry_service():
    print("[*] starting the entry service [*]")
    while True:
        for strategy in strategies:
            print(f'[*] running strategy {strategy["name"]} [*]')

            for ticker in strategy["strategy_tickers"]:
                historical_data = pd.DataFrame(
                    kite.historical_data(
                        instrument_token=ticker["instrument_token"],
                        from_date=datetime.date.today(),
                        to_date=datetime.date.today(),
                        interval="5minute",
                    )
                )

                if len(historical_data) == 0:
                    continue

                print(historical_data.head())

                entry_indicator = abstract.Function(strategy["entry_node"]["value"])
                exit_indicator = abstract.Function(strategy["exit_node"]["value"])

                print(
                    entry_indicator(
                        historical_data,
                        **strategy["entry_node"]["kwargs"].get("inputs", {}),
                        **strategy["entry_node"]["kwargs"].get("parameters", {}),
                    )
                )

        time.sleep(300)


entry_service()
