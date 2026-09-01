import typing

from app.models import Event, Registration, Place, Seat
from app.shemas.events import Paginator
from app.shemas.registration import RegistrationRequest


class EventRepository(typing.Protocol):
    "Интерфейс репозитория для работы с событиями"
    async def get(self, event_id: str) -> Event | None:
        """Получить событие по ID"""
        raise NotImplementedError()

    async def get_all(self, paginator: Paginator)  -> list[Event]:
        """Получить список событий с фильтрацией"""
        raise NotImplementedError()

    async def save(self, event: Event) -> Event:
        """Сохранить событие (создать или обновить)"""
        raise NotImplementedError()

    async def delete(self, event_id: str) -> bool:
        """Удалить событие по ID"""
        raise NotImplementedError()

    async def register(
            self,
            event_id: str,
            first_name: str,
            last_name: str,
            seat: str,
            email: str
    ) -> Registration:
        """Регистрация на событие"""
        raise NotImplementedError()

    async def cancel_registration(self, registration_id: str) -> bool:
        """Отмена регистрации на событие"""
        raise NotImplementedError()

    async def create_place_with_seats(self, place_data: dict) -> Place:
        """Создает места по паттерну"""
        raise NotImplementedError()

    async def get_seat_by_number(
            self, event_id: str, seat_number: str
    ) -> Seat | None:
        """Получаем номер места"""
        raise NotImplementedError()