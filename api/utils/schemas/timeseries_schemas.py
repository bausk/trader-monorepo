from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class TickSchema(BaseModel):
    price: float
    timestamp: datetime
    queried_at: Optional[datetime]
    volume: Optional[float]
    funds: Optional[float]
