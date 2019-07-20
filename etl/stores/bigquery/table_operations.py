import asyncio
from time import sleep
from google.cloud import bigquery
from google.cloud import client
from google.api_core.exceptions import Conflict


async def create_table(client: bigquery.Client, table_name_tuple, schema):
    table = bigquery.Table('.'.join(table_name_tuple), schema=schema)
    result = None
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, client.create_dataset, table_name_tuple[1])
    except BaseException as e:
        if type(e) is not Conflict:
            raise
    try:
        result = await loop.run_in_executor(None, client.create_table, table)
        print(
            "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
        )
    except BaseException as e:
        if type(e) is not Conflict:
            raise
    return table


async def append_to_table(client: bigquery.Client, table, data):
    if not data:
        return
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, client.insert_rows, table, [data])


async def append_rows_to_table(client: bigquery.Client, table, data):
    if not data or len(data) == 0:
        return
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, client.insert_rows, table, data)
