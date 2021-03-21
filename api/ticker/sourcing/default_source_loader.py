import asyncio
import logging
from typing import List, AsyncGenerator
from utils.timeseries.constants import DATA_TYPES
from utils.sources.live_sources import AbstractSource
from utils.schemas.dataflow_schemas import SourceFetchResultSchema, SourceFetchSchema


logger = logging.getLogger(__name__)


async def default_sources_loader(
    sources: List[AbstractSource],
    queues,
    session,
    tick_timer: AsyncGenerator,
):
    """Default sources loader consumes an async tick timer generator.
    In its cycle, it calls get_latest on a list of sources
    and produces the resulting lists of ticks into queues to be consumed by strategies and/or postprocessors.
    Sources loader can terminate in two possible ways:
    -- on generator exhaustion (when running a backtest), or
    -- when it is closed externally by a scheduler (when running live).
    """

    for source in sources:
        source.session = session

    async for current_datetime in tick_timer:
        result_tasks = [
            asyncio.create_task(x.get_latest(current_datetime)) for x in sources
        ]
        results = await asyncio.wait_for(asyncio.gather(*result_tasks), timeout=4)

        # TODO: This is redundant and should be specified in source config
        data_types = [DATA_TYPES.ticks_primary, DATA_TYPES.ticks_secondary]
        # TODO: reimplement this with proper exception handling
        # Only generate ticks if all sources succeeded
        # if all(x in done for x in result_tasks):
        try:
            ticks_results: List[SourceFetchSchema] = []
            for result, source, data_type in zip(results, sources, data_types):
                source_label = source.config.get(
                    "label", getattr(source, "label", None)
                )
                assert source_label is not None
                ticks_result = SourceFetchSchema(
                    ticks=result,
                    label=source_label,
                    data_type=data_type,
                )
                ticks_results.append(ticks_result)
            fetch_result = SourceFetchResultSchema(
                ticks=ticks_results,
                timestamp=current_datetime,
            )
            for q in queues:
                await q.async_q.put(fetch_result)
        except Exception as e:
            logger.info("Source fetch raised an exception")
            logger.info(e)
    print("sources loader: exit")
    for q in queues:
        await q.async_q.put(None)
