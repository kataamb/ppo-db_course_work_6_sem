from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from typing import Optional, cast
from sqlalchemy.engine import RowMapping

from abstract_repositories.iliked_repository import ILikedRepository
from models.advert import Advert
from models.liked import Liked

class LikedRepository(ILikedRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_to_liked(self, user_id: int, advert_id: int) -> Optional[Liked]:
        max_id_query = text("SELECT MAX(id) AS max_id FROM adv.liked")
        result = await self.session.execute(max_id_query)
        row: Optional[RowMapping] = result.mappings().first()
        max_id = cast(Optional[int], row["max_id"]) if row is not None else None
        next_id = (max_id or 0) + 1

        insert_query = text("""
                        INSERT INTO adv.liked (id, id_customer, id_advert)
                        VALUES (:id, :id_customer, :id_advert)
                        RETURNING id, id_customer, id_advert, date_created
                    """)
        result = await self.session.execute(insert_query, {
            "id": next_id,
            "id_customer": user_id,
            "id_advert": advert_id
        })
        row = result.mappings().first()
        await self.session.commit()
        if row:
            return Liked(**row)
        return None

    async def remove_from_liked(self, user_id: int, advert_id: int) -> None:
        query = text("DELETE FROM adv.likes WHERE id_advert = :advert_id AND id_customer = :user_id")
        try:
            await self.session.execute(query, {"advert_id": advert_id, "user_id": user_id})
            await self.session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при удалении объявления {advert_id}: {e}")
            await self.session.rollback()

    async def get_liked_by_user(self, user_id: int)-> List[Advert]:
        try:
            query = text("""
                SELECT * 
                FROM adv.profile join adv.likes on adv.user.id = adv.likes.id_customer as p join adv.adverts on adv.adverts.id = p.id_advert
                WHERE id_seller = :user_id
            """)
            result = await self.session.execute(query, {"user_id": user_id,
            })
            return [Advert(**row) for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявления: {e}")
            return []



    async def is_liked(self, user_id: int, advert_id: int) -> bool:
        query = text("SELECT * FROM adv.likes WHERE id_customer = :uid AND id_advert = :aid")
        row = await self.session.execute(query, {"uid": user_id, "aid": advert_id})
        await self.session.commit()
        res = [Liked(**row) for row in row.mappings()]
        if len(res):
            return True
        return False