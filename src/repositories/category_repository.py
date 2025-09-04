from models.category import Category
from abstract_repositories.icategory_repository import ICategoryRepository


from sqlalchemy import text
from sqlalchemy.exc import  SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

class CategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session



    async def get_all(self) -> List[Category]:
        query = text("SELECT * FROM adv.categories ")
        try:
            result = await self.session.execute(query)
            return [Category(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка categoory: {e}")
            return []

    async def get_name_by_id(self, id_category: int) -> str:
        query = text("SELECT name FROM adv.categories WHERE id = :id")
        try:
            result = await self.session.execute(query, {'id': id_category})
            category = result.mappings().first()  # Получаем первую (и единственную) строку результата
            if category:
                return category['name']  # Возвращаем имя категории
            else:
                return "Категория не найдена"  # Если категория не найдена
        except SQLAlchemyError as e:
            print(f"Ошибка при получении категории: {e}")
            return "Ошибка при получении категории"