from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_tables
from app.routers import events


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()


    # async def periodic_sync():
    #     sync_service = SyncService()
    #     while True:
    #         try:
    #             async for session in get_session():
    #                 repo = PostgresEventRepository(session)
    #                 await sync_service.sync_events(repo)
    #                 break
    #         except Exception as e:
    #             print(f"Sync error: {e}")
    #
    #         await asyncio.sleep(300)
    #
    # task = asyncio.create_task(periodic_sync())

    yield
    # task.cancel()
    # await task


app = FastAPI(lifespan=lifespan)

app.include_router(events.router)

