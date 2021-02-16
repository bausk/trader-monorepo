from aiohttp import web

import aiohttp_cors
import asyncio
from dbmodels.db import init_middleware
from server.security import get_middleware
from server.routes import routes
from utils.timescaledb.tsdb_manage import pool_context
from utils.initializators import process_init, ptvsd_debugger_init


ptvsd_debugger_init()
process_init()

auth_middleware = asyncio.get_event_loop().run_until_complete(get_middleware())

app = web.Application(middlewares=[auth_middleware])
db_middleware = init_middleware(app)
app.middlewares.append(db_middleware)
app.add_routes(routes)

cors = aiohttp_cors.setup(
    app,
    defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    },
)
for route in list(app.router.routes()):
    cors.add(route)


app.cleanup_ctx.append(pool_context)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)
