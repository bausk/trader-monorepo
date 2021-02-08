from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Union

from parameters.enums import IndicatorsEnum, SignalResultsEnum


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
    label: IndicatorsEnum
    indicator: List[TimeseriesSchema]


class SignalSchema(ValidatedAssignmentSchema):
    timestamp: Optional[datetime]
    direction: SignalResultsEnum
    value: Optional[float]
    traceback: Optional[Union[Dict, List]]


class CalculationSchema(BaseModel):
    indicators: List[IndicatorSchema]
    signal: SignalSchema


class SourceFetchResultSchema(ValidatedAssignmentSchema):
    timestamp: datetime
    ticks_primary: Optional[List[TickSchema]]
    label_primary: Optional[str]
    ticks_secondary: Optional[List[TickSchema]]
    label_secondary: Optional[str]
