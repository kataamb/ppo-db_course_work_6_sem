from abc import ABC, abstractmethod
from typing import List
from models.advert import Advert
from models.deal import Deal


class IDealRepository(ABC):
    @abstractmethod
    async def create_deal(self, user_id: int, advert_id :int) -> Deal: ...

    @abstractmethod
    async def get_deals_by_user(self, user_id: int) -> List[Advert]: ...

    @abstractmethod
    async def is_in_deals(self, user_id: int, advert_id: int) -> bool: ...