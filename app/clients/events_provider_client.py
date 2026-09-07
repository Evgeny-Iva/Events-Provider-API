import httpx
from app.core.config import settings


class EventsProviderClient:
    """Клиент для взаимодействия с внешним API событий."""

    def __init__(self):
        self.base_url = settings.EXTERNAL_API_URL
        self.api_key = settings.EXTERNAL_API_KEY
        self.timeout = settings.EXTERNAL_API_TIMEOUT

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "X-API-Key": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    async def get_all_events(self, params: dict) -> list[dict]:
        """Получить список событий."""
        try:
            response = await self._client.get("/events", params=params)
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Ошибка: {e}")
            return []