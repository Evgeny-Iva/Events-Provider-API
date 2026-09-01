from fastapi import APIRouter, Depends

from app.repositories.events.postgres import PostgresEventRepository
from app.routers.events import get_postgres_repository
from app.shemas.place import CreatePlaceRequest
from app.usecases.create_place_usecase import CreatePlaceUsecase


router = APIRouter(prefix="/places", tags=["places"])

def get_create_place_usecase(
        repo: PostgresEventRepository = Depends(get_postgres_repository)
) -> CreatePlaceUsecase:
    """Получает репозиторий и возращает usecase"""
    return CreatePlaceUsecase(repo)


@router.post("/")
async def created_place(
        data: CreatePlaceRequest,
        usecase: CreatePlaceUsecase = Depends(get_create_place_usecase)
):
    """Принимает JSON от клиента, возвращает созданную площадку"""
    place = await usecase.do(data)
    return place

