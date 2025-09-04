from fastapi import FastAPI
from routers.main import main_router
from routers.user import user_router

# потом подключишь routers.advert и т.д.

from routers.advert import advert_router
from routers.liked import likes_router


from fastapi import Request

from core.create_jwt import JWTManager

app = FastAPI()


# -------------------
# Middleware: определяет текущего пользователя
# -------------------
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    request.state.user = None
    if token:
        try:
            payload = JWTManager.decode_token(token)
            request.state.user = {
                "id": payload.get("id"),
                "email": payload.get("sub"),
                "role": payload.get("role"),
            }
        except Exception:
            request.state.user = None
    response = await call_next(request)
    return response




app.include_router(main_router)
app.include_router(user_router)
app.include_router(advert_router)
app.include_router(likes_router)