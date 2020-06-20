from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


class TickSchema(BaseModel):
    price: float
    timestamp: datetime
    queried_at: Optional[datetime]
    volume: Optional[float]
    funds: Optional[float]


class ProcessTaskSchema(BaseModel):
    ticks: Optional[Dict[str, List[TickSchema]]]
    signals: Optional[List[dict]]
    orders: Optional[List[dict]]
    symbols: Optional[List[dict]]
