from app.models import Event, Place
from app.repositories.events.interface import EventRepository
from app.clients.events_provider_client import EventsProviderClient
from app.schemas.events import Paginator
from datetime import datetime
import uuid


def parse_date(value):
    """Превращает строку из API в datetime."""
    if isinstance(value, str):
        try:
            value = value.replace('Z', '+00:00')
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value


def ensure_uuid(value):
    """Преобразует значение в UUID или строку UUID."""
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, str):
        return value
    return str(value)


class ExternalEventRepository(EventRepository):
    """Реализация репозитория для внешнего API."""

    def __init__(self, client: EventsProviderClient):
        self.client = client

    async def get_all(self, paginator: Paginator) -> list[Event]:
        """Получить список событий из внешнего API"""
        params = paginator.model_dump(exclude_none=True)

        if (
                "changed_at" in params
                and isinstance(params["changed_at"], datetime)
        ):
            params["changed_at"] = params["changed_at"].strftime("%Y-%m-%d")

        raw_events = await self.client.get_all_events(params=params)

        events = []
        for raw in raw_events:
            place_data = raw.get("place")
            if not place_data:
                continue

            place_uuid = ensure_uuid(place_data.get("id"))

            place = Place(
                uuid=place_uuid,
                name=place_data.get("name"),
                city=place_data.get("city"),
                address=place_data.get("address"),
                seats_pattern=place_data.get("seats_pattern"),
            )

            event_uuid = ensure_uuid(raw.get("id"))

            event = Event(
                uuid=event_uuid,
                name=raw.get("name"),
                event_time=parse_date(raw.get("event_time")),
                registration_deadline=parse_date(
                    raw.get("registration_deadline")),
                status=raw.get("status"),
                number_of_visitors=raw.get("number_of_visitors", 0),
                changed_at=parse_date(raw.get("changed_at")),
                created_at=parse_date(raw.get("created_at")),
                status_changed_at=parse_date(raw.get("status_changed_at")),
                place=place,
                place_id=place.uuid,
            )
            events.append(event)

        return events