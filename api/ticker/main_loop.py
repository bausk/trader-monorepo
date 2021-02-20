import sys
from ticker.timing import live_timer, tick_timer
from ticker.processing.process_ticks import write_ticks_to_session_store
import traceback
import asyncio
import aiojobs
from aiojobs._job import Job
from janus import Queue

from dbmodels.db import db, StrategyModel
from dbmodels.strategy_models import StrategySchema
from dbmodels.source_models import ResourceModel, ResourceSchema, Source
from parameters.enums import SessionDatasetNames, StrategiesEnum
from strategies.monitor_strategy import monitor_strategy_executor
from utils.timescaledb.tsdb_manage import get_pool
from utils.sources.select import select_live_sources

from ticker.processing.default_postprocessor import default_postprocessor
from ticker.sourcing.default_source_loader import default_sources_loader

STRATEGY_EXECUTORS = {
    StrategiesEnum.monitor: monitor_strategy_executor,
}


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
        self.active_schedulers = {}
        self.resource_schedulers = {}
        self.strategy_queues = {}
        self.ticks_awaiting_processing_queues = {}
        self.queues_per_resource = {}

    async def run(self, app):
        self.app = app
        await self.start_ticker()

    async def start_ticker(self):
        print("init DB")
        self.timeseries_connection_pool = await get_pool()
        self.scheduler = await aiojobs.create_scheduler()
        tick_count = 0
        while True:
            tick_count += 1
            try:
                timer = asyncio.create_task(asyncio.sleep(self.BASE_TICK_TIME))
                job: Job = await self.scheduler.spawn(self.check_resources(tick_count))
                await asyncio.wait({timer, job.wait()})
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)

    async def check_resources(self, tick_count):
        active_resources = {}
        primary_live_source = Source.alias()
        secondary_live_source = Source.alias()
        primary_backtest_source = Source.alias()
        secondary_backtest_source = Source.alias()
        async with db.transaction():
            query = (
                ResourceModel.load(
                    strategy=StrategyModel.on(
                        ResourceModel.id == StrategyModel.resource_id
                    )
                )
                .load(
                    primary_live_source_model=primary_live_source.on(
                        primary_live_source.id == ResourceModel.primary_live_source_id
                    )
                )
                .load(
                    secondary_live_source_model=secondary_live_source.on(
                        secondary_live_source.id
                        == ResourceModel.secondary_live_source_id
                    )
                )
                .load(
                    primary_backtest_source_model=primary_backtest_source.on(
                        primary_backtest_source.id
                        == ResourceModel.primary_backtest_source_id
                    )
                )
                .load(
                    secondary_backtest_source_model=secondary_backtest_source.on(
                        secondary_backtest_source.id
                        == ResourceModel.secondary_backtest_source_id
                    )
                )
                .where(StrategyModel.live_session_id.isnot(None))
            )
            resources_list = await query.gino.all()
            resources_hash = {}
            unique_resources = []
            active_strategies = {}
            active_resources = {}
            for resource in resources_list:
                validated = ResourceSchema.from_orm(resource)
                strategy = StrategySchema.from_orm(resource.strategy)
                active_strategies[strategy.id] = strategy
                active_resources[validated.id] = validated
                if validated.id not in resources_hash:
                    resources_hash[validated.id] = [strategy]
                    unique_resources.append(validated)
                else:
                    resources_hash[validated.id].append(strategy)
            inactive_strategies = [
                x for x in self.strategy_queues if x not in active_strategies
            ]
            for x in inactive_strategies:
                print(f"stopping inactive strategy {x}")
                await self.stop_strategy(x)

            schedulers_without_active_strategy = [
                x for x in self.resource_schedulers if x not in active_resources
            ]
            for x in schedulers_without_active_strategy:
                print(f"stopping inactive resource {x}")
                await self.stop_resource(x)

            for _, strategy in active_strategies.items():
                await self.ensure_started_strategy(strategy)

            # Reschedule strategy queues to update data in resources
            for resource_id, strategy_list in resources_hash.items():
                self.queues_per_resource[resource_id] = [
                    self.ticks_awaiting_processing_queues[s.id] for s in strategy_list
                ]

            for _, resource in active_resources.items():
                await self.ensure_started_resource(resource)

    async def stop_strategy(self, x):
        queue = self.strategy_queues[x]
        await queue.async_q.put(None)
        queue = self.ticks_awaiting_processing_queues[x]
        await queue.async_q.put(None)
        del self.strategy_queues[x]
        del self.ticks_awaiting_processing_queues[x]

    async def stop_resource(self, resource_id: int):
        scheduler = self.resource_schedulers[resource_id]
        if scheduler.closed:
            print(f"Deleting scheduler {resource_id}")
            del self.resource_schedulers[resource_id]
        else:
            print(f"Closing scheduler {resource_id}")
            await scheduler.close()

    async def ensure_started_resource(self, resource: ResourceSchema):
        res_id = resource.id
        active_scheduler = self.resource_schedulers.get(res_id)
        if active_scheduler and active_scheduler.closed:
            print(f"Deleting closed executor {res_id}")
            active_scheduler = None
            del self.resource_schedulers[res_id]
        if not active_scheduler:
            print(f"Activating executor {res_id}")
            scheduler: aiojobs.Scheduler = await aiojobs.create_scheduler()
            session = self.app["PERSISTENT_SESSION"]
            sources = select_live_sources(resource=resource)
            queues = self.queues_per_resource[resource.id]
            timer = tick_timer(live_timer(), 8)
            await scheduler.spawn(
                default_sources_loader(sources, queues, session, timer)
            )
            self.resource_schedulers[res_id] = scheduler

    async def ensure_started_strategy(self, strategy: StrategyModel):
        if not self.strategy_queues.get(strategy.id):
            ticks_to_write_q = Queue()
            source_q = Queue()
            processing_q = Queue()
            dataset_name = SessionDatasetNames.live
            await self.scheduler.spawn(
                write_ticks_to_session_store(
                    dataset_name,
                    self.timeseries_connection_pool,
                    strategy.live_session_id,
                    ticks_to_write_q,
                    source_q,
                )
            )
            await self.scheduler.spawn(
                monitor_strategy_executor(
                    dataset_name,
                    self.timeseries_connection_pool,
                    strategy.live_session_id,
                    source_q,
                    processing_q,
                )
            )
            await self.scheduler.spawn(
                default_postprocessor(
                    dataset_name,
                    self.timeseries_connection_pool,
                    strategy.live_session_id,
                    processing_q,
                )
            )
            self.strategy_queues[strategy.id] = source_q
            self.ticks_awaiting_processing_queues[strategy.id] = ticks_to_write_q
