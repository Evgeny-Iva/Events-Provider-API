import typing

from app.models import Event
from app.shemas.events import Paginator


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