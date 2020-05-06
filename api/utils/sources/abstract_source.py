
class AbstractSource:
    """
    Interface for source of data selectable and viewable from frontend.
    """
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
