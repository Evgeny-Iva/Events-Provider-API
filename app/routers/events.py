from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.exceptions import (
    SeatNotFoundError,
    SeatNotAvailableError,
    EventNotFoundError,
    EventNotPublishedError
)
from app.dependencies.auth import verify_api_key
from app.usecases import *
from app.database import get_session
from app.repositories.events.postgres import PostgresEventRepository
from app.shemas.registration import RegistrationRequest, RegistrationResponse
from app.shemas.events import EventListResponse, Paginator


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
        usecase: GetEventsUsecase = Depends(get_events_usecase),
        api_key: str = Depends(verify_api_key)
):
    """Получить список событий."""
    try:
        if (
            paginator.from_date
            and not isinstance(paginator.from_date, datetime)
        ):
            raise HTTPException(
                status_code=400,
                detail={
                    "from_date": ["Enter a valid date."]
                }
            )

        events = await usecase.do(paginator)

        return EventListResponse(
            data=events,
            meta={
                "limit": paginator.limit,
                "offset": paginator.offset,
                "total": len(events)
            }
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail={"detail": str(e)}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(
            status_code=500,
            detail={"detail": "Internal server error"}
        )


def get_register_usecase(
        repo: PostgresEventRepository = Depends(get_postgres_repository)
) -> RegisterForEventUsecase:
    return RegisterForEventUsecase(repo)


@router.post("/{event_id}/register", response_model=RegistrationResponse)
async def register_for_event(
        event_id: str,
        data: RegistrationRequest,
        usecase: RegisterForEventUsecase = Depends(get_register_usecase),
        api_key: str = Depends(verify_api_key)
):
    """Зарегистрировать пользователя на событие."""
    try:
        registration = await usecase.do(event_id, data)

        return RegistrationResponse(
            ticket_id=registration.ticket_id,
        )

    except SeatNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    except SeatNotAvailableError:
        raise HTTPException(
            status_code=400,
            detail="This ticket is not available (already sold)."
        )

    except EventNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    except EventNotPublishedError:
        raise HTTPException(
            status_code=400,
            detail="Event is not published for registration"
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


def get_cancel_registration_usecase(
        repo: PostgresEventRepository = Depends(get_postgres_repository)
) -> CancelRegistrationUsecase:
    return CancelRegistrationUsecase(repo)


@router.post("/{event_id}/unregister")
async def unregister_from_event(
        event_id: str,
        ticket_id: str,
        api_key: str = Depends(verify_api_key),
        usecase: CancelRegistrationUsecase = Depends(
            get_cancel_registration_usecase
        )
):
    """Отменить регистрацию на событие."""
    try:
        await usecase.do(event_id, ticket_id)
        return {"message": "Регистрация отменена", "ticket_id": ticket_id}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


def get_available_seat_usecase(
        repo: PostgresEventRepository = Depends(get_postgres_repository)
) -> GetAvailableSeatsUsecase:
    return GetAvailableSeatsUsecase(repo)


@router.get("/{event_id}/seats")
async def get_available_seats(
        event_id: str,
        usecase: GetAvailableSeatsUsecase = Depends(get_available_seat_usecase),
        api_key: str = Depends(verify_api_key)
):
    try:
        event = await usecase.get_event(event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        if event.status != "published":
            raise HTTPException(
                status_code=400,
                detail="Event is not published for registration"
            )

        seats = await usecase.do(event_id)

        return {
            "event_id": event_id,
            "available_seats": [
                {
                    "section": seat.section,
                    "seat_number": seat.seat_number
                }
                for seat in seats
            ],
            "count": len(seats)
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении мест: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )