import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from traderutils.datatypes.cache import ForwardOnceCache
from traderutils.constants import currencies
from traderutils.sources.historical import CryptowatchSource, KunaIoSource


class DataManager:
    def __init__(self):
        self.tasks = {}
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.loop = asyncio.get_event_loop()
        self.app = None
        self._datasources = {
            'kunaio': KunaIoSource(currency=currencies.BTC),
            'cryptowatch': CryptowatchSource(currency=currencies.BTC)
        }
        self._data = {
            'kunaio': ForwardOnceCache('timestamp'),
            'cryptowatch': ForwardOnceCache('timestamp')
        }

    async def start_background_tasks(self, app):
        self.app = app
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
        for source_name, source in self._datasources.items():
            if source:
                future = self.loop.run_in_executor(self.pool, source.fetch_latest_trades)

                def callback(fut):
                    try:
                        result = fut.result()
                        current_cache = self._data[source_name]
                        current_cache.put(result)
                    except Exception as e:
                        print(e)
                    else:
                        pass

                future.add_done_callback(callback)
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
                        possible_future = handler(result)
                        if asyncio.iscoroutine(possible_future):
                            asyncio.create_task(possible_future)
                except Exception as e:
                    errors.append(e)
                else:
                    pass

            future.add_done_callback(partial(callback, errors=errors))
            await asyncio.sleep(period)
