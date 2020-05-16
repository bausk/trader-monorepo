import enum
import json
from typing import List, Optional, Tuple, Union, Any, Type
from pydantic import validator, ValidationError
from datetime import datetime

from .common_models import Privatable
from .db import db
from .strategy_params_models import StrategyParamsSchema


class StrategyTypesEnum(str, enum.Enum):
    interexchangearbitrage = "interexchangearbitrage"
    signalbased = "signalbased"


# class Source(Base):
class StrategyModel(db.Model):
    __tablename__ = 'strategies'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default='Unnamed')
    typename = db.Column(db.Enum(
        StrategyTypesEnum,
        values_callable=lambda x: [e.value for e in x]
    ))
    is_live = db.Column(db.Boolean(), default=False)
    config_json = db.Column(db.Unicode(), default='{}')


class StrategySchema(Privatable):
    class Config:
        orm_mode = True

    id: Optional[int]
    name: str = 'Default'
    typename: StrategyTypesEnum
    is_live: Optional[bool]
    config_json: StrategyParamsSchema

    @validator('config_json', pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            return StrategyParamsSchema(**json.loads(v))
        return None

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        result['config_json'] = json.dumps(result['config_json'])
        return result
