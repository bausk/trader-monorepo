from typing import Optional, Type
from pydantic import BaseModel
from datetime import datetime, date


class TimeseriesSchema(BaseModel):
    price: float
    queried_at: Optional[Type[datetime]]
    timestamp: Type[datetime]
    volume: Optional[float]
