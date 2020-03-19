import loadenv
from aiohttp import web, ClientSession

import ptvsd
ptvsd.enable_attach()

import aiohttp_cors
import asyncio
from dbmodels.db import db, User, init_middleware
from server.init import setup_aiohttp_security, setup_scheduler
from server.security import get_middleware
from server.errors_middleware import create_error_middleware
from server.routes import routes

# Load encrypted config
from secrets_management.manage import decrypt_credentials, load_credentials
load_credentials(decrypt_credentials())


async def main():

    # Create tables
    await db.gino.create_all()

    # Create object, `id` is assigned by database
    u1 = await User.create(nickname='fantix')
    print(u1.id, u1.nickname)  # 1 fantix

    # Returns all user objects with "d" in their nicknames
    users = await User.query.where(User.nickname.contains('d')).gino.all()
    print(users)  # [<User object>, <User object>]

    # Find one user object, None if not found
    user = await User.query.where(User.nickname == 'daisy').gino.first()
    print(user)  # <User object> or None

    # Execute complex statement and return command status
    status, result = await User.update.values(
        nickname='No.' + db.cast(User.id, db.Unicode),
    ).where(
        User.id > 10,
    ).gino.status()
    print(status)  # UPDATE 8

    # Iterate over the results of a large query in a transaction as required
    async with db.transaction():
        async for u in User.query.order_by(User.id).gino.iterate():
            print(u.id, u.nickname)


auth_middleware = asyncio.get_event_loop().run_until_complete(get_middleware())

app = web.Application(middlewares=[auth_middleware])
db_middleware = init_middleware(app)
app.middlewares.append(db_middleware)
app.add_routes(routes)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})
for route in list(app.router.routes()):
    cors.add(route)


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
