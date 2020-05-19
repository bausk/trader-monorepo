import json
from typing import List, Optional, Tuple, Union, Any, Type
from pydantic import validator, ValidationError
from datetime import datetime

from parameters.enums import StrategyTypesEnum

from .common_models import Privatable
from .db import db
from .strategy_params_models import BacktestParamsSchema, LiveParamsSchema
from .session_models import LiveSessionSchema


class StrategyModel(db.Model):
    __tablename__ = 'strategies'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default='Unnamed')
    typename = db.Column(db.Enum(
        StrategyTypesEnum,
        values_callable=lambda x: [e.value for e in x]
    ))
    live_session_id = db.Column(db.Integer, db.ForeignKey('live_sessions.id'), nullable=True)
    config_json = db.Column(db.Unicode(), default='{}')


class StrategySchema(Privatable):
    class Config:
        orm_mode = True

    id: Optional[int]
    name: str = 'Default'
    typename: StrategyTypesEnum
    live_session_id: Optional[int]
    live_session: Optional[LiveSessionSchema]
    config_json: Optional[LiveParamsSchema]

    @validator('config_json', pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            if isinstance(v, str):
                return LiveParamsSchema(**json.loads(v))
            return LiveParamsSchema(**v)
        return None

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        result['config_json'] = json.dumps(result['config_json'])
        return result
