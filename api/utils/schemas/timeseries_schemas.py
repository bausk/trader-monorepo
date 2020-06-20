from typing import Optional, Type
from pydantic import BaseModel
from datetime import datetime, date


class TickSchema(BaseModel):
    price: float
    timestamp: datetime
    queried_at: Optional[Type[datetime]]
    volume: Optional[float]
    funds: Optional[float]
