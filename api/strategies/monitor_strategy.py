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
from utils.timescaledb.tsdb_read import get_prices
from .monitor_strategy_signal import calculate_indicators, calculate_signal


logger = logging.getLogger(__name__)


async def default_strategy_executor(
    market_data_q: _ProcQueue, strategy_results_qs: List[_ProcQueue]
):
    workers = []
    with ProcessPoolExecutor(max_workers=8) as pool:
        for i, q in enumerate(strategy_results_qs):
            loop = get_event_loop_with_exceptions()
            worker = loop.run_in_executor(
                pool, sync_strategy_worker, market_data_q, q, i
            )
            workers.append(worker)
            print("Instantiated worker...")
        await asyncio.wait({*workers})
    print("...Strategy executor done and exiting.")


def sync_strategy_worker(
    market_data_q: _ProcQueue, strategy_results_q: _ProcQueue, i: int
):
    print(f"#{i} started")
    timer = Timer(f'strategy #{i}', report_every=10)
    while True:
        task = market_data_q.get()
        if task is None:
            market_data_q.put(None)
            strategy_results_q.put(None)
            return
        timer.start()
        results = run_arbitrage_strategy(*task)
        timer.stop()
        strategy_results_q.put(results)


def run_arbitrage_strategy(market_inputs, timestamp):
    indicators: List[IndicatorSchema] = calculate_indicators(market_inputs)
    signal: SignalSchema = calculate_signal(indicators, timestamp)
    return CalculationSchema(indicators=indicators, signal=signal)


async def fetcher(ts, tasks, q, params):
    params['counter'] += 1
    done, pending = await asyncio.wait({*tasks}, timeout=4)
    if all(x in done for x in tasks):
        market_inputs = []
        for task in tasks:
            data_from_db: List[PricepointSchema] = task.result()
            market_data = InputMarketDataSchema(ticks=data_from_db)
            market_inputs.append(market_data)
        result = (market_inputs, ts)
        await q.coro_put(result)
    else:
        for coro in done:
            coro.cancel()
        for coro in pending:
            coro.cancel()
    params['counter'] -= 1


async def default_strategy_data_fetcher(
    dataset_name: SessionDatasetNames,
    tsdb_pool,
    session_id: int,
    in_queue: AsyncQueue,
    out_queue: _ProcQueue,
):
    print(f"Session ID: {session_id}")
    prms = {'counter': 0}

    async def backpressure(q):
        while True:
            if prms['counter'] < 20:
                return True
            await asyncio.sleep(0)

    timer_f = Timer('Fetch')
    timer_w = Timer('Wait_In')
    timer_b = Timer('Backpressure')
    while True:
        timer_b.start()
        await backpressure(out_queue)
        timer_b.stop()
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
                task = asyncio.create_task(
                    get_prices(dataset_name, session_id, params, tsdb_pool)
                )
                tasks.append(task)
            asyncio.create_task(fetcher(source_result.timestamp, tasks, out_queue, prms))
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
                market_inputs = []
                for task in tasks:
                    data_from_db: List[PricepointSchema] = task.result()
                    market_data = InputMarketDataSchema(ticks=data_from_db)
                    market_inputs.append(market_data)
                indicators: List[IndicatorSchema] = calculate_indicators(market_inputs)
                signal: SignalSchema = calculate_signal(
                    indicators, source_result.timestamp
                )

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
        in_queue.async_q.task_done()
