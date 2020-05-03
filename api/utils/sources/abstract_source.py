
class AbstractSource:
    """
    Interface for source of data selectable and viewable from frontend.
    """

    async def list_availability_intervals(
        self,
        interval: int,
        table_fullname: str,
        limit: int = 100
    ) -> list:
        raise NotImplementedError('Implement get_availability_intervals')

    async def get_latest(self):
        raise NotImplementedError('Implement get_availability_intervals')
