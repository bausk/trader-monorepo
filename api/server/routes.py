from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, Source, SourceSchema
# from dbmodels.schemas import SourceSchema
from server.security import check_permission, Permissions


routes = web.RouteTableDef()


@routes.view('/sources')
class SourcesView(web.View, CorsViewMixin):
    cors_config = {
        "*": ResourceOptions(
            allow_credentials=True,
            allow_headers="*",
            expose_headers="*",
        )
    }
    schema = SourceSchema()
    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        sources = []
        async with db.transaction():
            async for s in Source.query.order_by(Source.id).gino.iterate():
                sources.append((s.id, s.type))
        return web.json_response(sources)

    async def post(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        sources = []
        try:
            raw_data = await self.request.json()
            load_data = self.schema.load(raw_data)
            async with db.transaction():
                await Source.create(**load_data)
                async for s in Source.query.order_by(Source.id).gino.iterate():
                    sources.append((s.id, s.type))
        except Exception as e:
            raise web.HTTPBadRequest
        return web.json_response(sources)
