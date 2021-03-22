import asyncio
from datetime import datetime, timedelta


def live_timer():
    while True:
        yield datetime.now()


def backtest_timer(backtest_session):
    assert isinstance(backtest_session.start_datetime, datetime)
    assert isinstance(backtest_session.end_datetime, datetime)
    assert isinstance(backtest_session.config_json["tick_duration_seconds"], int)

    current_datetime = backtest_session.start_datetime
    increment = timedelta(seconds=backtest_session.config_json["tick_duration_seconds"])
    while True:
        yield current_datetime
        current_datetime += increment
        if current_datetime > backtest_session.end_datetime:
            break


async def tick_timer(timer_gen, sleep_seconds):
    """Async generator that issues datetime from timer_gen every sleep_seconds"""
    for tick in timer_gen:
        yield tick
        # TODO: Figure out whether this influences productivity
        # await asyncio.sleep(sleep_seconds)
