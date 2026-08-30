from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging


from app.database import get_session
from app.repositories.events.postgres import PostgresEventRepository
from app.usecases.get_events_usecase import GetEventsUsecase
from app.shemas.events import EventListResponse, Paginator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])

def get_postgres_repository(session: AsyncSession = Depends(get_session)):
    """Создает репозиторий для работы с PostgreSQL"""
    return PostgresEventRepository(session)


def get_events_usecase(
        repo: PostgresEventRepository = Depends(get_postgres_repository)
):
    """Создает UseCase с обоими репозиториями"""
    return GetEventsUsecase(repo)


@router.get("/", response_model=EventListResponse)
async def get_events(
        paginator: Paginator = Depends(),
        usecase: GetEventsUsecase = Depends(get_events_usecase)
):
    """Получить список событий."""
    try:
        events = await usecase.do(paginator)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return EventListResponse(
        data=events,
        meta={
            "limit": paginator.limit,
            "offset": paginator.offset,
            "total": len(events)
        }
    )