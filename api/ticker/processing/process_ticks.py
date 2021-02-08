import asyncio
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import SourceFetchResultSchema
from utils.timescaledb.tsdb_write import (
    write_ticks,
)
from utils.timeseries.constants import DATA_TYPES


async def write_ticks_to_session_store(
    pool,
    strategy: StrategySchema,
    ticks_queue: Queue,
):
    session_id = strategy.live_session_id
    if not session_id:
        raise Exception(
            "Data integrity loss: no session ID available during tick processing"
        )
    while True:
        task: SourceFetchResultSchema = await ticks_queue.async_q.get()
        if task is None:
            return
        t1 = t2 = None
        if task.ticks_primary:
            t1 = asyncio.create_task(
                write_ticks(
                    session_id,
                    DATA_TYPES.ticks_primary,
                    task.label_primary,
                    task.ticks_primary,
                    pool,
                )
            )
        if task.ticks_secondary:
            t2 = asyncio.create_task(
                write_ticks(
                    session_id,
                    DATA_TYPES.ticks_secondary,
                    task.label_secondary,
                    task.ticks_secondary,
                    pool,
                )
            )
        await asyncio.wait(set([x for x in [t1, t2] if x]), timeout=6)
        ticks_queue.async_q.task_done()
