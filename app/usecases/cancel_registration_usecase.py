from app.repositories.events.interface import EventRepository


class CancelRegistrationUsecase:
    """UseCase для отмены регистрации."""

    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def do(self, event_id: str, ticket_id: str) -> bool:
        """Отмена регистрации"""
        result = await self.repo.get_registration_by_ticket(ticket_id)

        if not result:
            raise ValueError(f"Регистрация по ticket_id {ticket_id} не найдена")

        if result.event_id != event_id:
            raise ValueError("Билет не принадлежит этому событию")

        return await self.repo.cancel_registration(result.id)