from kiteconnect import KiteTicker
from entities.redis_db import DB
from entities.tick import LiveTicker


class KiteLiveDataServer(KiteTicker):
    def __init__(
        self,
        api_key,
        access_token,
        db: DB,
        debug=False,
        root=None,
        reconnect=True,
    ):
        super().__init__(
            api_key,
            access_token,
            debug=debug,
            root=root,
            reconnect=reconnect,
        )

        self.db: DB = db

    def start(self):
        def on_connect(ws, response):
            print("[connecting to websocket]")

            self.subscribe([408065, 884737])
            self.set_mode(self.MODE_FULL, [408065, 884737])

        def on_error(ws, code, reason):
            print(f"[error :- {code} - {reason}]")

        def on_ticks(ws, ticks):
            for tick_ in ticks:
                tick = LiveTicker(tick_)
                print(tick)

        self.on_ticks = on_ticks
        self.on_connect = on_connect
        self.on_error = on_error

        self.connect()
