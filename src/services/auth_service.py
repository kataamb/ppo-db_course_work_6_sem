from abc import ABC, abstractmethod
from models.user import User
from abstract_repositories.iuser_repository import IUserRepository
from core.create_jwt import JWTManager
from sqlalchemy.ext.asyncio import AsyncSession


class IAuthService(ABC):
    @abstractmethod
    async def register(self, db: AsyncSession, user: dict) -> User: ...

    @abstractmethod
    async def login(self, db: AsyncSession, email: str, password: str) -> str: ...

    @abstractmethod
    async def logout(self, token: str) -> bool: ...

    @abstractmethod
    def verify_token(self, token: str) -> dict: ...


class AuthService(IAuthService):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.invalidated_tokens: set[str] = set()

    async def register(self, db: AsyncSession, user: dict) -> User:
        if await self.user_repo.find_by_email(db, user["email"]):
            raise ValueError("User already exists")
        if user["password"] != user["repeat_password"]:
            raise ValueError("Passwords didn't matched!")

        user_create = User(**user) #delete odd
        return await self.user_repo.create(user_create)

    async def login(self, db: AsyncSession, email: str, password: str) -> str:
        user = await self.user_repo.find_by_email(db, email)
        if user and user.password == password:
            return JWTManager.create_access_token({"sub": user.email, "id": user.id, "role": "authorized_user"})

        raise ValueError("Invalid credentials")

    async def logout(self, token: str) -> bool:
        self.invalidated_tokens.add(token)
        return True

    def verify_token(self, token: str) -> dict:
        if token in self.invalidated_tokens:
            raise ValueError("Token revoked")
        return JWTManager.decode_token(token)
