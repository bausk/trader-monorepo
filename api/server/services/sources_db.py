from dbmodels.source_models import SourceSchema, SourceSchemaWithStats
from dbmodels.db import db, Source, BaseModel
from typing import List, Type


schema: Type[BaseModel] = SourceSchema
detailed_schema: Type[BaseModel] = SourceSchemaWithStats
model: db.Model = Source


async def sources_get() -> List[SourceSchemaWithStats]:
    response: List[SourceSchemaWithStats] = []
    async with db.transaction():
        async for s in model.query.order_by(model.id).gino.iterate():
            response.append(schema.from_orm(s))
    return response


async def source_create(data: SourceSchema) -> List[SourceSchema]:
    response = []
    async with db.transaction():
        await model.create(**data.private_dict())
        async for s in model.query.order_by(model.id).gino.iterate():
            response.append(schema.from_orm(s))
    return response


async def source_delete(data: SourceSchema) -> List[SourceSchema]:
    response = []
    async with db.transaction():
        await model.delete.where(model.id == data.id).gino.status()
        async for s in model.query.order_by(model.id).gino.iterate():
            response.append(schema.from_orm(s))
    return response
