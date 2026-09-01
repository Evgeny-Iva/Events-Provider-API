from app.repositories.events.interface import EventRepository


class GetAvailableSeatUsecase:
    """UseCase для получение свободных мест"""
    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def do(self, event_id: str):
        """Получение свободных мест"""
        seats = await self.repo.get_available_seats(event_id)
        return seats
