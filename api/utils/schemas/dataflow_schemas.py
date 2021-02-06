import json
from datetime import datetime
from pydantic import BaseModel, validator, parse_obj_as
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
    session_id: Optional[int]
    timestamp: datetime
    bucket_timestamp: Optional[datetime]
    direction: SignalResultsEnum
    value: Optional[float]
    primitives: Optional[List[List[TimeseriesSchema]]]

    @validator("primitives", pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            if isinstance(v, str):
                return parse_obj_as(List[List[TimeseriesSchema]], json.loads(v))
            elif isinstance(v, list):
                return parse_obj_as(List[List[TimeseriesSchema]], v)
            else:
                return v
        return None


class SignalsListSchema(BaseModel):
    __root__: List[SignalResultSchema]


class ProcessTaskSchema(BaseDataflowSchema):
    timestamp: datetime
    ticks_primary: Optional[List[TickSchema]]
    label_primary: Optional[str]
    ticks_secondary: Optional[List[TickSchema]]
    label_secondary: Optional[str]
    signals: List[SignalResultSchema] = []
    orders: Optional[List[dict]] = []
    symbols: Optional[List[dict]] = []
