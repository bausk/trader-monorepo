from asyncio import sleep, gather
from datetime import datetime
from google.cloud import bigquery
from tasks.collect import collect_cryptowatch_trades, collect_kunaio_orderbook, collect_kunaio_trades
from stores.bigquery import BigQueryStore
from stores.bigquery.adapters import adapt_orderbook_to_bigquery, adapt_ticks_to_bigquery, adapt_trades_to_bigquery
from datatypes.cache import ForwardOnceCache
from stores.bigquery.schemas import KUNAIO_SNAPSHOT_SCHEMA, CRYPTOWATCH_SNAPSHOT_SCHEMA, KUNAIO_ORDERBOOK_SCHEMA, \
    CRYPTOWATCH_TICKS_SCHEMA, KUNAIO_TICKS_SCHEMA


cryptowatch_trades_store = BigQueryStore('kunaSnapshotsBTCUSD', CRYPTOWATCH_SNAPSHOT_SCHEMA, adapt_trades_to_bigquery)
cryptowatch_ticks_store = BigQueryStore('cryptowatchTicksBTCUSD', CRYPTOWATCH_TICKS_SCHEMA, adapt_ticks_to_bigquery)
cryptowatch_cache = ForwardOnceCache('timestamp')

kunaio_trades_store = BigQueryStore('cryptowatchSnapshotsBTCUAH', KUNAIO_SNAPSHOT_SCHEMA, adapt_trades_to_bigquery)
kunaio_orderbook_store = BigQueryStore('kunaOrderbooksBTCUAH', KUNAIO_ORDERBOOK_SCHEMA, adapt_orderbook_to_bigquery)
kunaio_ticks_store = BigQueryStore('kunaTicksBTCUAH', KUNAIO_TICKS_SCHEMA, adapt_ticks_to_bigquery)
kunaio_cache = ForwardOnceCache('timestamp')


async def scrape_data(app):
    dat = datetime.now()
    app.last_scraped = dat.strftime("%d-%m-%Y %H:%M:%S")

    cryptowatch_trades = collect_cryptowatch_trades()
    cryptowatch_ticks = cryptowatch_cache.put(cryptowatch_trades)
    kunaio_trades = collect_kunaio_trades()
    kunaio_ticks = kunaio_cache.put(kunaio_trades)
    kunaio_orderbook = collect_kunaio_orderbook()
    print(cryptowatch_ticks)
    # await gather([
    #     cryptowatch_trades_store.write(cryptowatch_trades),
    #     cryptowatch_ticks_store.write(cryptowatch_ticks),
    #     kunaio_trades_store.write(kunaio_trades),
    #     kunaio_ticks_store.write(kunaio_ticks),
    #     kunaio_orderbook_store.write(kunaio_orderbook)
    # ])


async def scrape_data_process(app):
    counter = 0
    while True:
        await sleep(13)
        if app.active:
            counter += 1
            await scrape_data(app)
