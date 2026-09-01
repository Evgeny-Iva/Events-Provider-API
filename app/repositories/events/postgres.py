import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Event, Registration, Place, Seat
from app.repositories.events.interface import EventRepository
from app.shemas.events import Paginator
from app.utils.seat_parser import parser_seats_patern


class PostgresEventRepository(EventRepository):
    """
    Реализация репозитория для PostgreSQL.
    Здесь мы пишем SQL-запросы (через SQLAlchemy).
    """

    def __init__(self, session: AsyncSession):
        self.session = session


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
            self, event_id: str, seat_number: str
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
        seat_obj = await self.get_seat_by_number(event_id, seat)

        if not seat_obj:
            raise ValueError(f"Место {seat} не найдено")

        if seat_obj.is_available == False:
            raise ValueError(f"Место {seat} уже занято")

        registration = Registration(
            first_name=first_name,
            last_name=last_name,
            seat=seat,
            email=email,
            event_id=event_id
        )

        self.session.add(registration)
        seat_obj.is_available = False
        await self.session.commit()
        await self.session.refresh(registration)

        return registration

    async def cancel_registration(self, ticket_id: str) -> bool:
        """Отмена регистрации на событие"""
        result = await self.session.execute(
            select(Registration).where(Registration.ticket_id == ticket_id)
        )
        registration = result.scalar_one_or_none()

        if not registration:
            return False

        seat_obj = await self.session.execute(
            select(Seat).where(Seat.id == registration.seat_id)
        )

        if seat_obj:
            seat_obj.is_available = True

        await self.session.delete(registration)
        await self.session.commit()

        return True

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