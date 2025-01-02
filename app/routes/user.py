from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import security, get_db
from ..schemas.user import ConfirmAction
from ..models import User
from ..services.user import user_services


def create_user_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/users/manage-account", tags=["users"])

    @router.post('/request-account-removal', response_model=ConfirmAction, status_code=status.HTTP_200_OK)
    async def request_account_removal(bg_tasks: BackgroundTasks,
                                      user: User = Depends(security.get_current_user),
                                      db: AsyncSession = Depends(get_db)) -> ConfirmAction:
        response = await user_services.process_account_removal_request(user, db, bg_tasks)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

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
