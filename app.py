import os
import time


from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB
from threading import Thread


API_KEY = os.environ["API_KEY"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]

db = DB()
ticker = KiteLiveDataServer(api_key=API_KEY, access_token=ACCESS_TOKEN, db=db)

ticker.start()


def entry_service():
    while True:
        print("This is entry service.....")
        time.sleep(3000)


entry_service()
