from dbmodels.session_models import (
    BacktestSessionInputSchema,
    BacktestSessionSourceModel,
)
from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from server.security import check_permission, Permissions
from typing import Type
from dbmodels.db import (
    db,
    StrategyModel,
    BacktestSessionModel,
    BacktestSessionSchema,
    BaseModel,
)
from dbmodels.source_models import Source
from utils.processing.processor import start_subprocess_and_listen
from server.endpoints.routedef import routes
from server.utils.streaming import create_streaming_response
from ticker.backtest_loop import backtest


CORS_CONFIG = {
    "*": ResourceOptions(
        allow_credentials=True,
        allow_headers="*",
        expose_headers="*",
    )
}


@routes.view(r"/backtesting")
class BacktestSessionView(web.View, CorsViewMixin):
    """Initiate a backtest"""

    cors_config = CORS_CONFIG
    schema: Type[BaseModel] = BacktestSessionSchema

    async def post(self: web.View) -> Response:
        await check_permission(self.request, Permissions.READ_HISTORY)
        raw_data = await self.request.json()
        incoming: BacktestSessionInputSchema = BacktestSessionInputSchema(**raw_data)

        async with db.transaction():
            new_session_model = await BacktestSessionModel.create(
                **incoming.private_dict(without=["sources_ids"])
            )
            if incoming.sources_ids:
                for order, source_id in enumerate(incoming.sources_ids):
                    await BacktestSessionSourceModel.create(
                        backtest_session_id=new_session_model.id,
                        source_id=source_id,
                        order=order + 1,
                    )
            query = (
                BacktestSessionModel.outerjoin(BacktestSessionSourceModel)
                .outerjoin(Source)
                .select()
            )
            session_with_sources = (
                await query.where(BacktestSessionModel.id == new_session_model.id)
                .gino.load(
                    BacktestSessionModel.distinct(BacktestSessionModel.id).load(
                        add_source=Source.distinct(Source.id)
                    )
                )
                .all()
            )
            session = self.schema.from_orm(session_with_sources[0])
            session.config_json = {"tick_duration_seconds": 8}
            strategy = await StrategyModel.get(
                BacktestSessionModel.strategy_id == session.strategy_id
            )
            try:
                iterator = start_subprocess_and_listen(backtest, session, strategy)
                return await create_streaming_response(self.request, iterator)
            except Exception as e:
                print(e)
                raise web.HTTPBadRequest
