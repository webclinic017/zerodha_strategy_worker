import redis
import json
from threading import Thread


class DB:
    def __init__(self, host="localhost"):
        self.redis = redis.StrictRedis(host=host)

    def write(self, key: str, data: dict, threaded=False):
        serialized_data = json.dumps(data, default=str)

        if threaded:
            Thread(target=self.redis.set, args=[serialized_data])
        else:
            self.redis.set(key, serialized_data)
