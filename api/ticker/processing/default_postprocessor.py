import asyncio
from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import ProcessTaskSchema
from utils.timeseries.timescale_utils import write_ticks
from utils.timeseries.constants import DATA_TYPES


async def default_postprocessor(pool, strategy: StrategySchema, process_queue):
    session_id = strategy.live_session_id
    if not session_id:
        raise Exception("Data integrity loss: no session ID available during postprocessor start")
    while True:
        task: ProcessTaskSchema = await process_queue.async_q.get()
        if task is None:
            return
        t1 = t2 = None
        if task.ticks_primary:
            t1 = asyncio.create_task(write_ticks(
                session_id,
                DATA_TYPES.ticks_primary,
                task.label_primary,
                task.ticks_primary,
                pool
            ))
        if task.ticks_secondary:
            t2 = asyncio.create_task(write_ticks(
                session_id,
                DATA_TYPES.ticks_secondary,
                task.label_secondary,
                task.ticks_secondary,
                pool
            ))
        await asyncio.wait(set([x for x in [t1, t2] if x]), timeout=6)
        process_queue.async_q.task_done()
