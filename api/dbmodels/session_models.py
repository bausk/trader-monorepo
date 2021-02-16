import json
from typing import Optional
from pydantic import validator
from datetime import datetime

from dbmodels.db_init import db
from dbmodels.common_models import Privatable
from dbmodels.strategy_params_models import LiveParamsSchema


class BacktestSessionModel(db.Model):
    __tablename__ = "backtest_sessions"
    id = db.Column(db.Integer(), primary_key=True)

    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id"))
    start_datetime = db.Column(db.DateTime(), nullable=True)
    end_datetime = db.Column(db.DateTime(), nullable=True)
    config_json = db.Column(db.Unicode(), default="{}")
    backtest_type = db.Column(db.Unicode(), default="")


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
    strategy_id: int
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    config_json: Optional[dict]
    backtest_type: Optional[str]

    @validator("config_json", pre=True)
    def deserialize_config(cls, v, values, **kwargs):
        if v:
            if isinstance(v, str):
                return json.loads(v)
            return v
        return None

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        if "config_json" in result:
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
