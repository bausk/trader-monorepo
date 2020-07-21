from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any, Dict, Union

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


class TimeseriesSchema(BaseModel):
    timestamp: datetime
    value: float


class PrimitivesSchema(BaseModel):
    __root__: List[List[TimeseriesSchema]]


class SignalResultSchema(BaseDataflowSchema):
    direction: SignalResultsEnum
    timestamp: datetime
    value: Optional[float]
    primitives: Optional[PrimitivesSchema]


class ProcessTaskSchema(BaseDataflowSchema):
    timestamp: datetime
    ticks_primary: Optional[List[TickSchema]]
    label_primary: Optional[str]
    ticks_secondary: Optional[List[TickSchema]]
    label_secondary: Optional[str]
    signals: List[SignalResultSchema] = []
    orders: Optional[List[dict]] = []
    symbols: Optional[List[dict]] = []
