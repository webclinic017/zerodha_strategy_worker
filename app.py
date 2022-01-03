import os
import json
from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB
from flask import Flask
from threading import Thread

secrets = json.loads(open("secrets.env.json", "r").read())

API_KEY = secrets["api_key"]
ACCESS_TOKEN = secrets["access_token"]

db = DB()
app = Flask(__name__)
ticker = KiteLiveDataServer(api_key=API_KEY, access_token=ACCESS_TOKEN, db=db)


@app.route("/subscribe/<int:instrument_token>")
def subscribe_tick(instrument_token):
    ticker.subscribe([instrument_token])
    ticker.set_mode(ticker.MODE_FULL, [instrument_token])

    return ""


Thread(target=app.run).start()
Thread(target=ticker.start).start()
