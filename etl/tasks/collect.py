from constants import currencies
from sources.historical import CryptowatchSource, KunaIoSource
from constants import formats
from datetime import timedelta

# 1. Pick up where we left off, if any
# source_store = TimeSeriesStore(name="bitfinex_btcusd", columns=formats.history_format, time_unit="s", time_field="timestamp", update_period=timedelta(seconds=30))
# target_store = TimeSeriesStore(name="kuna_btcuah", columns=formats.history_format, time_unit="s", update_period=timedelta(seconds=30))
# orderbook_store = TimeSeriesStore(name="kuna_orderbook", columns=formats.orderbook_format, time_unit="s", update_period=timedelta(seconds=30))
cryptowatch_rates = CryptowatchSource(currency=currencies.BTC)
kuna_rates = KunaIoSource(currency=currencies.BTC)


def collect_data():
    rates1 = cryptowatch_rates.fetch_latest_trades(limit=100)
    rates2 = kuna_rates.fetch_latest_trades()
    order_book = kuna_rates.fetch_order_book()
    return [rates1, rates2, order_book]