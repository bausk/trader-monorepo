import enum
import os
from gino.ext.aiohttp import Gino
from gino.dialects.asyncpg import AsyncEnum
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime


db = Gino()

def get_url():
    url = os.environ.get('DB_URL')
    assert url, "Database URL must be specified in DB_URL environment variable"
    return url


def init_middleware(app):
    db.init_app(app, config={
        'dsn': get_url()
    })
    return db


class SourceTypesEnum(str, enum.Enum):
    bigquery = 'bigquery'
    kuna = 'kuna'
    cryptowatch = 'cryptowatch'


class Privatable(BaseModel):
    def private_dict(self):
        res = self.dict()
        del res['id']
        return res


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname')


# class Source(Base):
class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default='Unnamed')
    typename = db.Column(db.Enum(
        SourceTypesEnum,
        values_callable=lambda x: [e.value for e in x]
    ))
    config_json = db.Column(db.Unicode(), default='{}')


class SourceSchema(Privatable):
    class Config:
        orm_mode = True
    id: Optional[int]
    name: str = 'Unnamed'
    typename: SourceTypesEnum
    config_json: Optional[str]

    def private_dict(self):
        res = self.dict()
        del res['id']
        return res

class SourceSchemaWithStats(Privatable):
    available_intervals: List[Tuple[datetime, datetime]]
