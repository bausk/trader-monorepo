from aiohttp import web
from aiohttp.web import Request, Response
# from handlers import handler_root, handler_login, handler_logout, handler_listen, handler_profile
from dbmodels.db import db, User
from server.security import check_permission, Permissions


routes = web.RouteTableDef()


@routes.get('/')
async def index(request: Request) -> Response:
    await check_permission(request, Permissions.READ)
    users = []
    async with db.transaction():
        async for u in User.query.order_by(User.id).gino.iterate():
            users.append((u.id, u.nickname))
    return web.json_response({
        'users': users
        })


@routes.post('/')
async def post_root(request: Request) -> Response:
    await check_permission(request, Permissions.READ)
    users = []
    async with db.transaction():
        async for u in User.query.order_by(User.id).gino.iterate():
            users.append((u.id, u.nickname))
    return web.json_response({
        'users': users
        })
