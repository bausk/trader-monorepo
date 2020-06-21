from dbmodels.strategy_models import StrategySchema
from utils.schemas.dataflow_schemas import ProcessTaskSchema
from utils.timeseries.timescale_utils import write_ticks


async def default_postprocessor(pool, strategy: StrategySchema, config, process_queue):
    session_id = strategy.live_session_id
    if not session_id:
        raise Exception("Data integrity loss: no session ID available during postprocessor start")
    while True:
        task: ProcessTaskSchema = await process_queue.async_q.get()
        for ticks_key, ticks in task.ticks.items():
            print(f'---writing {ticks_key}---')
            await write_ticks('livewater', session_id, ticks_key, ticks, pool)
        process_queue.async_q.task_done()
