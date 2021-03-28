import logging
from datetime import datetime, timedelta
from itertools import count
from asyncpg.pool import Pool
from typing import List, Tuple
from pydantic import parse_obj_as
from sortedcontainers import SortedKeyList
from parameters.enums import SessionDatasetNames, SignalResultsEnum
from utils.timeseries.pandas_utils import resample_primitives
from utils.schemas.response_schemas import (
    OHLCSchema,
    PricepointSchema,
    SignalResultSchema,
    SignalsListSchema,
)
from utils.schemas.request_schemas import DataRequestSchema, MarkersRequestSchema


logger = logging.getLogger(__name__)


class SequentialBatchTSDBFetcher:
    def __init__(self, pool, dataset_name, session_id, block_range=timedelta(hours=10)):
        self.fetched_blocks = {}
        self.pool = pool
        self.block_range: timedelta = block_range
        self.dataset_name = dataset_name
        self.session_id = session_id

    async def fetch_block(
        self,
        request_params: DataRequestSchema,
    ) -> Tuple[SortedKeyList, datetime]:
        from_datetime = request_params.from_datetime
        to_datetime = from_datetime + self.block_range
        async with self.pool.acquire() as conn:
            query = f"""
            SELECT
                time_bucket_gapfill($1, timestamp) AS time,
                locf(avg(price)) as price,
                sum(volume) as volume
            FROM {self.dataset_name}_ticks
            WHERE session_id = $2
            and label = $3
            and data_type = $4
            and timestamp BETWEEN $5 and $6
            GROUP BY time
            ORDER BY time ASC;
            """
            params = (
                timedelta(minutes=request_params.period),
                self.session_id,
                request_params.label,
                request_params.data_type,
                from_datetime,
                to_datetime,
            )
            result = list(await conn.fetch(query, *params))
            print(f'Fetched list: {len(result)}')
            return SortedKeyList(result, key=lambda x: x['time'].timestamp()), to_datetime

    async def get_block(self, request_params: DataRequestSchema):
        access_hash = f'{request_params.label}:{request_params.data_type}'
        candidate_block = self.fetched_blocks.get(access_hash)
        is_no_block = candidate_block is None
        is_stale_block = not is_no_block and candidate_block['to_datetime'] <= request_params.to_datetime
        if is_no_block or is_stale_block:
            block, to_datetime = await self.fetch_block(request_params)
            candidate_block = dict(to_datetime=to_datetime, data=block)
            self.fetched_blocks[access_hash] = candidate_block
        return candidate_block['data']

    async def get_prices(
        self,
        request_params: DataRequestSchema,
    ) -> List[PricepointSchema]:
        block: SortedKeyList = await self.get_block(request_params)
        result = list(block.irange_key(request_params.from_datetime.timestamp(), request_params.to_datetime.timestamp()))
        return result


async def get_prices(
    dataset_name: SessionDatasetNames,
    session_id,
    request_params: DataRequestSchema,
    pool: Pool,
) -> List[PricepointSchema]:
    """Get prices."""
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    async with pool.acquire() as conn:
        query = f"""
        SELECT
            -- time_bucket_gapfill($1, timestamp, now() - INTERVAL '2 hours', now()) AS time,
            time_bucket_gapfill($1, timestamp) AS time,
            locf(avg(price)) as price,
            sum(volume) as volume
        FROM {dataset_name}_ticks
        WHERE session_id = $2
        and label = $3
        and data_type = $4
        and timestamp BETWEEN $5 and $6
        GROUP BY time
        ORDER BY time ASC;
        """
        params = (
            timedelta(minutes=request_params.period),
            session_id,
            request_params.label,
            request_params.data_type,
            request_params.from_datetime,
            request_params.to_datetime,
        )
        result = list(await conn.fetch(query, *params))
        return parse_obj_as(List[PricepointSchema], result)


signal_weights = {
    SignalResultsEnum.NO_DATA: 0,
    SignalResultsEnum.AMBIGUOUS: 1,
    SignalResultsEnum.SELL_ALL: 2,
    SignalResultsEnum.BUY_ALL: 2,
}


