from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, ResourceModel, ResourceSchema, BaseModel
from server.services.resources_db import (
    resource_create,
    resource_delete,
    resources_get_with_sources,
)
from server.security import check_permission, Permissions
from typing import Type

from server.endpoints.routedef import routes


@routes.view("/resources")
class ResourcesView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
            expose_headers="*",
        )
    }
    schema: Type[BaseModel] = ResourceSchema
    model: db.Model = ResourceModel

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        response = [x.dict() for x in await resources_get_with_sources()]
        return web.json_response(response)

    async def post(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        try:
            raw_data = await self.request.json()
            incoming = self.schema(**raw_data)
            response = [x.dict() for x in await resource_create(incoming)]
        except Exception as e:
            print(e)
            raise web.HTTPBadRequest
        return web.json_response(response)

    async def delete(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        try:
            raw_data = await self.request.json()
            incoming = self.schema(**raw_data)
            response = [x.dict() for x in await resource_delete(incoming)]
        except Exception as e:
            print(e)
            raise web.HTTPBadRequest
        return web.json_response(response)
