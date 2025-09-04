from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class AdvertWithCategoryDTO(BaseModel):
    id: int
    content: str
    description: str
    id_category: int
    category_name: str | None = None
    price: int
    status: int
    id_seller: int
    seller_name: str | None = None
    date_created: Optional[datetime]


    is_favorite: bool = False
    is_bought: bool = False
    is_created: bool = False
