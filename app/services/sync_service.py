from app.repositories.events.external import ExternalEventRepository
from app.repositories.events.postgres import PostgresEventRepository
from app.schemas.events import Paginator
from app.clients.events_provider_client import EventsProviderClient


class SyncService:
    def __init__(self):
        self.client = EventsProviderClient()
        self.external_repo = ExternalEventRepository(self.client)

    async def sync_events(self, postgres_repo: PostgresEventRepository):
        paginator = Paginator(
            limit=2,
            changed_at="2026-09-05"
        )
        api_events = await self.external_repo.get_all(paginator)

        for event in api_events:
            await postgres_repo.save(event)