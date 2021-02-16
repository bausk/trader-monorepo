import asyncio
from time import sleep
from multiprocessing import Manager, cpu_count
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def AsyncProcessQueue(maxsize=0):
    m = Manager()
    q = m.Queue(maxsize=maxsize)
    return _ProcQueue(q)


class _ProcQueue(object):
    def __init__(self, q):
        self._queue = q
        self._real_executor = None
        self._cancelled_join = False

    @property
    def _executor(self):
        if not self._real_executor:
            self._real_executor = ThreadPoolExecutor(max_workers=cpu_count())
        return self._real_executor

    def __getstate__(self):
        self_dict = self.__dict__
        self_dict["_real_executor"] = None
        return self_dict

    def __getattr__(self, name):
        if name in [
            "qsize",
            "empty",
            "full",
            "put",
            "put_nowait",
            "get",
            "get_nowait",
            "close",
        ]:
            return getattr(self._queue, name)
        else:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (self.__class__.__name__, name)
            )

    async def coro_put(self, item):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.put, item)

    async def coro_get(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.get)

    def cancel_join_thread(self):
        self._cancelled_join = True
        self._queue.cancel_join_thread()

    def join_thread(self):
        self._queue.join_thread()
        if self._real_executor and not self._cancelled_join:
            self._real_executor.shutdown()


async def _do_coro_proc_work(q, stuff, stuff2):
    ok = stuff + stuff2
    print("Passing %s to parent" % ok)
    await q.coro_put(ok)  # Non-blocking
    print("Process is blocking...")
    sleep(5)
    print("...Process is unblocked")
    print("Process is blocking on queue.get...")
    item = q.get()  # Can be used with the normal blocking API, too
    print("got %s back from parent" % item)
    print("Process is blocking...")
    sleep(5)
    print("...Process is unblocked")


def do_coro_proc_work(q, stuff, stuff2):
    _loop = asyncio.new_event_loop()
    _loop.run_until_complete(_do_coro_proc_work(q, stuff, stuff2))


async def sentinel():
    x = 5
    while x > 0:
        await asyncio.sleep(3)
        print(f"({x}) event loop is not blocked")
        x -= 1


async def do_work(q):
    loop.run_in_executor(ProcessPoolExecutor(max_workers=1), do_coro_proc_work, q, 1, 2)
    done, pending = await asyncio.wait(
        {asyncio.create_task(q.coro_get()), asyncio.create_task(sentinel())}
    )
    print("Got from worker")
    print(done, pending)
    q.put(25)


if __name__ == "__main__":
    q = AsyncProcessQueue()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_work(q))
