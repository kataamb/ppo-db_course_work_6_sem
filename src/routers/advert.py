from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services.advert_service import AdvertService
from services.liked_service import *
from services.deal_service import *
from repositories.liked_repository import *
from repositories.deal_repository import *
from repositories.advert_repository import AdvertsRepository

from models.advert import Advert

from repositories.category_repository import *
from services.category_service import *

from core.db import create_session


templates = Jinja2Templates(directory="templates")
advert_router = APIRouter()


@advert_router.get("/profile/create_advert", response_class=HTMLResponse)
async def create_advert_form(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login", status_code=303)

    db = create_session("authorized_user")
    try:
        category_service = CategoryService(CategoryRepository(db))
        categories = await category_service.get_all()
        return templates.TemplateResponse(
            "create_advert.html",
            {
                "request": request,
                "user": request.state.user,
                "categories": categories
            }
        )
    finally:
        await db.close()



@advert_router.post("/profile/create_advert")
async def create_advert(
    request: Request,

):
    if not request.state.user:
        return RedirectResponse(url="/login", status_code=303)

    db = create_session("authorized_user")
    try:
        advert_repo = AdvertsRepository(db)
        advert_service = AdvertService(advert_repo)

        form_data = await request.form()
        content = form_data.get("content")
        description = form_data.get("description")
        price = int(form_data.get("price"))
        id_category = int(form_data.get("id_category"))
        advert_obj = Advert(
            content=content,
            description=description,
            id_category=id_category,
            price=price,
            id_seller=request.state.user["id"],
            status=1,
        )

        # Создание объявления через сервис
        await advert_service.create_advert(advert_obj)

        return RedirectResponse(url="/profile/my_adverts", status_code=303)
    except Exception as e:
        # При ошибке повторно показываем форму
        categories = await CategoryService(CategoryRepository(db)).get_all()
        return templates.TemplateResponse(
            "create_advert.html",
            {
                "request": request,
                "user": request.state.user,
                "categories": categories,
                "error": str(e)
            }
        )
    finally:
        await db.close()