import enum
import json
from typing import List, Optional, Tuple, Union
from datetime import datetime, date
from parameters.enums import StrategiesEnum, LiveSourcesEnum

from .common_models import Privatable


class BacktestParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True

    strategy_name: str
    start_at: Optional[Union[datetime, date]]
    finish_at: Optional[Union[datetime, date]]
    # source_primary: Optional[SourceTypesEnum]
    # source_secondary: Optional[SourceTypesEnum]
    tick_frequency: Optional[int]


class LiveParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True

    strategy_name: Optional[StrategiesEnum]
    source_primary: Optional[LiveSourcesEnum]
    source_secondary: Optional[LiveSourcesEnum]
    tick_frequency: Optional[int]
