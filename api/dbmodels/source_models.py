import json
from pydantic import validator
from typing import List, Optional, Tuple, Union
from datetime import datetime

from parameters.enums import SourcesEnum
from .common_models import Privatable
from dbmodels.db_init import db


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default="Unnamed")
    typename = db.Column(db.Unicode(), nullable=False)
    config_json = db.Column(db.Unicode(), default="{}")


class SourceSchema(Privatable):
    class Config:
        validate_assignment = True
        orm_mode = True

    id: Optional[int]
    name: str = "Unnamed"
    typename: SourcesEnum
    config_json: dict = {}

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



class ResourceModel(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), default="Unnamed")
    is_always_on = db.Column(db.Boolean, default=False)

    primary_live_source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id"), nullable=True
    )
    secondary_live_source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id"), nullable=True
    )
    primary_backtest_source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id"), nullable=True
    )
    secondary_backtest_source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id"), nullable=True
    )


class ResourceSchema(Privatable):
    class Config:
        validate_assignment = True
        orm_mode = True

    id: Optional[int]
    name: str = "Unnamed"
    is_always_on: bool = False
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
