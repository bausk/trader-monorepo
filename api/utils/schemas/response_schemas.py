from typing import Optional, List, Dict, Union
from pydantic import BaseModel
from datetime import datetime
from parameters.enums import SignalResultsEnum


class OHLCSchema(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class PricepointSchema(BaseModel):
    time: datetime
    price: Optional[float] = 0.0
    volume: Optional[float] = 0.0


class SignalResponseSchema(BaseModel):
    timestamp: datetime
    session_id: int
    direction: SignalResultsEnum
    value: float
    primitives: str


class SignalResponseListSchema(BaseModel):
    __root__: List[SignalResponseSchema]
