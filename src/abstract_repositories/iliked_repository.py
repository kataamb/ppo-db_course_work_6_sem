from abc import ABC, abstractmethod
from typing import List, Optional
from models.advert import Advert
from models.liked import Liked


class ILikedRepository(ABC):
    @abstractmethod
    async def add_to_liked(self, id_advert: int, id_user: int) -> Optional[Liked]: ...

    @abstractmethod
    async def remove_from_liked(self, user_id: int, advert_id: int): ...

    @abstractmethod
    async def get_liked_by_user(self, id_user: int)-> List[Advert]: ...

    @abstractmethod
    async def is_liked(self, user_id: int, advert_id: int) -> bool: ...