import json
from parameters.enums import BacktestTypesEnum
from typing import List, Optional
from pydantic import validator
from datetime import datetime

from dbmodels.db_init import db
from dbmodels.common_models import Privatable
from dbmodels.strategy_params_models import LiveParamsSchema
from dbmodels.source_models import SourceSchema


class BacktestSessionModel(db.Model):
    __tablename__ = "backtest_sessions"
    id = db.Column(db.Integer(), primary_key=True)

    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id"))
    start_datetime = db.Column(db.DateTime(), nullable=True)
    end_datetime = db.Column(db.DateTime(), nullable=True)
    config_json = db.Column(db.Unicode(), default="{}")
    backtest_type = db.Column(db.Unicode(), default="")

    def __init__(self, **kw):
        super().__init__(**kw)
        self._sources = set()

    @property
    def backtest_sources(self):
        return self._sources

    def add_source(self, source):
        self._sources.add(source)


class BacktestSessionSourceModel(db.Model):
    __tablename__ = "backtest_sessions_sources"
    backtest_session_id = db.Column(
        db.Integer, db.ForeignKey("backtest_sessions.id"), primary_key=True
    )
    source_id = db.Column(db.Integer, db.ForeignKey("sources.id"), primary_key=True)
    order = db.Column(db.Integer, nullable=False)


class LiveSessionModel(db.Model):
    __tablename__ = "live_sessions"
    id = db.Column(db.Integer(), primary_key=True)
    start_datetime = db.Column(db.DateTime(), nullable=True)
    end_datetime = db.Column(db.DateTime(), nullable=True)

    # Used for logging only. Model config is copied
    config_json = db.Column(db.Unicode(), default="{}")


class BaseBacktestSessionSchema(Privatable):
    start_datetime: datetime
    end_datetime: datetime
    strategy_id: int
    config_json: dict = {}
    backtest_type: BacktestTypesEnum = BacktestTypesEnum.test

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


class BacktestSessionInputSchema(BaseBacktestSessionSchema):
    sources_ids: Optional[List[int]]


class BacktestSessionSchema(BaseBacktestSessionSchema):
    class Config:
        orm_mode = True

    id: int
    backtest_sources: List[SourceSchema]


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
