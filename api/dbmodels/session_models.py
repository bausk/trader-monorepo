import enum
import json
from typing import List, Optional, Tuple, Union, Any, Type
from pydantic import validator, ValidationError
from datetime import datetime

from .common_models import Privatable
from .db import db
from .strategy_params_models import BacktestParamsSchema, LiveParamsSchema


class BacktestSessionModel(db.Model):
    __tablename__ = "backtest_sessions"
    id = db.Column(db.Integer(), primary_key=True)

    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id"))
    created_at = db.Column(db.DateTime(), nullable=True)
    config_json = db.Column(db.Unicode(), default="{}")


class LiveSessionModel(db.Model):
    __tablename__ = "live_sessions"
    id = db.Column(db.Integer(), primary_key=True)
    start_datetime = db.Column(db.DateTime(), nullable=True)
    end_datetime = db.Column(db.DateTime(), nullable=True)

    # Used for logging only. Model config is copied
    config_json = db.Column(db.Unicode(), default="{}")


class BacktestSessionSchema(Privatable):
    class Config:
        orm_mode = True

    id: Optional[int]
    strategy_id: Optional[int]
    strategy: Optional[int]
    created_at: Optional[datetime]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    config_json: Optional[BacktestParamsSchema]

    @validator("config_json", pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            if isinstance(v, str):
                return BacktestParamsSchema(**json.loads(v))
            return BacktestParamsSchema(**v)
        return None

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        result["config_json"] = json.dumps(result["config_json"])
        return result


class LiveSessionSchema(Privatable):
    class Config:
        orm_mode = True

    id: Optional[int]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    config_json: Optional[LiveParamsSchema]

    @validator("config_json", pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            if isinstance(v, str):
                return LiveParamsSchema(**json.loads(v))
            return LiveParamsSchema(**v)
        return None

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        result["config_json"] = json.dumps(result["config_json"])
        return result
