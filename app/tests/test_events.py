import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_events(client: AsyncClient, api_key: str, test_event: str):
    """Проверка получение описания события событий"""
    event_id = test_event
    response = await client.get(
        f"/api/events/{event_id}",
        headers={"api-key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "place" in data


@pytest.mark.asyncio
async def test_get_all_events_invalid_event_id(
        client: AsyncClient,
        api_key: str,
):
    """Проверка получение описания события событий с неверным event_id"""
    response = await client.get(
        f"/api/events/12345678-1234-1234-1234-123456789012",
        headers={"api-key": api_key}
    )
    assert response.status_code == 404
    assert "detail" in response.json()



@pytest.mark.asyncio
async def test_get_all_events(client: AsyncClient, api_key: str):
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
        "/api/events/?limit=10",
        headers={"api-key": "wrong-key"}
    )
    assert response.status_code == 401