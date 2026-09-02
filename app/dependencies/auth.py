from fastapi import Depends, HTTPException, Header
from app.core.config import settings

async def verify_api_key(api_key: str = Header(...)):
    """Проверка API ключа"""
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Отсутствует или неверный API ключ"
        )
    return api_key