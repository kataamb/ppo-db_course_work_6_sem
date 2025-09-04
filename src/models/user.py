from pydantic import BaseModel


class User(BaseModel):
    id: int
    nickname: str
    fio: str
    email: str
    phone_number: str
    password: str
