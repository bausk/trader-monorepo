import asyncio
from functools import partial

class DataManager:
    def __init__(self):
        self.tasks = {}
        self._data = {
            'kunaio': None,
        }

    async def start_background_tasks(self, app):
        self.tasks['data'] = app.loop.create_task(self._schedule(3, self._retrieve_data, print))
        self.tasks['signal'] = app.loop.create_task(self._schedule(5, self._calculate_signal, print))

    async def cleanup_background_tasks(self, app):
        for _, task in self.tasks.items():
            task.cancel()
            await task

    def setup_tasks(self, app):
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)

    def get_data(self):
        return self._data

    async def _retrieve_data(self):
        await asyncio.sleep(0.1)
        return "ok"

    async def _calculate_signal(self):
        a = {}
        print('producing error in signal')
        print(a['b'])
        return 3

    async def _schedule(self, period, coro, handler, *args, **kwargs):
        errors = []
        while True:
            if errors:
                print(errors)
                errors = []
            future = asyncio.create_task(coro(*args, **kwargs))

            def callback(fut, errors):
                try:
                    result = fut.result()
                    if handler:
                        asyncio.create_task(handler(result))
                except Exception as e:
                    errors.append(e)
                else:
                    pass

            future.add_done_callback(partial(callback, errors=errors))
            await asyncio.sleep(period)
