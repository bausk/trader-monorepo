import sys, traceback
import json
from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import BaseModel
from server.security import check_permission, Permissions
from typing import Type, List
from utils.schemas.request_schemas import DataRequestSchema
from utils.schemas.response_schemas import OHLCSchema
from utils.timeseries.timescale_utils import get_terminal_data
from server.endpoints.routedef import routes


CORS_CONFIG = {
    "*": ResourceOptions(
        allow_credentials=True,
        allow_headers="*",
        expose_headers="*",
    )
}


@routes.view(r'/sessions/{id:\d+}')
class SessionDataView(web.View, CorsViewMixin):
    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = DataRequestSchema

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        try:
            session_id = int(self.request.match_info['id'])
            request_data = self.schema(**self.request.query)
            validated = await get_terminal_data(session_id, request_data, self.request)
            return web.json_response(body=json.dumps([json.loads(x.json()) for x in validated]))
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise web.HTTPBadRequest
