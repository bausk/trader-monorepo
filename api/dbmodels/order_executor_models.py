import enum
from typing import List, Optional, Tuple, Union
from datetime import datetime, date

from .common_models import Privatable


class OrderExecutorsEnum(str, enum.Enum):
    live = 'live'
    backtest = 'backtest'


class OrderExecutorSchema(Privatable):
    id: Optional[int]
    name: Optional[str]
