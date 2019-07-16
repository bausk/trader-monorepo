import asyncio
from google.cloud import bigquery
from google.cloud import client


async def create_table(client, table_name, schema):
    if schema is None:
        schema = [
            bigquery.SchemaField("full_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("age", "INTEGER", mode="REQUIRED"),
        ]
    table = bigquery.Table(table_name, schema=schema)
    result = None
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, client.create_table, table)
    except BaseException as e:
        print("an exception occurred")
        print(e)
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )
    return result
