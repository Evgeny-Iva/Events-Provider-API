import uuid
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime


class Paginator(BaseModel):
    """Параметры пагинации и фильтрации"""
    limit: int = Field(100, ge=1, le=1000, description="Количество записей")
    cursor: str | None = Field(
        None, description="Курсор для пагинации (UUID последнего события)"
    )
    status: str | None = Field(None, description="Фильтр по статусу")
    from_date: datetime | None = Field(None, description="Дата начала (с)")
    to_date: datetime | None= Field(None, description="Дата начала (по)")
    changed_at: datetime | None = Field(None, description="Фильтр события")

    @model_validator(mode='after')
    def validate_dates(self):
        """Проверка, что from_date <= to_date"""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date не может быть позже to_date")
        return self

    @field_validator('changed_at', mode='before')
    def parse_changed_at(cls, v):
        """Превращает строку 'YYYY-MM-DD' в datetime"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("changed_at must be in YYYY-MM-DD format")
        return v


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


class PlaceInfo(BaseModel):
    """Информация о площадке"""
    id: uuid.UUID
    name: str
    city: str
    address: str
    seats_pattern: str


class EventDetailResponse(BaseModel):
    """Детальная информация о событии"""
    id: uuid.UUID
    name: str
    place: PlaceInfo
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int