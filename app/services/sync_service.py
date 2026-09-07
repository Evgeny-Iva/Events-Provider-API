from app.repositories.events.external import ExternalEventRepository
from app.repositories.events.postgres import PostgresEventRepository
from app.schemas.events import Paginator
from app.clients.events_provider_client import EventsProviderClient
import traceback


class SyncService:
    def __init__(self):
        self.client = EventsProviderClient()
        self.external_repo = ExternalEventRepository(self.client)

    async def sync_events(self, postgres_repo: PostgresEventRepository):
        paginator = Paginator(limit=1000, changed_at="2000-01-01")

        api_events = await self.external_repo.get_all(paginator)

        for idx, event in enumerate(api_events):
            try:
                if not event.place:
                    continue

                await postgres_repo.save_or_update(event)

            except Exception as e:
                print(f"Ошибка при обработке события {idx + 1}:")
                print(f"Тип ошибки: {type(e).__name__}")
                print(f"Сообщение: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                await postgres_repo.session.rollback()
                raise