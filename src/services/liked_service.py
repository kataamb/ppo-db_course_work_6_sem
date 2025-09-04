from abc import ABC, abstractmethod
from typing import List, Optional
from models.liked import Liked
from models.advert import Advert

from abstract_repositories.iliked_repository import ILikedRepository


class ILikedService(ABC):
    @abstractmethod
    async def add_to_liked(self, user_id: int, advert_id :int) -> Optional[Liked]: ...

    @abstractmethod
    async def get_liked_by_user(self, user_id: int) -> List[Advert]: ...

    @abstractmethod
    async def remove_from_liked(self, user_id: int, advert_id: int) -> None: ...

    @abstractmethod
    async def is_liked(self, user_id: int, advert_id: int) -> bool: ...

class LikedService(ILikedService):
    def __init__(self, repo: ILikedRepository):
        self.repo = repo

    async def add_to_liked(self, user_id: int, advert_id: int) -> Optional[Liked]:
        result = await self.repo.add_to_liked(user_id, advert_id)
        return result

    async def get_liked_by_user(self, user_id: int) -> List[Advert]:
        return await self.repo.get_liked_by_user(user_id)

    async def remove_from_liked(self, user_id: int, advert_id: int) -> None:
        return await self.repo.remove_from_liked(user_id, advert_id)

    async def is_liked(self, user_id: int, advert_id: int) -> bool:
        return await self.repo.is_liked(user_id, advert_id)






















