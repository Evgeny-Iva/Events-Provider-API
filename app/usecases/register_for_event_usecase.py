from app.repositories.events.interface import EventRepository
from app.shemas.registration import RegistrationRequest
from app.models import Registration, Event


class RegisterForEventUsecase:
    """UseCase для регистрации на событие."""

    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def do(self, event_id: str, data: RegistrationRequest) -> Registration:
        """Зарегистрировать пользователя на событие"""
        registration = await self.repo.register(
            first_name=data.first_name,
            last_name=data.last_name,
            seat=data.seat,
            email=str(data.email),
            event_id=event_id
        )

        return registration

    async def get_event(self, event_id: str) -> Event | None:
        """Получить событие по ID"""
        return await self.repo.get(event_id)