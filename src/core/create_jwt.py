import jwt
from datetime import datetime, timedelta
from typing import Any

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class JWTManager:
    @staticmethod
    def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            raise ValueError("Invalid token")
