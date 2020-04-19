from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from .db import Source


class SourceSchema(SQLAlchemyAutoSchema):
    class Meta:
        table = Source.__table__
        # model = Source
        # include_relationships = True
        # load_instance = True
        transient = True
    id = auto_field()
    type = auto_field()