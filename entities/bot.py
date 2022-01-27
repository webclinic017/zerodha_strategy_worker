from kiteconnect import KiteConnect
from entities.tick import LiveTicker
import redis
import os
import json


class TradeBot:
    def __init__(self):
        self.kite = KiteConnect(
            api_key=os.environ["API_KEY"], access_token=os.environ["ACCESS_TOKEN"]
        )

        self.r = redis.Redis(decode_responses=True)

    def live_data(self, token) -> LiveTicker:
        tick = self.r.get(token)

        if tick == None:
            tick = {}

        return LiveTicker(json.loads(tick))
