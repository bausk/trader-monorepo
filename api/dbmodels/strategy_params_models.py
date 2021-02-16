import enum
import json
from typing import List, Optional, Tuple, Union
from datetime import datetime, date
from parameters.enums import StrategiesEnum, SourcesEnum

from .common_models import Privatable


class BacktestParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True

    strategy_name: str
    tick_frequency: Optional[int]


# TODO: CURRENTLY NOT IN USE AT ALL
class LiveParamsSchema(Privatable):
    class Config:
        arbitrary_types_allowed = True

    strategy_name: Optional[StrategiesEnum]
    source_primary: Optional[SourcesEnum]
    source_secondary: Optional[SourcesEnum]
    tick_frequency: Optional[int]
