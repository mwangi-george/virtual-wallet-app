import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks

from ..models import User, Wallet
from ..schemas.auth import CreateUser, UpdateUserPassword
from ..core import security, create_logger, email_services, settings

# set up logging
logger = create_logger(__name__, logging.ERROR)


class AuthServices:
    """
    AuthServices handles authentication-related actions for user management.

    This service class provides functionality for user registration, login, password updates, account verification,
    and other authentication processes. It interacts with the database to create and manage user accounts, validate
    login credentials, and facilitate secure access tokens. The class also ensures security measures like hashing passwords,
    validating tokens, and checking user status (active/verified).

    Key Methods:
        - create_user: Registers a new user, hashes their password, and creates a wallet for them.
        - verify_user: Verifies a user's account using a token.
        - login_user: Authenticates a user and generates an access token if valid.
        - update_user_password: Allows a user to update their password using a valid token.
        - deny_access: Helper method for denying access to unauthorized users.
    """

    @staticmethod
    def deny_access(reason: str) -> HTTPException:
        """
        Denies access to the user with an HTTP 401 Unauthorized status.

        This method is used to raise an HTTPException that indicates the user is not authorized
        to access the requested resource. It is commonly used for scenarios such as invalid
        authentication or insufficient permissions.

        Args:
            reason (str): A message explaining why access is denied, which will be included in
                          the HTTP exception details.

        Raises:
            HTTPException: An exception with HTTP status code 401 and the provided reason.
        """
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=reason,
        )

    @staticmethod
    async def create_user(user: CreateUser, db: AsyncSession, bg_tasks: BackgroundTasks) -> str:
        """
        Creates a new user and an associated wallet, then sends a confirmation email to the user.

        This method handles the user registration process by first checking if the provided email
        already exists in the database. If the email is unique, a new user record is created along with
        a wallet for the user with a starting balance of 0.00. The method also generates a verification token
        for email confirmation and sends a verification email to the user.

        Args:
            user (CreateUser): The user data required to create the account (email, name, password).
            db (AsyncSession): The database session used to interact with the database.
            bg_tasks (BackgroundTasks): The background tasks object used to send the verification email.

        Returns:
            str: A success message indicating the user has been created successfully.

        Raises:
            HTTPException: If the email is already registered or if an error occurs during user creation.
        """

        # Check if email exists
        if await security.get_user(user.email, db):
            logger.error(f"{user.email} is trying to signup but the email is already taken")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # Begin a single transaction for user and wallet creation
        try:
            # Create the user
            new_user = User(
                email=user.email,
                name=user.name,
                password_hash=security.get_password_hash(user.password),
            )
            db.add(new_user)
            await db.flush()  # Flush to generate the user ID without committing

            # Create the wallet for the user
            # Upon registration, a wallet is automatically created for the user with a starting balance of 0.00
            wallet = Wallet(user_id=new_user.id, balance=0.0)
            db.add(wallet)

            # Commit both changes in a single transaction
            await db.commit()

            # Refresh the user to fetch any updated/generated fields
            await db.refresh(new_user)

            # send email to complete registration
            reset_token = security.create_access_token(data={'sub': new_user.email})
            confirmation_link = f"{settings.BACKEND_DOMAIN}/api/v1/auth/verify-account?token={reset_token}"

            bg_tasks.add_task(
                func=email_services.send_email_with_brevo,
                recipient=new_user.email,
                subject="Activate your Account",
                body=email_services.generate_account_verification_email(new_user, confirmation_link),
            )

            logger.info(f"Created new user with email {user.email}")
            return f"User with id '{new_user.id}' created successfully"

        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during user registration:"
            )

    @staticmethod
    async def verify_user(token: str, db: AsyncSession) -> str:
        """
        Verifies a user account based on the provided token.

        The method first validates the token and retrieves the corresponding user from the database.
        If the user is found and not already verified, their `verified` status is set to `True`,
        and a success message is returned. If the user is already verified, a message is returned indicating this.
        If the token is invalid or an error occurs during the process, an HTTP exception is raised.

        Args:
            token (str): The token that was sent to the user's email for account verification.
            db (AsyncSession): The database session to query user data.

        Returns:
            str: A message indicating the verification status of the user.

        Raises:
            HTTPException: If the token is invalid or if there is an error during the verification process.
        """
        email = security.validate_token(token)
        user = await security.get_user(email, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        try:
            if user.verified:
                return f"'{user.email}' is already verified"
            else:
                user.verified = True
                await db.commit()
                await db.refresh(user)
                return f"'{user.email}' has been verified successfully"
        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during user verification. Please contact support."
            )

    async def login_user(self, email: str, password: str, db: AsyncSession) -> dict:
        """
        Handles user login by authenticating the provided email and password.

        The method attempts to authenticate the user using the provided credentials. If the credentials are incorrect,
        or if the user is not verified or active, access is denied with an appropriate error message.
        If authentication is successful and the user is verified and active, an access token is generated and returned.

        Args:
            email (str): The email of the user attempting to log in.
            password (str): The password provided by the user for authentication.
            db (AsyncSession): The database session to query user data.

        Returns:
            dict: A dictionary containing the access token and token type.

        Raises:
            HTTPException: If the email or password is incorrect, or if the user is not verified or active.
        """
        user = await security.authenticate_user(email, password, db)
        if not user:
            self.deny_access("Incorrect email or password")
        if not user.verified:
            logger.critical(f"User with email '{email}' is trying to log in but is not verified")
            self.deny_access("User is not verified")
        if not user.active:
            logger.critical(f"User with email '{email}' is trying to log in but is deactivated")
            self.deny_access("User is not active")

        access_token = security.create_access_token(data={"sub": user.email})
        logger.info(f"Logged in user with email {user.email}")
        return {"access_token": access_token, "token_type": "Bearer"}

    @staticmethod
    async def update_user_password(data: UpdateUserPassword, db: AsyncSession):
        """
        Updates the user's password based on the provided token and new password.

        The method validates the provided token to identify the user. If the user is found, their password is updated
        with the new password provided in the request. The password is securely hashed before storing. If any issues occur
        during the process, the operation is rolled back and an error message is returned.

        Args:
            data (UpdateUserPassword): The data object containing the user's token and new password.
            db (AsyncSession): The database session to query and update user data.

        Returns:
            str: A message confirming the successful password update.

        Raises:
            HTTPException: If the user is not found, or if there is an error during the password update process.
        """
        user_email = security.validate_token(data.token)

        user = await security.get_user(user_email, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        try:
            user.password_hash = security.get_password_hash(data.new_password)
            await db.commit()
            return f"Password updated successfully"
        except Exception as e:
            await db.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during password update. Please contact support."
            )


# instantiate the class
auth_services = AuthServices()
