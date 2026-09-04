import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_seats(client: AsyncClient, api_key: str, test_event: str):
    """Проверка получение списка свободных мест"""
    event_id = test_event
    response = await client.get(
        f"/api/events/{event_id}/seats/",
        headers={"api-key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "event_id" in data
    assert "available_seats" in data
    assert data["count"] == 10

@pytest.mark.asyncio
async def test_get_seats_event_not_found(client: AsyncClient, api_key: str):
    """Проверка получение списка свободных мест с неверным uuid события"""
    response = await client.get(
        "/api/events/12345678-1234-1234-1234-123456789012/seats/",
        headers={"api-key": api_key}
    )
    assert response.status_code == 404