from typing import Type
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from utils.sources.live_sources import select_live_source
from utils.sources.abstract_source import AbstractSource
from parameters.enums import LiveSourcesEnum


async def monitor_strategy_executor(strategy: StrategySchema, in_queue: Queue, out_queue: Queue):
    config = strategy.config_json
    while True:
        tick_result = await in_queue.get()
        result = {
            "signals": None,
            "orders": None,
            "symbols": None
        }
        await out_queue.put(result)
        tick_result.task_done()