def reduce_signals(signals: list, period: int) -> list:
    result = {}
    for signal in signals:
        key_value = signal["bucket_timestamp"]
        new_wins = False
        if key_value not in result:
            new_wins = True
        else:
            old_signal = result[key_value]
            if (
                signal_weights[signal["direction"]]
                > signal_weights[old_signal["direction"]]
            ):
                new_wins = True
            elif (
                signal_weights[signal["direction"]]
                == signal_weights[old_signal["direction"]]
                and signal["value"] >= old_signal["value"]
            ):
                new_wins = True
        if new_wins:
            result[key_value] = signal
    return list(filter(bool, [resample_primitives(result[x], period) for x in result]))


async def get_reduced_signals(
    dataset_name: SessionDatasetNames,
    session_id,
    request_params: MarkersRequestSchema,
    request,
) -> SignalsListSchema:
    pool: Pool = request.app["TIMESCALE_POOL"]
    if not request_params.period:
        raise Exception("Period not provided for reduced signals calculation!")
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()

    reduced_result: List[SignalResultSchema] = []
    async with pool.acquire() as conn:
        query = f"""
        SELECT
            time_bucket($1, timestamp) AS bucket_timestamp,
            *
        FROM {dataset_name}_signals
        WHERE session_id = $2
        and timestamp BETWEEN $3 and $4
        ORDER BY timestamp ASC;
        """
        params = [
            timedelta(minutes=request_params.period),
            session_id,
            request_params.from_datetime,
            request_params.to_datetime,
        ]
        try:
            async with conn.transaction():
                current_timestamp = None
                bucket = []
                async for record in conn.cursor(query, *params):
                    ts = record["bucket_timestamp"]
                    if ts == current_timestamp:
                        bucket.append(record)
                    else:
                        reduced_result.extend(
                            reduce_signals(bucket, request_params.period)
                        )
                        bucket = []
                        current_timestamp = ts
        except Exception as e:
            print(e)
            raise e
    return parse_obj_as(SignalsListSchema, list(reduced_result))


async def get_signals(
    dataset_name: SessionDatasetNames,
    session_id,
    request_params: MarkersRequestSchema,
    request,
) -> SignalsListSchema:
    pool: Pool = request.app["TIMESCALE_POOL"]
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    fields = "*"
    n = count(1)
    params = []
    if request_params.period:
        params.append(timedelta(minutes=request_params.period))
        fields = f"time_bucket(${next(n)}, timestamp) AS bucket_timestamp," f"*"

    async with pool.acquire() as conn:
        query = f"""
        SELECT
            {fields}
        FROM {dataset_name}_signals
        WHERE session_id = ${next(n)}
        and timestamp BETWEEN ${next(n)} and ${next(n)}
        ORDER BY timestamp ASC;
        """
        params.extend(
            [session_id, request_params.from_datetime, request_params.to_datetime]
        )
        result: SignalResultSchema = await conn.fetch(query, *params)
        return parse_obj_as(SignalsListSchema, list(result))


async def get_terminal_data(
    dataset_name: SessionDatasetNames,
    session_id,
    request_params: DataRequestSchema,
    request,
):
    # TODO: use only session_id from request_params
    pool: Pool = request.app["TIMESCALE_POOL"]
    if not request_params.to_datetime:
        request_params.to_datetime = datetime.now()
    period = timedelta(minutes=request_params.period)

    # TODO: Peg to and from datetimes to period breakpoints
    async with pool.acquire() as conn:
        query = f"""
        SELECT
            time_bucket($1, timestamp) AS time,
            first(price, timestamp) as open,
            max(price) as high,
            min(price) as low,
            last(price, timestamp) as close,
            sum(volume) as volume
        FROM {dataset_name}_ticks
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
            request_params.to_datetime,
        )
        return parse_obj_as(List[OHLCSchema], list(await conn.fetch(query, *params)))
