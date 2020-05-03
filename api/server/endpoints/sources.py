from datetime import datetime
import pytz
import asyncio
import json
from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, Source, SourceSchema, SourceSchemaWithStats, SourceTypesEnum, BaseModel
from server.security import check_permission, Permissions
from google.oauth2 import service_account
from google.cloud import bigquery
from typing import Type
from secrets_management.manage import decrypt_credentials
from utils.sources.select import select_source

from server.endpoints.routedef import routes


credfile = decrypt_credentials(which=['./.secrets/keyring.json'])
creds_json = json.loads(credfile[0])
creds = service_account.Credentials.from_service_account_info(creds_json)
bigquery_client = bigquery.Client(
    credentials=creds, project=creds_json['project_id'])


def exec_query(query, **kwargs) -> bigquery.table.RowIterator:
    job = bigquery_client.query(query, **kwargs)
    return job.result()


@routes.view('/sources')
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
        response = []
        async with db.transaction():
            async for s in Source.query.order_by(Source.id).gino.iterate():
                validated = self.schema.from_orm(s)
                response.append(validated.dict())
        return web.json_response(response)

    async def post(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        response = []
        try:
            raw_data = await self.request.json()
            incoming = self.schema(**raw_data)
            async with db.transaction():
                await Source.create(**incoming.private_dict())
                async for s in Source.query.order_by(Source.id).gino.iterate():
                    response.append(self.schema.from_orm(s).dict())
        except Exception as e:
            raise web.HTTPBadRequest
        return web.json_response(response)

    async def delete(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        raw_data = await self.request.json()
        incoming = self.schema(**raw_data)
        response = []
        async with db.transaction():
            await Source.delete.where(Source.id == incoming.id).gino.status()
            async for s in Source.query.order_by(Source.id).gino.iterate():
                validated = self.schema.from_orm(s)
                response.append(validated.dict())
        return web.json_response(response)


@routes.view(r'/sources/{id:\d+}/stats')
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
        source_id = int(self.request.match_info['id'])
        async with db.transaction():
            source = await Source.get(source_id)
        dict_source = source.to_dict()
        source_config = json.loads(source.config_json)
        table_fullname = source_config['table_fullname']
        if not table_fullname:
            raise web.HTTPConflict(text="table_fullname not defined in source config")
        availability_intervals = await select_source(source).list_availability_intervals(
            interval=3600,
            table_fullname=table_fullname
        )
        dict_source['available_intervals'] = []
        for res in availability_intervals:
            dict_source['available_intervals'].append([res[0], res[1]])
        return web.json_response(self.schema.dump(dict_source))

    async def delete(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        source_id = int(self.request.match_info['id'])
        async with db.transaction():
            res = await Source.delete.where(Source.id == source_id).gino.status()
        return web.json_response(res)
