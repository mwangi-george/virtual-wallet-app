import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, BackgroundTasks
from datetime import datetime
from ..models import User, AccountRemovalRequest
from ..core import email_services, create_logger, security, settings
from ..schemas.user import RemoveAccountRequest, UpdateProfileRequest

logger = create_logger(__name__, logging.ERROR)


class UserServices:

    @staticmethod
    async def process_account_removal_request(details: RemoveAccountRequest, user: User, db: AsyncSession, bg_tasks: BackgroundTasks):
        existing_request_query = select(AccountRemovalRequest).filter_by(user_id=user.id)
        existing_request = await db.execute(existing_request_query)

        if existing_request.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A request with this user already exists. Status: Pending",
            )

        try:
            account_removal_request = AccountRemovalRequest(
                user_id=user.id,
                request_timestamp=datetime.now(),
                details=details
            )
            db.add(account_removal_request)
            await db.commit()
            await db.refresh(account_removal_request)

            bg_tasks.add_task(
                email_services.send_email_with_brevo,
                recipient=user.email,
                subject="Account removal request received",
                body=email_services.generate_account_removal_request_email_body(user)
            )
            return f"Account removal request received. Request ID: {account_removal_request.id}"
        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process request. Please contact support."
            )

    @staticmethod
    async def update_user_profile(data: UpdateProfileRequest, user: User, db: AsyncSession):
        try:
            user.name = data.name
            await db.commit()
            await db.refresh(user)
            return "User profile updated successfully"
        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process request. Please contact support."
            )

    @staticmethod
    async def process_password_reset_request(user: User, bg_tasks: BackgroundTasks):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        try:

            token = security.create_access_token({"sub": user.email})
            reset_link = f"{settings.BACKEND_DOMAIN}/api/v1/auth/forms/password-reset?token={token}"
            user_name = user.name if user.name else user.email
            bg_tasks.add_task(
                email_services.send_email_with_brevo,
                recipient=user.email,
                subject="Password reset request",
                body=email_services.generate_password_reset_email_body(user_name, reset_link)
            )
            return f"Password reset request received. Request ID: {user.id}"
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process request. Please contact support."
            )


user_services = UserServices()
