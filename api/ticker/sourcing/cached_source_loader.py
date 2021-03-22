import asyncio
import logging
from asyncio import Queue

from datetime import datetime
from utils.async_primitives import async_wrap_iter
from dbmodels.session_models import BacktestSessionSchema
from typing import List, AsyncGenerator
from utils.sources.live_sources import AbstractSource
from ticker.sourcing.default_source_loader import default_sources_loader
from utils.processing.async_queue import _ProcQueue
from utils.timescaledb.tsdb_write import (
    stream_write_ticks,
)


logger = logging.getLogger(__name__)


async def cached_source_loader(
    backtest_session: BacktestSessionSchema,
    dataset_name: str,
    pool,
    sources: List[AbstractSource],
    queues: List[Queue],
    session,
    db_q: _ProcQueue,
    tick_timer: AsyncGenerator,
):
    """Cached sources loader wraps default sources loader.
    It checks if session's data is not available in timeseries DB,
    and pre-loads data into timeseries DB if needed. After that,
    is passes control to default_sources_loader which operates normally
    since it calls get_latest and for backtest sources it returns empty list.
    """
    cached_session_id = backtest_session.cached_session_id
    if not cached_session_id:
        print('Starting preloading')
        tasks = []
        for source in sources:
            async_gen = async_wrap_iter(source.get_all_data_gen(
                start_datetime=backtest_session.start_datetime,
                end_datetime=backtest_session.end_datetime,
            ))
            task = asyncio.create_task(
                stream_write_ticks(
                    dataset_name,
                    backtest_session.id,
                    source.config['data_type'],
                    source.config['label'],
                    pool,
                    async_gen,
                )
            )
            tasks.append(task)
        await asyncio.wait({*tasks})
    db_q.put(
        dict(finished_datetime=datetime.now())
    )
    await default_sources_loader(sources, queues, session, tick_timer)
