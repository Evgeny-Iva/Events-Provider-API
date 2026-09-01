from app.repositories.events.interface import EventRepository


class CancelRegistrationUsecase:
    """UseCase для отмены регистрации."""

    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def do(self, ticket_id: str) -> bool:
        """Отмена регистрации"""
        result = await self.repo.cancel_registration(ticket_id)

        if not result:
            raise ValueError(f"Регистрация по ticket_id {ticket_id} не найдена")

        return result