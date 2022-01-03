import redis
import json


class DB:
    def __init__(self, host="localhost"):
        self.redis = redis.StrictRedis(host=host)

    def write(self, key: str, data: dict):
        self.redis.set(key, json.dumps(data, default=str))
