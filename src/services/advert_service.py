from abc import ABC, abstractmethod
from typing import List, Optional
from models.advert import Advert
from dto.advert_dto import AdvertWithCategoryDTO
from abstract_repositories.iadvert_repository import IAdvertRepository

class IAdvertService(ABC):
    @abstractmethod
    async def create_advert(self, advert: Advert) -> Advert: ...

    @abstractmethod
    async def get_advert(self, advert_id: int) -> Optional[Advert]: ...

    @abstractmethod
    async def get_all_adverts(self) -> List[Advert]: ...

    @abstractmethod
    async def get_advert_by_user(self, user_id: int) -> List[Advert]: ...

    @abstractmethod
    async def is_created(self, user_id: int, advert_id: int) -> bool: ...

    @abstractmethod
    async def get_adverts_by_key_word(self, key_word: str) -> List[Advert]: ...

    @abstractmethod
    async def get_adverts_by_category(self, category_id: int) -> List[Advert]: ...

    @abstractmethod
    async def delete_advert(self, advert_id: int, user_id: int) -> None: ...

    @abstractmethod
    async def get_all_adverts_for_user(self, user_id: int | None) -> List[AdvertWithCategoryDTO]: ...

    @abstractmethod
    async def get_adverts_by_category_authorized(self, category_id: int, user_id: int) -> List[AdvertWithCategoryDTO]: ...

class AdvertService(IAdvertService):
    def __init__(self, repo: IAdvertRepository):
        self.repo = repo
        #self.liked_serv = liked_serv
        #self.deals_serv = deals_serv

    async def create_advert(self, advert: Advert) -> Advert:
        result = await self.repo.create(advert)
        return result

    async def get_advert(self, advert_id: int) -> Optional[Advert]:
        return await self.repo.get_by_id(advert_id)

    async def get_all_adverts(self) -> List[Advert]:
        return await self.repo.get_all_adverts()

    async def get_advert_by_user(self, user_id: int) -> List[Advert]:
        return await self.repo.get_advert_by_user(user_id)

    async def is_created(self, user_id: int, advert_id: int) -> bool:
        return await self.repo.is_created(user_id, advert_id)

    async def get_adverts_by_key_word(self, key_word: str) -> List[Advert]:
        return await self.repo.get_adverts_by_key_word(key_word)


    async def get_adverts_by_category(self, category_id: int) -> List[Advert]:
        return await self.repo.get_adverts_by_category(category_id)


    async def delete_advert(self, advert_id: int, user_id: int) -> None:
        advert = await self.repo.get_by_id(advert_id)
        if not advert:
            raise ValueError("Advert not found")
        if advert.id_seller != user_id:
            raise PermissionError("Not allowed to delete this advert")
        await self.repo.delete(advert_id)

    async def get_all_adverts_for_user(self, user_id: int | None) -> List[AdvertWithCategoryDTO]:
        adverts = await self.repo.get_all_with_full_info(user_id)
        #adverts = [AdvertWithCategoryDTO(**row) for row in raw_rows]

        '''if user_id:
            for advert in adverts:
                advert.is_favorite = await self.liked_serv.is_liked(user_id, advert.id)
                advert.is_bought = await self.deals_serv.is_in_deals(user_id, advert.id)
        '''
        return adverts

    async def get_adverts_by_category_authorized(self, category_id: int, user_id: int) -> List[AdvertWithCategoryDTO]:
        adverts = await self.repo.get_all_by_category_authorized(category_id, user_id)
        for advert in adverts:
            advert.is_created = advert.id_seller == user_id
        print(user_id, adverts)
        return adverts