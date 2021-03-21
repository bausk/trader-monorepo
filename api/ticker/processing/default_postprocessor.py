import asyncio
from parameters.enums import SessionDatasetNames
from utils.schemas.dataflow_schemas import CalculationSchema
from utils.processing.async_queue import _ProcQueue
from utils.timescaledb.tsdb_write import Writers, get_buffered_writer, write_signals, write_indicators


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


async def cached_postprocessor(
    dataset_name: SessionDatasetNames, pool, session_id: int, process_queue: _ProcQueue,
):
    if not session_id:
        raise Exception(
            "Data integrity loss: no session ID available during signal postprocessing"
        )
    IndicatorWriter = get_buffered_writer(writer_type=Writers.INDICATORS)
    SignalWriter = get_buffered_writer(writer_type=Writers.SIGNALS)
    async with IndicatorWriter(
        dataset_name=dataset_name,
        session_id=session_id,
        pool=pool,
    ) as indicator_writer:
        async with SignalWriter(
            dataset_name=dataset_name,
            session_id=session_id,
            pool=pool,
        ) as signal_writer:
            while True:
                task: CalculationSchema = await process_queue.coro_get()
                # process_queue.async_q.task_done()
                if task is None:
                    print("postprocessor exit")
                    await process_queue.coro_put(None)
                    return
                indicators_task = asyncio.create_task(
                    indicator_writer.write(task.indicators)
                )
                signals_task = asyncio.create_task(
                    signal_writer.write([task.signal])
                )
                await asyncio.wait(set([signals_task, indicators_task]), timeout=60)
