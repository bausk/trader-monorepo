from gino.ext.aiohttp import Gino
import os


db = Gino()


def get_url():
    url = os.environ.get('DB_URL')
    assert url, "Database URL must be specified in DB_URL environment variable"
    return url


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname')
