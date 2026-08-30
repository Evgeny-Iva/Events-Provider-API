from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Event
from app.repositories.events.interface import EventRepository
from app.shemas.events import Paginator


class PostgresEventRepository(EventRepository):
    """
    Реализация репозитория для PostgreSQL.
    Здесь мы пишем SQL-запросы (через SQLAlchemy).
    """

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, paginator: Paginator) -> list[Event]:
        """Получение списка событий"""
        query = select(Event)

        filters = []
        if paginator.status:
            filters.append(Event.status == paginator.status)

        if paginator.from_date:
            filters.append(Event.event_time >= paginator.from_date)

        if paginator.to_date:
            filters.append(Event.event_time <= paginator.to_date)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Event.event_time.desc())
        query = query.limit(paginator.limit).offset(paginator.offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def save(self, event: Event) -> Event:
        """Сохранить событие в БД"""
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def delete(self, event_id: str) -> bool:
        """Удалить событие из БД"""
        event = await self.get(event_id)
        if not event:
            return False
        await self.session.delete(event)
        await self.session.commit()
        return True

