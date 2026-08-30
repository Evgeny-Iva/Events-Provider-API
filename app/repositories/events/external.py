from app.models import Event
from app.repositories.events.interface import EventRepository
from app.clients.events_provider_client import EventsProviderClient
from app.shemas.events import Paginator


class ExternalEventRepository(EventRepository):
    """
    Реализация репозитория для внешнего API.
    Здесь делаем HTTP-запросы.
    """

    def __init__(self, client: EventsProviderClient):
        self.client = client


    async def get_all(self, paginator: Paginator) -> list[Event]:
        """Получить список событий из внешнего API"""
        params = paginator.model_dump(exclude_none=True)
        raw_events = await self.client.get_all_events(params=params)

        events = []
        for raw in raw_events:
            event = Event(**raw)
            events.append(event)

        return events
