from timeit import default_timer as timer
from time import sleep
import os
import threading
import asyncio
import concurrent.futures
import functools
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import click
import datetime
import pytz
from janus import Queue
import influxdb_client
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
from secrets_management.manage import encrypt_credentials, decrypt_credentials, load_credentials
from utils.test_utils import generate_data, format_int


print('Loading development env...')
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


async def test_influxdb():
    url = "http://influxdb:9999"
    bucket = "ticks"
    org = "livewater"
    token = "token"
    async with aiohttp.ClientSession() as session:
        payload = {
            "bucket": bucket,
            "org": org,
            "username": "influx",
            "password": "influxdb",
            "token": token,
        }
        async with session.post(f"{url}/api/v2/setup", json=payload) as resp:
            result = await resp.json()
    auth = result.get("auth")
    token = auth["token"] if auth else token

    iterations = 1000

    async def feed_data(q):
        data_source = generate_data(datetime.datetime(2020, 1, 1))
        nonlocal iterations
        counter = iterations
        print('starting feeding data')
        for raw_data in data_source:
            counter -= 1
            if counter < 0:
                print('finishing feeding data')
                break
            await q.put(raw_data)
        return None

    def write_data(q, i):
        nonlocal token
        client = InfluxDBClient(url="http://influxdb:9999", token=token)
        write_api = client.write_api(write_options=ASYNCHRONOUS)
        for datapoint in iter(q.get, None):
            datapoint['timestamp'] = datetime.datetime.fromtimestamp(datapoint['timestamp']).replace(tzinfo=pytz.UTC)
            p = influxdb_client.Point("tick") \
                .time(datapoint['timestamp']) \
                .tag("session_id", datapoint['timestamp']) \
                .tag("label", datapoint['label']) \
                .tag("data_type", datapoint['data_type']) \
                .tag("funds", datapoint['funds']) \
                .field("price", datapoint['funds']) \
                .field("volume", datapoint['volume'])
            write_api.write(bucket=bucket, org=org, record=p)
            q.task_done()
        write_api.__del__()

    TCOUNT = 30
    loop = asyncio.get_running_loop()
    start = timer()
    ticks_q = Queue(50000)
    producer = asyncio.create_task(feed_data(ticks_q.async_q))
    executor = concurrent.futures.ThreadPoolExecutor(TCOUNT)
    consumers = [loop.run_in_executor(executor, write_data, ticks_q.sync_q, x) for x in range(TCOUNT)]

    await producer
    print('---- done producing')
    for _ in consumers:
        await ticks_q.async_q.put(None)
    await asyncio.wait({*consumers})

    print('---- done consuming')
    end1 = timer()
    elapsed_clean = round(end1 - start, 4)

    ticks_q = Queue(50000)
    producer = asyncio.create_task(feed_data(ticks_q.async_q))
    # executor = concurrent.futures.ThreadPoolExecutor(90)
    consumers = [loop.run_in_executor(executor, write_data, ticks_q.sync_q, x) for x in range(TCOUNT)]

    await producer
    print('---- done producing')
    for _ in consumers:
        await ticks_q.async_q.put(None)
    await asyncio.wait({*consumers})

    print('---- done consuming')
    end2 = timer()
    elapsed_upsert = round(end2 - end1, 4)

    client = InfluxDBClient(url="http://influxdb:9999", token=token)

    query = f"""
        open = from(bucket:"{bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) =>
            r._measurement == "tick" and
            r._field == "price"
        )
        |> aggregateWindow(
            every: 30m, fn: first
        )
        |> map(fn: (r) =>
            ({{r with _field: "open"}})
        )
        |> yield(name: "first")
        volume = from(bucket: "{bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) =>
            r._measurement == "tick" and
            r._field == "volume"
        )
        |> aggregateWindow(
            every: 30m, fn: sum
        )
        |> map(fn: (r) =>
            ({{r with _field: "volume"}})
        )
        |> yield(name: "volume")
        union(tables: [open, volume])
        |> yield()
    """
    query = f"""
        open = from(bucket:"{bucket}")
        |> range(start: -100d, stop: now())
        |> filter(fn: (r) =>
            r._measurement == "tick" and
            r._field == "price"
        )
        |> aggregateWindow(
            every: 30m, fn: first
        )
        |> map(fn: (r) =>
            ({{r with _field: "open"}})
        )
        |> yield(name: "first")
        volume = from(bucket: "{bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) =>
            r._measurement == "tick" and
            r._field == "volume"
        )
        |> aggregateWindow(
            every: 30m, fn: sum
        )
        |> map(fn: (r) =>
            ({{r with _field: "volume"}})
        )
        |> yield(name: "volume")
        union(tables: [open, volume])
        |> yield()
    """
    rows1 = None

    def read_query(client, query, org):
        print("one man enters")
        return client.query_api().query(query=query, org=org)

    # result = await loop.run_in_executor(executor, read_query, client, query, org)
    # print(result)
    # for table in result:
    #     rows1 = len(table.records)
    end3 = timer()
    elapsed_1min = round(end3 - end2, 4)
    rows5 = []
    end4 = timer()
    elapsed_5min = round(end4 - end3, 4)
    rows30 = []
    end5 = timer()
    elapsed_30min = round(end5 - end4, 4)

    print(f"{format_int(iterations)} datapoints write from scratch: {elapsed_clean}(s) elapsed.")
    print(f"{format_int(iterations)} datapoints on-conflict upsert: {elapsed_upsert}(s) elapsed.")
    print(f"1min OHLCV aggregation: {rows1} rows {elapsed_1min}(s) elapsed.")
    print(f"5min OHLCV aggregation: {elapsed_5min}(s) elapsed.")
    print(f"30min OHLCV aggregation: {elapsed_30min}(s) elapsed.")
    # sleep(5)


def main():
    load_credentials(decrypt_credentials(which=['*.env']))
    asyncio.get_event_loop().run_until_complete(test_influxdb())


if __name__ == '__main__':
    start = timer()
    print("InfluxDB test start")
    main()
    end = timer()
    elapsed = end - start
    print(f"Total: {elapsed}s elapsed.")
