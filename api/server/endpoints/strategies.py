import json
from datetime import datetime
from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from dbmodels.db import db, StrategyModel, LiveSessionModel, LiveSessionSchema, StrategySchema, BaseModel
from server.security import check_permission, Permissions
from typing import Type
from utils.sources.select import select_source
from server.endpoints.routedef import routes


CORS_CONFIG = {
    "*": ResourceOptions(
        allow_credentials=True,
        allow_headers="*",
        expose_headers="*",
    )
}


@routes.view('/strategies')
class StrategiesView(web.View, CorsViewMixin):
    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = StrategySchema

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        response = []
        async with db.transaction():
            async for s in StrategyModel.query.order_by(StrategyModel.id).gino.iterate():
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
                await StrategyModel.create(**incoming.private_dict())
                async for s in StrategyModel.query.order_by(StrategyModel.id).gino.iterate():
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
            await StrategyModel.delete.where(StrategyModel.id == incoming.id).gino.status()
            async for s in StrategyModel.query.order_by(StrategyModel.id).gino.iterate():
                validated = self.schema.from_orm(s)
                response.append(validated.dict())
        return web.json_response(response)


@routes.view(r'/strategies/{id:\d+}')
class StrategyDetailView(web.View, CorsViewMixin):
    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = StrategySchema

    async def get(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        strategy_id = int(self.request.match_info['id'])
        async with db.transaction():
            source = await StrategyModel.get(strategy_id)
        source_model = self.schema.from_orm(source)
        source_config = json.loads(source_model.config_json)
        table_fullname = source_config['table_name']
        if not table_fullname:
            raise web.HTTPConflict(text="table_name not defined in source config")
        availability_intervals = await select_source(source).list_availability_intervals(
            interval=3600,
            table_fullname=table_fullname
        )
        source_model.available_intervals = []
        for res in availability_intervals:
            source_model.available_intervals.append([res[0], res[1]])
        return web.json_response(body=source_model.json())

    async def put(self: web.View) -> Response:
        await check_permission(self.request, Permissions.WRITE_OBJECTS)
        strategy_id = int(self.request.match_info['id'])
        response = None
        try:
            raw_data = await self.request.json()
            incoming = self.schema(**raw_data)
            async with db.transaction():
                obj = await StrategyModel.get(strategy_id)
                await obj.update(**incoming.private_dict()).apply()
                response = self.schema.from_orm(await StrategyModel.get(strategy_id))
        except Exception as e:
            raise web.HTTPBadRequest

        return web.json_response(response.dict())


@routes.view(r'/strategies/{id:\d+}/live')
class StrategyLiveView(web.View, CorsViewMixin):
    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = StrategySchema

    async def put(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ)
        try:
            strategy_id = int(self.request.match_info['id'])
            raw_data = await self.request.json()
            should_live = bool(raw_data['live'])
            async with db.transaction():
                strategy = await StrategyModel.get(strategy_id)
                strategy_model = self.schema.from_orm(strategy)
                strategy_is_live = bool(strategy_model.live_session_id)
                if strategy_is_live == should_live:
                    return web.json_response(strategy_model.dict())
                if should_live:
                    session = LiveSessionSchema(
                        start_datetime=datetime.now()
                    )
                    session.config_json = strategy_model.config_json
                    live_session = await LiveSessionModel.create(**session.private_dict())
                    strategy_model.live_session_id = live_session.id
                    await strategy.update(**strategy_model.private_dict()).apply()
                else:
                    live_session = await LiveSessionModel.get(strategy_model.live_session_id)
                    session = LiveSessionSchema.from_orm(live_session)
                    session.end_datetime = datetime.now()
                    await live_session.update(**session.private_dict()).apply()
                    strategy_model.live_session_id = None
                    await strategy.update(live_session_id=None).apply()
            return web.json_response(strategy_model.dict())
        except Exception as e:
            raise web.HTTPBadRequest
