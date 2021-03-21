from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import aggregate_order_by
from dbmodels.db import db
from dbmodels.session_models import BacktestSessionInputSchema, BacktestSessionModel, BacktestSessionSchema, BacktestSessionSourceModel
from typing import List


model: db.Model = BacktestSessionModel


async def get_sessions_with_cached_data(session: BacktestSessionInputSchema) -> List[BacktestSessionSchema]:
    response: List[BacktestSessionSchema] = []
    sources_ids = session.sources_ids
    async with db.transaction():
        query = (
            db.select(BacktestSessionModel)
            .select_from(BacktestSessionModel.join(BacktestSessionSourceModel))
            .where(and_(
                BacktestSessionModel.cached_session_id == None,
                BacktestSessionModel.finished_datetime.isnot(None),
                BacktestSessionModel.start_datetime <= session.start_datetime,
                BacktestSessionModel.end_datetime >= session.end_datetime,
            ))
            .group_by(BacktestSessionModel.id)
            .having(
                db.func.array_agg(
                    aggregate_order_by(
                        BacktestSessionSourceModel.source_id,
                        BacktestSessionSourceModel.source_id.asc()
                    )
                ) == sources_ids
            )
        )
        async for s in query.gino.iterate():
            response.append(BacktestSessionSchema.from_orm(s))
    return response
