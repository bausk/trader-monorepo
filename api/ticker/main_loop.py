import sys, traceback
import asyncio
import aiojobs

from dbmodels.db import db, StrategyModel, StrategySchema, BaseModel


BASE_TICK_TIME = 5


async def run_ticker(app):
    scheduler = await aiojobs.create_scheduler()
    tick_count = 0
    while True:
        tick_count += 1
        try:
            print('spawning job')
            timer = asyncio.create_task(asyncio.sleep(BASE_TICK_TIME))
            job = await scheduler.spawn(check_strategies(app, tick_count))
            await asyncio.wait({timer, job.wait()})
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)




async def check_strategies(app, tick_count):
    print(f'-- executing task {tick_count}...')
    strategies = []
    schema: Type[BaseModel] = StrategySchema
    async with db.transaction():
        async for s in StrategyModel.query.where(StrategyModel.is_live == True).order_by(StrategyModel.id).gino.iterate():
            validated = schema.from_orm(s)
            strategies.append(validated.dict())
    print('-- task done')
