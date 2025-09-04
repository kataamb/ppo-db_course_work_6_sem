from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from typing import Optional, cast
from sqlalchemy.engine import RowMapping

from abstract_repositories.ideal_repository import IDealRepository
from models.advert import Advert
from models.deal import Deal


class DealRepository(IDealRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_deal(self, user_id: int, advert_id: int) -> Deal:
        max_id_query = text("SELECT MAX(id) AS max_id FROM adv.deals")
        result = await self.session.execute(max_id_query)
        row_max: Optional[RowMapping] = result.mappings().first()
        max_id = cast(Optional[int], row_max["max_id"]) if row_max is not None else None
        next_id = (max_id or 0) + 1

        insert_query = text("""
             INSERT INTO adv.deals (id, id_customer, id_advert, address)
             VALUES (:id, :id_customer, :id_advert, :address)
             RETURNING id, id_customer, id_advert, date_created, address
         """)
        result = await self.session.execute(insert_query, {
            "id": next_id,
            "id_customer": user_id,
            "id_advert": advert_id,
            "address": "online"
        })
        row_insert: Optional[RowMapping] = result.mappings().first()
        await self.session.commit()
        if row_insert is None:
            raise SQLAlchemyError("INSERT INTO adv.deals returned no row")
        return Deal(**row_insert)

    async def get_deals_by_user(self, user_id: int) -> List[Advert]:
        try:
            query = text("""
                SELECT * 
                FROM adv.profile join adv.deals on adv.profile.id = adv.deals.id_customer as p join adv.adverts on adv.adverts.id = p.id_advert
                WHERE id_seller = :user_id
            """)
            result = await self.session.execute(query, {"user_id": user_id,
            })
            return [Advert(**row)  for row in result.mappings()]
        except SQLAlchemyError as e:
            print(f"Ошибка при получении объявления: {e}")
            return []


    async def is_in_deals(self, user_id: int, advert_id: int) -> bool:
        query = text("SELECT * FROM adv.deals WHERE id_customer = :uid AND id_advert = :aid")
        row = await self.session.execute(query, {"uid": user_id, "aid": advert_id})
        await self.session.commit()
        res = [Deal(**row)  for row in row.mappings()]
        if len(res):
            return True
        return False