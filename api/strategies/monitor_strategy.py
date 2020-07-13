from typing import Type
from janus import Queue
from dbmodels.strategy_models import StrategySchema
from parameters.enums import LiveSourcesEnum
from utils.schemas.dataflow_schemas import ProcessTaskSchema


async def monitor_strategy_executor(strategy: StrategySchema, in_queue: Queue, out_queue: Queue) -> None:
    while True:
        result: ProcessTaskSchema = await in_queue.async_q.get()
        await out_queue.async_q.put(result)
        in_queue.async_q.task_done()
        if result is None:
            return
