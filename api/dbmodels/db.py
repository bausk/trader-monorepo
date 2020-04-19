import os
from gino.ext.aiohttp import Gino
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


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


# class User(Base):
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname')


# class Source(Base):
class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.Unicode(), default='')


class SourceSchema(SQLAlchemyAutoSchema):
    class Meta:
        table = Source.__table__
        # model = Source
        # include_relationships = True
        # load_instance = True
        transient = True
    # id = auto_field()
    # type = auto_field()