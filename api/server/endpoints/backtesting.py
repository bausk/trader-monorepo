import asyncio

from aiohttp import web
from aiohttp.web import Response
from aiohttp_cors import CorsViewMixin, ResourceOptions
from typing import Type
from utils.timeseries.constants import DATA_TYPES
from dbmodels.session_models import (
    BacktestSessionInputSchema,
    BacktestSessionSourceModel,
)
from dbmodels.db import (
    db,
    StrategyModel,
    BacktestSessionModel,
    BacktestSessionSchema,
    BaseModel,
)
from dbmodels.source_models import Source
from server.endpoints.routedef import routes
from server.security import check_permission, Permissions
from server.services.sessions_db import get_sessions_with_cached_data
from server.utils.streaming import create_streaming_response
from ticker.backtest_loop import backtest
from utils.processing.processor import start_subprocess_and_listen


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
            sessions = await get_sessions_with_cached_data(incoming)
            if len(sessions) > 0:
                incoming.cached_session_id = sessions[0].id
            else:
                incoming.cached_session_id = None

            new_session_model = await BacktestSessionModel.create(
                **incoming.private_dict(without=['sources_ids', 'sample_rate', 'subprocess'])
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
            # session.backtest_sources contain sources bound to this session
            session.config_json = {
                "tick_duration_seconds": incoming.sample_rate,
                "subprocess": incoming.subprocess,
            }
            strategy = await StrategyModel.get(session.strategy_id)
            for source in session.backtest_sources:
                if source.config_json["label"] == "btcuah":
                    source.config_json["data_type"] = DATA_TYPES.ticks_secondary
                else:
                    source.config_json["data_type"] = DATA_TYPES.ticks_primary
            try:
                from utils.processing.async_queue import AsyncProcessQueue

                db_q = AsyncProcessQueue()

                async def execute_backwrite():
                    value = await db_q.coro_get()
                    await (
                        BacktestSessionModel.update.values(**value)
                        .where(BacktestSessionModel.id == session.id)
                        .gino.status()
                    )
                    print("Executed backwrite")

                asyncio.create_task(execute_backwrite())
                iterator = start_subprocess_and_listen(
                    backtest, session, strategy, db_q=db_q
                )
                return await create_streaming_response(self.request, iterator)
            except Exception as e:
                print(e)
                raise web.HTTPBadRequest
