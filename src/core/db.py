from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Literal

# Конфиг подключения для разных ролей
DATABASES = {
    "admin":            "postgresql+asyncpg://admin:admin@localhost:5433/adverts_db",
    "authorized_user":  "postgresql+asyncpg://authorized_user:user@localhost:5433/adverts_db",
    "any_user":         "postgresql+asyncpg://any_user:anon@localhost:5433/adverts_db",
}

# Создаём движки
_engines = {role: create_async_engine(url, future=True) for role, url in DATABASES.items()}

# Создаём async sessionmakers
async_sessionmakers = {
    role: async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    for role, engine in _engines.items()
}

SessionLocal = async_sessionmakers

# -----------------
# Функция для создания сессии (для репозиториев)
# -----------------
def create_session(role: Literal["admin", "authorized_user", "any_user"] = "any_user") -> AsyncSession:
    """
    Создает и возвращает асинхронную сессию БД для выбранной роли.

    """
    print('there', type(async_sessionmakers[role]()))
    return async_sessionmakers[role]()

# -----------------
# Фабрика зависимостей для FastAPI
# -----------------
async def get_session(role: Literal["admin", "authorized_user", "any_user"] = "any_user"):
    """
    Возвращает асинхронную сессию БД для выбранной роли.
    По умолчанию — "any_user".
    """
    async_session = async_sessionmakers[role]()
    try:
        return async_session
    finally:
        await async_session.close()