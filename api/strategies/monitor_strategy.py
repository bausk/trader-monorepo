from itertools import count
import logging
import asyncio
from typing import List
from datetime import timedelta
from concurrent.futures.process import ProcessPoolExecutor
from utils.processing.async_queue import _ProcQueue
from utils.profiling.timer import Timer
from utils.async_primitives import get_event_loop_with_exceptions
from asyncio import Queue as AsyncQueue
from janus import Queue
from parameters.enums import SessionDatasetNames
from utils.schemas.dataflow_schemas import (
    CalculationSchema,
    IndicatorSchema,
    SignalSchema,
    SourceFetchResultSchema,
)
from utils.schemas.request_schemas import DataRequestSchema
from utils.schemas.response_schemas import InputMarketDataSchema, PricepointSchema
from utils.timescaledb.tsdb_read import SequentialBatchTSDBFetcher, get_prices
from .monitor_strategy_signal import calculate_indicators, calculate_signal


logger = logging.getLogger(__name__)


async def default_strategy_executor(
    market_data_q: _ProcQueue,
    strategy_results_qs: List[_ProcQueue],
    trading_q: _ProcQueue,
):
    workers = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i, q in enumerate(strategy_results_qs):
            loop = get_event_loop_with_exceptions()
            worker = loop.run_in_executor(
                pool, sync_strategy_worker, market_data_q, q, trading_q, i
            )
            workers.append(worker)
            print("Instantiated worker...")
        await asyncio.wait({*workers})
    print("...Strategy executor done and exiting.")


def sync_strategy_worker(
    market_data_q: _ProcQueue,
    strategy_results_q: _ProcQueue,
    trading_queue: _ProcQueue,
    i: int,
):
    print(f"#{i} started")
    timer = Timer(f"strategy #{i}", report_every=10)
    while True:
        task = market_data_q.get()
        if task is None:
            market_data_q.put(None)
            strategy_results_q.put(None)
            trading_queue.put(None)
            return
        timer.start()
        results = run_arbitrage_strategy(*task)
        timer.stop()
        strategy_results_q.put(results)
        trading_queue.put(results)


def run_arbitrage_strategy(market_inputs, timestamp, increasing_id):
    indicators: List[IndicatorSchema] = calculate_indicators(market_inputs)
    signal: SignalSchema = calculate_signal(indicators, timestamp)
    return CalculationSchema(
        indicators=indicators,
        signal=signal,
        increasing_id=increasing_id,
        market_inputs=market_inputs,
    )


async def default_strategy_data_fetcher(
    dataset_name: SessionDatasetNames,
    tsdb_pool,
    session_id: int,
    in_queue: AsyncQueue,
    out_queue: _ProcQueue,
):
    print(f"Session ID: {session_id}")

    timer_f = Timer("Fetch")
    timer_w = Timer("Wait_In")
    fetcher = SequentialBatchTSDBFetcher(
        pool=tsdb_pool,
        dataset_name=dataset_name,
        session_id=session_id,
    )
    monotonous_counter = count()
    while True:
        timer_w.start()
        source_result: SourceFetchResultSchema = await in_queue.get()
        timer_w.stop()
        if source_result is None:
            await out_queue.coro_put(None)
            await in_queue.put(None)
            print("strategy fetcher exit")
            return
        timer_f.start()
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
                    session_id=session_id,
                )
                task = asyncio.create_task(fetcher.get_prices(params))
                tasks.append(task)
            done, pending = await asyncio.wait({*tasks}, timeout=20)
            if all(x in done for x in tasks):
                market_inputs = []
                for task in tasks:
                    data_from_db: List[PricepointSchema] = task.result()
                    market_data = InputMarketDataSchema(ticks=data_from_db)
                    market_inputs.append(market_data)

                result = (
                    market_inputs,
                    source_result.timestamp,
                    next(monotonous_counter),
                )
                await out_queue.coro_put(result)
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
        except Exception as e:
            logger.error("Strategy execution failed")
            logger.error(e)
        in_queue.task_done()
        timer_f.stop()


async def monitor_strategy_executor(
    dataset_name: SessionDatasetNames,
    tsdb_pool,
    session_id: int,
    in_queue: Queue,
    out_queue: Queue,
) -> None:
    print(f"Session ID: {session_id}")
    while True:
        source_result: SourceFetchResultSchema = await in_queue.async_q.get()
        # TODO: # 1. Error management
        # 2. Refactor strategy executor: make tools to get data without cruft
        # 4. Maybe: chain/parallel strategies?

        if source_result is None:
            await out_queue.async_q.put(None)
            await in_queue.async_q.put(None)
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
                    session_id=session_id,
                )
                task = asyncio.create_task(
                    get_prices(dataset_name, session_id, params, tsdb_pool)
                )
                tasks.append(task)
            done, pending = await asyncio.wait({*tasks}, timeout=4)
            if all(x in done for x in tasks):
                market_inputs: List[InputMarketDataSchema] = []
                for task in tasks:
                    data_from_db: List[PricepointSchema] = task.result()
                    market_data = InputMarketDataSchema(ticks=data_from_db)
                    market_inputs.append(market_data)
                indicators: List[IndicatorSchema] = calculate_indicators(market_inputs)
                signal: SignalSchema = calculate_signal(
                    indicators, source_result.timestamp
                )

                await out_queue.async_q.put(
                    CalculationSchema(
                        indicators=indicators,
                        signal=signal,
                        market_inputs=market_inputs,
                    )
                )
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
        except Exception as e:
            logger.error("Strategy execution failed")
            logger.error(e)
        in_queue.async_q.task_done()
