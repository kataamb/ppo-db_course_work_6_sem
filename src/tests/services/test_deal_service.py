import unittest
from unittest.mock import AsyncMock

from models.advert import Advert
from models.deal import Deal
from services.deal_service import DealsService
from abstract_repositories.ideal_repository import IDealRepository


import unittest
from unittest.mock import AsyncMock


class TestDealsService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock(spec=IDealRepository)
        self.service = DealsService(self.repo)

        self.fake_deal = Deal(id=1, id_customer=1, id_advert=5)
        self.fake_advert = Advert(
            id=5,
            content="Тестовый контент",
            description="Описание объявления",
            id_category=1,
            price=1000,
            id_seller=42,
            status=1,
        )

    async def test_create_deal(self):
        self.repo.create_deal.return_value = self.fake_deal
        result = await self.service.create_deal(1, 5)
        self.assertEqual(result.id_advert, 5)
        self.repo.create_deal.assert_awaited_once_with(1, 5)

    async def test_get_deals_by_user(self):
        # Репозиторий возвращает список Advert
        self.repo.get_deals_by_user.return_value = [self.fake_advert]
        adverts = await self.service.get_deals_by_user(42)
        self.assertEqual(len(adverts), 1)
        self.assertEqual(adverts[0].id, 5)
        self.assertEqual(adverts[0].id_seller, 42)
        self.repo.get_deals_by_user.assert_awaited_once_with(42)

    async def test_is_in_deals(self):
        self.repo.is_in_deals.return_value = True
        self.assertTrue(await self.service.is_in_deals(1, 5))
        self.repo.is_in_deals.assert_awaited_once_with(1, 5)