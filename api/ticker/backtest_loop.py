import asyncio
from utils.profiling.queues import MeteredQueue
from strategies.monitor_strategy import (
    default_strategy_data_fetcher,
    default_strategy_executor,
)
from ticker.processing.default_postprocessor import cached_postprocessor
from dbmodels.strategy_models import StrategySchema
from dbmodels.session_models import BacktestSessionSchema
from parameters.enums import BacktestTypesEnum, SessionDatasetNames
import aiohttp
from asyncio import Queue
from utils.processing.async_queue import AsyncProcessQueue, _ProcQueue
from utils.profiling.timer import Timer


async def backtest(
    timer,
    backtest_session: BacktestSessionSchema,
    strategy: StrategySchema,
    db_queue: _ProcQueue = None,
) -> None:
    from utils.timescaledb.tsdb_manage import get_pool
    from utils.sources.select import select_backtest_sources
    from ticker.sourcing.cached_source_loader import cached_source_loader

    timeseries_connection_pool = await get_pool()
    session = aiohttp.ClientSession()
    sources = select_backtest_sources(backtest_session)

    queue_manager = MeteredQueue()

    source_q = queue_manager(Queue(1000))
    dataset_name = (
        SessionDatasetNames.test
        if backtest_session.backtest_type == BacktestTypesEnum.test
        else SessionDatasetNames.backtest
    )

    source_session_id = backtest_session.cached_session_id or backtest_session.id
    strategy_fetch_q = queue_manager(AsyncProcessQueue(1000))
    processing_queues = [queue_manager(AsyncProcessQueue(200)) for i in range(8)]

    source_loader = cached_source_loader(
        backtest_session,
        dataset_name,
        timeseries_connection_pool,
        sources,
        [source_q],
        session,
        db_queue,
        timer,
    )

    strategy_data_fetcher = default_strategy_data_fetcher(
        dataset_name,
        timeseries_connection_pool,
        source_session_id,
        source_q,
        strategy_fetch_q,
    )
    strategy_executor = default_strategy_executor(strategy_fetch_q, processing_queues)
    postprocessors = [
        cached_postprocessor(
            dataset_name,
            timeseries_connection_pool,
            backtest_session.id,
            q,
        )
        for q in processing_queues
    ]

    coros = [
        source_loader,
        # TODO: execute actual strategy instead of monitor strategy
        strategy_data_fetcher,
        strategy_executor,
        *postprocessors,
    ]
    tasks = [asyncio.create_task(x) for x in coros]
    timer = Timer('Backtest Loop')
    print("============STARTING BACKTEST SESSION=============")
    timer.start()
    try:
        sentinel_coro = queue_manager.start()
        await asyncio.wait({*tasks})
    except Exception as e:
        print(e)
    await session.close()
    print("============FINISHED BACKTEST SESSION=============")
    timer.stop()
    sentinel_coro.cancel()
