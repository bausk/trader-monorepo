import asyncio
import logging
import signal
import threading


def async_wrap_iter(it):
    """Wrap blocking iterator into an asynchronous one"""
    print('urr')
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)
    exception = None
    _END = object()

    print('urr2')

    async def yield_queue_items():
        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def iter_to_queue():
        nonlocal exception
        try:
            for item in it:
                # This runs outside the event loop thread, so we
                # must use thread-safe API to talk to the queue.
                asyncio.run_coroutine_threadsafe(q.put(item), loop).result()
        except Exception as e:
            exception = e
        finally:
            asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

    threading.Thread(target=iter_to_queue).start()
    print('urr3')
    return yield_queue_items()


async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logging.info(f'Received exit signal {signal.name}...')
    logging.info('Closing database connections')


def get_event_loop_with_exceptions(name='default', handler=None, new=False):

    def default_exception_handler(loop, context):
        msg = context.get('exception', context['message'])
        logging.error(f'[{name}] Caught exception: {msg}')
        print(f'[{name}] Caught exception: {msg}')
        logging.info(f'[{name}] Shutting down...')
        asyncio.create_task(shutdown(loop))

    if handler is None:
        handler = default_exception_handler

    if new:
        loop = asyncio.new_event_loop()
    else:
        loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s)))
    loop.set_exception_handler(handler)

    return loop
