from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Union

from parameters.enums import SignalResultsEnum
from utils.schemas.response_schemas import InputMarketDataSchema


class ValidatedAssignmentSchema(BaseModel):
    class Config:
        validate_assignment = True


class TickSchema(ValidatedAssignmentSchema):
    price: float
    source_id: Optional[int]
    timestamp: datetime
    queried_at: Optional[datetime]
    volume: Optional[float]
    funds: Optional[float]


class TimeseriesSchema(BaseModel):
    timestamp: datetime
    value: float


class IndicatorSchema(BaseModel):
    label: str
    indicator: List[TimeseriesSchema]


class SignalSchema(ValidatedAssignmentSchema):
    timestamp: Optional[datetime]
    direction: SignalResultsEnum
    value: Optional[float]
    traceback: Optional[Union[List, Dict]]


class CalculationSchema(BaseModel):
    increasing_id: Optional[int]
    indicators: List[IndicatorSchema]
    signal: SignalSchema
    market_inputs: List[InputMarketDataSchema]


class SourceFetchSchema(BaseModel):
    ticks: List[TickSchema]
    label: str
    data_type: Optional[int]


class SourceFetchResultSchema(ValidatedAssignmentSchema):
    timestamp: datetime
    ticks: List[SourceFetchSchema]
