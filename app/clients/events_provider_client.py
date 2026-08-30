import httpx
from typing import Dict
from app.core.config import settings


class EventsProviderClient:
    """Клиент для взаимодействия с внешним API событий."""

    def __init__(self):
        """Инициализация клиента с настройками из конфига"""
        self.base_url = settings.EXTERNAL_API_URL
        self.api_key = settings.EXTERNAL_API_KEY
        self.timeout = settings.EXTERNAL_API_TIMEOUT

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )


    async def get_all_events(self, params: Dict) -> list[Dict]:
        """Получить список событий."""
        try:
            response = await self._client.get("/events", params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("items", [])

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch events: {e}")


    async def register(self, event_id: str, first_name: str, seat: str) -> str: ...