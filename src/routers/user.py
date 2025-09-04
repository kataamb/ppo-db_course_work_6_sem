from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import create_session
from services.auth_service import AuthService
from repositories.user_repository import UserRepository


templates = Jinja2Templates(directory="templates")
user_router = APIRouter()

# Страница логина
@user_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    print('ggg')
    return templates.TemplateResponse("login.html", {"request": request})


# Обработка формы логина
@user_router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(lambda: create_session("authorized_user"))
):
    print(type(db), db)
    repo = UserRepository(db)
    service = AuthService(repo)
    form_data = await request.form()

    email = form_data.get("email")
    password = form_data.get("password")

    #token = await service.login(db, email, password)
    try:
        token = await service.login(db, email, password)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=token, httponly=True)
        print('ok')
        return response
    except Exception as e:
        print(e)
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e)})
    finally:
        await db.close()


# -------------------
# Регистрация
# -------------------
@user_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "user": request.state.user})


@user_router.post("/register")
async def register(
    request: Request,
    nickname: str = Form(...),
    fio: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    repeat_password: str = Form(...),
    db: AsyncSession = Depends(lambda: create_session("authorized_user")),
):
    repo = UserRepository(db)
    service = AuthService(repo)
    try:
        await service.register(
            db,
            {
                "nickname": nickname,
                "fio": fio,
                "email": email,
                "phone_number": phone_number,
                "password": password,
                "repeat_password": repeat_password,
            },
        )
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "user": None, "error": str(e)})
    finally:
        await db.close()


# -------------------
# Логаут
# -------------------
@user_router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


# -------------------
# Профиль
# -------------------
@user_router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("profile.html", {"request": request, "user": request.state.user})