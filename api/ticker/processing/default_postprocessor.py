
async def default_postprocessor(config, process_queue):
    while True:
        task = await process_queue.async_q.get()
        print("[result tick] executing result:")
        print(task)
        print("============")
        print(config)
        process_queue.async_q.task_done()
