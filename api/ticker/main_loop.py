import sys, traceback
import asyncio
import aiojobs
from aiojobs._job import Job
from typing import Type, List

from dbmodels.db import db, StrategyModel, StrategySchema, BaseModel


def acquire_executor(strategy: Type[StrategySchema]):
    DEFAULT_STRATEGY_TICK = 8
    strategy_typename = strategy.typename

    async def executor():
        while True:
            await asyncio.sleep(DEFAULT_STRATEGY_TICK)
            print(f"[strategy tick] {strategy_typename}...")
    return executor


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
                job = await self.scheduler.spawn(self.check_strategies(tick_count))
                await asyncio.wait({timer, job.wait()})
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)

    async def check_strategies(self, tick_count):
        active_strategies = {}
        schema: Type[BaseModel] = StrategySchema
        async with db.transaction():
            async for s in StrategyModel.query.where(StrategyModel.is_live == True).order_by(StrategyModel.id).gino.iterate():
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
            self.active_executors[strategy_id] = await self.scheduler.spawn(acquire_executor(strategy)())

    async def stop_executor(self, executor_id: int):
        executor = self.active_executors.get(executor_id)
        if executor.closed:
            print(f'Deleting executor {executor_id}')
            del self.active_executors[executor_id]
        else:
            print(f'Deactivating executor {executor_id}')
            await executor.close()
