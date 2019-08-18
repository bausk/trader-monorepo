from aiohttp import web, ClientSession
from aiohttp_security import check_permission
from aiohttp_security import setup as setup_security, SessionIdentityPolicy
from auth.apiAuth import SimpleAuthorizationPolicy
import aiohttp_cors
from .routes import routes
from taskmanager import DataManager

class TerminalApi:
    def __init__(self):
        self._manager = None

    async def _check_permission(self, request):
        return await check_permission(request, 'read')

    def _protected_method(self, method):
        async def _call(request):
            await self._check_permission(request)
            return await method(request)
        return _call

    async def get_status(self, request):
        return web.json_response({'status': 'ok'})

    async def get_markets_data(self, request):
        data = self.manager.
        return web.json_response(data)

    async def post_status(self, request):
        data = await request.post()
        return web.json_response(dict(data))

    def setup_api(self, app: web.Application, data_manager: DataManager):
        self._manager = data_manager
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        for route in routes:
            cors.add(app.router.add_resource(route[1]).add_route(route[0], route[2]))

        app.add_routes([
            web.get('/status', self._protected_method(self.get_status)),
            web.post('/status', self._protected_method(self.post_status)),
        ])
        policy = SessionIdentityPolicy()
        setup_security(app, policy, SimpleAuthorizationPolicy())
