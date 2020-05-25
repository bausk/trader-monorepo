import enum
import json
from typing import List, Optional, Tuple, Union
from datetime import datetime, date
from parameters.enums import OrderExecutorsEnum, StrategiesEnum, LiveSourcesEnum

from .common_models import Privatable
from .source_models import SourceTypesEnum


class BacktestParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True
    strategy_name: str
    start_at: Optional[Union[datetime, date]]
    finish_at: Optional[Union[datetime, date]]
    source_primary: Optional[SourceTypesEnum]
    source_secondary: Optional[SourceTypesEnum]


class LiveParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True
    strategy_name: Optional[StrategiesEnum]
    order_executor: Optional[OrderExecutorsEnum]
    source_primary: Optional[LiveSourcesEnum]
    source_secondary: Optional[LiveSourcesEnum]
