from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import User
from ..core import create_logger
from ..schemas.admin import StatusChangeRequest, RoleChangeRequest
import logging

logger = create_logger(__name__, logging.ERROR)


class AdminServices:
    """ Services class that defines what Admins can do """

    @staticmethod
    async def fetch_users_paginated(db: AsyncSession, start: int = 0, limit: int = 20) -> [User]:
        results = await db.execute(select(User).offset(start).limit(limit))
        users = results.scalars().all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        return users

    @staticmethod
    async def fetch_user_by_email(email: str, db: AsyncSession) -> User | None:
        results = await db.execute(select(User).filter_by(email=email))
        user = results.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")
        return user

    async def modify_user_status(self, data: StatusChangeRequest, db: AsyncSession):
        user = await self.fetch_user_by_email(data.email, db)
        if data.new_status == user.active:
            if data.new_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{user.email} is already activated",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{user.email} is already deactivated",
                )
        user.active = data.new_status
        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user_by_email(self, email: str, db: AsyncSession):
        user = await self.fetch_user_by_email(email, db)
        if user.role in ["admin", "master-admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot delete {user.email} since they have admin rights",
            )
        await db.delete(user)
        await db.commit()
        return f"User {email} deleted successfully"

    async def modify_user_role(self, data: RoleChangeRequest, db: AsyncSession):
        user = await self.fetch_user_by_email(data.email, db)
        if data.new_role == user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{user.email} already has {data.new_role} rights",
            )
        user.role = data.new_role
        await db.commit()
        await db.refresh(user)
        return user


admin_services = AdminServices()
