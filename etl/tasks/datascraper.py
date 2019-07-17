from asyncio import sleep
from datetime import datetime
from google.cloud import bigquery
from tasks.collect import collect_data
from stores.bigquery import BigQueryStore
from stores.bigquery.schemas import KUNAIO_SNAPSHOT_SCHEMA


store = BigQueryStore('kunaBTCUAH', KUNAIO_SNAPSHOT_SCHEMA)

async def scrape_data(app):
    dat = datetime.now()
    app.last_scraped = dat.strftime("%d-%m-%Y %H:%M:%S")
    app.results = collect_data()
    await store.write(app.results)

async def scrape_data_process(app):
    counter = 0
    while True:
        await sleep(13)
        if app.active:
            counter += 1
            await scrape_data(app)
