from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.db import create_session
from services.advert_service import AdvertService
from services.liked_service import *
from services.deal_service import *
from repositories.liked_repository import *
from repositories.deal_repository import *
from repositories.advert_repository import AdvertsRepository

from repositories.category_repository import *
from services.category_service import *


from fastapi.responses import RedirectResponse

from dto.advert_dto import AdvertWithCategoryDTO



templates = Jinja2Templates(directory="templates")
main_router = APIRouter()


@main_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # токен можно проверять здесь, чтобы в хедере решать, что показывать
    token = request.cookies.get("access_token")
    #return templates.TemplateResponse("index.html", {"request": request, "token": token})
    #return templates.TemplateResponse("index.html", {"request": request, "user": request.state.user})

    if request.state.user:
        db = create_session("authorized_user")
    else:
        db = create_session("any_user")
    user_id = request.state.user["id"] if request.state.user else None
    try:
        category_repo = CategoryRepository(db)
        categories = await CategoryService(category_repo).get_all()
        repo =  AdvertsRepository(db)

        adverts_dto = []

        adverts = await AdvertService(repo).get_all_adverts()
        for advert in adverts:
            advert_dict = advert.model_dump()

            dto = AdvertWithCategoryDTO(**advert_dict)
            dto.category_name = await CategoryService(category_repo).get_name_by_id(dto.id_category)

            if request.state.user:
                dto.is_favorite = await LikedService(LikedRepository(db)).is_liked(user_id, dto.id)
                dto.is_bought = await DealsService(DealRepository(db)).is_in_deals(user_id, dto.id)
                dto.is_created = await AdvertService(AdvertsRepository(db)).is_created(user_id, dto.id)
            adverts_dto.append(dto)

    finally:
        await db.close()

    #print(request.state.user, user_id)
    #print(adverts_dto)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": request.state.user,
            "user_id": user_id,
            "adverts": adverts_dto,
            "categories": categories
        },
    )


@main_router.get("/category/{category_id}", response_class=HTMLResponse)
async def adverts_by_category(request: Request, category_id: int):
    if request.state.user:
        db = create_session("authorized_user")
    else:
        db = create_session("any_user")
    user_id = request.state.user["id"] if request.state.user else None
    try:
        category_repo = CategoryRepository(db)
        categories = await CategoryService(category_repo).get_all()

        repo = AdvertsRepository(db)
        adverts = []
        if request.state.user:

            adverts = await AdvertService(repo).get_adverts_by_category_authorized(user_id, category_id)  # fix!!!!
        else:
            adverts = await AdvertService(repo).get_adverts_by_category(category_id)
    finally:
        await db.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": request.state.user,
            "user_id": user_id,
            "adverts": adverts,
            "categories": categories
        },
    )


@main_router.get("/search", response_class=HTMLResponse)
async def search_adverts(request: Request, q: str):
    db: AsyncSession = create_session("any_user" if not request.state.user else "authorized_user")
    try:
        advert_repo = AdvertsRepository(db)
        advert_service = AdvertService(advert_repo)
        adverts = await advert_service.get_adverts_by_key_word(q)

        category_repo = CategoryRepository(db)
        categories = await category_repo.get_all()
    finally:
        await db.close()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": request.state.user, "adverts": adverts, "categories": categories}
    )

@main_router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("profile.html", {"request": request, "user": request.state.user})


'''


@main_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get("access_token")
    db = create_session("any_user")
    try:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        user_id = await auth_service.get_current_user_id(token)

        repo = AdvertsRepository(db)
        adverts = await AdvertService(repo).get_all_adverts_for_user(user_id)
    finally:
        await db.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": request.state.user,
            "user_id": user_id,   
            "adverts": adverts,
        },
    )
'''