from datetime import datetime, timedelta
from utils.schemas.dataflow_schemas import TickSchema
from .abstract_source import AbstractSource


class LiveKunaSource(AbstractSource):
    latest_endpoint = "https://kuna.io/api/v2/trades?market={currency}"
    label = "btcuah"
    config = dict(currency="btcuah")

    def format_endpoint(self):
        return self.latest_endpoint.format(**self.config)

    def to_trades(self, in_data):
        trades = []
        for result in in_data:
            trade = TickSchema(
                price=result["price"],
                volume=result["volume"],
                funds=result["funds"],
                timestamp=result["created_at"],
            )
            trades.append(trade)
        return self.deduplicate(trades)

    async def get_latest(self, current_datetime):
        async with self.session.get(self.format_endpoint()) as resp:
            return self.to_trades(await resp.json())


class LiveCryptowatchSource(AbstractSource):
    latest_endpoint = "https://api.cryptowat.ch/markets/gdax/{currency}/trades?limit={limit}&since={after}"
    label = "btcusd"
    config = dict(currency="btcusd", limit=100, after=timedelta(minutes=2))

    def format_endpoint(self):
        after = int((datetime.utcnow() - self.config["after"]).timestamp())
        return self.latest_endpoint.format(**{**self.config, "after": after})

    def to_trades(self, in_data):
        trades = []
        data = in_data["result"]
        for result in data:
            trade = TickSchema(
                price=result[2],
                volume=result[3],
                funds=result[2] * result[3],
                timestamp=result[1],
            )
            trades.append(trade)
        return self.deduplicate(trades)

    async def get_latest(self, current_datetime):
        async with self.session.get(self.format_endpoint()) as resp:
            return self.to_trades(await resp.json())


class LiveCoinbaseSource(AbstractSource):
    latest_endpoint = "https://api.pro.coinbase.com/products/{currency}/trades"
    label = "btcusd"
    config = dict(
        currency="BTC-USD",
    )

    def format_endpoint(self):
        return self.latest_endpoint.format(**self.config)

    def to_trades(self, in_data):
        trades = []
        for result in in_data:
            trade = TickSchema(
                price=result["price"],
                volume=result["size"],
                funds=float(result["price"]) * float(result["size"]),
                timestamp=result["time"],
            )
            trades.append(trade)
        return self.deduplicate(trades)

    async def get_latest(self, current_datetime):
        async with self.session.get(self.format_endpoint()) as resp:
            return self.to_trades(await resp.json())
