import os
from datetime import datetime, timedelta
from itertools import count
import pytz
import asyncpg
from asyncpg.pool import Pool
from typing import List
from pydantic import parse_obj_as
from parameters.enums import SignalResultsEnum
from utils.timeseries.pandas_utils import resample_primitives
from utils.schemas.response_schemas import OHLCSchema, PricepointSchema
from utils.schemas.dataflow_schemas import TickSchema, SignalResultSchema, SignalsListSchema, PrimitivesSchema
from utils.schemas.request_schemas import DataRequestSchema, MarkersRequestSchema


DEFAULT_DBNAME = 'livewater'


async def pool_context(app):
    app['TIMESCALE_POOL'] = pool = await get_pool(DEFAULT_DBNAME)
    yield
    await pool.close()


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
    await init_signals_table(conn)


async def init_signals_table(conn):
    SIGNALS_TABLE_SCHEMA = """signals (
        timestamp TIMESTAMPTZ NOT NULL,
        source_id VARCHAR(70), -- third-party signal ID
        session_id INTEGER, -- session id associated with the tick
        label VARCHAR(50), -- asset name or other string identifier if N/A
        direction VARCHAR(50),
        value DOUBLE PRECISION,
        primitives JSONB
    )"""
    await conn.execute(f"CREATE TABLE IF NOT EXISTS {SIGNALS_TABLE_SCHEMA};")
    try:
        await conn.execute("SELECT create_hypertable('signals', 'timestamp');")
        print('created signals hypertable')
    except asyncpg.exceptions.UnknownPostgresError:
        pass

    await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_signals \
        ON signals(timestamp, source_id, session_id, label);")


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
        print('created ticks hypertable')
    except asyncpg.exceptions.UnknownPostgresError:
        pass

    await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_ticks \
        ON ticks(timestamp, source_id, session_id, data_type, label, funds);")


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


async def get_pool(dbname=DEFAULT_DBNAME) -> asyncpg.pool.Pool:
    await init_db(dbname)
    try:
        return await asyncpg.create_pool(
            f"{get_url()}{dbname}",
            max_inactive_connection_lifetime=10
        )
    except Exception as e:
        print('Failed to start up connection pool')
        raise e


async def get_prices(session_id, request_params: DataRequestSchema, pool: Pool) -> List[PricepointSchema]:
    period = timedelta(minutes=request_params.period)
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    async with pool.acquire() as conn:
        query = """
        SELECT
            -- time_bucket_gapfill($1, timestamp, now() - INTERVAL '2 hours', now()) AS time,
            time_bucket_gapfill($1, timestamp) AS time,
            locf(avg(price)) as price,
            sum(volume) as volume
        FROM ticks
        WHERE session_id = $2
        and label = $3
        and data_type = $4
        and timestamp BETWEEN $5 and $6
        GROUP BY time
        ORDER BY time ASC;
        """
        params = (
            period,
            session_id,
            request_params.label,
            request_params.data_type,
            request_params.from_datetime,
            request_params.to_datetime
        )
        return parse_obj_as(List[PricepointSchema], list(await conn.fetch(query, *params)))


signal_weights = {
    SignalResultsEnum.NO_DATA: 0,
    SignalResultsEnum.AMBIGUOUS: 1,
    SignalResultsEnum.SELL_ALL: 2,
    SignalResultsEnum.BUY_ALL: 2
}


def reduce_signals(signals: list, period: int) -> list:
    result = {}
    for signal in signals:
        key_value = signal['bucket_timestamp']
        new_wins = False
        if (key_value not in result):
            new_wins = True
        else:
            old_signal = result[key_value]
            if signal_weights[signal['direction']] > signal_weights[old_signal['direction']]:
                new_wins = True
            elif signal_weights[signal['direction']] == signal_weights[old_signal['direction']] and signal['value'] >= old_signal['value']:
                new_wins = True
        if new_wins:
            result[key_value] = signal
    return list(filter(bool, [resample_primitives(result[x], period) for x in result]))


async def get_reduced_signals(session_id, request_params: MarkersRequestSchema, request) -> SignalsListSchema:
    pool: Pool = request.app['TIMESCALE_POOL']
    if not request_params.period:
        raise Exception('Period not provided for reduced signals calculation!')
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()

    reduced_result = []
    async with pool.acquire() as conn:
        query = """
        SELECT
            time_bucket($1, timestamp) AS bucket_timestamp,
            *
        FROM signals
        WHERE session_id = $2
        and timestamp BETWEEN $3 and $4
        ORDER BY timestamp ASC;
        """
        params = [
            timedelta(minutes=request_params.period),
            session_id,
            request_params.from_datetime,
            request_params.to_datetime
        ]
        try:
            async with conn.transaction():
                current_timestamp = None
                bucket = []
                async for record in conn.cursor(query, *params):
                    ts = record['bucket_timestamp']
                    if ts == current_timestamp:
                        bucket.append(record)
                    else:
                        reduced_result.extend(reduce_signals(bucket, request_params.period))
                        bucket = []
                        current_timestamp = ts
        except Exception as e:
            print(e)
            raise e
    return SignalsListSchema(__root__=reduced_result)


