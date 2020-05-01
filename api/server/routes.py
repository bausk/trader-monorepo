from datetime import datetime
import pytz
import asyncio
import json
from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, Source, SourceSchema, SourceSchemaWithStats, SQLAlchemyAutoSchema
from server.security import check_permission, Permissions
from google.oauth2 import service_account
from google.cloud import bigquery
from secrets_management.manage import decrypt_credentials

routes = web.RouteTableDef()
credfile = decrypt_credentials(which=['./.secrets/keyring.json'])

print(credfile)
creds_json = json.loads(credfile[0])
creds = service_account.Credentials.from_service_account_info(creds_json)
bigquery_client = bigquery.Client(
    credentials=creds, project=creds_json['project_id'])


def exec_query(query, **kwargs) -> bigquery.table.RowIterator:
    job = bigquery_client.query(query, **kwargs)
    return job.result()

async def coroutine_job(job):
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
    schema: SQLAlchemyAutoSchema = SourceSchema()

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        response = []
        async with db.transaction():
            async for s in Source.query.order_by(Source.id).gino.iterate():
                response.append(self.schema.dump(s))
        return web.json_response(response)

    async def post(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        response = []
        try:
            raw_data = await self.request.json()
            validated_data = self.schema.load(raw_data)
            async with db.transaction():
                await Source.create(**validated_data)
                async for s in Source.query.order_by(Source.id).gino.iterate():
                    response.append(self.schema.dump(s))
        except Exception as e:
            raise web.HTTPBadRequest
        return web.json_response(response)

    async def delete(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        raw_data = await self.request.json()
        validated_data = self.schema.load(raw_data)
        obj = Source(**validated_data)
        response = []
        async with db.transaction():
            res = await Source.delete.where(Source.id == obj.id).gino.status()
            async for s in Source.query.order_by(Source.id).gino.iterate():
                response.append(self.schema.dump(s))
        return web.json_response(response)


@routes.view(r'/sources/{id:\d+}')
class SourcesView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
            expose_headers="*",
        )
    }
    schema: SQLAlchemyAutoSchema = SourceSchemaWithStats()

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        source_id = int(self.request.match_info['id'])
        async with db.transaction():
            source = await Source.get(source_id)
        source = source.to_dict()
        source['available_intervals'] = [
            [datetime(2018, 12, 12, tzinfo=pytz.UTC), datetime(2019, 2, 12, tzinfo=pytz.UTC)],
            [datetime(2019, 3, 12, tzinfo=pytz.UTC), datetime(2019, 4, 12, tzinfo=pytz.UTC)],
            [datetime(2019, 12, 12, tzinfo=pytz.UTC), datetime(2019, 12, 30, tzinfo=pytz.UTC)],
        ]
        sql_query = r"""
with
  c as (select *,
    TIMESTAMP_ADD(queried_at, INTERVAL 3600 SECOND) as queried_end,
    max(TIMESTAMP_ADD(queried_at, INTERVAL 3600 SECOND)) over (order by queried_at rows between unbounded preceding and 1 preceding) as previous_max
    from `livewater.production.kunaTicksBTCUAH`
  )
select queried_at, 
    coalesce(lead(previous_max) over (order by queried_at),
   (select max(queried_end) from c)
               ) as queried_end
from c 
where previous_max < queried_at 
   or previous_max is null
order by queried_at desc
limit 100
        """
        loop = asyncio.get_running_loop()
        bigquery_result = await loop.run_in_executor(None, exec_query, sql_query)
        source['available_intervals'] = []
        for res in bigquery_result:
            source['available_intervals'].append([res[0], res[1]])
        return web.json_response(self.schema.dump(source))

    async def delete(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        source_id = int(self.request.match_info['id'])
        async with db.transaction():
            res = await Source.delete.where(Source.id == source_id).gino.status()
        return web.json_response(res)
