from types import SimpleNamespace
from string import Template
from datetime import timedelta, datetime
from dateutil import parser
import requests

from constants import currencies, periods, remote


class CurrencySource(SimpleNamespace):
    source = Template("")
    source_trades = Template("")
    name = ""
    period = ""
    currencies = {}
    periods = {}

    def _get_after_time(self, aftertime):
        return int(parser.parse(aftertime, ignoretz=True).timestamp())

    def _get_before_time(self, beforetime):
        return int((parser.parse(beforetime, ignoretz=True) + timedelta(days=1)).timestamp())

    def fetch_historical(self, after="2000-01-01", before="2001-01-01", **kwargs):
        after = self._get_after_time(after)
        before = self._get_before_time(before)
        endpoint = self.source.substitute(
            currency=self.currencies[self.currency],
            period=self.periods[self.period],
            after=after,
            before=before,
            **kwargs)
        result = requests.get(endpoint)
        return result.json()

    def fetch_latest_trades(self, minutes=2, limit=50, raise_error=True, **kwargs):
        after = int((datetime.utcnow() - timedelta(minutes=minutes)).timestamp())
        endpoint = self.source_trades.substitute(
            currency=self.currencies[self.currency].get('trade', None),
            after=after,
            limit=limit,
            **kwargs)
        try:
            result = requests.get(endpoint).json()
        except BaseException as e:
            print(e)
            result = []

        return self._postprocess(result, **kwargs)

    def _postprocess(self, response, **kwargs):
        return response


class CryptowatchSource(CurrencySource):
    source = Template(
        'https://api.cryptowat.ch/markets/gdax/$currency/ohlc?periods=$period&before=$before&after=$after'
    )
    source_trades = Template(
        'https://api.cryptowat.ch/markets/gdax/$currency/trades?limit=$limit&since=$after'
    )

    currencies = {
        currencies.BTC: dict(historical="btc", trade="btcusd"),
        currencies.ETH: "eth"
    }

    periods = {
        periods.P5M: 5 * 60,
        periods.P15M: 15 * 60,
        periods.P30M: 30 * 60
    }

    def _postprocess(self, response, **kwargs):
        try:
            res = response.get('result', [])
            print(int(response.get('allowance', dict(remaining=0))['remaining']/1000))
            res = [dict(timestamp=x[1], price=x[2], volume=x[3]) for x in res]
        except BaseException as e:
            res = []
        return res


class KunaIoSource(CurrencySource):
    source_trades = Template(
        'https://kuna.io/api/v2/trades?market=$currency'
    )

    currencies = {
        currencies.BTC: dict(historical="", trade="btcuah")
    }

    def fetch_historical(self, **kwargs):
        raise NotImplementedError('No historical data for kuna.io!')

    def fetch_order_book(self, **kwargs):
        endpoint = "https://kuna.io/api/v2/order_book?market=btcuah"
        try:
            result = requests.get(endpoint).json()
        except BaseException as e:
            print(e)
            result = {"asks": [], "bids": []}
        return result

    def _postprocess(self, response, convert_to=None):
        if convert_to is not None:
            conversion_rate = float(remote.get_UAH_rate(convert_to))
        else:
            conversion_rate = 1

        return [dict(
            timestamp=int(parser.parse(x['created_at']).timestamp()),
            created_at=x['created_at'],
            price=float(x['price']) / conversion_rate,
            volume=float(x['volume']),
            id=int(x['id'])
        ) for x in response]


class BitfinexSource(CurrencySource):
    source = Template(
        'https://api.bitfinex.com/v2/candles/trade:$period:t$currency/hist?start=$after&end=$before'
    )

    currencies = {
        currencies.BTC: "BTCUSD",
        currencies.ETH: "ETHUSD"
    }

    periods = {
        periods.P5M: "5m",
        periods.P15M: "15m",
        periods.P30M: "30m"
    }

    def _get_after_time(self, aftertime):
        return int(parser.parse(aftertime, ignoretz=True).timestamp()) * 1000

    def _get_before_time(self, beforetime):
        return int((parser.parse(beforetime, ignoretz=True) + timedelta(days=1)).timestamp()) * 1000

