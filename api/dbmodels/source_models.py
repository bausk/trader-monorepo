import enum
from typing import List, Optional, Tuple, Union
from datetime import datetime

from .common_models import Privatable
from .db import db
from .session_models import LiveSessionSchema


class SourceTypesEnum(str, enum.Enum):
    bigquery = 'bigquery'
    kuna = 'kuna'
    cryptowatch = 'cryptowatch'


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
        validate_assignment = True
        orm_mode = True
    id: Optional[int]
    name: str = 'Unnamed'
    typename: SourceTypesEnum
    config_json: Optional[str]


class ResourceModel(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default='Unnamed')
    is_always_on = db.Column(db.Boolean, default=False)
    live_session_id = db.Column(db.Integer, db.ForeignKey('live_sessions.id'), nullable=True)

    primary_live_source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=True)
    secondary_live_source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=True)
    primary_backtest_source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=True)
    secondary_backtest_source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=True)


class ResourceSchema(Privatable):
    class Config:
        validate_assignment = True
        orm_mode = True
    id: Optional[int]
    name: str = 'Unnamed'
    is_always_on: bool = False
    live_session_id: Optional[int]
    live_session_model: Optional[LiveSessionSchema]
    primary_live_source_id: Optional[int]
    primary_live_source_model: Optional[SourceSchema]
    secondary_live_source_id: Optional[int]
    secondary_live_source_model: Optional[SourceSchema]
    primary_backtest_source_id: Optional[int]
    primary_backtest_source_model: Optional[SourceSchema]
    secondary_backtest_source_id: Optional[int]
    secondary_backtest_source_model: Optional[SourceSchema]


class SourceSchemaWithStats(SourceSchema):
    class Config:
        validate_assignment = True
        orm_mode = True
    available_intervals: Optional[List[Tuple[datetime, datetime]]]
    data: Optional[List[Union[dict, str]]] = []
