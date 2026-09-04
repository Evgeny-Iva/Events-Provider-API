import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine
from app.models import Event, Place, Seat
from app.utils.seat_parser import parser_seats_patern
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


@pytest_asyncio.fixture
async def client():
    """
    Фикстура выполняет:
    - Создание всех таблиц в БД перед тестом
    - Предоставляет тестовый клиент для отправки HTTP-запросов
    - Удаляет все данные из таблиц после теста
    - Закрывает подключение к БД после теста
    """
    async with engine.begin() as conn:
        from app.database import Base

        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
        await conn.commit()

    await engine.dispose()

@pytest_asyncio.fixture
def api_key():
    return "my-secret-key"

@pytest_asyncio.fixture
async def test_event():
    """Создаёт тестовое событие с местами и возвращает его UUID."""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        place_uuid = uuid.uuid4()
        place = Place(
            uuid=place_uuid,
            name="Тестовая площадка",
            city="Москва",
            address="ул. Тестовая, 1",
            seats_pattern="A1-10"
        )
        session.add(place)
        await session.flush()

        ranges = parser_seats_patern(place.seats_pattern)
        for r in ranges:
            for number in range(r["start"], r["end"] + 1):
                seat = Seat(
                    place_id=place_uuid,
                    section=r["section"],
                    seat_number=number,
                    is_available=True
                )
                session.add(seat)
        await session.flush()

        event_uuid = uuid.uuid4()
        now = datetime.now(timezone.utc)
        event = Event(
            uuid=event_uuid,
            place_id=place_uuid,
            name="Тестовый концерт",
            event_time=now + timedelta(days=7),
            registration_deadline=now + timedelta(days=6),
            status="published"
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)

        yield event_uuid