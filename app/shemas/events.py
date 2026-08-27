from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Paginator(BaseModel):
    """Параметры пагинации и фильтрации"""
    limit: int = Field(100, ge=1, le=1000, description="Количество записей")
    offset: int = Field(0, ge=0, description="Смещение (пропустить N записей)")
    status: Optional[str] = Field(None, description="Фильтр по статусу")
    from_date: Optional[datetime] = Field(None, description="Дата начала (с)")
    to_date: Optional[datetime] = Field(None, description="Дата начала (по)")

    @model_validator(mode='after')
    def validate_dates(self):
        """Проверка, что from_date <= to_date"""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date не может быть позже to_date")
        return self