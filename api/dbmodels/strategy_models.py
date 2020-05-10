import enum
from typing import List, Optional, Tuple, Union
from datetime import datetime

from .common_models import Privatable
from .db import db


class StrategyTypesEnum(str, enum.Enum):
    interexchange_arbitrage = "interexchange_arbitrage"


# class Source(Base):
class StrategyModel(db.Model):
    __tablename__ = 'strategies'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default='Unnamed')
    typename = db.Column(db.Enum(
        StrategyTypesEnum,
        values_callable=lambda x: [e.value for e in x]
    ))
    config_json = db.Column(db.Unicode(), default='{}')


class StrategySchema(Privatable):
    class Config:
        orm_mode = True
    id: Optional[int]
    name: str = 'Default'
    typename: StrategyTypesEnum
    config_json: Optional[str]
