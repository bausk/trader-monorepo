from aiohttp import web, ClientSession
from view.api import TerminalApi


class Api(TerminalApi):
    def __init__(self, terminal):
        super().__init__(terminal)

    async def get_status(self, request):
        await self._check_permission(request)
        return web.json_response({'status': 'ok'})

