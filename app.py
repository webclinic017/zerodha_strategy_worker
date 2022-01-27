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
pubsub = bot.r.pubsub()

pubsub.subscribe("live:data")


def entry_service():
    print("[*] starting the entry service [*]")

    for message in pubsub.listen():
        if message["type"] == "subscribe":
            continue

        live_data = dict(
            map(lambda x: (x["instrument_token"], x), json.loads(message["data"]))
        )

        print(live_data)

        # loop over all tickers
        for strategy in strategies:
            for ticker in strategy["strategy_tickers"]:
                if ticker["instrument_token"] not in live_data:
                    continue

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

                live_ticker = live_data[ticker["instrument_token"]]

                print(live_ticker)
                print(historical_data.head())


entry_service()
