import sys, traceback
from aiohttp import web

import asyncio
import aiojobs

from dbmodels.db import init_middleware

# Load encrypted config
from secrets_management.manage import decrypt_credentials, load_credentials, get_environment


if get_environment() == 'development':
    import ptvsd
    print('[Scheduler] debug mode')
    try:
        ptvsd.enable_attach(address=('0.0.0.0', 5680))
        ptvsd.wait_for_attach(3)
    except:
        print('[Scheduler] ptvsd attach aborted')
        pass


load_credentials(decrypt_credentials(which=['*.env']))

app = web.Application()
db_middleware = init_middleware(app)
app.middlewares.append(db_middleware)

async def run_on_startup(app):
    scheduler = await aiojobs.create_scheduler()
    print('running on startup')
    app['redis_listener'] = await scheduler.spawn(listen_forever())


async def listen_forever():
    while True:
        try:
            await asyncio.sleep(3)
            print('listening forever')
            printl('listening forever')
        except Exception:
            traceback.print_exc(file=sys.stdout)


app.on_startup.append(run_on_startup)
print('[Scheduler started]')
