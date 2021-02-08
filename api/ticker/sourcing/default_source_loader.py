import asyncio
import logging
from datetime import datetime
from dbmodels.source_models import ResourceSchema
from utils.sources.live_sources import AbstractSource
from utils.sources.select import LIVE_SOURCES
from utils.schemas.dataflow_schemas import SourceFetchResultSchema


logger = logging.getLogger(__name__)


async def default_resource_loader(
    resource: ResourceSchema, queues_per_resource, session, is_live=True
):
    # TODO: get cycle period from resource config
    sleep_seconds = 8
    primary_source = None
    if resource.primary_live_source_model:
        primary_source: AbstractSource = LIVE_SOURCES.get(
            resource.primary_live_source_model.typename
        )(session)
    secondary_source = None
    if resource.secondary_live_source_model:
        secondary_source: AbstractSource = LIVE_SOURCES.get(
            resource.secondary_live_source_model.typename
        )(session)

    async def no_result():
        return None

    while True:
        logger.info("[source tick]")
        primary_result = asyncio.create_task(
            primary_source.get_latest() if primary_source else no_result()
        )
        secondary_result = asyncio.create_task(
            secondary_source.get_latest() if secondary_source else no_result()
        )
        done, pending = await asyncio.wait(
            {primary_result, secondary_result}, timeout=4
        )
        if primary_result in done and secondary_result in done:
            try:
                ticks_primary = primary_result.result()
                ticks_secondary = secondary_result.result()
                task = SourceFetchResultSchema(
                    ticks_primary=ticks_primary,
                    label_primary=primary_source.label if primary_source else None,
                    ticks_secondary=ticks_secondary,
                    label_secondary=secondary_source.label
                    if secondary_source
                    else None,
                    timestamp=datetime.now(),
                )
                queues = queues_per_resource[resource.id]
                for q in queues:
                    await q.async_q.put(task)
            except Exception as e:
                logger.info("Source fetch raised an exception")
                logger.info(e)
        else:
            for coro in done:
                coro.cancel()
            for coro in pending:
                coro.cancel()

        # TODO: wrap the above into concurrent wait so that total cycle time doesn't depend on network response time
        await asyncio.sleep(sleep_seconds)
