from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import security, get_db
from ..schemas import ConfirmAction
from ..schemas.user import RemoveAccountRequest, UpdateProfileRequest
from ..models import User
from ..services.user import user_services


def create_user_router() -> APIRouter:
    """
    Create and configure the user router for managing user account settings.

    The user router provides endpoints for account management, including requesting account removal,
    updating user profiles, and requesting password resets. These operations are restricted to
    authenticated users.

    Returns:
        APIRouter: Configured router for user account settings.

    Routes:
        - **POST /request-account-removal**:
            Allows users to request the removal of their account.
            Parameters:
                - `data` (RemoveAccountRequest): Details of the account removal request.
            Permissions: User must be authenticated.
            Response: `ConfirmAction` with a success message.

        - **POST /update-profile**:
            Updates the user's profile information.
            Parameters:
                - `data` (UpdateProfileRequest): The updated profile data.
            Permissions: User must be authenticated.
            Response: `ConfirmAction` with a success message.

        - **POST /request-password-reset**:
            Initiates a password reset process for the user.
            Parameters:
                - `bg_tasks` (BackgroundTasks): Background tasks for asynchronous processing.
            Permissions: User must be authenticated.
            Response: `ConfirmAction` with a success message.
    """
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
