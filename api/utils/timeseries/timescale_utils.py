import os
import datetime
import pytz
import asyncpg
from typing import List
from utils.schemas.dataflow_schemas import TickSchema


def get_url():
    url = os.environ.get('TIMESCALEDB_URL')
    assert url, "Time-series DB URL must be specified in TIMESCALEDB_URL environment variable"
    return url


async def init_connection(dbname):
    return await asyncpg.connect(f"{get_url()}{dbname}")


async def reset_db(dbname):
    conn = await asyncpg.connect(f"{get_url()}template1")
    await conn.execute(f"DROP DATABASE IF EXISTS {dbname};")
    await conn.execute(f"CREATE DATABASE {dbname};")
    await conn.close()
    conn = await init_connection(dbname)
    await init_ticks_table(conn)


async def init_ticks_table(conn):
    TICKS_TABLE_SCHEMA = """ticks (
        timestamp TIMESTAMPTZ NOT NULL,
        source_id VARCHAR(70), -- third-party tick ID
        session_id INTEGER, -- session id associated with the tick
        data_type INTEGER, -- type of data (primary_ticks = 1, secondary_ticks = 2 etc)
        label VARCHAR(50), -- asset name or other string identifier if N/A
        price DOUBLE PRECISION,
        volume DOUBLE PRECISION,
        funds DOUBLE PRECISION
    )"""
    await conn.execute(f"CREATE TABLE IF NOT EXISTS {TICKS_TABLE_SCHEMA};")
    try:
        await conn.execute("SELECT create_hypertable('ticks', 'timestamp');")
        print('created hypertable')
    except asyncpg.exceptions.UnknownPostgresError:
        pass

    await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_ticks \
        ON ticks(timestamp, source_id, session_id, data_type, label, funds);")


async def init_db(dbname):
    conn = await asyncpg.connect(f"{get_url()}template1")
    try:
        await conn.execute(f"CREATE DATABASE {dbname};")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    await conn.close()
    conn = await init_connection(dbname)
    await init_ticks_table(conn)


async def get_pool(dbname) -> asyncpg.pool.Pool:
    await init_db(dbname)
    try:
        return await asyncpg.create_pool(
            f"{get_url()}{dbname}",
            max_inactive_connection_lifetime=10
        )
    except Exception as e:
        print('Failed to start up connection pool')
        raise e

DATA_TYPES = {
    'primary_ticks': 1,
    'secondary_ticks': 2
}

LABELS = {
    'primary_ticks': 'BTCUSD',
    'secondary_ticks': 'BTCUAH'
}


async def write_ticks(dbname, session_id, key, ticks: List[TickSchema], pool):
    tick_strings = []
    for tick in ticks:
        timestamp = tick.timestamp.replace(tzinfo=pytz.UTC)
        data_type = DATA_TYPES.get(key, 0)
        label = LABELS.get(key, 'UNDEFINED')
        values = f"""('{timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")}',
            {session_id},
            {data_type},
            '{label}',
            {tick.price},
            {tick.volume},
            {tick.funds})
        """
        tick_strings.append(values)

    async with pool.acquire() as conn:
        try:
            await conn.execute(f'''
                INSERT INTO ticks(timestamp, session_id, data_type, label, price, volume, funds)
                VALUES {', '.join(tick_strings)}
                ON CONFLICT (timestamp, source_id, session_id, data_type, label, funds) DO UPDATE
                SET price=EXCLUDED.price,
                    volume=EXCLUDED.volume;
            ''')
        except asyncpg.exceptions.UniqueViolationError:
            pass
