import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Event, Registration, Place, Seat
from app.repositories.events.interface import EventRepository
from app.shemas.events import Paginator
from app.utils.seat_parser import parser_seats_patern
from app.core.exceptions import SeatNotFoundError, SeatNotAvailableError


class PostgresEventRepository(EventRepository):
    """
    Реализация репозитория для PostgreSQL.
    Здесь мы пишем SQL-запросы (через SQLAlchemy).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, event_id: str) -> Event | None:
        """Получить событие по UUID."""
        result = await self.session.execute(
            select(Event).where(Event.uuid == event_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, paginator: Paginator) -> list[Event]:
        """Получение списка событий"""
        query = select(Event)

        filters = []
        if paginator.status:
            filters.append(Event.status == paginator.status)

        if paginator.from_date:
            filters.append(Event.event_time >= paginator.from_date)

        if paginator.to_date:
            filters.append(Event.event_time <= paginator.to_date)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Event.event_time.desc())
        query = query.limit(paginator.limit).offset(paginator.offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def save(self, event: Event) -> Event:
        """Сохранить событие в БД"""
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def delete(self, event_id: str) -> bool:
        """Удалить событие из БД"""
        event = await self.get(event_id)
        if not event:
            return False
        await self.session.delete(event)
        await self.session.commit()
        return True

    async def _parse_seat(self, seat_number: str) -> tuple[str, int] | None:
        """Парсит номер места из строки"""
        match = re.match(r"^([A-Z]+)(\d+)$", seat_number)
        if not match:
            return None

        return match.group(1), int(match.group(2))

    async def get_seat_by_number(
            self, event_id: str, seat_number: str, lock: bool = False
    ) -> Seat | None:
        """Находит место (Seat) по номеру места и идентификатору события"""
        parsed = await self._parse_seat(seat_number)
        if not parsed:
            return None

        section, number = parsed

        query = select(Seat).join(
            Place, Place.uuid == Seat.place_id
        ).join(
            Event, Event.place_id == Place.uuid
        ).where(
            Event.uuid == event_id,
            Seat.section == section,
            Seat.seat_number == number
        )

        if lock:
            query = query.with_for_update()

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def register(
            self,
            event_id: str,
            first_name: str,
            last_name: str,
            seat: str,
            email: str
    ) -> Registration:
        """Регистрация на событие"""
        try:
            seat_obj = await self.get_seat_by_number(event_id, seat, lock=True)

            if not seat_obj:
                raise SeatNotFoundError(f"Место {seat} не найдено")

            if seat_obj.is_available == False:
                raise SeatNotAvailableError(f"Место {seat} уже занято")

            registration = Registration(
                first_name=first_name,
                last_name=last_name,
                seat_id=seat_obj.id,
                email=email,
                event_id=event_id
            )

            self.session.add(registration)
            seat_obj.is_available = False
            await self.session.commit()
            await self.session.refresh(registration)

            return registration

        except Exception:
            await self.session.rollback()
            raise

    async def get_registration_by_ticket(self, ticket_id: str) -> Registration | None:
        """Найти регистрацию по ticket_id"""
        result = await self.session.execute(
            select(Registration).where(Registration.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def cancel_registration(self, ticket_id: str) -> bool:
        """Отмена регистрации на событие"""
        try:
            result = await self.session.execute(
                select(Registration).where(Registration.ticket_id == ticket_id)
            )
            registration = result.scalar_one_or_none()

            if not registration:
                return False

            seat_result = await self.session.execute(
                select(Seat).where(Seat.id == registration.seat_id)
            )
            seat = seat_result.scalar_one_or_none()

            if seat:
                seat.is_available = True

            await self.session.delete(registration)
            await self.session.commit()

            return True

        except Exception:
            await self.session.rollback()
            raise

    async def get_available_seat(self, event_id) -> dict:
        """Получение свободных мест на событие"""
        query = select(Seat).join(
            Place, Place.uuid == Seat.place_id
        ).join(
            Event, Event.place_id == Place.uuid
        ).where(
            Event.uuid == event_id,
            Seat.is_available == True
        )

        result = await self.session.execute(query)
        return result.scalars().all()