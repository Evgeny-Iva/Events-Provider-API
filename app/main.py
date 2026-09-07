import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import create_tables, get_session
from app.repositories.events.postgres import PostgresEventRepository
from app.routers import events
from app.services.sync_service import SyncService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()

    async def periodic_sync():
        sync_service = SyncService()
        while True:
            try:
                async with get_session() as session:
                    repo = PostgresEventRepository(session)
                    await sync_service.sync_events(repo)
            except Exception as e:
                print(f"Sync error: {e}")

            await asyncio.sleep(24*60*60)

    task = asyncio.create_task(periodic_sync())

    yield
    task.cancel()
    await task


app = FastAPI(lifespan=lifespan)

app.include_router(events.router)

