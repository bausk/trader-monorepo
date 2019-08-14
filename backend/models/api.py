from aiohttp import web, ClientSession
from aiohttp_security import is_anonymous, remember, forget, check_permission


class TerminalApi:
    def __init__(self, terminal):
        self.terminal = terminal

    async def _check_permission(self, request):
        return await check_permission(request, 'read')

    async def get_status(self, request):
        return web.json_response({'status': 'ok'})

    def protected_method(self, method):
        async def _call(request):
            await self._check_permission(request)
            return await method(request)
        return _call

    def bind(self, app: web.Application):
        app.add_routes([
            web.get('/status', self.protected_method(self.get_status)),
        ])
