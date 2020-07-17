from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

from parameters.enums import SignalResultsEnum


class BaseDataflowSchema(BaseModel):
    class Config:
        validate_assignment = True


class TickSchema(BaseDataflowSchema):
    price: float
    source_id: Optional[int]
    timestamp: datetime
    queried_at: Optional[datetime]
    volume: Optional[float]
    funds: Optional[float]


class ProcessTaskSchema(BaseDataflowSchema):
    ticks_primary: Optional[List[TickSchema]]
    label_primary: Optional[str]
    ticks_secondary: Optional[List[TickSchema]]
    label_secondary: Optional[str]
    signals: Optional[List[dict]] = []
    orders: Optional[List[dict]] = []
    symbols: Optional[List[dict]] = []


class SignalResultSchema(BaseDataflowSchema):
    decision: SignalResultsEnum
    value: Optional[float]
    timestamp: datetime
