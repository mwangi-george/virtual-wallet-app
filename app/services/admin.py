from uuid import UUID

from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import User, AccountRemovalRequest
from ..core import create_logger, email_services, security
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

    @staticmethod
    async def activate_user_account_by_id(user_id: UUID, db: AsyncSession, bg_tasks: BackgroundTasks):
        query = await db.execute(select(User).filter_by(id=user_id))
        user = query.scalars().one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        if user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id: '{user_id}' is already activated",
            )

        try:
            user.active = True
            user.name = security.decrypt_text(user.name)
            user.email = security.decrypt_text(user.email)
            await db.commit()
            await db.refresh(user)

            bg_tasks.add_task(
                email_services.send_email_with_brevo,
                recipient=user.email,
                subject=f"Your account has been activated",
                body=email_services.generate_account_activation_email_body(user.email)
            )

            return "Account activated successfully"
        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An error occurred while processing activation request",
            )

    @staticmethod
    async def deactivate_user_account_by_id(user_id: UUID, db: AsyncSession, bg_tasks: BackgroundTasks):
        query = await db.execute(select(User).filter_by(id=user_id))
        user = query.scalars().one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id: '{user_id}' is already deactivated",
            )

        user_email = user.email
        try:
            user.active = False
            user.name = security.encrypt_text(user.name)
            user.email = security.encrypt_text(user.email)

            await db.commit()
            bg_tasks.add_task(
                email_services.send_email_with_brevo,
                recipient=user_email,
                subject=f"Your account has been deactivated",
                body=email_services.generate_account_deactivation_email_body(user_email)
            )

            return "Account deactivated successfully"
        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An error occurred while processing deactivation request",
            )

    @staticmethod
    async def delete_deactivated_account_by_id(user_id: UUID, db: AsyncSession, bg_tasks: BackgroundTasks):
        query = await db.execute(select(User).filter_by(id=user_id))
        user = query.scalars().one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        if user.role in ["master-admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot delete {user.email} since they have master-admin rights",
            )
        user_email = security.decrypt_text(user.email)
        await db.delete(user)
        await db.commit()

        bg_tasks.add_task(
            email_services.send_email_with_brevo,
            recipient=user_email,
            subject=f"Your account has been deleted",
            body=email_services.generate_account_deletion_success_email_body(user),
        )
        return f"User with id '{user_id}' deleted successfully"

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

    @staticmethod
    async def fetch_pending_account_removal_requests(db: AsyncSession):
        try:
            query = select(AccountRemovalRequest).filter_by(status="Pending")
            results = await db.execute(query)
            acc_removal_requests = results.scalars().all()
            return acc_removal_requests
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Could not process request, please check app logs"
            )


admin_services = AdminServices()
