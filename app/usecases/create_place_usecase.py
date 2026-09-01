from app.repositories.events.interface import EventRepository
from app.models.place import Place
from app.shemas.place import CreatePlaceRequest


class CreatePlaceUsecase:
    """UseCase для создания новой площадки (Place) со всеми местами (Seats)"""
    def __init__(self, repo: EventRepository):
        """Инициализация Usecase"""
        self.repo = repo

    async def do(self, data: CreatePlaceRequest) -> Place:
        """Выполнить создание площадки"""
        place_data = data.model_dump()

        place = await self.repo.create_place_with_seats(place_data)
        return place