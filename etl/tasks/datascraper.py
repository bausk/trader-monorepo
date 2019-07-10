from asyncio import sleep
from datetime import datetime
from google.cloud import bigquery

from tasks.collect import collect_data

bigquery_client = bigquery.Client()

async def scrape_data(app):
    counter = 0
    while True:

        await sleep(30)
        if app.active:
            dat = datetime.now()
            counter += 1

        #     query_job = bigquery_client.query("""
        # SELECT
        #   CONCAT(
        #     'https://stackoverflow.com/questions/',
        #     CAST(id as STRING)) as url,
        #   view_count
        # FROM `bigquery-public-data.stackoverflow.posts_questions`
        # WHERE tags like '%google-bigquery%'
        # ORDER BY view_count DESC
        # LIMIT 10""")

            # results = query_job.result()  # Waits for job to complete.
            app.last_scraped = dat.strftime("%d-%m-%Y %H:%M:%S")
            app.results = collect_data()
