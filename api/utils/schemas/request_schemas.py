from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from utils.timeseries.constants import DATA_TYPES


class DataRequestSchema(BaseModel):
    from_datetime: datetime
    to_datetime: Optional[datetime]
    period: int
    label: str = "btcusd"
    data_type: int = DATA_TYPES.ticks_primary
    session_id: int


class MarkersRequestSchema(BaseModel):
    from_datetime: datetime
    to_datetime: Optional[datetime]
    period: Optional[int]
