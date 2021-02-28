import json
from server.services.sources_db import source_create, source_delete, sources_get
from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, Source, SourceSchema, SourceSchemaWithStats, BaseModel
from server.security import check_permission, Permissions
from typing import Type
from utils.sources.abstract_source import AbstractSource
from utils.sources.select import LIVE_SOURCES

from server.endpoints.routedef import routes


@routes.view("/sources")
class SourcesView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
            expose_headers="*",
        )
    }
    schema: Type[BaseModel] = SourceSchema

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        response = [x.dict() for x in await sources_get()]
        return web.json_response(response)

    async def post(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        try:
            raw_data = await self.request.json()
            incoming = self.schema(**raw_data)
            response = [x.dict() for x in await source_create(incoming)]
        except Exception as e:
            print(e)
            raise web.HTTPBadRequest
        return web.json_response(response)

    async def delete(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        try:
            raw_data = await self.request.json()
            incoming = self.schema(**raw_data)
            response = [x.dict() for x in await source_delete(incoming)]
        except Exception as e:
            print(e)
            raise web.HTTPBadRequest
        return web.json_response(response)


@routes.view(r"/sources/{id:\d+}/stats")
class SourcesStatsView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
            expose_headers="*",
        )
    }
    schema: Type[BaseModel] = SourceSchemaWithStats

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        source_id = int(self.request.match_info["id"])
        async with db.transaction():
            source = await Source.get(source_id)
        source_model = self.schema.from_orm(source)
        source_config = json.loads(source_model.config_json)
        table_fullname = source_config["table_name"]
        if not table_fullname:
            raise web.HTTPConflict(text="table_name not defined in source config")
        source_executor: AbstractSource = LIVE_SOURCES[source_model.typename]
        availability_intervals = await source_executor.list_availability_intervals(
            interval=3600, table_fullname=table_fullname
        )
        source_model.available_intervals = []
        for res in availability_intervals:
            source_model.available_intervals.append([res[0], res[1]])
        return web.json_response(body=source_model.json())


@routes.view(r"/sources/{id:\d+}/interval")
class SourcesIntervalView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
            expose_headers="*",
        )
    }
    schema: Type[BaseModel] = SourceSchemaWithStats

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        source_id = int(self.request.match_info["id"])
        async with db.transaction():
            source = await Source.get(source_id)
        source_model = self.schema.from_orm(source)
        source_config = json.loads(source_model.config_json)
        table_fullname = source_config["table_name"]
        if not table_fullname:
            raise web.HTTPConflict(text="table_name not defined in source config")
        source_executor: AbstractSource = LIVE_SOURCES[source_model.typename]
        res = await source_executor.list_data_in_interval(
            table_fullname=table_fullname,
            start=self.request.query.get("start"),
            end=self.request.query.get("end"),
        )
        source_model.data = res
        return web.json_response(body=source_model.json())
