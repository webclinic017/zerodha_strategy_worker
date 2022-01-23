import os
import time
import requests
import json
import time

from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB
from threading import Thread


API_KEY = os.environ["API_KEY"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
BITTRADE_HOST = os.environ["BITTRADE_HOST"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]

db = DB()
ticker = KiteLiveDataServer(api_key=API_KEY, access_token=ACCESS_TOKEN, db=db)

ticker.start()
time.sleep(5)

strategies = requests.get(
    BITTRADE_HOST + "/strategy_builder/get_strategies",
    headers={"Authorization": f"Token {AUTH_TOKEN}"},
).json()

token_set = set()

for strategy in strategies:
    for _ticker in strategy["strategy_tickers"]:
        token_set.add(_ticker["instrument_token"])

if len(token_set) > 0: 
    ticker.subscribe(list(token_set))
    ticker.set_mode(ticker.MODE_FULL, list(token_set))


def entry_service():
    while True:
        print("This is entry service.....")
        time.sleep(3000)


entry_service()
