from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import security, get_db
from ..schemas import ConfirmAction
from ..schemas.user import RemoveAccountRequest, UpdateProfileRequest
from ..models import User
from ..services.user import user_services


def create_user_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/users/manage-account", tags=["User Account Settings"])

    @router.post('/request-account-removal', response_model=ConfirmAction, status_code=status.HTTP_200_OK)
    async def request_account_removal(data: RemoveAccountRequest, bg_tasks: BackgroundTasks,
                                      user: User = Depends(security.get_current_user),
                                      db: AsyncSession = Depends(get_db)) -> ConfirmAction:
        response = await user_services.process_account_removal_request(data.details, user, db, bg_tasks)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.post('/update-profile', response_model=ConfirmAction, status_code=status.HTTP_201_CREATED)
    async def update_profile(data: UpdateProfileRequest,
                             user: User = Depends(security.get_current_user),
                             db: AsyncSession = Depends(get_db)):
        response = await user_services.update_user_profile(data, user, db)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.post('/request-password-reset', response_model=ConfirmAction, status_code=status.HTTP_201_CREATED)
    async def request_password_reset(bg_tasks: BackgroundTasks, user: User = Depends(security.get_current_user)):
        response = await user_services.process_password_reset_request(user, bg_tasks)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    return router
