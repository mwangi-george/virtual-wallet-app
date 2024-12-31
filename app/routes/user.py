from fastapi import Depends, APIRouter, status, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user import CreateUser, ConfirmAction, TokenData
from ..services.user import user_services
from ..core import get_db


def create_auth_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/auth", tags=["User Management"])

    # referencing the directory with static files
    router.mount("/static", StaticFiles(directory="static"), name="static")

    # referencing the directory with html for home page
    templates = Jinja2Templates(directory="templates")

    @router.post('/signup', response_model=ConfirmAction, status_code=status.HTTP_201_CREATED)
    async def signup(user: CreateUser, bg_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
        response = await user_services.create_user(user, db, bg_tasks)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.get('/verify-account', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
    async def verify_account(token: str, request: Request,  db: AsyncSession = Depends(get_db)):
        response = await user_services.verify_user(token, db)
        return templates.TemplateResponse(
            name="verification_success.html",
            context={"request": request, "message": response}
        )

    @router.post('/login', response_model=TokenData, status_code=status.HTTP_200_OK)
    async def login(user_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
        token_data = await user_services.login_user(user_data.username, user_data.password, db)
        return token_data

    @router.post('/request-account-removal')
    async def request_account_removal():
        pass

    @router.post('/update-profile')
    async def update_profile():
        pass

    @router.post('/request-password-reset')
    async def request_password_reset():
        pass

    @router.post('/reset-password')
    async def reset_password():
        pass

    @router.post('/change-password')
    async def change_password():
        pass

    return router
