from pydantic import BaseModel, Field


class CreatePlaceRequest(BaseModel):
    """Схема для создания места"""
    name: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    seats_pattern: str