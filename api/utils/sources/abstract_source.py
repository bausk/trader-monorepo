from datetime import datetime
from typing import Type


class AbstractSource:
    """
    Interface for source of data selectable and viewable from frontend.
    """

    def __init__(self, session=None, config=None):
        self.session = session
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
