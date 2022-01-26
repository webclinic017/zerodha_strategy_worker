import redis
import json
from threading import Thread


class DB:
    def __init__(self, host="localhost"):
        self.redis = redis.StrictRedis(host=host)

    def __write(self, key, data):
        self.redis.set(key, json.dumps(data))

    def write(self, key, data: dict):
        Thread(target=self.__write, args=[key, data]).start()
