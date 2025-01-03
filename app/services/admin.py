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
    """
    A service class that provides administrative functionality for managing users and their accounts.

    This class defines various methods that allow administrators to perform actions such as:
    - Fetching user data
    - Activating or deactivating user accounts
    - Modifying user roles
    - Deleting user accounts
    - Managing pending account removal requests

    Each method typically interacts with the database to fetch or modify user-related data and may involve email notifications
    to users when certain actions are performed (e.g., account activation or deactivation).

    Methods in this class ensure that proper checks are in place, such as verifying user roles, handling edge cases,
    and raising appropriate HTTP exceptions in case of errors or invalid actions.
    """

    @staticmethod
    async def fetch_users_paginated(db: AsyncSession, start: int = 0, limit: int = 20) -> [User]:
        """
        Fetch a paginated list of users from the database.

        This method retrieves users in a paginated format based on the specified start index and limit.
        It is used by the admin router to list users for administrative purposes.

        Args:
            db (AsyncSession): The database session for querying the users.
            start (int, optional): The starting index for pagination. Defaults to 0.
            limit (int, optional): The maximum number of users to retrieve. Defaults to 20.

        Returns:
            List[User]: A list of `User` objects retrieved from the database.

        Raises:
            HTTPException: If no users are found, raises a 404 Not Found error with an appropriate message.
        """
        results = await db.execute(select(User).offset(start).limit(limit))
        users = results.scalars().all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        return users

    @staticmethod
    async def fetch_user_by_email(email: str, db: AsyncSession) -> User | None:
        """
        Fetch a user from the database by their email address.

        This method retrieves a single user based on the provided email. It is used by the admin router
        to allow administrators to access user details.

        Args:
            email (str): The email address of the user to be retrieved.
            db (AsyncSession): The database session for querying the user.

        Returns:
            User | None: The `User` object if found, otherwise raises an exception.

        Raises:
            HTTPException: If no user with the given email is found, raises a 404 Not Found error with
            an appropriate message.
        """
        results = await db.execute(select(User).filter_by(email=email))
        user = results.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")
        return user

    async def modify_user_status(self, data: StatusChangeRequest, db: AsyncSession) -> User:
        """
        Modify the status (active/inactive) of a user.

        This method allows an administrator to change a user's account status. If the new status is the same
        as the current status, an error is raised. It is used by the admin router to activate or deactivate
        a user account.

        Args:
            data (StatusChangeRequest): The request data containing the user's email and the new status.
            db (AsyncSession): The database session for updating the user's status.

        Returns:
            User: The `User` object with the updated status.

        Raises:
            HTTPException: If the user is already in the requested status, a 400 Bad Request error is raised with
            an appropriate message.
        """
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
    async def activate_user_account_by_id(user_id: UUID, db: AsyncSession, bg_tasks: BackgroundTasks) -> str:
        """
        Activate a user account by their user ID.

        This method is used to activate a user's account by setting their status to active. If the account is
        already active, it raises a 400 Bad Request error. After activation, a confirmation email is sent to
        the user asynchronously.

        Args:
            user_id (UUID): The ID of the user whose account is to be activated.
            db (AsyncSession): The database session for updating the user's status.
            bg_tasks (BackgroundTasks): Background tasks for sending the confirmation email asynchronously.

        Returns:
            str: A success message confirming the account activation.

        Raises:
            HTTPException:
                - 404 Not Found: If the user with the given ID is not found.
                - 400 Bad Request: If the user account is already activated, or if an error occurs during activation.
        """
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
    async def deactivate_user_account_by_id(user_id: UUID, db: AsyncSession, bg_tasks: BackgroundTasks) -> str:
        """
        Deactivate a user account by their user ID.

        This method deactivates a user's account by setting their status to inactive. If the account is already
        inactive, it raises a 400 Bad Request error. After deactivation, a confirmation email is sent to the user
        asynchronously.

        Args:
            user_id (UUID): The ID of the user whose account is to be deactivated.
            db (AsyncSession): The database session for updating the user's status.
            bg_tasks (BackgroundTasks): Background tasks for sending the confirmation email asynchronously.

        Returns:
            str: A success message confirming the account deactivation.

        Raises:
            HTTPException:
                - 404 Not Found: If the user with the given ID is not found.
                - 400 Bad Request: If the user account is already deactivated, or if an error occurs during deactivation.
        """
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
    async def delete_deactivated_account_by_id(user_id: UUID, db: AsyncSession, bg_tasks: BackgroundTasks) -> str:
        """
        Delete a deactivated user account by their user ID.

        This method deletes a user account if it is deactivated and the user is not a master-admin. If the user is
        active, a 400 Bad Request error is raised, instructing the admin to deactivate the account first. A confirmation
        email is sent to the user after deletion. If the user is a master-admin, a 403 Forbidden error is raised.

        Args:
            user_id (UUID): The ID of the user whose account is to be deleted.
            db (AsyncSession): The database session for deleting the user's account.
            bg_tasks (BackgroundTasks): Background tasks for sending the confirmation email asynchronously.

        Returns:
            str: A success message confirming the account deletion.

        Raises:
            HTTPException:
                - 404 Not Found: If the user with the given ID is not found.
                - 403 Forbidden: If the user has master-admin rights and cannot be deleted.
                - 400 Bad Request: If the user is active and the account cannot be deleted.
        """
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
        if user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can not delete an active user. Please deactivate their account first",
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

    async def modify_user_role(self, data: RoleChangeRequest, db: AsyncSession) -> User:
        """
        Modify the role of an existing user.

        This method updates the role of a user based on the provided email. If the user already has the specified role,
        a 400 Bad Request error is raised. After the role change, the user's updated information is committed to the database.

        Args:
            data (RoleChangeRequest): A request object containing the email of the user and the new role to be assigned.
            db (AsyncSession): The database session used to retrieve and update the user's role.

        Returns:
            User: The updated user object with the new role.

        Raises:
            HTTPException:
                - 400 Bad Request: If the user already has the specified role.
                - 404 Not Found: If the user with the specified email is not found.
        """
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
        """
        Fetch all pending account removal requests.

        This method retrieves all account removal requests with a "Pending" status from the database. If any error occurs
        while processing the request, a 400 Bad Request error is raised.

        Args:
            db (AsyncSession): The database session used to execute the query and fetch the account removal requests.

        Returns:
            List[AccountRemovalRequest]: A list of account removal requests that are currently pending.

        Raises:
            HTTPException:
                - 400 Bad Request: If there is an error while processing the request.
        """
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
