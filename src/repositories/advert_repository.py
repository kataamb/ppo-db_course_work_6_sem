from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional, cast
from sqlalchemy.engine import RowMapping

from abstract_repositories.iadvert_repository import IAdvertRepository
from models.advert import Advert
from dto.advert_dto import AdvertWithCategoryDTO

class AdvertsRepository(IAdvertRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, advert: Advert) -> Optional[Advert]:
        try:
            # Получаем максимальный id
            max_id_query = text("SELECT MAX(id) AS max_id FROM adv.adverts")
            result = await self.session.execute(max_id_query)
            row: Optional[RowMapping] = result.mappings().first()
            max_id = cast(Optional[int], row["max_id"]) if row is not None else None
            next_id = (max_id or 0) + 1

            # Вставляем с явным id
            insert_query = text("""
                INSERT INTO adv.adverts (id, content, description, id_category, price, status, id_seller)
                VALUES (:id, :content, :description, :id_category, :price, :status, :id_seller)
                RETURNING id, content, description, id_category, price, status, id_seller, date_created
            """)
            result = await self.session.execute(insert_query, {
                "id": next_id,
                "content": advert.content,
                "description": advert.description,
                "id_category": advert.id_category,
                "price": advert.price,
                "status": advert.status,
                "id_seller": advert.id_seller
            })
            row = result.mappings().first()
            await self.session.commit()
            if row:
                return Advert(**row)

        except IntegrityError:
            print("Ошибка: такое объявление уже существует.")
            await self.session.rollback()
        except SQLAlchemyError as e:
            print(f"Ошибка при создании объявления: {e}")
            await self.session.rollback()

        return None

    async def get_by_id(self, advert_id: int) -> Optional[Advert]:
        query = text("SELECT * FROM adv.adverts WHERE id = :id")
        try:
            result = await self.session.execute(query, {"id": advert_id})
            row = result.mappings().first()
            return Advert(**row) if row else None
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявления {advert_id}: {e}")
            return None

    async def get_all_adverts(self) -> List[Advert]:
        query = text("SELECT * FROM adv.adverts ORDER BY date_created DESC")
        try:
            result = await self.session.execute(query)
            return [Advert(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка объявлений: {e}")
            return []

    async def get_advert_by_user(self, user_id: int) -> List[Advert]:
        query = text("SELECT * FROM adv.adverts WHERE id_seller = :user_id ORDER BY date_created DESC")
        try:
            result = await self.session.execute(query, {"user_id": user_id})
            return [Advert(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявлений пользователя {user_id}: {e}")
            return []

    async def is_created(self, user_id: int, advert_id: int) -> bool:
        query = text("SELECT * FROM adv.adverts WHERE id_seller = :uid AND id = :aid")
        row = await self.session.execute(query, {"uid": user_id, "aid": advert_id})
        await self.session.commit()

        res = [Advert(**row)  for row in row.mappings()]
        if len(res):
            return True
        return False

    async def get_adverts_by_key_word(self, key_word: str) -> List[Advert]:
        query = text("SELECT * FROM adv.search_adverts(:kw)")
        try:
            result = await self.session.execute(query, {"kw": f"%{key_word}%"})
            return [Advert(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при поиске объявлений по ключевому слову '{key_word}': {e}")
            return []

    async def get_adverts_by_filter(self, begin_time: datetime, end_time: datetime) -> List[Advert]:
        query = text("""
            SELECT * FROM adv.adverts 
            WHERE date_created BETWEEN :begin_time AND :end_time
            ORDER BY date_created DESC
        """)
        try:
            result = await self.session.execute(query, {"begin_time": begin_time, "end_time": end_time})
            return [Advert(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при фильтрации объявлений: {e}")
            return []

    async def get_adverts_by_category(self, category_id: int) -> List[Advert]:
        query = text("SELECT * FROM adv.adverts WHERE id_category = :category_id ORDER BY date_created DESC")
        try:
            result = await self.session.execute(query, {"category_id": category_id})
            return [Advert(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявлений по категории {category_id}: {e}")
            return []

    async def delete_advert(self, advert_id: int, user_id: int) -> None:
        query = text("DELETE FROM adv.adverts WHERE id = :advert_id AND id_seller = :user_id")
        try:
            await self.session.execute(query, {"advert_id": advert_id, "user_id": user_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении объявления {advert_id}: {e}")
            await self.session.rollback()

    async def get_all_with_full_info(self, user_id: int | None = None):
        query = text("""
                  SELECT 
    a.id,
    a.content,
    a.description,
    a.id_category,
    c.name AS category_name,
    a.price,
    a.status,
    a.id_seller,
    p.fio AS seller_name,
    a.date_created,
    CASE WHEN f.id_customer IS NOT NULL THEN true ELSE false END AS is_favorite,
    CASE WHEN pur.id IS NOT NULL THEN true ELSE false END AS is_bought,
    CASE WHEN a.id_seller = :customer_id THEN true ELSE false END AS is_created
FROM adv.adverts a
JOIN adv.categories c ON a.id_category = c.id
JOIN adv.sellers s ON a.id_seller = s.id
JOIN adv.profiles p ON s.profile_id = p.id
LEFT JOIN adv.likes f ON f.id_advert = a.id AND f.id_customer = :customer_id
LEFT JOIN adv.deals pur ON pur.id_advert = a.id AND pur.id_customer = :customer_id
ORDER BY a.date_created DESC
                """)

        try:
            result = await self.session.execute(query, {"customer_id": user_id})
            rows = result.mappings().all()
            return [AdvertWithCategoryDTO(**row) for row in rows]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявлений с категориями и флагами: {e}")
            return []

    async def get_all_by_category_authorized(self, category_id: int, user_id: int):
        query = text("""
                            SELECT 
                                a.id,
                                a.content,
                                a.description,
                                a.id_category,
                                c.name AS category_name,
                                a.price,
                                a.status,
                                a.id_seller,
                                p.fio AS seller_name,
                                a.date_created,
                                CASE WHEN f.id_customer IS NOT NULL THEN true ELSE false END AS is_favorite,
                                CASE WHEN pur.id IS NOT NULL THEN true ELSE false END AS is_bought
                            FROM adv.adverts a
                            JOIN adv.categories c ON a.id_category = c.id
                            JOIN adv.sellers s ON a.id_seller = s.id
                            JOIN adv.profiles p ON s.profile_id = p.id
                            LEFT JOIN adv.likes f 
                                   ON f.id_advert = a.id AND f.id_customer = :customer_id
                            LEFT JOIN adv.deals pur 
                                   ON pur.id_advert = a.id AND pur.id_customer = :customer_id
                            WHERE id_category = :category_id
                            ORDER BY a.date_created DESC
                        """)

        try:
            result = await self.session.execute(query, {"customer_id": user_id, "category_id":category_id})
            rows = result.mappings().all()
            return [AdvertWithCategoryDTO(**row) for row in rows]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявлений с категориями и флагами: {e}")
            return []
