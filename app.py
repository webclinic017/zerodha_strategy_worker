import os
import time
import requests
import json
import time
import datetime
from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB
from entities.bot import TradeBot
from entities.node import ConditionNode
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


bot = TradeBot()
pubsub = bot.r.pubsub()

pubsub.subscribe("live:data")


def entry_service():
    print("[*] starting the entry service [*]")

    entry_nodes = dict()
    exit_nodes = dict()

    for message in pubsub.listen():
        if message["type"] == "subscribe":
            continue

        live_data = dict(
            map(lambda x: (x["instrument_token"], x), json.loads(message["data"]))
        )

        # print(live_data)

        # loop over all tickers
        for strategy in strategies:
            if strategy["id"] not in entry_nodes:
                entry_nodes[strategy["id"]] = ConditionNode.from_dict(
                    strategy["entry_node"]
                )

                exit_nodes[strategy["id"]] = ConditionNode.from_dict(
                    strategy["exit_node"]
                )

            for ticker in strategy["strategy_tickers"]:
                if ticker["instrument_token"] not in live_data:
                    continue

                # if the ticker is already entered then dont enter it for next 5 minute
                if bot.r.get(f"ENTERED:{ticker['instrument_token']}"):
                    continue

                try:
                    if bot.r.get(f"HISTORICAL:{ticker['instrument_token']}"):
                        historical_data = pd.DataFrame(
                            json.loads(
                                bot.r.get(f"HISTORICAL:{ticker['instrument_token']}")
                            )
                        )
                    else:
                        data = kite.historical_data(
                            instrument_token=ticker["instrument_token"],
                            from_date=datetime.date.today(),
                            to_date=datetime.date.today(),
                            interval="5minute",
                        )
                        bot.r.set(
                            f"HISTORICAL:{ticker['instrument_token']}",
                            json.dumps(data, default=str),
                            datetime.timedelta(minutes=5),
                        )
                        historical_data = pd.DataFrame(data)

                except Exception:
                    # if fetching of historical data is unsuccessful due to network error
                    # then continue with next ticker
                    continue

                if len(historical_data) == 0:
                    continue

                live_ticker = live_data[ticker["instrument_token"]]

                if entry_nodes[strategy["id"]].evaluate(historical_data, live_ticker):
                    print(f"[*] BUY THE TICKER: {ticker['ticker']} {strategy['id']}")

                    # add the ticker to entered tickers and set its expiry to 5 minute
                    # so that until next 5 minute the ticker is not entered
                    bot.r.set(
                        f"ENTERED:{ticker['instrument_token']}",
                        1,
                        datetime.timedelta(minutes=5),
                    )

                if bot.r.get(f"ENTERED:{ticker['instrument_token']}") and exit_nodes[
                    strategy["id"]
                ].evaluate(historical_data, live_ticker):

                    print(f"[*] EXIT THE TICKER: {ticker['ticker']}")


entry_service()
