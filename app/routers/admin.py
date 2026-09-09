from fastapi import HTTPException, APIRouter
import logging

from app.database import get_session
from app.repositories.events.postgres import PostgresEventRepository
from app.services.sync_service import SyncService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/sync/trigger")
async def trigger_sync():
    """Ручной запуск синхронизации."""
    try:
        async with get_session() as session:
            repo = PostgresEventRepository(session)
            sync_service = SyncService()
            await sync_service.sync_events(repo)
        return {"status": "sync completed"}
    except Exception as e:
        raise HTTPException(500, f"Sync failed: {e}")
