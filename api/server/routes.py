from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, Source, SourceSchema, SQLAlchemyAutoSchema
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
