import unittest
from unittest.mock import AsyncMock

from models.advert import Advert
from services.advert_service import AdvertService
from abstract_repositories.iadvert_repository import IAdvertRepository


class TestAdvertService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock(spec=IAdvertRepository)
        self.service = AdvertService(self.repo)

        self.advert = Advert(
            id=10,
            content="Контент",
            description="Описание",
            id_category=2,
            price=1500,
            status=1,
            id_seller=100,
        )
        self.advert_other = Advert(
            id=11,
            content="Другой",
            description="Описание 2",
            id_category=3,
            price=2500,
            status=1,
            id_seller=200,
        )

    async def test_create_advert(self):
        self.repo.create.return_value = self.advert
        created = await self.service.create_advert(self.advert)
        self.assertEqual(created.id, 10)
        self.repo.create.assert_awaited_once_with(self.advert)

    async def test_get_advert_found(self):
        self.repo.get_by_id.return_value = self.advert
        found = await self.service.get_advert(10)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, 10)
        self.repo.get_by_id.assert_awaited_once_with(10)

    async def test_get_advert_not_found(self):
        self.repo.get_by_id.return_value = None
        found = await self.service.get_advert(999)
        self.assertIsNone(found)
        self.repo.get_by_id.assert_awaited_once_with(999)

    async def test_get_all_adverts(self):
        self.repo.get_all_adverts.return_value = [self.advert, self.advert_other]
        items = await self.service.get_all_adverts()
        self.assertEqual(len(items), 2)
        self.repo.get_all_adverts.assert_awaited_once()

    async def test_get_advert_by_user(self):
        self.repo.get_advert_by_user.return_value = [self.advert]
        items = await self.service.get_advert_by_user(100)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id_seller, 100)
        self.repo.get_advert_by_user.assert_awaited_once_with(100)

    async def test_get_adverts_by_category(self):
        self.repo.get_adverts_by_category.return_value = [self.advert]
        items = await self.service.get_adverts_by_category(2)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id_category, 2)
        self.repo.get_adverts_by_category.assert_awaited_once_with(2)

    async def test_get_adverts_by_key_word(self):
        self.repo.get_adverts_by_key_word.return_value = [self.advert]
        items = await self.service.get_adverts_by_key_word("Контент")
        self.assertEqual(len(items), 1)
        self.assertIn("Контент", items[0].content)
        self.repo.get_adverts_by_key_word.assert_awaited_once_with("Контент")

    async def test_is_created_true(self):
        self.repo.is_created.return_value = True
        self.assertTrue(await self.service.is_created(100, 10))
        self.repo.is_created.assert_awaited_once_with(100, 10)

    async def test_is_created_false(self):
        self.repo.is_created.return_value = False
        self.assertFalse(await self.service.is_created(200, 10))
        self.repo.is_created.assert_awaited_once_with(200, 10)

    async def test_delete_advert_success(self):
        # владелец совпадает
        self.repo.get_by_id.return_value = self.advert
        await self.service.delete_advert(advert_id=10, user_id=100)
        # Сервис вызывает repo.delete(advert_id)
        self.repo.delete.assert_awaited_once_with(10)

    async def test_delete_advert_not_found(self):
        self.repo.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            await self.service.delete_advert(advert_id=999, user_id=100)
        self.repo.delete.assert_not_called()

    async def test_delete_advert_permission_denied(self):
        # владелец не совпадает
        self.repo.get_by_id.return_value = self.advert_other  # id_seller=200
        with self.assertRaises(PermissionError):
            await self.service.delete_advert(advert_id=11, user_id=100)
        self.repo.delete.assert_not_called()