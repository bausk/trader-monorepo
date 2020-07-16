import asyncio
from datetime import datetime, timedelta
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import ProcessTaskSchema
from utils.schemas.request_schemas import DataRequestSchema
from utils.timeseries.constants import DATA_TYPES
from utils.timeseries.timescale_utils import get_prices


async def monitor_strategy_executor(pool, strategy: StrategySchema, in_queue: Queue, out_queue: Queue) -> None:
    while True:
        task: ProcessTaskSchema = await in_queue.async_q.get()
        try:
            session_id = strategy.live_session_id
            from_datetime = datetime.today() - timedelta(hours=2)
            primary_params = DataRequestSchema(
                from_datetime=from_datetime,
                period=1,
                label=task.label_primary,
                data_type=DATA_TYPES.ticks_primary,
            )
            secondary_params = DataRequestSchema(
                from_datetime=from_datetime,
                period=1,
                label=task.label_secondary,
                data_type=DATA_TYPES.ticks_secondary,
            )
            primary_data_coro = asyncio.create_task(get_prices(session_id, primary_params, pool))
            secondary_data_coro = asyncio.create_task(get_prices(session_id, secondary_params, pool))
            done, pending = await asyncio.wait({primary_data_coro, secondary_data_coro}, timeout=4)
            if primary_data_coro in done and secondary_data_coro in done:
                primary_data = primary_data_coro.result()
                secondary_data = secondary_data_coro.result()
                print(f"Results: {len(primary_data)} , {len(secondary_data)}")
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
        except Exception as e:
            pass
            # print(e)
        await out_queue.async_q.put(task)
        in_queue.async_q.task_done()
        if task is None:
            return