async def get_signals(session_id, request_params: MarkersRequestSchema, request) -> SignalsListSchema:
    pool: Pool = request.app['TIMESCALE_POOL']
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    fields = "*"
    n = count(1)
    params = []
    if request_params.period:
        params.append(timedelta(minutes=request_params.period))
        fields = (
            f"time_bucket(${next(n)}, timestamp) AS bucket_timestamp,"
            f"*"
        )

    async with pool.acquire() as conn:
        query = f"""
        SELECT
            {fields}
        FROM signals
        WHERE session_id = ${next(n)}
        and timestamp BETWEEN ${next(n)} and ${next(n)}
        ORDER BY timestamp ASC;
        """
        params.extend([
            session_id,
            request_params.from_datetime,
            request_params.to_datetime
        ])
        result = await conn.fetch(query, *params)
        return SignalsListSchema(__root__=list(result))


async def get_terminal_data(session_id, request_params: DataRequestSchema, request):
    pool: Pool = request.app['TIMESCALE_POOL']
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    period = timedelta(minutes=request_params.period)

    # TODO: Peg to and from datetimes to period breakpoints
    async with pool.acquire() as conn:
        query = """
        SELECT
            time_bucket($1, timestamp) AS time,
            first(price, timestamp) as open,
            max(price) as high,
            min(price) as low,
            last(price, timestamp) as close,
            sum(volume) as volume
        FROM ticks
        WHERE session_id = $2
        and label = $3
        and data_type = $4
        and timestamp BETWEEN $5 and $6
        GROUP BY time
        ORDER BY time ASC;
        """
        params = (
            period,
            session_id,
            request_params.label,
            request_params.data_type,
            request_params.from_datetime,
            request_params.to_datetime
        )
        return parse_obj_as(List[OHLCSchema], list(await conn.fetch(query, *params)))


def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta


async def mock_get_terminal_data(session_id, request_params: DataRequestSchema, request):
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    period = timedelta(minutes=request_params.period)
    from_dt = ceil_dt(request_params.from_datetime, period)
    to_dt = ceil_dt(request_params.to_datetime, period)
    assert from_dt < to_dt
    data = []
    while from_dt < to_dt:
        ohlc = OHLCSchema(
            time=from_dt,
            open=10.0,
            high=15.5,
            low=8.1,
            close=14.1,
            volume=20,
        )
        data.append(ohlc)
        from_dt = from_dt + period
    return data


async def write_signals(
    session_id,
    pool,
    signals: List[SignalResultSchema]
) -> None:
    prepared_signals = []
    for signal in signals:
        values = (
            signal.timestamp,
            session_id,
            signal.direction,
            signal.value,
            parse_obj_as(PrimitivesSchema, signal.primitives).json() if signal.primitives else None
        )
        prepared_signals.append(values)
    async with pool.acquire() as conn:
        try:
            await conn.executemany('''
                INSERT INTO signals(timestamp, session_id, direction, value, primitives)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (timestamp, source_id, session_id, label) DO UPDATE
                SET value=EXCLUDED.value,
                    primitives=EXCLUDED.primitives;
            ''', prepared_signals)
        except asyncpg.exceptions.UniqueViolationError:
            pass


async def write_ticks(session_id, data_type, label, ticks: List[TickSchema], pool):
    prepared_ticks = []
    for tick in ticks:
        timestamp = tick.timestamp.replace(tzinfo=pytz.UTC)
        values = (
            timestamp,
            session_id,
            data_type,
            label,
            tick.price,
            tick.volume,
            tick.funds
        )
        prepared_ticks.append(values)

    async with pool.acquire() as conn:
        try:
            await conn.executemany('''
                INSERT INTO ticks(timestamp, session_id, data_type, label, price, volume, funds)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (timestamp, source_id, session_id, data_type, label, funds) DO UPDATE
                SET price=EXCLUDED.price,
                    volume=EXCLUDED.volume;
            ''', prepared_ticks)
        except asyncpg.exceptions.UniqueViolationError:
            pass
