import json
from typing import Optional, List, Dict, Union
from datetime import datetime
from pydantic import BaseModel, validator, parse_obj_as
from parameters.enums import SignalResultsEnum


class OHLCSchema(BaseModel):
    """OHLCSchema:
    Data representing a single OHCLV candle, `time` is start time
    """

    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = 0.0


class PricepointSchema(BaseModel):
    """PricepointSchema:
    Data representing one market tick
    """

    time: datetime
    price: Optional[float] = 0.0
    volume: Optional[float] = 0.0


class InputMarketDataSchema(BaseModel):
    """InputMarketDataSchema:
    Time-series of market data representing input to calculate indicator from.
    """

    ticks: Optional[List[PricepointSchema]]
    candles: Optional[List[PricepointSchema]]


class SignalResultSchema(BaseModel):
    class Config:
        validate_assignment = True

    session_id: Optional[int]
    timestamp: datetime
    bucket_timestamp: Optional[datetime]
    direction: SignalResultsEnum
    value: Optional[float]
    traceback: Optional[Union[Dict, List]]

    @validator("traceback", pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            if isinstance(v, str):
                return parse_obj_as(Union[Dict, List], json.loads(v))
            elif isinstance(v, (dict, list)):
                return parse_obj_as(Union[Dict, List], v)
            else:
                return v
        return None


class SignalsListSchema(BaseModel):
    __root__: List[SignalResultSchema]
