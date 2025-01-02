from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..models import User
from ..core import get_db, RoleChecker
from ..schemas.admin import Users, UserData, RoleChangeRequest, AccountRemovalRequests
from ..schemas.auth import CreateUser, ConfirmAction
from ..services.auth import auth_services
from ..services.admin import admin_services


def create_admin_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["Admin Actions"])

    @router.get("/fetch-users", response_model=Users, status_code=status.HTTP_200_OK)
    async def get_users(start: int = 0,
                        limit: int = 20,
                        user: User = Depends(RoleChecker(["admin", "master-admin"])),
                        db: AsyncSession = Depends(get_db)):
        users = await admin_services.fetch_users_paginated(db, start, limit)
        users_formatted = Users(users=users)
        return users_formatted

    @router.get("/fetch-user", response_model=UserData, status_code=status.HTTP_200_OK)
    async def get_user(email: str, user: User = Depends(RoleChecker(["admin", "master-admin"])),
                       db: AsyncSession = Depends(get_db)):
        user = await admin_services.fetch_user_by_email(email, db)
        return user

    @router.put("/activate-user-account", response_model=ConfirmAction, status_code=status.HTTP_200_OK)
    async def activate_user_account(user_id: UUID, bg_tasks: BackgroundTasks,
                                    user: User = Depends(RoleChecker(["admin", "master-admin"])),
                                    db: AsyncSession = Depends(get_db)):
        response = await admin_services.activate_user_account_by_id(user_id, db, bg_tasks)
        formatted_response = ConfirmAction(message=response)
        return formatted_response

    @router.put("/deactivate-user-account", response_model=ConfirmAction, status_code=status.HTTP_200_OK)
    async def deactivate_user_account(user_id: UUID, bg_tasks: BackgroundTasks,
                                      user: User = Depends(RoleChecker(["master-admin"])),
                                      db: AsyncSession = Depends(get_db)):
        response = await admin_services.deactivate_user_account_by_id(user_id, db, bg_tasks)
        formatted_response = ConfirmAction(message=response)
        return formatted_response

    @router.post("/add-user", response_model=ConfirmAction, status_code=status.HTTP_201_CREATED)
    async def add_user(data: CreateUser, bg_tasks: BackgroundTasks,
                       user: User = Depends(RoleChecker(["admin", "master-admin"])),
                       db: AsyncSession = Depends(get_db)):
        response = await auth_services.create_user(data, db, bg_tasks)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.delete("/remove-user", response_model=ConfirmAction, status_code=status.HTTP_200_OK)
    async def delete_deactivated_account(user_id: UUID, bg_tasks: BackgroundTasks,
                                         user: User = Depends(RoleChecker(["master-admin"])),
                                         db: AsyncSession = Depends(get_db)):
        response = await admin_services.delete_deactivated_account_by_id(user_id, db, bg_tasks)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.put("/update-user-role", response_model=UserData, status_code=status.HTTP_201_CREATED)
    async def change_user_role(data: RoleChangeRequest, user: User = Depends(RoleChecker(["master-admin"])),
                               db: AsyncSession = Depends(get_db)):
        user = await admin_services.modify_user_role(data, db)
        return user

    @router.get("/account-removal-requests", response_model=AccountRemovalRequests, status_code=status.HTTP_200_OK)
    async def get_account_removal_requests(user: User = Depends(RoleChecker(["admin", "master-admin"])),
                                           db: AsyncSession = Depends(get_db)):
        acc_removal_requests = await admin_services.fetch_pending_account_removal_requests(db)
        acc_removal_requests_formatted = AccountRemovalRequests(requests=acc_removal_requests)
        return acc_removal_requests_formatted

    return router
