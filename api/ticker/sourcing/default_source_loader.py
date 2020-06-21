import asyncio
from datetime import timedelta
from parameters.enums import LiveSourcesEnum
from dbmodels.strategy_params_models import LiveParamsSchema
from utils.sources.live_sources import LiveCryptowatchSource, LiveKunaSource
from utils.schemas.dataflow_schemas import ProcessTaskSchema


LIVE_SOURCES = {
    LiveSourcesEnum.kunaio: LiveKunaSource,
    LiveSourcesEnum.cryptowatch: LiveCryptowatchSource,
}


async def default_source_loader(config: LiveParamsSchema, strategy, source_queue, session):
    primary_source = LIVE_SOURCES.get(config.source_primary)(
        session=session,
        config=dict(
            currency="btcusd",
            limit=100,
            after=timedelta(minutes=2)
        )
    )
    secondary_source = LIVE_SOURCES.get(config.source_secondary)(
        session=session,
        config=dict(currency="btcuah")
    )
    sleep_seconds = config.tick_frequency
    while True:
        print(f"[source tick] for {strategy.id}...")
        primary_result = asyncio.create_task(primary_source.get_latest())
        secondary_result = asyncio.create_task(secondary_source.get_latest())
        done, pending = await asyncio.wait({primary_result, secondary_result}, timeout=4)
        if primary_result in done and secondary_result in done:
            result = {}
            for key, coro in [('primary_ticks', primary_result), ('secondary_ticks', secondary_result)]:
                try:
                    result[key] = coro.result()
                except Exception:
                    print('Source fetch failed!')
            if len(result) == len(done):
                task = ProcessTaskSchema(ticks=result)
                await source_queue.async_q.put(task)
        else:
            for coro in done:
                coro.cancel()
            for coro in pending:
                coro.cancel()
        await asyncio.sleep(sleep_seconds)
