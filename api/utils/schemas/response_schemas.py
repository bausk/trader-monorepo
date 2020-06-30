from typing import Optional, List, Dict, Union
from pydantic import BaseModel
from datetime import datetime


class OHLCSchema(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
