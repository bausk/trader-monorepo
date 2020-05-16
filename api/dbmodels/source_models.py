import enum
from typing import List, Optional, Tuple, Union
from datetime import datetime

from .common_models import Privatable
from .db import db


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
        orm_mode = True
    id: Optional[int]
    name: str = 'Unnamed'
    typename: SourceTypesEnum
    config_json: Optional[str]


class SourceSchemaWithStats(SourceSchema):
    class Config:
        validate_assignment = True
        orm_mode = True
    available_intervals: Optional[List[Tuple[datetime, datetime]]]
    data: Optional[List[Union[dict, str]]] = []
