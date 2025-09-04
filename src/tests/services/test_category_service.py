import unittest
from unittest.mock import AsyncMock

from models.category import Category
from services.category_service import CategoryService
from abstract_repositories.icategory_repository import ICategoryRepository


class TestCategoryService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock(spec=ICategoryRepository)
        self.service = CategoryService(self.repo)

        self.cat1 = Category(id=1, name="Электроника")
        self.cat2 = Category(id=2, name="Книги")

    async def test_get_all_returns_list(self):
        self.repo.get_all.return_value = [self.cat1, self.cat2]

        items = await self.service.get_all()

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].name, "Электроника")
        self.repo.get_all.assert_awaited_once()

    async def test_get_all_empty(self):
        self.repo.get_all.return_value = []

        items = await self.service.get_all()

        self.assertEqual(items, [])
        self.repo.get_all.assert_awaited_once()

    async def test_get_name_by_id_found(self):
        self.repo.get_name_by_id.return_value = "Электроника"

        name = await self.service.get_name_by_id(1)

        self.assertEqual(name, "Электроника")
        self.repo.get_name_by_id.assert_awaited_once_with(1)