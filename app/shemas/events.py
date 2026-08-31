import uuid
from pydantic import BaseModel, Field, model_validator
from datetime import datetime


class Paginator(BaseModel):
    """Параметры пагинации и фильтрации"""
    limit: int = Field(100, ge=1, le=1000, description="Количество записей")
    offset: int = Field(0, ge=0, description="Смещение (пропустить N записей)")
    status: str | None = Field(None, description="Фильтр по статусу")
    from_date: datetime | None = Field(None, description="Дата начала (с)")
    to_date: datetime | None= Field(None, description="Дата начала (по)")

    @model_validator(mode='after')
    def validate_dates(self):
        """Проверка, что from_date <= to_date"""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date не может быть позже to_date")
        return self


class EventResponse(BaseModel):
    """Схема для ответа с одним событием"""
    uuid: uuid.UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    place_id: uuid.UUID
    created_at: datetime
    changed_at: datetime
    status_changed_at: datetime | None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Схема для ответа со списком событий"""
    data: list[EventResponse]
    meta: dict