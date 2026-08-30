from app.repositories.events.interface import EventRepository
from app.shemas.events import Paginator


class GetEventsUsecase:
    """UseCase для получения списка событий"""

    def __init__(self, events: EventRepository):
        """Внедряем репозиторий через конструктор"""
        self.events = events

    async def do(self, paginator: Paginator):
        """Получить список событий с пагинацией."""
        return await self.events.get_all(paginator)