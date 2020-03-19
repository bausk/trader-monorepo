from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


import asyncio
from dbmodels.db import db, User, get_url

async def init():
    await db.set_bind(get_url())

async def main():
    await init()

    # Create tables
    print('Creating tables or something')
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




if __name__ == '__main__':
    print('Performing DB task')
    asyncio.get_event_loop().run_until_complete(main())
    print('Done!')
