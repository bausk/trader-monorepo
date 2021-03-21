from typing import List
from datetime import datetime, timedelta
from utils.schemas.dataflow_schemas import TickSchema
from ..abstract_source import AbstractSource


PRIMARY_DATA = {
    "phase1": (5000.0, 12.0),
    "phase2": (5200.0, 22.0),
    "phase3": (5100.0, 11.0),
}

GENERATION_START = datetime(2020, 1, 1, 0, 0, 0)
PRIMARY_SURGE_START = GENERATION_START + timedelta(hours=2)
PRIMARY_SURGE_END = PRIMARY_SURGE_START + timedelta(minutes=20)
GENERATION_END = PRIMARY_SURGE_END + timedelta(hours=1)

SECONDARY_DATA = {
    "phase1": (140000.0, 4.0),
    "phase2": (145000.0, 7.0),
    "phase3": (143000.0, 3.0),
}

SECONDARY_SURGE_START = PRIMARY_SURGE_START + timedelta(minutes=1)
SECONDARY_SURGE_END = PRIMARY_SURGE_END + timedelta(minutes=2)


def derive_primary_tick(timepoint):
    data = None
    if timepoint < PRIMARY_SURGE_START:
        data = "phase1"
    elif timepoint < PRIMARY_SURGE_END:
        data = "phase2"
    else:
        data = "phase3"
    values = PRIMARY_DATA[data]
    return TickSchema(price=values[0], timestamp=timepoint, volume=values[1])


def derive_secondary_tick(timepoint):
    data = None
    if timepoint < SECONDARY_SURGE_START:
        data = "phase1"
    elif timepoint < SECONDARY_SURGE_END:
        data = "phase2"
    else:
        data = "phase3"
    values = SECONDARY_DATA[data]
    return TickSchema(price=values[0], timestamp=timepoint, volume=values[1])


def derive_timestamps(current_datetime):
    earliest = current_datetime - timedelta(seconds=60)
    actual_earliest = max(earliest, GENERATION_START)
    tick = actual_earliest
    while True:
        if tick > current_datetime:
            break
        yield tick
        tick += timedelta(seconds=5)


class TestPrimaryBacktestSource(AbstractSource):
    label = "btcusd"
    config = dict(
        currency="BTC-USD",
        label="btcusd",
    )

    async def get_latest(self, current_datetime: datetime) -> List[TickSchema]:
        """Return deterministic ticks for the last 12 seconds
        no later than current_datetime.
        """
        tick_timestamps_gen = derive_timestamps(current_datetime)
        return [derive_primary_tick(x) for x in tick_timestamps_gen]


class TestSecondaryBacktestSource(AbstractSource):
    label = "btcuah"
    config = dict(
        currency="BTC-UAH",
        label="btcuah",
    )

    async def get_latest(self, current_datetime: datetime) -> List[TickSchema]:
        """Return deterministic ticks for the last 12 seconds
        no later than current_datetime.
        """
        tick_timestamps_gen = derive_timestamps(current_datetime)
        return [derive_secondary_tick(x) for x in tick_timestamps_gen]
