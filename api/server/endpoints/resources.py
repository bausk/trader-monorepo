from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, Source, ResourceModel, ResourceSchema, BaseModel
from server.security import check_permission, Permissions
from typing import Type

from server.endpoints.routedef import routes


@routes.view('/resources')
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
        response = []
        primary_live_source = Source.alias()
        secondary_live_source = Source.alias()
        primary_backtest_source = Source.alias()
        secondary_backtest_source = Source.alias()
        async with db.transaction():
            async for s in self.model.load(
                primary_live_source_model=primary_live_source.on(
                    primary_live_source.id == self.model.primary_live_source_id
                )
            ).load(
                secondary_live_source_model=secondary_live_source.on(
                    secondary_live_source.id == self.model.secondary_live_source_id
                )
            ).load(
                primary_backtest_source_model=primary_backtest_source.on(
                    primary_backtest_source.id == self.model.primary_backtest_source_id
                )
            ).load(
                secondary_backtest_source_model=secondary_backtest_source.on(
                    secondary_backtest_source.id == self.model.secondary_backtest_source_id
                )
            ).order_by(self.model.id).gino.iterate():
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
                await self.model.create(**incoming.private_dict())
                async for s in self.model.query.order_by(self.model.id).gino.iterate():
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
            await self.model.delete.where(self.model.id == incoming.id).gino.status()
            async for s in self.model.query.order_by(self.model.id).gino.iterate():
                validated = self.schema.from_orm(s)
                response.append(validated.dict())
        return web.json_response(response)
