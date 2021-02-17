from typing import List
import logging
import asyncio
from datetime import datetime, timedelta
from janus import Queue
from utils.schemas.dataflow_schemas import (
    CalculationSchema,
    IndicatorSchema,
    SignalSchema,
    SourceFetchResultSchema,
)
from utils.schemas.request_schemas import DataRequestSchema
from utils.schemas.response_schemas import InputMarketDataSchema, PricepointSchema
from utils.timescaledb.tsdb_read import get_prices
from .monitor_strategy_signal import calculate_indicators, calculate_signal


logger = logging.getLogger(__name__)


async def monitor_strategy_executor(
    pool, session_id: int, in_queue: Queue, out_queue: Queue
) -> None:
    print(f"Session ID: {session_id}")
    while True:
        source_result: SourceFetchResultSchema = await in_queue.async_q.get()
        # TODO: # 1. Error management
        # 2. Refactor strategy executor: make tools to get data without cruft
        # 4. Maybe: chain/parallel strategies?
        in_queue.async_q.task_done()
        if source_result is None:
            await out_queue.async_q.put(None)
            print("strategy executor exit")
            return

        try:
            from_datetime = source_result.timestamp - timedelta(hours=2)
            tasks = []
            for tick_source in source_result.ticks:
                params = DataRequestSchema(
                    from_datetime=from_datetime,
                    to_datetime=source_result.timestamp,
                    period=1,
                    label=tick_source.label,
                    data_type=tick_source.data_type,
                )
                task = asyncio.create_task(get_prices(session_id, params, pool))
                tasks.append(task)
            done, pending = await asyncio.wait({*tasks}, timeout=4)
            if all(x in done for x in tasks):
                market_inputs = []
                for task in tasks:
                    data_from_db: List[PricepointSchema] = task.result()
                    market_data = InputMarketDataSchema(ticks=data_from_db)
                    market_inputs.append(market_data)
                indicators: List[IndicatorSchema] = calculate_indicators(market_inputs)
                signal: SignalSchema = calculate_signal(indicators, source_result.timestamp)
                await out_queue.async_q.put(
                    CalculationSchema(indicators=indicators, signal=signal)
                )
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
        except Exception as e:
            logger.error("Strategy execution failed")
            logger.error(e)
