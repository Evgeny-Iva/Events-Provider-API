from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging


from app.database import get_session
from app.repositories.events.postgres import PostgresEventRepository
from app.shemas.registration import RegistrationRequest, RegistrationResponse
from app.usecases.cancel_registration_usecase import CancelRegistrationUsecase
from app.usecases.get_events_usecase import GetEventsUsecase
from app.shemas.events import EventListResponse, Paginator
from app.usecases.register_for_event_usecase import RegisterForEventUsecase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

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


def get_register_usecase(
        repo: PostgresEventRepository = Depends(get_postgres_repository)
) -> RegisterForEventUsecase:
    return RegisterForEventUsecase(repo)


@router.post("/{event_id}/register", response_model=RegistrationResponse)
async def register_for_event(
        event_id: str,
        data: RegistrationRequest,
        usecase: RegisterForEventUsecase = Depends(get_register_usecase)
):
    """Зарегистрировать пользователя на событие."""
    try:
        registration = await usecase.do(event_id, data)

        return RegistrationResponse(
            ticket_id=registration.ticket_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


def get_cancel_registration_usecase(
    repo: PostgresEventRepository = Depends(get_postgres_repository)
) -> CancelRegistrationUsecase:
    return CancelRegistrationUsecase(repo)


@router.post("/{event_id}/unregister")
async def unregister_from_event(
    ticket_id: str,
    usecase: CancelRegistrationUsecase = Depends(
        get_cancel_registration_usecase
    )
):
    """Отменить регистрацию на событие."""
    try:
        await usecase.do(ticket_id)
        return {"message": "Регистрация отменена", "ticket_id": ticket_id}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")