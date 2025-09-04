from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Deal(BaseModel):
    id: int | None = None
    id_advert: int
    id_customer: int
    date_created: Optional[datetime] = None
    status: int = 0
    address: str | None  = "online"
