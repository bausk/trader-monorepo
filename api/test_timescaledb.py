import asyncio
import asyncpg
import datetime
from dotenv import load_dotenv
from janus import Queue
from pathlib import Path
import pytz
from timeit import default_timer as timer
from secrets_management.manage import decrypt_credentials, load_credentials
from utils.formatting import format_int
from utils.mocks.ticks import generate_data
from utils.timescaledb.tsdb_manage import init_db, init_connection


print("Loading development env...")
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


async def test_asyncpg():
    await init_db("test")

    iterations = 1000

    async def feed_data(q):
        data_source = generate_data(datetime.datetime(2020, 1, 1))
        nonlocal iterations
        counter = iterations
        print("starting feeding data")
        for raw_data in data_source:
            counter -= 1
            if counter < 0:
                print("finishing feeding data")
                break
            await q.put(raw_data)

    async def write_data(q):
        conn = await init_connection("test")
        try:
            while True:
                datapoint = await q.get()
                datapoint["timestamp"] = datetime.datetime.fromtimestamp(
                    datapoint["timestamp"]
                ).replace(tzinfo=pytz.UTC)
                vals = [
                    (key, f"${i + 1}", value)
                    for i, (key, value) in enumerate(datapoint.items())
                ]
                keys, formats, values = zip(*vals)
                keys = ", ".join(keys)
                formats = ", ".join(formats)
                try:
                    await conn.execute(
                        f"""
                        INSERT INTO ticks({keys}) VALUES({formats})
                        ON CONFLICT (timestamp, session_id, data_type, label, funds) DO UPDATE
                        SET price=EXCLUDED.price,
                            volume=EXCLUDED.volume;
                    """,
                        *values,
                    )
                except asyncpg.exceptions.UniqueViolationError:
                    pass
                q.task_done()
        except asyncio.CancelledError:
            await conn.close()
            raise

    start = timer()
    ticks_q = Queue(50000)
    producer = asyncio.create_task(feed_data(ticks_q.async_q))
    consumers = [asyncio.create_task(write_data(ticks_q.async_q)) for _ in range(90)]

    await producer
    print("---- done producing")

    await ticks_q.async_q.join()
    for c in consumers:
        c.cancel()

    print("---- done consuming")
    end1 = timer()
    elapsed_clean = round(end1 - start, 4)

    ticks_q = Queue(50000)
    producer = asyncio.create_task(feed_data(ticks_q.async_q))
    consumers = [asyncio.create_task(write_data(ticks_q.async_q)) for _ in range(90)]
    await producer
    print("---- done producing")

    await ticks_q.async_q.join()
    for c in consumers:
        c.cancel()

    end2 = timer()
    elapsed_upsert = round(end2 - end1, 4)

    query = """
        SELECT
            time_bucket('{minutes} minutes', timestamp) AS time,
            first(price, timestamp) as open,
            max(price) as high,
            min(price) as low,
            last(price, timestamp) as close,
            sum(volume) as volume
        FROM ticks
        WHERE session_id = 123
        GROUP BY time
        ORDER BY time ASC;
    """

    conn = await init_connection("test")
    await conn.fetch(query.format(minutes=1))
    end3 = timer()
    elapsed_1min = round(end3 - end2, 4)
    await conn.fetch(query.format(minutes=5))
    end4 = timer()
    elapsed_5min = round(end4 - end3, 4)
    rows30 = await conn.fetch(query.format(minutes=30))
    end5 = timer()
    elapsed_30min = round(end5 - end4, 4)

    for row in rows30:
        print(
            f"{row['time']}\tO{row['open']}\tH{row['high']}\tL{row['low']}\tC{row['close']}\tV{row['volume']}"
        )
    await conn.close()

    print(
        f"{format_int(iterations)} datapoints, write from scratch: {elapsed_clean}(s) elapsed."
    )
    print(
        f"{format_int(iterations)} datapoints, on-conflict upsert: {elapsed_upsert}(s) elapsed."
    )
    print(f"1min OHLCV aggregation: {elapsed_1min}(s) elapsed.")
    print(f"5min OHLCV aggregation: {elapsed_5min}(s) elapsed.")
    print(f"30min OHLCV aggregation: {elapsed_30min}(s) elapsed.")


def main():
    load_credentials(decrypt_credentials(which=["*.env"]))
    asyncio.get_event_loop().run_until_complete(test_asyncpg())


if __name__ == "__main__":
    start = timer()
    print("TimescaleDB test start")
    main()
    end = timer()
    elapsed = end - start
    print(f"Total: {elapsed}s elapsed.")
