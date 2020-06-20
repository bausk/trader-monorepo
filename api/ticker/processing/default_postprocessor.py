from utils.timeseries.timescale_utils import init_db


async def default_postprocessor(config, process_queue):
    await init_db('livewater')
    while True:
        task = await process_queue.async_q.get()
        print("[result tick] executing result:")
        print(task)
        print("============")
        print(config)
        process_queue.async_q.task_done()
