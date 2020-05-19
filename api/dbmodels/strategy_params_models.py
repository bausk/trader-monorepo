import enum
import json
from typing import List, Optional, Tuple, Union
from datetime import datetime, date

from .common_models import Privatable
from .source_models import SourceTypesEnum
from .order_executor_models import OrderExecutorsEnum


class BacktestParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True
    start_at: Optional[Union[datetime, date]]
    finish_at: Optional[Union[datetime, date]]
    source_primary: Optional[SourceTypesEnum]
    source_secondary: Optional[SourceTypesEnum]


class LiveParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True
    order_executor: Optional[OrderExecutorsEnum]
    source_primary: Optional[SourceTypesEnum]
    source_secondary: Optional[SourceTypesEnum]
