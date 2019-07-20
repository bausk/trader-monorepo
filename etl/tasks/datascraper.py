from asyncio import sleep
from datetime import datetime
from google.cloud import bigquery
from tasks.collect import collect_cryptowatch_trades, collect_kunaio_orderbook, collect_kunaio_trades
from stores.bigquery import BigQueryStore
from datatypes.cache import ForwardOnceCache
from stores.bigquery.schemas import KUNAIO_SNAPSHOT_SCHEMA, CRYPTOWATCH_SNAPSHOT_SCHEMA, KUNAIO_ORDERBOOK_SCHEMA


cryptowatch_trades_store = BigQueryStore('kunaSnapshotsBTCUAH', KUNAIO_SNAPSHOT_SCHEMA)
kunaio_trades_store = BigQueryStore('cryptowatchSnapshotsBTCUSD', KUNAIO_SNAPSHOT_SCHEMA)
kunaio_orderbook_store = BigQueryStore('kunaOrderbooksBTCUAH', KUNAIO_SNAPSHOT_SCHEMA)
kunaio_trades_store = BigQueryStore('cryptowatchTradesBTCUSD', KUNAIO_SNAPSHOT_SCHEMA)
kunaio_trades_store = BigQueryStore('kunaTradesBTCUAH', KUNAIO_SNAPSHOT_SCHEMA)

async def scrape_data(app):
    dat = datetime.now()
    app.last_scraped = dat.strftime("%d-%m-%Y %H:%M:%S")

    cryptowatch_trades = collect_cryptowatch_trades()
    kunaio_trades = collect_kunaio_trades()
    kunaio_orderbook = collect_kunaio_orderbook()
    return True
    # await store.write(cryptowatch_trades)


async def scrape_data_process(app):
    counter = 0
    while True:
        await sleep(13)
        if app.active:
            counter += 1
            await scrape_data(app)
