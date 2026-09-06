from app.models import Event
from app.repositories.events.interface import EventRepository


class GetEventUsecase:
    """UseCase для получения одного события по ID."""

    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def do(self, event_id: str) -> Event | None:
        """Получить событие по ID."""
        return await self.repo.get(event_id)