from dbmodels.db import db, Source, ResourceModel, ResourceSchema, BaseModel
from typing import List, Type


schema: Type[BaseModel] = ResourceSchema
model: db.Model = ResourceModel


async def resources_get_with_sources() -> List[ResourceSchema]:
    response: List[ResourceSchema] = []
    primary_live_source = Source.alias()
    secondary_live_source = Source.alias()
    primary_backtest_source = Source.alias()
    secondary_backtest_source = Source.alias()
    async with db.transaction():
        async for s in model.load(
            primary_live_source_model=primary_live_source.on(
                primary_live_source.id == model.primary_live_source_id
            )
        ).load(
            secondary_live_source_model=secondary_live_source.on(
                secondary_live_source.id == model.secondary_live_source_id
            )
        ).load(
            primary_backtest_source_model=primary_backtest_source.on(
                primary_backtest_source.id == model.primary_backtest_source_id
            )
        ).load(
            secondary_backtest_source_model=secondary_backtest_source.on(
                secondary_backtest_source.id == model.secondary_backtest_source_id
            )
        ).order_by(
            model.id
        ).gino.iterate():
            response.append(schema.from_orm(s))
    return response


async def resource_create(data: ResourceSchema) -> List[ResourceSchema]:
    response = []
    async with db.transaction():
        await model.create(**data.private_dict())
        async for s in model.query.order_by(model.id).gino.iterate():
            response.append(schema.from_orm(s))
    return response


async def resource_delete(data: ResourceSchema) -> List[ResourceSchema]:
    response = []
    async with db.transaction():
        await model.delete.where(model.id == data.id).gino.status()
        async for s in model.query.order_by(model.id).gino.iterate():
            response.append(schema.from_orm(s))
    return response
