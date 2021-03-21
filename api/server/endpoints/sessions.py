import sys
import traceback
import json

from datetime import datetime, timedelta
from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import BaseModel
from server.security import check_permission, Permissions
from typing import Type, List
from parameters.enums import SessionDatasetNames
from utils.schemas.request_schemas import DataRequestSchema, MarkersRequestSchema
from utils.schemas.response_schemas import OHLCSchema, SignalsListSchema
from utils.timescaledb.tsdb_read import (
    get_terminal_data,
    get_signals,
    get_reduced_signals,
)
from server.endpoints.routedef import routes


CORS_CONFIG = {
    "*": ResourceOptions(
        allow_credentials=True,
        allow_headers="*",
        expose_headers="*",
    )
}


@routes.view(r"/sessions/{id:\d+}")
class SessionDataView(web.View, CorsViewMixin):
    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = DataRequestSchema

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        try:
            session_id = int(self.request.match_info["id"])
            request_data = self.schema(
                **self.request.query,
                session_id=session_id,
            )
            validated: List[OHLCSchema] = await get_terminal_data(
                SessionDatasetNames.live, session_id, request_data, self.request
            )
            return web.json_response(
                body=json.dumps([json.loads(x.json()) for x in validated])
            )
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise web.HTTPBadRequest


@routes.view(r"/sessions/{id:\d+}/markers")
class SignalsDataView(web.View, CorsViewMixin):
    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = MarkersRequestSchema

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        try:
            session_id = int(self.request.match_info["id"])
            from_datetime = datetime.now() - timedelta(hours=8)
            request_data: MarkersRequestSchema = self.schema(
                from_datetime=from_datetime, **self.request.query
            )
            if not request_data.period:
                result: SignalsListSchema = await get_signals(
                    SessionDatasetNames.live, session_id, request_data, self.request
                )
            else:
                result: SignalsListSchema = await get_reduced_signals(
                    SessionDatasetNames.live, session_id, request_data, self.request
                )
            return web.json_response(body=result.json())
        except Exception:
            traceback.print_exc(file=sys.stdout)
            raise web.HTTPBadRequest
