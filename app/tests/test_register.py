import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient, api_key: str, test_event: str):
    """Проверка регистрации на мероприятие"""
    event_id = test_event
    data = {
        "first_name": "Peta",
        "last_name": "Ivan",
        "seat": "A1",
        "email": "ivan@example.com"
    }
    response = await client.post(
        f"/api/events/{event_id}/register",
        headers={"api-key": api_key},
        json=data
    )
    assert response.status_code == 200
    assert "ticket_id" in response.json()

@pytest.mark.asyncio
async def test_register_seat_taken(
        client: AsyncClient,
        api_key: str,
        test_event: str
):
    """Проверка на невозможность зарегистрироваться на занятое место"""
    event_id = test_event
    data = {
        "first_name": "Peta",
        "last_name": "Ivan",
        "seat": "A1",
        "email": "ivan@example.com"
    }

    await client.post(
        f"/api/events/{event_id}/register",
        headers={"api-key": api_key},
        json=data
    )

    response = await client.post(
        f"/api/events/{event_id}/register",
        headers={"api-key": api_key},
        json=data
    )
    assert response.status_code == 400
    assert "already sold" in response.text


@pytest.mark.asyncio
async def test_register_concurrent(
        client: AsyncClient,
        api_key: str,
        test_event: str
):
    """
    Проверка, что два пользователя не могут занять одно место одновременно.
    """
    event_id = test_event

    user1 = {
        "first_name": "Анна",
        "last_name": "Петрова",
        "seat": "A1",
        "email": "anna@example.com"
    }
    user2 = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "seat": "A1",
        "email": "ivan@example.com"
    }

    async def register_user(data):
        return await client.post(
            f"/api/events/{event_id}/register",
            headers={"api-key": api_key},
            json=data
        )

    responses = await asyncio.gather(
        register_user(user1),
        register_user(user2)
    )

    statuses = [r.status_code for r in responses]

    assert statuses.count(200) == 1, (
        f"Ожидался ровно один успешный ответ,"
        f"получено: {statuses.count(200)}"
    )

    assert statuses.count(400) == 1, (
        f"Ожидался ровно один ответ с ошибкой 400,"
        f"получено: {statuses.count(400)}"
    )

    for r in responses:
        if r.status_code == 400:
            assert ("already sold" in r.text.lower()
                    or "занято" in r.text.lower())