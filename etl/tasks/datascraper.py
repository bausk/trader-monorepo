from asyncio import sleep
from datetime import datetime
from google.cloud import bigquery


bigquery_client = bigquery.Client()

async def scrape_data(app):
    counter = 0

    while True:
        await sleep(5)
        dat = datetime.now()
        counter += 1
        app.some_state[counter] = dat

        query_job = bigquery_client.query("""
    SELECT
      CONCAT(
        'https://stackoverflow.com/questions/',
        CAST(id as STRING)) as url,
      view_count
    FROM `bigquery-public-data.stackoverflow.posts_questions`
    WHERE tags like '%google-bigquery%'
    ORDER BY view_count DESC
    LIMIT 10""")

        results = query_job.result()  # Waits for job to complete.
        app.results = ""
        for row in results:
            app.results += "\nTake {}: {} : {} views".format(counter, row.url, row.view_count)
