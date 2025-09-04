from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import create_session
from services.liked_service import LikedService
from repositories.liked_repository import LikedRepository


templates = Jinja2Templates(directory="templates")
likes_router = APIRouter()


@likes_router.post("/like/{item_id}")
async def add_like(
        request: Request,
        db: AsyncSession = Depends(lambda: create_session("authorized_user"))
):
    if not request.state.user:
        return RedirectResponse(url="/login", status_code=303)

    user_id = request.state.user.id
    repo = LikedRepository(db)

    try:
        #await repo.cre(user_id, item_id)
        pass
        return RedirectResponse(url=request.referrer, status_code=303)  # Вернуться на страницу, откуда пришли
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})
    finally:
        await db.close()


@likes_router.post("/unlike/{item_id}")
async def remove_like(
        request: Request,
        item_id: int,
        db: AsyncSession = Depends(lambda: create_session("authorized_user"))
):
    if not request.state.user:
        return RedirectResponse(url="/login", status_code=303)


    repo = LikedRepository(db)
    serv = LikedService(repo)
    if request.state.user:
        db = create_session("authorized_user")
    else:
        db = create_session("any_user")
    user_id = request.state.user["id"] if request.state.user else None
    try:
        await serv.remove_from_liked(user_id, item_id)
        return RedirectResponse(url= "/", status_code=303)  # Вернуться на страницу
    except Exception as e:
        #return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})
        print(e)
    finally:
        await db.close()