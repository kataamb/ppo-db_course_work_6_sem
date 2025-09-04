# src/service_locator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

# твои фабрики сессий по ролям
from core.db import SessionLocal

# твои репозитории
from repositories.user_repository import UserRepository
from repositories.advert_repository import AdvertsRepository
from repositories.category_repository import CategoryRepository
#from repositories.liked_repository import LikedRepository
#from repositories.deal_repository import DealsRepository  # если есть

# твои сервисы
from services.auth_service import AuthService
from services.advert_service import AdvertService
from services.category_service import CategoryService
from services.liked_service import LikedService
# добавь, если есть сервис для deals
# from services.deal_service import DealService


# ----------------------------
#  Контейнеры зависимостей
# ----------------------------
@dataclass
class Repositories:
    users: UserRepository
    adverts: AdvertsRepository
    categories: CategoryRepository
    likes: LikedRepository
    # deals: DealsRepository | None = None


@dataclass
class Services:
    auth: AuthService
    adverts: AdvertService
    categories: CategoryService
    likes: LikedService
    # deals: DealService | None = None


class ServiceLocator:
    """Простой локатор, чтобы не тащить всё в Depends по одному."""

    def __init__(self, session: AsyncSession, repositories: Repositories, services: Services) -> None:
        self.session = session
        self.repositories = repositories
        self.services = services

    # --- геттеры, если тебе так удобнее пользоваться ---
    def get_user_repo(self) -> UserRepository:
        return self.repositories.users

    def get_advert_repo(self) -> AdvertsRepository:
        return self.repositories.adverts

    def get_category_repo(self) -> CategoryRepository:
        return self.repositories.categories

    def get_liked_repo(self) -> LikedRepository:
        return self.repositories.likes

    def get_auth_service(self) -> AuthService:
        return self.services.auth

    def get_advert_service(self) -> AdvertService:
        return self.services.adverts

    def get_category_service(self) -> CategoryService:
        return self.services.categories

    def get_liked_service(self) -> LikedService:
        return self.services.likes


# ----------------------------
#  Фабрики локаторов по ролям
# ----------------------------
async def _make_locator(role: str) -> AsyncGenerator[ServiceLocator, None]:
    """
    Общая фабрика: открываем сессию для нужной роли, собираем репозитории/сервисы,
    отдаём через yield, после запроса сессия корректно закроется.
    """
    # открываем сессию для конкретной роли (admin | authorized_user | any_user)
    async with SessionLocal[role]() as session:
        # --- репозитории (работают на одной и той же сессии/роли) ---
        user_repo = UserRepository(session)
        advert_repo = AdvertsRepository(session)
        category_repo = CategoryRepository(session)
        liked_repo = LikedRepository(session)
        # deals_repo = DealsRepository(session)

        repositories = Repositories(
            users=user_repo,
            adverts=advert_repo,
            categories=category_repo,
            likes=liked_repo,
            # deals=deals_repo,
        )

        # --- сервисы, получают интерфейсы репозиториев ---
        auth_service = AuthService(user_repo)              # JWT логин/регистрация/логаут
        advert_service = AdvertService(advert_repo)        # CRUD объявлений
        category_service = CategoryService(category_repo)  # справочник категорий
        liked_service = LikedService(liked_repo)           # избранное
        # deal_service = DealService(deals_repo)

        services = Services(
            auth=auth_service,
            adverts=advert_service,
            categories=category_service,
            likes=liked_service,
            # deals=deal_service,
        )

        locator = ServiceLocator(session=session, repositories=repositories, services=services)
        # отдаём локатор “живым” до конца обработки HTTP-запроса
        yield locator
        # тут автоматически выйдем из async with, и сессия закроется


# ------------- готовые зависимости для FastAPI -------------
# Пример использования:
#   from fastapi import Depends
#   from service_locator import get_authorized_locator, ServiceLocator
#
#   @router.get("/adverts")
#   async def list_adverts(sl: ServiceLocator = Depends(get_authorized_locator)):
#       return await sl.get_advert_service().get_all_adverts()

async def get_admin_locator() -> AsyncGenerator[ServiceLocator, None]:
    async for loc in _make_locator("admin"):
        yield loc


async def get_authorized_locator() -> AsyncGenerator[ServiceLocator, None]:
    async for loc in _make_locator("authorized_user"):
        yield loc


async def get_anon_locator() -> AsyncGenerator[ServiceLocator, None]:
    async for loc in _make_locator("any_user"):
        yield loc
