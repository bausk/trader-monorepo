from typing import List
import asyncio
from datetime import datetime, timedelta
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import ProcessTaskSchema, SignalResultSchema
from utils.schemas.request_schemas import DataRequestSchema
from utils.schemas.response_schemas import PricepointSchema
from utils.timeseries.constants import DATA_TYPES
from utils.timeseries.timescale_utils import get_prices
from .monitor_strategy_signal import calculate_signal


async def monitor_strategy_executor(
    pool, strategy: StrategySchema, in_queue: Queue, out_queue: Queue
) -> None:
    while True:
        task: ProcessTaskSchema = await in_queue.async_q.get()
        # TODO: # 1. Error management
        # 2. Refactor strategy executor: make tools to get data without cruft
        # 3. Refactor executor: pass data to postprocessing without relying on strategy
        # 4. Maybe: chain/parallel strategies?
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
            primary_data_coro = asyncio.create_task(
                get_prices(session_id, primary_params, pool)
            )
            secondary_data_coro = asyncio.create_task(
                get_prices(session_id, secondary_params, pool)
            )
            done, pending = await asyncio.wait(
                {primary_data_coro, secondary_data_coro}, timeout=4
            )
            if primary_data_coro in done and secondary_data_coro in done:
                primary_data: List[PricepointSchema] = primary_data_coro.result()
                secondary_data: List[PricepointSchema] = secondary_data_coro.result()
                signal: SignalResultSchema = calculate_signal(
                    primary_data, secondary_data
                )
                task.signals += [signal]
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
        except Exception as e:
            print(e)
        await out_queue.async_q.put(task)
        in_queue.async_q.task_done()
        if task is None:
            return
