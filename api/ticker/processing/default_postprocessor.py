from utils.schemas.dataflow_schemas import ProcessTaskSchema
from utils.timeseries.timescale_utils import write_ticks


async def default_postprocessor(config, process_queue):

    while True:
        task: ProcessTaskSchema = await process_queue.async_q.get()
        if 'primary' in task.ticks:
            print('---')
            print(task.ticks['primary'])
            print(config)
            await write_ticks('livewater', task.ticks['primary'])
        process_queue.async_q.task_done()
