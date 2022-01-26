class OHLC:
    def __init__(self, ohlc: dict):
        self.open = ohlc.get("open")
        self.high = ohlc.get("high")
        self.low = ohlc.get("low")
        self.close = ohlc.get("close")


class Depth:
    class DepthInfo:
        def __init__(self, depth: dict):
            self.price = depth["price"]
            self.orders = depth["orders"]
            self.quantity = depth["quantity"]

    def __init__(self, depth: dict):
        self.buy: List[Depth.DepthInfo] = []
        self.sell: List[Depth.DepthInfo] = []

        for depth_info in depth.get("buy", []):
            self.buy.append(Depth.DepthInfo(depth_info))

        for depth_info in depth.get("sell", []):
            self.sell.append(Depth.DepthInfo(depth_info))


class LiveTicker:
    def __init__(self, live_ticker: dict):
        self.json = live_ticker

        self.instrument_token: int = live_ticker.get("instrument_token")
        self.mode: str = live_ticker.get("mode")
        self.volume: int = live_ticker.get("volume")
        self.last_price: float = live_ticker.get("last_price")
        self.average_price: float = live_ticker.get("average_price")
        self.last_quantity: int = live_ticker.get("last_quantity")
        self.total_buy_quantity: int = live_ticker.get("total_buy_quantity")
        self.total_sell_quantity: int = live_ticker.get("total_sell_quantity")
        self.change: float = live_ticker.get("change")
        self.last_trade_time: datetime.datetime = live_ticker.get("last_trade_time")
        self.timestamp: datetime.datetime = live_ticker.get("timestamp")
        self.oi: int = live_ticker.get("oi")
        self.oi_day_low: int = live_ticker.get("oi_day_low")
        self.ohlc = OHLC(live_ticker.get("ohlc", {}))
        self.tradable: bool = live_ticker.get("tradable", False)
        self.depth: Depth = Depth(live_ticker.get("depth", {}))
