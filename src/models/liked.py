from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Liked(BaseModel):
    id: int | None = None
    id_customer: int
    id_advert: int
    date_created: Optional[datetime] = None