from abc import ABC, abstractmethod
from typing import List
from models.deal import Deal
from models.advert import Advert
from abstract_repositories.ideal_repository import IDealRepository


class IDealsService(ABC):
    @abstractmethod
    async def create_deal(self, user_id: int, advert_id :int) -> Deal: ...

    @abstractmethod
    async def get_deals_by_user(self, user_id: int) -> List[Advert]: ...

    @abstractmethod
    async def is_in_deals(self, user_id: int, advert_id: int) -> bool: ...

class DealsService(IDealsService):
    def __init__(self, repo: IDealRepository):
        self.repo = repo

    async def create_deal(self, user_id: int, advert_id :int) -> Deal:
        result = await self.repo.create_deal(user_id, advert_id)
        return result

    async def get_deals_by_user(self, user_id: int) -> List[Advert]:
        return await self.repo.get_deals_by_user(user_id)

    async def is_in_deals(self, user_id: int, advert_id: int) -> bool:
        return await self.repo.is_in_deals(user_id, advert_id)






















