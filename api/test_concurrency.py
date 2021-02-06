import asyncio
import concurrent.futures
from time import sleep
from janus import Queue


async def test_concurrency():
    # Database init from scratch

    iterations = 10

    # Feed and write
    async def produce_data(q):
        nonlocal iterations
        print("starting producing")
        for raw_data in range(iterations):
            await q.put(raw_data)
        print("finishing feeding data")
        return None

    def consume_data(q, i):
        print(f"{i} init")
        try:
            for datapoint in iter(q.get, None):
                print(f"{i} cycle")
                # Do some work
                sleep(1)
                q.task_done()
        except Exception as e:
            print("error is:")
            print(e)
            print("consumer exiting on error")
            raise
        print(f"{i} producer exit")

    loop = asyncio.get_running_loop()
    q = Queue(50000)
    producer = asyncio.create_task(produce_data(q.async_q))
    executor = concurrent.futures.ThreadPoolExecutor()
    # consumers = [loop.run_in_executor(executor, consume_data, q.sync_q, x) for x in range(20)]
    consumers = [
        loop.run_in_executor(executor, consume_data, q.sync_q, x) for x in range(20)
    ]

    await asyncio.wait({producer})
    print("---- done producing")
    for _ in consumers:
        await q.async_q.put(None)
    await asyncio.wait({*consumers})
    for c in consumers:
        print("canceling")
        c.cancel()

    print("---- done consuming")


def main():
    asyncio.get_event_loop().run_until_complete(test_concurrency())


if __name__ == "__main__":
    main()
