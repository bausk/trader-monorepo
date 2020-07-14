import os
from gino.ext.aiohttp import Gino


db = Gino()

from .common_models import BaseModel
from .source_models import (
    Source, SourceSchema, SourceSchemaWithStats,
    ResourceModel, ResourceSchema
)
from .strategy_models import StrategyModel, StrategySchema, StrategyTypesEnum
from .session_models import BacktestSessionModel, LiveSessionModel, BacktestSessionSchema, LiveSessionSchema


def get_url():
    url = os.environ.get('DB_URL')
    assert url, "Database URL must be specified in DB_URL environment variable"
    return url


def init_middleware(app):
    db.init_app(app, config={
        'dsn': get_url()
    })
    return db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname')
