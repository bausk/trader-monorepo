import asyncio
from datetime import datetime, timedelta


class Source:
    async def get_latest(self, dt=None):
        print("ME:")
        await asyncio.sleep(2)
        print(dt)
        raise Exception("Exception")


sources = [Source(), Source()]
current_datetime = datetime.now()


async def worker():
    result_tasks = [
        asyncio.create_task(x.get_latest(current_datetime)) for x in sources
    ]
    print("=====================results")
    print({*result_tasks})
    try:
        results = await asyncio.wait_for(asyncio.gather(*result_tasks), timeout=4)
    except Exception as e:
        print(e)
        results = None
    print("=====================results 2")
    print(results)


asyncio.get_event_loop().run_until_complete(worker())
