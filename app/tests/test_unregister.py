import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unregister(client: AsyncClient, api_key: str, test_event: str):
    """Проверка отмены регистрации"""
    event_id = test_event

    data = {
        "first_name": "Peta",
        "last_name": "Ivan",
        "seat": "A2",
        "email": "ivan@example.com"
    }
    register_response = await client.post(
        f"/api/events/{event_id}/register/",
        headers={"api-key": api_key},
        json=data
    )
    assert register_response.status_code == 200
    ticket_id = register_response.json()["ticket_id"]

    response = await client.post(
        f"/api/events/{event_id}/unregister/?ticket_id={ticket_id}",
        headers={"api-key": api_key}
    )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_unregister_ticket_not_found(
        client: AsyncClient,
        api_key: str,
        test_event: str
):
    """Проверка отмены регистрации с не верным uuid мероприятия"""
    event_id = test_event
    response = await client.post(
        (f"/api/events/{event_id}/"
         f"unregister/?ticket_id=12345678-1234-1234-1234-123456789012"),
        headers={"api-key": api_key}
    )
    assert response.status_code == 404