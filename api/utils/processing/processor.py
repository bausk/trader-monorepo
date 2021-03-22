import logging
from concurrent.futures import CancelledError
from utils.async_primitives import get_event_loop_with_exceptions
from utils.initializators import ptvsd_debugger_init


def _worker_sync(async_worker, q, backtest_session, strategy, db_q):
    from utils.initializators import process_init
    from ticker.timing import backtest_timer, tick_timer

    ptvsd_debugger_init(5681, 3)
    process_init()

    backtest_timer_gen = backtest_timer(backtest_session)
    timer_async_gen = tick_timer(backtest_timer_gen, 0)
    start = backtest_session.start_datetime.timestamp()
    range = backtest_session.end_datetime.timestamp() - start

    async def new_timer_gen(async_gen, q):
        threshold = 0
        async for t in async_gen:
            yield t
            if ((t.timestamp() - start) / range) * 100 > threshold:
                print(f"{threshold}%...")
                await q.coro_put(str(threshold))
                threshold += 5

    timer = new_timer_gen(timer_async_gen, q)

    loop = get_event_loop_with_exceptions(new=True)
    coro = async_worker(timer, backtest_session, strategy, db_q)
    try:
        loop.run_until_complete(coro)
    except CancelledError:
        logging.debug("Cancelled %s: %s", coro, coro.cancelled())
    q.put_nowait(None)


async def start_subprocess_and_listen(async_worker, backtest_session, strategy, db_q=None):
    from concurrent.futures.process import ProcessPoolExecutor
    from utils.processing.async_queue import AsyncProcessQueue

    q = AsyncProcessQueue()

    loop = get_event_loop_with_exceptions()
    print('running in executor')
    loop.run_in_executor(
        ProcessPoolExecutor(max_workers=1),
        _worker_sync,
        async_worker,
        q,
        backtest_session,
        strategy,
        db_q,
    )

    while True:
        result = await q.coro_get()
        if result is None:
            return
        yield result
