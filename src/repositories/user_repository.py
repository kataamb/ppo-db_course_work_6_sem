from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, cast
from sqlalchemy.engine import RowMapping
from models.user import User
from abstract_repositories.iuser_repository import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> Optional[User]:
        try:
            max_id_query = text("SELECT MAX(id) AS max_id FROM adv.profiles")
            result = await self.session.execute(max_id_query)
            row: Optional[RowMapping] = result.mappings().first()
            max_id = cast(Optional[int], row["max_id"]) if row is not None else None
            next_id = (max_id or 0) + 1

            # Вставка в profiles
            insert_profile = text("""
                INSERT INTO adv.profiles (id, nickname, fio, email, phone_number, password)
                VALUES (:id, :nickname, :fio, :email, :phone_number, :password)
            """)
            await self.session.execute(insert_profile, {
                "id": next_id,
                "nickname": user.nickname,
                "fio": user.fio,
                "email": user.email,
                "phone_number": user.phone_number,
                "password": user.password
            })

            # Вставка в customers
            insert_customer = text("""
                INSERT INTO adv.customers (profile_id, rating)
                VALUES (:profile_id, :rating)
            """)
            await self.session.execute(insert_customer, {"profile_id": next_id, "rating": getattr(user, "rating", 0)})

            # Вставка в sellers
            insert_seller = text("""
                INSERT INTO adv.sellers (profile_id, rating)
                VALUES (:profile_id, :rating)
            """)
            await self.session.execute(insert_seller, {"profile_id": next_id, "rating": getattr(user, "rating", 0)})

            await self.session.commit()
            return User(id=next_id, nickname=user.nickname, fio=user.fio, email=user.email, phone_number=user.phone_number, password=user.password)

        except IntegrityError as e:
            print(f"Ошибка: пользователь с такими данными уже существует: {e}")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при создании пользователя: {e}")
            await self.session.rollback()
        return None

    async def delete(self, profile_id: int) -> bool:
        """
        Удаляет пользователя: profile + customer + seller
        """
        try:
            # Удаляем сначала customer и seller (если CASCADE не настроен)
            await self.session.execute(text("DELETE FROM adv.customers WHERE profile_id = :id"), {"id": profile_id})
            await self.session.execute(text("DELETE FROM adv.sellers WHERE profile_id = :id"), {"id": profile_id})
            # Удаляем профиль
            await self.session.execute(text("DELETE FROM adv.profiles WHERE id = :id"), {"id": profile_id})

            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении пользователя {profile_id}: {e}")
            await self.session.rollback()
            return False

    async def find_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        try:
            query = text("SELECT * FROM adv.profiles WHERE email = :email")
            result = await self.session.execute(query, {"email": email})
            row = result.mappings().first()
            return User(**row) if row else None
        except SQLAlchemyError as e:
            print(f"Ошибка при поиске пользователя по email {email}: {e}")
            return None
