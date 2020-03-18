from aiohttp import web
from dbmodels.db import db


routes = web.RouteTableDef()


@routes.get('/')
def index(req):
    users = []
    async with db.transaction():
        async for u in User.query.order_by(User.id).gino.iterate():
            users.append((u.id, u.nickname))
    return web.json_response({
        'users': users
        })