import sys, traceback
import asyncio
import aiojobs
from aiojobs._job import Job
from janus import Queue
from typing import Type

from dbmodels.db import db, StrategyModel, BaseModel, LiveSessionModel
from dbmodels.strategy_models import StrategySchema
from dbmodels.strategy_params_models import LiveParamsSchema
from parameters.enums import StrategiesEnum, LiveSourcesEnum
from strategies.monitor_strategy import monitor_strategy_executor
from utils.timeseries.timescale_utils import init_db, get_pool
from .processing.default_postprocessor import default_postprocessor
from .sourcing.default_source_loader import default_source_loader


STRATEGY_EXECUTORS = {
    StrategiesEnum.monitor: monitor_strategy_executor,
}

DEFAULT_STRATEGY_TICK = 8


async def acquire_executor(strategy: Type[StrategySchema], app, pool):
    config: LiveParamsSchema = strategy.config_json
    # TODO: Use strategy typename and/or something else to customize execution
    # strategy_typename = strategy.typename
    config.strategy_name = StrategiesEnum.monitor
    config.source_primary = LiveSourcesEnum.cryptowatch
    config.source_secondary = LiveSourcesEnum.kunaio
    config.tick_frequency = DEFAULT_STRATEGY_TICK
    strategy_ontick_function = STRATEGY_EXECUTORS.get(config.strategy_name)
    if strategy_ontick_function is None:
        return MockExecutor()

    scheduler = await aiojobs.create_scheduler()
    source_queue = Queue()
    processing_queue = Queue()

    session = app['PERSISTENT_SESSION']
    await scheduler.spawn(default_source_loader(config, strategy, source_queue, session))
    await scheduler.spawn(strategy_ontick_function(strategy, source_queue, processing_queue))
    await scheduler.spawn(default_postprocessor(pool, strategy, config, processing_queue))

    return scheduler


class MockExecutor:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


class Ticker:
    BASE_TICK_TIME = 5

    def __init__(self):
        self.app = None
        self.scheduler = None
        self.active_executors = {}

    async def run(self, app):
        self.app = app
        await self.start_ticker()

    async def start_ticker(self):
        print('init DB')
        self.timeseries_connection_pool = await get_pool('livewater')
        self.scheduler = await aiojobs.create_scheduler()
        tick_count = 0
        while True:
            tick_count += 1
            try:
                timer = asyncio.create_task(asyncio.sleep(self.BASE_TICK_TIME))
                job: Job = await self.scheduler.spawn(self.check_strategies(tick_count))
                await asyncio.wait({timer, job.wait()})
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)

    async def check_strategies(self, tick_count):
        active_strategies = {}
        schema: Type[BaseModel] = StrategySchema
        async with db.transaction():
            async for s in StrategyModel.load(
                live_session_model=LiveSessionModel
            ).query.where(StrategyModel.live_session_id.isnot(None)).order_by(StrategyModel.id).gino.iterate():
                validated = schema.from_orm(s)
                active_strategies[validated.id] = validated
        # Stop removed or inactive strategies
        executor_ids_to_stop = [x for x in self.active_executors if x not in active_strategies]
        for executor_id in executor_ids_to_stop:
            await self.stop_executor(executor_id)

        # Ensure all active strategies have running executors
        for strategy_id, strategy in active_strategies.items():
            await self.start_strategy(strategy)

    async def start_strategy(self, strategy: Type[StrategySchema]):
        strategy_id = strategy.id
        active_executor = self.active_executors.get(strategy_id)
        if active_executor and active_executor.closed:
            print(f'Deleting closed executor {strategy_id}')
            active_executor = None
            del self.active_executors[strategy_id]
        if not active_executor:
            print(f'Activating executor {strategy_id}')
            # TODO: remove cruft
            # strategy_executor = await acquire_executor(strategy)
            self.active_executors[strategy_id] = await acquire_executor(
                strategy,
                self.app,
                self.timeseries_connection_pool
            )
            # if strategy_executor:
            #     self.active_executors[strategy_id]: Job = await self.scheduler.spawn(strategy_executor(self.app))
            # else:
            #     self.active_executors[strategy_id] = MockExecutorJob()

    async def stop_executor(self, executor_id: int):
        executor = self.active_executors.get(executor_id)
        if executor.closed:
            print(f'Deleting executor {executor_id}')
            del self.active_executors[executor_id]
        else:
            print(f'Deactivating executor {executor_id}')
            await executor.close()
