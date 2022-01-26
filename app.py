import os
import time
import requests
import json
import time
import datetime

from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB
from threading import Thread

import talib as ta
import pandas as pd

from kiteconnect import KiteConnect


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


def entry_service():
    print("[*] starting the entry service [*]")
    while True:
        for ticker in tickers:
            print(f"[*] running strategy for {ticker} [*]")

            print(f"[*] fetching the historical data of {ticker} [*]")
            historical_df = pd.DataFrame(
                kite.historical_data(
                    instrument_token=tickers[ticker]["instrument_token"],
                    from_date=(datetime.date.today() - datetime.timedelta(days=1)),
                    to_date=(datetime.date.today() - datetime.timedelta(days=1)),
                    interval="5minute",
                )
            )

            print(f"[*] historical data of {ticker} [*]")
            print(historical_df.tail())

            print(f"[*] fetching the indicators [*]")

            indicators = ta.get_functions()

            for indicator in indicators:
                print(f"[*] fetching {indicator} for {ticker} [*]")

                try:
                    print(getattr(ta, indicator)(historical_df.close))
                except Exception as e:
                    print(f"[*] Exception {e} [*]")

        time.sleep(300)


entry_service()
