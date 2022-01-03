import os
import json
from entities.kite_ticker import KiteLiveDataServer
from entities.redis_db import DB

secrets = json.loads(open("secrets.env.json", "r").read())

API_KEY = secrets["api_key"]
ACCESS_TOKEN = secrets["access_token"]

db = DB()

ticker = KiteLiveDataServer(api_key=API_KEY, access_token=ACCESS_TOKEN, db=db)

ticker.start()
