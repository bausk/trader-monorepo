import asyncio
from parameters.enums import SessionDatasetNames
from janus import Queue
from utils.schemas.dataflow_schemas import SourceFetchResultSchema
from utils.timescaledb.tsdb_write import (
    write_ticks,
)


async def write_ticks_to_session_store(
    dataset_name: SessionDatasetNames,
    pool,
    session_id: int,
    ticks_queue: Queue,
    out_queue: Queue,
):
    if not session_id:
        raise Exception(
            "Data integrity loss: no session ID available during tick processing"
        )
    while True:
        task: SourceFetchResultSchema = await ticks_queue.async_q.get()
        ticks_queue.async_q.task_done()
        if task is None:
            await out_queue.async_q.put(None)
            print("ticks write exit")
            return
        tasks = []
        for ticks_result in task.ticks:
            tick_task = asyncio.create_task(
                write_ticks(
                    dataset_name,
                    session_id,
                    ticks_result.data_type,
                    ticks_result.label,
                    ticks_result.ticks,
                    pool,
                )
            )
            tasks.append(tick_task)
        await asyncio.wait(tasks, timeout=6)
        await out_queue.async_q.put(task)
