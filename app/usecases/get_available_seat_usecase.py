from app.models import Event
from app.repositories.events.interface import EventRepository


class GetAvailableSeatsUsecase:
    """UseCase для получение свободных мест"""
    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def do(self, event_id: str) -> dict:
        """Получение свободных мест"""
        seats = await self.repo.get_available_seat(event_id)
        return seats

    async def get_event(self, event_id: str) -> Event | None:
        """Получить событие по ID"""
        return await self.repo.get(event_id)