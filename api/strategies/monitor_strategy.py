from typing import Type
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from parameters.enums import LiveSourcesEnum


async def monitor_strategy_executor(strategy: StrategySchema, in_queue: Queue, out_queue: Queue):
    config = strategy.config_json
    while True:
        tick_result = await in_queue.async_q.get()
        # print(tick_result)
        result = {
            "signals": strategy.id,
            "orders": strategy.id,
            "symbols": strategy.id
        }
        await out_queue.async_q.put(result)
        in_queue.async_q.task_done()
