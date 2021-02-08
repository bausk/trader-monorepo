import asyncio
from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import SourceFetchResultSchema
from utils.timescaledb.tsdb_write import write_signals, write_indicators


async def default_postprocessor(pool, strategy: StrategySchema, process_queue):
    session_id = strategy.live_session_id
    if not session_id:
        raise Exception(
            "Data integrity loss: no session ID available during signal postprocessing"
        )
    while True:
        task: SourceFetchResultSchema = await process_queue.async_q.get()
        if task is None:
            return
        if len(task.signals) > 0:
            signals_task = asyncio.create_task(
                write_indicators(session_id, pool, task.signals)
            )
            indicators_task = asyncio.create_task(
                write_signals(session_id, pool, task.signals)
            )
            await asyncio.wait(set([signals_task, indicators_task]), timeout=6)
        process_queue.async_q.task_done()
