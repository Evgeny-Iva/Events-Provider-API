import uuid
from pydantic import BaseModel, Field, EmailStr


class RegistrationRequest(BaseModel):
    """Схема запроса регистрации"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    seat: str #TODO наверное валидация место тоже было бы не плохо
    email: EmailStr
    event_id: uuid.UUID


class RegistrationResponse(BaseModel):
    """Схема ответа регистрации"""
    ticket_id: uuid.UUID