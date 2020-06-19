from timeit import default_timer as timer
import math
import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path
import click
import datetime
import pytz
import asyncpg
from janus import Queue
from secrets_management.manage import encrypt_credentials, decrypt_credentials, load_credentials
from utils.test_utils import generate_data, format_int


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
        session_id INTEGER,
        data_type INTEGER,
        label VARCHAR(50),
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
        ON ticks(timestamp, session_id, data_type, label, funds);")


async def init_db(dbname):
    conn = await asyncpg.connect(f"{get_url()}template1")
    try:
        await conn.execute(f"CREATE DATABASE {dbname};")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    await conn.close()
    conn = await init_connection(dbname)
    await init_ticks_table(conn)
