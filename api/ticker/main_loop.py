import sys, traceback
import asyncio
import aiojobs
from aiojobs._job import Job
from janus import Queue
from typing import Type, List

from dbmodels.db import db, StrategyModel, BaseModel
from dbmodels.strategy_models import StrategySchema
from dbmodels.strategy_params_models import LiveParamsSchema
from parameters.enums import StrategiesEnum, LiveSourcesEnum
from strategies.monitor_strategy import monitor_strategy_executor
from utils.sources.live_sources import LiveCryptowatchSource, LiveKunaSource


STRATEGY_EXECUTORS = {
    StrategiesEnum.monitor: monitor_strategy_executor,
}

LIVE_SOURCES = {
    LiveSourcesEnum.kunaio: LiveKunaSource,
    LiveSourcesEnum.cryptowatch: LiveCryptowatchSource,
}


async def acquire_executor(strategy: Type[StrategySchema], app):
    config: LiveParamsSchema = strategy.config_json
    DEFAULT_STRATEGY_TICK = 8
    strategy_typename = strategy.typename
    config.strategy_name = StrategiesEnum.monitor
    config.source_primary = LiveSourcesEnum.cryptowatch
    config.source_secondary = LiveSourcesEnum.kunaio
    strategy_tick_func = STRATEGY_EXECUTORS.get(config.strategy_name)
    if strategy_tick_func is None:
        return MockExecutor()

    session = app['PERSISTENT_SESSION']
    strategy_scheduler = await aiojobs.create_scheduler()
    source_queue = Queue()
    signal_queue = Queue()

    async def source_executor(config, source_queue, session):
        primary_source = LIVE_SOURCES.get(config.source_primary)
        secondary_source = LIVE_SOURCES.get(config.source_secondary)
        while True:
            print(f"[source tick] for {strategy.id}...")
            primary_result = asyncio.create_task(primary_source.get_latest())
            secondary_result = asyncio.create_task(secondary_source.get_latest())
            done, pending = await asyncio.wait({primary_result, secondary_result}, timeout=4)
            if primary_result in done and secondary_result in done:
                result = []
                for coro in [primary_result, secondary_result]:
                    try:
                        result.append(coro.result())
                    except Exception:
                        print('Source fetch failed!')
                if len(result) == len(done):
                    await source_queue.async_q.put(result)
            else:
                for coro in done:
                    coro.cancel()
                for coro in pending:
                    coro.cancel()
            await asyncio.sleep(DEFAULT_STRATEGY_TICK)

    await strategy_scheduler.spawn(source_executor(config, source_queue, session))
    await strategy_scheduler.spawn(strategy_tick_func(strategy, source_queue, signal_queue))

    async def order_executor(config, signal_queue):
        while True:
            task = await signal_queue.async_q.get()
            print(f"[result tick] executing result for {task}")
            signal_queue.async_q.task_done()
    await strategy_scheduler.spawn(order_executor(config, signal_queue))

    return strategy_scheduler


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
            async for s in StrategyModel.query.where(StrategyModel.live_session_id.isnot(None)).order_by(StrategyModel.id).gino.iterate():
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
            # strategy_executor = await acquire_executor(strategy)
            self.active_executors[strategy_id] = await acquire_executor(strategy, self.app)
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
