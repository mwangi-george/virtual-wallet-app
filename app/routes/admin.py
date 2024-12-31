from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User
from ..core import get_db, RoleChecker
from ..schemas.admin import Users, UserData, StatusChangeRequest, RoleChangeRequest
from ..schemas.user import CreateUser, ConfirmAction
from ..services.user import user_services
from ..services.admin import admin_services


def create_admin_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["Admin"])

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

    @router.put("/change-user-status", response_model=UserData,
                status_code=status.HTTP_201_CREATED, name="Activate or deactivate a user")
    async def change_user_status(data: StatusChangeRequest, user: User = Depends(RoleChecker(["admin", "master-admin"])),
                                 db: AsyncSession = Depends(get_db)):
        user = await admin_services.modify_user_status(data, db)
        return user

    @router.post("/add-user", response_model=ConfirmAction, status_code=status.HTTP_201_CREATED)
    async def add_user(data: CreateUser, user: User = Depends(RoleChecker(["admin", "master-admin"])),
                       db: AsyncSession = Depends(get_db)):
        response = await user_services.create_user(data, db)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.delete("/remove-user", response_model=ConfirmAction, status_code=status.HTTP_200_OK)
    async def remove_user(email: str, user: User = Depends(RoleChecker(["admin", "master-admin"])),
                          db: AsyncSession = Depends(get_db)):
        response = await admin_services.delete_user_by_email(email, db)
        response_formatted = ConfirmAction(message=response)
        return response_formatted

    @router.put("/update-user-role", response_model=UserData, status_code=status.HTTP_201_CREATED)
    async def change_user_role(data: RoleChangeRequest, user: User = Depends(RoleChecker(["master-admin"])),
                               db: AsyncSession = Depends(get_db)):
        user = admin_services.modify_user_role(data, db)
        return user

    return router
