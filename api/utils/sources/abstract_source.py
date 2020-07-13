from datetime import datetime
from typing import Type, List
from utils.schemas.dataflow_schemas import TickSchema


class AbstractSource:
    """
    Interface for source of data selectable and viewable from frontend.
    """

    def __init__(self, session, config=None):
        self.session = session
        if config:
            self.config = config

    @classmethod
    async def list_availability_intervals(
        cls,
        interval: int,
        table_fullname: str,
        limit: int = 100
    ) -> list:
        raise NotImplementedError('Implement get_availability_intervals')

    @classmethod
    async def get_latest(cls):
        raise NotImplementedError('Implement get_availability_intervals')

    @classmethod
    async def list_data_in_interval(cls, table_fullname: str, start: Type[datetime], end: Type[datetime]) -> list:
        raise NotImplementedError('Implement list_data_in_interval')

    @classmethod
    def deduplicate(cls, ticks_chunk: List[TickSchema]) -> list:
        checker = set()
        tracker = dict()

        def check_tick(tick, i, ticks):
            hashable_repr = tuple(tick.dict().items())
            if hashable_repr in checker:
                tick.volume = tick.volume * 2
                z = tracker[hashable_repr]
                ticks[z].volume = 0.0
                checker.remove(hashable_repr)
                check_tick(tick, i, ticks)
            else:
                checker.add(hashable_repr)
                tracker[hashable_repr] = i

        for i, tick in enumerate(ticks_chunk):
            check_tick(tick, i, ticks_chunk)

        return [x for x in ticks_chunk if x.volume != 0.0]
