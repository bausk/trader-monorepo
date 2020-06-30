from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


class TickSchema(BaseModel):
    price: float
    source_id: Optional[int]
    timestamp: datetime
    queried_at: Optional[datetime]
    volume: Optional[float]
    funds: Optional[float]


class ProcessTaskSchema(BaseModel):
    ticks_primary: Optional[List[TickSchema]]
    label_primary: Optional[str]
    ticks_secondary: Optional[List[TickSchema]]
    label_secondary: Optional[str]
    signals: Optional[List[dict]]
    orders: Optional[List[dict]]
    symbols: Optional[List[dict]]
