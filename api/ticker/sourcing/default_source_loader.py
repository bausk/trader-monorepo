import asyncio
from datetime import timedelta
from parameters.enums import LiveSourcesEnum
from dbmodels.strategy_params_models import LiveParamsSchema
from dbmodels.source_models import ResourceSchema
from utils.sources.live_sources import AbstractSource, LiveCryptowatchSource, LiveKunaSource, LiveCoinbaseSource
from utils.schemas.dataflow_schemas import ProcessTaskSchema


# TODO: Remove dependency on enum in highly variable source entity
LIVE_SOURCES = {
    LiveSourcesEnum.kunaio: LiveKunaSource,
    LiveSourcesEnum.cryptowatch: LiveCoinbaseSource,
}


async def default_resource_loader(resource: ResourceSchema, queues_per_resource, session, is_live=True):
    # TODO: get cycle period from resource config
    sleep_seconds = 8
    primary_source = None
    if resource.primary_live_source_model:
        primary_source: AbstractSource = LIVE_SOURCES.get(resource.primary_live_source_model.typename)(session)
    secondary_source = None
    if resource.secondary_live_source_model:
        secondary_source: AbstractSource = LIVE_SOURCES.get(resource.secondary_live_source_model.typename)(session)

    async def no_result():
        return None

    while True:
        print("[source tick]")
        primary_result = asyncio.create_task(primary_source.get_latest() if primary_source else no_result())
        secondary_result = asyncio.create_task(secondary_source.get_latest() if secondary_source else no_result())
        done, pending = await asyncio.wait({primary_result, secondary_result}, timeout=4)
        if primary_result in done and secondary_result in done:
            try:
                ticks_primary = primary_result.result()
                ticks_secondary = secondary_result.result()
                task = ProcessTaskSchema(
                    ticks_primary=ticks_primary,
                    label_primary=primary_source.label if primary_source else None,
                    ticks_secondary=ticks_secondary,
                    label_secondary=secondary_source.label if secondary_source else None,
                )
                queues = queues_per_resource[resource.id]
                for q in queues:
                    await q.async_q.put(task)
            except Exception as e:
                print('Source fetch failed:')
                print(e)
        else:
            for coro in done:
                coro.cancel()
            for coro in pending:
                coro.cancel()

        # TODO: wrap the above into concurrent wait so that total cycle time doesn't depend on network response time
        await asyncio.sleep(sleep_seconds)
