import enum
import json
from typing import List, Optional, Tuple, Union
from datetime import datetime, date

from .common_models import Privatable
from .source_models import SourceTypesEnum
from .order_executor_models import OrderExecutorsEnum


class StrategyParamsSchema(Privatable):
    id: Optional[int]
    name: Optional[str]
    variable_params: Optional[dict] = {}
    start_at: Optional[Union[datetime, date]]
    finish_at: Optional[Union[datetime, date]]
    order_executor: Optional[OrderExecutorsEnum]
    source_primary: Optional[SourceTypesEnum]
    source_secondary: Optional[SourceTypesEnum]
