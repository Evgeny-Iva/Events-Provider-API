import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Event, Registration, Place, Seat
from app.repositories.events.interface import EventRepository
from app.schemas.events import Paginator
from app.core.exceptions import SeatNotFoundError, SeatNotAvailableError
from sqlalchemy.orm import joinedload


class PostgresEventRepository(EventRepository):
    """
    Реализация репозитория для PostgreSQL.
    Здесь мы пишем SQL-запросы (через SQLAlchemy).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, event_id: str) -> Event | None:
        """
        Возвращает полную информацию о событии, включая данные о площадке.

        Пример запроса:
        GET /api/event/event_id

        Пример ответа:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Концерт",
            "place":
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Крокус Сити Холл",
                "city": "Москва",
                "address": "ул. Международная, 20",
                "seats_pattern": "A1-100,B1-200"
            },
            "event_time": "2026-09-12T20:00:00+03:00",
            "registration_deadline": "2026-09-11T20:00:00+03:00",
            "status": "published",
            "number_of_visitors": 0
        }
        """
        result = await self.session.execute(
            select(Event)
            .where(Event.uuid == event_id)
            .options(joinedload(Event.place))
        )
        return result.scalar_one_or_none()

    async def get_all(
            self, paginator: Paginator
    ) -> tuple[list[Event], str | None, str | None]:
        """
        Возвращает список всех событий с пагинацией и фильтрацией.
        Данные берутся из локальной БД (синхронизируются с внешним API).

        Пример запроса:
        GET /api/event/

        Пример ответа:
        {
            "data": [
            {
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Концерт",
                "event_time": "2026-09-12T20:00:00+03:00",
                "registration_deadline": "2026-09-11T20:00:00+03:00",
                "status": "published",
                "number_of_visitors": 0,
                "place_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2026-09-01T10:00:00+03:00",
                "changed_at": "2026-09-05T10:00:00+03:00",
                "status_changed_at": null
            }
            ],
                "meta": {
                "limit": 100,
                "next": "/api/events/?cursor=123e4567...",
                "previous": null
            }
        }
        """
        query = select(Event)

        filters = []
        if paginator.changed_at:
            filters.append(Event.changed_at >= paginator.changed_at)

        if paginator.status:
            filters.append(Event.status == paginator.status)

        if paginator.from_date:
            filters.append(Event.event_time >= paginator.from_date)

        if paginator.to_date:
            filters.append(Event.event_time <= paginator.to_date)

        if paginator.cursor:
            try:
                cursor_uuid = uuid.UUID(paginator.cursor)
                filters.append(
                    Event.uuid > cursor_uuid)
            except ValueError:
                pass

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Event.changed_at.asc(), Event.uuid.asc())
        query = query.limit(paginator.limit + 1)

        result = await self.session.execute(query)
        events = result.scalars().all()

        next_cursor = None
        previous_cursor = None

        if len(events) > paginator.limit:
            next_cursor = str(events[-2].uuid)
            events = events[:-1]

        if paginator.cursor:
            try:
                cursor_uuid = uuid.UUID(paginator.cursor)
                prev_filters = filters.copy() if filters else []
                prev_filters.append(Event.uuid < cursor_uuid)

                prev_query = select(Event).where(and_(*prev_filters))
                prev_query = prev_query.order_by(Event.uuid.desc()).limit(
                    paginator.limit
                )

                prev_result = await self.session.execute(prev_query)
                prev_events = prev_result.scalars().all()

                if prev_events:
                    previous_cursor = str(prev_events[-1].uuid)
            except ValueError:
                pass

        return events, next_cursor, previous_cursor

    async def get_place(self, place_id: str) -> Place | None:
        """Получить площадку по UUID."""
        result = await self.session.execute(
            select(Place).where(Place.uuid == place_id)
        )
        return result.scalar_one_or_none()

    async def save_place(self, place: Place) -> Place:
        """Сохранить площадку в БД."""
        self.session.add(place)
        await self.session.commit()
        await self.session.refresh(place)
        return place

    async def get_available_seat(self, event_id) -> list[Seat]:
        """
        Возвращает список свободных мест на мероприятии.

        Пример запроса:
        GET /api/events/{event_id}/seats/

        Пример ответа:
        {
            "event_id": "123e4567-e89b-12d3-a456-426614174000",
            "available_seats":
            [
                {"section": "A", "seat_number": 1},
                {"section": "A", "seat_number": 2}
            ],
            "count": 2
        }
        """
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

    async def register(
            self,
            event_id: str,
            first_name: str,
            last_name: str,
            seat: str,
            email: str
    ) -> Registration:
        """
        Регистрация на событие.

        Пример запроса:
        POST /api/events/{event_id}/register/
        {
            "first_name": "Иван",
            "last_name": "Иванов",
            "seat": "A12",
            "email": "ivan@example.com"
        }

        Пример ответа:
        {
            "ticket_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        """
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

    async def cancel_registration(self, ticket_id: str) -> bool:
        """
        Отмена регистрации на событие.

        Пример запроса:
        POST /api/events/{event_id}/unregister/
        {
            "ticket_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        Пример ответа:
        {
            "success": true
        }
        """
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

    async def get_registration_by_ticket(self, ticket_id: str) -> Registration | None:
        """Найти регистрацию по ticket_id"""
        result = await self.session.execute(
            select(Registration).where(Registration.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

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

    async def save_or_update(self, event: Event) -> Event:
        """
        Сохранить или обновить событие с площадкой.
        """
        if event.place:
            place_uuid = event.place.uuid
            if isinstance(place_uuid, str):
                place_uuid = uuid.UUID(place_uuid)

            existing_place = await self.get_place(place_uuid)

            if existing_place:
                existing_place.name = event.place.name
                existing_place.city = event.place.city
                existing_place.address = event.place.address
                existing_place.seats_pattern = event.place.seats_pattern
                await self.session.flush()
                event.place_id = existing_place.uuid
            else:
                place = Place(
                    uuid=place_uuid,
                    name=event.place.name,
                    city=event.place.city,
                    address=event.place.address,
                    seats_pattern=event.place.seats_pattern,
                )
                self.session.add(place)
                await self.session.flush()
                event.place_id = place.uuid

            event.place = None

        if not event.place_id:
            raise ValueError(f"place_id не установлен для события {event.uuid}")

        event_uuid = event.uuid
        if isinstance(event_uuid, str):
            event_uuid = uuid.UUID(event_uuid)

        existing_event = await self.get(event_uuid)

        if existing_event:
            existing_event.name = event.name
            existing_event.event_time = event.event_time
            existing_event.registration_deadline = event.registration_deadline
            existing_event.status = event.status
            existing_event.number_of_visitors = event.number_of_visitors
            existing_event.changed_at = event.changed_at
            existing_event.created_at = event.created_at
            existing_event.status_changed_at = event.status_changed_at
            existing_event.place_id = event.place_id

            await self.session.commit()
            await self.session.refresh(existing_event)
            return existing_event
        else:

            new_event = Event(
                uuid=event_uuid,
                place_id=event.place_id,
                name=event.name,
                event_time=event.event_time,
                registration_deadline=event.registration_deadline,
                status=event.status,
                number_of_visitors=event.number_of_visitors,
                changed_at=event.changed_at,
                created_at=event.created_at,
                status_changed_at=event.status_changed_at
            )
            self.session.add(new_event)
            await self.session.commit()
            await self.session.refresh(new_event)
            return new_event