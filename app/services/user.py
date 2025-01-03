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
    """
    UserServices class that defines methods related to user operations.

    This class provides services for managing user profiles, handling account removal requests, processing
    password reset requests, and updating user information. It encapsulates business logic related to user
    account management, allowing admins and users to perform necessary actions in a secure and efficient manner.

    Methods:
        - process_account_removal_request: Processes a request to remove a user's account.
        - update_user_profile: Updates the user's profile information.
        - process_password_reset_request: Sends a password reset link to a user.
    """

    @staticmethod
    async def process_account_removal_request(details: RemoveAccountRequest, user: User, db: AsyncSession,
                                              bg_tasks: BackgroundTasks) -> str:
        """
        Processes a user's request for account removal.

        This method checks if there is an existing account removal request for the user. If there is none,
        it creates a new request in the database and sends a confirmation email to the user. The process
        is done asynchronously in the background.

        Args:
            details (RemoveAccountRequest): The details of the account removal request.
            user (User): The user making the account removal request.
            db (AsyncSession): The database session for interacting with the database.
            bg_tasks (BackgroundTasks): A background task manager for handling asynchronous operations.

        Raises:
            HTTPException: If there is already a pending removal request or an error occurs during the process.

        Returns:
            str: A message confirming the request ID of the account removal request.
        """
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
    async def update_user_profile(data: UpdateProfileRequest, user: User, db: AsyncSession) -> str:
        """
        Updates the profile information of a user.

        This method allows users to update their profile details, such as their name. The changes are saved
        to the database, and the updated user data is refreshed.

        Args:
            data (UpdateProfileRequest): The new profile data to be updated for the user.
            user (User): The user whose profile is being updated.
            db (AsyncSession): The database session for interacting with the database.

        Raises:
            HTTPException: If an error occurs while updating the profile.

        Returns:
            str: A message confirming that the user's profile has been successfully updated.
        """
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
        """
        Processes a password reset request for a user.

        This method is responsible for handling a user's password reset request by generating a token for the
        password reset link, sending the reset link to the user's email, and scheduling the email to be sent.

        Args:
            user (User): The user who has requested a password reset.
            bg_tasks (BackgroundTasks): The background tasks to handle asynchronous operations like sending emails.

        Raises:
            HTTPException: If the user is not found or if there is an error during the process.

        Returns:
            str: A message confirming that the password reset request has been received and processed.
        """
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
