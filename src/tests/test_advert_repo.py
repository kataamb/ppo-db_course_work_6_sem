import pytest_asyncio
import pytest
from models.advert import Advert
from repositories.advert_repository import AdvertsRepository
from core.db import SessionLocal

@pytest_asyncio.fixture
async def admin_session():
    async with SessionLocal["admin"]() as session:
        yield session

@pytest_asyncio.fixture
async def user_session():
    async with SessionLocal["authorized_user"]() as session:
        yield session

@pytest_asyncio.fixture
async def anon_session():
    async with SessionLocal["any_user"]() as session:
        yield session

@pytest.mark.asyncio
async def test_admin_can_create_and_read(admin_session):
    repo = AdvertsRepository(admin_session)

    advert = Advert(
        content="Тестовое объявление",
        description="Описание",
        id_category=1,
        price=1000,
        status=1,
        id_seller=1,
    )
    created = await repo.create(advert)
    assert created is not None
    assert created.id is not None

    loaded = await repo.get_by_id(created.id)
    assert loaded is not None
    assert loaded.content == "Тестовое объявление"

@pytest.mark.asyncio
async def test_user_can_create_but_not_all(user_session):
    repo = AdvertsRepository(user_session)

    advert = Advert(
        content="От пользователя",
        description="Описание",
        id_category=1,
        price=500,
        status=1,
        id_seller=1,
    )
    created = await repo.create(advert)
    assert created is not None
    loaded = await repo.get_by_id(created.id)
    assert loaded.content == "От пользователя"

@pytest.mark.asyncio
async def test_anon_can_only_read(anon_session):
    repo = AdvertsRepository(anon_session)
    adverts = await repo.get_all_adverts()
    assert isinstance(adverts, list)

    # Аноним не может создавать
    advert = Advert(
        content="Анон",
        description="Описание",
        id_category=1,
        price=100,
        status=1,
        id_seller=1,
    )
    created = await repo.create(advert)
    assert created is None
