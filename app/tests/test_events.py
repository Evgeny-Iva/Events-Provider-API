import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_events(client: AsyncClient, api_key: str):
    """Проверка получение списка событий"""
    response = await client.get(
        "/api/events/?limit=10",
        headers={"api-key": api_key}
    )
    assert response.status_code == 200
    assert "data" in response.json()
    assert "meta" in response.json()

@pytest.mark.asyncio
async def test_get_events_invalid_api_key(client: AsyncClient):
    """Проверка получение списка событий с неверным api key"""
    response = await client.get(
        "/api/events/?limit=10/",
        headers={"api-key": "wrong-key"}
    )
    assert response.status_code == 401