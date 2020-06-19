from typing import Generator
import math
from datetime import datetime
import asyncio


def generate_data(start_time: datetime) -> Generator[dict, None, None]:
    initial_price = 10.0
    initial_timestamp = start_time.timestamp()
    time_increment = 0
    skip_points_between = (initial_timestamp + 7 * 60, initial_timestamp + 20 * 60)
    volume = 0.4
    while True:
        price = initial_price + round(math.sin(time_increment / 1000) * 3, 2)
        current_timestamp = initial_timestamp + time_increment
        time_increment += 0.1
        if current_timestamp > skip_points_between[0] and current_timestamp < skip_points_between[1]:
            # print(f"Skipping {datetime.fromtimestamp(current_timestamp)}")
            continue
        raw_point = dict(
            session_id=123,
            timestamp=current_timestamp,
            price=price,
            volume=volume,
            funds=price * volume,
            label="BTCUAH",
            data_type=1
        )
        yield raw_point


async def generate_data_async(start_time: datetime):
    gen = generate_data(start_time)
    while True:
        yield next(gen)
        await asyncio.sleep(0)


def format_int(num):
    m = int(math.log10(num) // 3)
    suffixes = ['', 'k', 'M', 'G', 'T', 'P']
    return f'{num / 1000.0 ** m:.{4}f}{suffixes[m]}'
