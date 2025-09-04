from abc import ABC, abstractmethod
from models.category import Category
from abstract_repositories.icategory_repository import ICategoryRepository

from typing import List


class ICategoryService(ABC):
    @abstractmethod
    async def get_all(self) -> List[Category]: ...

    @abstractmethod
    async def get_name_by_id(self, id_category: int) -> str: ...



class CategoryService(ICategoryService):
    def __init__(self, category_repo: ICategoryRepository):
        self.cat_repo = category_repo
        self.invalidated_tokens: set[str] = set()

    async def get_all(self) -> List[Category]:
        return await self.cat_repo.get_all()

    async def get_name_by_id(self, id_category: int) -> str:
        return await self.cat_repo.get_name_by_id(id_category)

