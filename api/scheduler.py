import aiohttp
from aiohttp import web

from dbmodels.db import init_middleware
from secrets_management.manage import decrypt_credentials, load_credentials, get_environment
from ticker.main_loop import Ticker


if get_environment() == 'development':
    import ptvsd
    print('[Scheduler] debug mode')
    try:
        ptvsd.enable_attach(address=('0.0.0.0', 5680))
        ptvsd.wait_for_attach(3)
    except:
        print('[Scheduler] ptvsd attach aborted')


load_credentials(decrypt_credentials(which=['*.env']))

app = web.Application()
db_middleware = init_middleware(app)
app.middlewares.append(db_middleware)


async def persistent_session(app):
    app['PERSISTENT_SESSION'] = session = aiohttp.ClientSession()
    yield
    await session.close()


app.cleanup_ctx.append(persistent_session)

ticker = Ticker()
app.on_startup.append(ticker.run)
print('[Scheduler started]')
