class LiveTicker:
    def __init__(self, live_ticker: dict):
        self.json = live_ticker
        self.instrument_token: int = live_ticker.get("instrument_token")
