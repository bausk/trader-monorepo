from typing import List
import logging
import asyncio
from datetime import datetime, timedelta
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import (
    CalculationSchema,
    IndicatorSchema,
    SignalSchema,
    SourceFetchResultSchema,
)
from utils.schemas.request_schemas import DataRequestSchema
from utils.schemas.response_schemas import InputMarketDataSchema, PricepointSchema
from utils.timeseries.constants import DATA_TYPES
from utils.timescaledb.tsdb_read import get_prices
from .monitor_strategy_signal import calculate_indicators, calculate_signal


logger = logging.getLogger(__name__)


async def monitor_strategy_executor(
    pool, strategy: StrategySchema, in_queue: Queue, out_queue: Queue
) -> None:
    while True:
        source_result: SourceFetchResultSchema = await in_queue.async_q.get()
        indicators = signal = None
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
                label=source_result.label_primary,
                data_type=DATA_TYPES.ticks_primary,
            )
            secondary_params = DataRequestSchema(
                from_datetime=from_datetime,
                period=1,
                label=source_result.label_secondary,
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
                primary_market_data = InputMarketDataSchema(ticks=primary_data)
                secondary_market_data = InputMarketDataSchema(ticks=secondary_data)
                indicators: List[IndicatorSchema] = calculate_indicators(
                    [
                        primary_market_data,
                        secondary_market_data,
                    ]
                )
                signal: SignalSchema = calculate_signal(indicators)
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
        except Exception as e:
            logger.error("Strategy execution failed")
            logger.error(e)
        await out_queue.async_q.put(
            CalculationSchema(indicators=indicators, signal=signal)
        )
        in_queue.async_q.task_done()
        if source_result is None:
            return
