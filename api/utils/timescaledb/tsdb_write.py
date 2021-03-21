import asyncpg
import json
import logging
import pytz
from enum import Enum, auto
from typing import Any, Dict, List, Tuple
from pydantic.tools import parse_obj_as
from parameters.enums import SessionDatasetNames
from utils.profiling.timer import Timer
from utils.schemas.dataflow_schemas import (
    IndicatorSchema,
    SignalSchema,
    TickSchema,
    TimeseriesSchema,
)


logger = logging.getLogger(__name__)


async def write_indicators(
    dataset_name: SessionDatasetNames,
    pool,
    session_id: int,
    indicators: List[IndicatorSchema],
) -> None:
    for indicator in indicators:
        indicator_tuples = []
        for datapoint in indicator.indicator:
            datapoint: TimeseriesSchema
            values = (
                datapoint.timestamp,
                session_id,
                indicator.label,
                datapoint.value,
            )
            indicator_tuples.append(values)
        async with pool.acquire() as conn:
            try:
                await conn.executemany(
                    f"""
                    INSERT INTO {dataset_name}_indicators(timestamp, session_id, label, value)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (timestamp, session_id, label) DO UPDATE
                    SET value=EXCLUDED.value;
                """,
                    indicator_tuples,
                )
            except asyncpg.exceptions.UniqueViolationError:
                pass


async def write_signals(
    dataset_name: SessionDatasetNames,
    pool,
    session_id: int,
    signals: List[SignalSchema],
) -> None:
    prepared_signals = []
    for signal in signals:
        values = (
            signal.timestamp,
            session_id,
            signal.direction,
            signal.value,
            json.dumps(signal.traceback),
        )
        prepared_signals.append(values)
    async with pool.acquire() as conn:
        try:
            await conn.executemany(
                f"""
                INSERT INTO {dataset_name}_signals(timestamp, session_id, direction, value, traceback)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (timestamp, session_id, label) DO UPDATE
                SET value=EXCLUDED.value,
                    direction=EXCLUDED.direction,
                    traceback=EXCLUDED.traceback;
            """,
                prepared_signals,
            )
        except asyncpg.exceptions.UniqueViolationError:
            logger.warning("UniqueViolationError on signals write to TimescaleDB")


class Writers(Enum):
    TICKS = auto()
    INDICATORS = auto()
    SIGNALS = auto()


class TSDBBufferedWriter:

    table_template = ""
    columns = []

    def __init__(
        self,
        dataset_name,
        session_id,
        pool,
        data_type=None,
        label=None,
        chunksize=50000,
    ):
        self.dataset_name = dataset_name
        self.session_id = session_id
        self.pool = pool
        self.data_type = data_type
        self.label = label
        self.chunksize = chunksize
        self.buffer = None
        self.flush_timer = Timer(f"<{self.__class__.__name__}> flush")

    async def __aenter__(self):
        self.buffer = {}
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if len(self.buffer) > 0:
            await self.flush()

    def prepare(self, input) -> Dict[Any, Tuple]:
        raise NotImplementedError("Implement prepare(input)!")

    async def write(self, input: List):
        self.buffer.update(self.prepare(input))
        if len(self.buffer) >= self.chunksize:
            await self.flush()

    async def flush(self):
        self.flush_timer.start()
        async with self.pool.acquire() as conn:
            try:
                print(f"Flushing {len(self.buffer)} datapoints...")
                await conn.copy_records_to_table(
                    self.table_template.format(self.dataset_name),
                    records=list(self.buffer.values()),
                    columns=self.columns,
                )
            except asyncpg.exceptions.UniqueViolationError:
                pass
        self.flush_timer.stop()
        self.buffer = {}


class TicksBufferedWriter(TSDBBufferedWriter):
    columns = [
        "timestamp",
        "session_id",
        "data_type",
        "label",
        "price",
        "volume",
        "funds",
    ]
    table_template = "{}_ticks"

    def prepare(self, input: List[TickSchema]) -> Dict[Any, Tuple]:
        prepared_ticks = {}
        for tick in input:
            timestamp = tick.timestamp.replace(tzinfo=pytz.UTC)
            values = (
                timestamp,
                self.session_id,
                self.data_type,
                self.label,
                tick.price,
                tick.volume,
                tick.funds,
            )
            prepared_ticks[timestamp] = values
        return prepared_ticks


class IndicatorsBufferedWriter(TSDBBufferedWriter):
    columns = [
        "timestamp",
        "session_id",
        "label",
        "value",
    ]
    table_template = "{}_indicators"

    def prepare(self, input: List[IndicatorSchema]) -> Dict[Any, Tuple]:
        indicator_tuples = {}
        for indicator in input:
            for datapoint in indicator.indicator:
                datapoint: TimeseriesSchema
                values = (
                    datapoint.timestamp,
                    self.session_id,
                    indicator.label,
                    datapoint.value,
                )
                indicator_tuples[(datapoint.timestamp, indicator.label)] = values
        return indicator_tuples


class SignalsBufferedWriter(TSDBBufferedWriter):
    columns = [
        "timestamp",
        "session_id",
        "direction",
        "value",
        "traceback",
    ]
    table_template = "{}_signals"

    def prepare(self, input: List[SignalSchema]) -> Dict[Any, Tuple]:
        prepared_signals = {}
        for signal in input:
            values = (
                signal.timestamp,
                self.session_id,
                signal.direction,
                signal.value,
                json.dumps(signal.traceback),
            )
            prepared_signals[signal.timestamp] = values
        return prepared_signals


def get_buffered_writer(writer_type: Writers) -> TSDBBufferedWriter:
    writers = {
        Writers.TICKS: TicksBufferedWriter,
        Writers.INDICATORS: IndicatorsBufferedWriter,
        Writers.SIGNALS: SignalsBufferedWriter,
    }
    return writers[writer_type]


async def write_ticks(
    dataset_name: SessionDatasetNames,
    session_id,
    data_type,
    label,
    ticks: List[TickSchema],
    pool,
):
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
            tick.funds,
        )
        prepared_ticks.append(values)

    async with pool.acquire() as conn:
        try:
            await conn.executemany(
                f"""
                INSERT INTO {dataset_name}_ticks(timestamp, session_id, data_type, label, price, volume, funds)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (timestamp, session_id, data_type, label) DO UPDATE
                SET price=EXCLUDED.price,
                    volume=EXCLUDED.volume,
                    funds=EXCLUDED.funds;
            """,
                prepared_ticks,
            )
        except asyncpg.exceptions.UniqueViolationError:
            pass


async def stream_write_ticks(
    dataset_name: SessionDatasetNames,
    session_id,
    data_type,
    label,
    pool,
    iterator,
):
    writer = get_buffered_writer(writer_type=Writers.TICKS)
    async with writer(
        dataset_name=dataset_name,
        session_id=session_id,
        pool=pool,
        data_type=data_type,
        label=label,
    ) as writer:
        async for data in iterator:
            await writer.write(
                parse_obj_as(List[TickSchema], data),
            )
