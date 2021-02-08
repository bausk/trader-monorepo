import os
import logging
import asyncpg


logger = logging.getLogger(__name__)

DEFAULT_DBNAME = "livewater"


async def pool_context(app):
    app["TIMESCALE_POOL"] = pool = await get_pool(DEFAULT_DBNAME)
    yield
    await pool.close()


def get_url():
    url = os.environ.get("TIMESCALEDB_URL")
    assert (
        url
    ), "Time-series DB URL must be specified in TIMESCALEDB_URL environment variable"
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
    await init_indicators_table(conn)
    await init_signals_table(conn)


async def init_signals_table(conn):
    NAME = "signals"
    SCHEMA = f"""{NAME} (
        timestamp TIMESTAMPTZ NOT NULL,
        session_id INTEGER, -- ID of session to which signal belongs
        label VARCHAR(50), -- asset name or other string identifier if N/A
        direction VARCHAR(50),
        value DOUBLE PRECISION,
        traceback JSONB
    )"""
    await conn.execute(f"CREATE TABLE IF NOT EXISTS {SCHEMA};")
    try:
        await conn.execute("SELECT create_hypertable('{NAME}', 'timestamp');")
        logger.info(f"Created hypertable: {NAME}")
    except asyncpg.exceptions.UnknownPostgresError:
        logger.info(f"Hypertable not created, assuming exists: {NAME}")

    await conn.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS unique_{NAME} \
        ON {NAME}(timestamp, session_id, label);"
    )


async def init_indicators_table(conn):
    NAME = "indicators"
    SCHEMA = f"""{NAME} (
        timestamp TIMESTAMPTZ NOT NULL,
        session_id INTEGER NOT NULL, -- ID of session to which indicator belongs
        label VARCHAR(50) NOT NULL, -- indicator name
        value DOUBLE PRECISION,
        datablob JSONB
    )"""
    await conn.execute(f"CREATE TABLE IF NOT EXISTS {SCHEMA};")
    try:
        await conn.execute("SELECT create_hypertable('{NAME}', 'timestamp');")
        logger.info(f"Created hypertable: {NAME}")
    except asyncpg.exceptions.UnknownPostgresError:
        logger.info(f"Hypertable not created, assuming exists: {NAME}")

    await conn.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS unique_{NAME} \
        ON {NAME}(timestamp, session_id, label);"
    )


async def init_ticks_table(conn):
    NAME = "ticks"
    SCHEMA = f"""{NAME} (
        timestamp TIMESTAMPTZ NOT NULL,
        session_id INTEGER, -- session id associated with the tick
        data_type INTEGER, -- type of data (primary_ticks = 1, secondary_ticks = 2 etc)
        label VARCHAR(50), -- asset name or other string identifier if N/A
        price DOUBLE PRECISION,
        volume DOUBLE PRECISION,
        funds DOUBLE PRECISION
    )"""
    await conn.execute(f"CREATE TABLE IF NOT EXISTS {SCHEMA};")
    try:
        await conn.execute("SELECT create_hypertable('{NAME}', 'timestamp');")
        logger.info(f"Created hypertable: {NAME}")
    except asyncpg.exceptions.UnknownPostgresError:
        logger.info(f"Hypertable not created, assuming exists: {NAME}")

    await conn.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS unique_{NAME} \
        ON {NAME}(timestamp, session_id, data_type, label, funds);"
    )


async def init_db(dbname=DEFAULT_DBNAME):
    conn = await asyncpg.connect(f"{get_url()}template1")
    try:
        await conn.execute(f"CREATE DATABASE {dbname};")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    await conn.close()
    conn = await init_connection(dbname)
    await init_ticks_table(conn)
    await init_signals_table(conn)
    await init_indicators_table(conn)


async def get_pool(dbname=DEFAULT_DBNAME) -> asyncpg.pool.Pool:
    await init_db(dbname)
    try:
        return await asyncpg.create_pool(
            f"{get_url()}{dbname}", max_inactive_connection_lifetime=10
        )
    except Exception as e:
        print("Failed to start up connection pool")
        raise e
