import asyncio
from parameters.enums import SessionDatasetNames
from utils.schemas.dataflow_schemas import CalculationSchema
from utils.timescaledb.tsdb_write import write_signals, write_indicators


async def default_postprocessor(
    dataset_name: SessionDatasetNames, pool, session_id: int, process_queue
):
    if not session_id:
        raise Exception(
            "Data integrity loss: no session ID available during signal postprocessing"
        )
    while True:
        task: CalculationSchema = await process_queue.async_q.get()
        process_queue.async_q.task_done()
        if task is None:
            print("postprocessor exit")
            return
        signals_task = asyncio.create_task(
            write_indicators(dataset_name, pool, session_id, task.indicators)
        )
        indicators_task = asyncio.create_task(
            write_signals(dataset_name, pool, session_id, [task.signal])
        )
        await asyncio.wait(set([signals_task, indicators_task]), timeout=6)
