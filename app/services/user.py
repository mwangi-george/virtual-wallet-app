import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks

from ..models import User, Wallet
from ..schemas.user import CreateUser
from ..core import security, create_logger, send_email

# set up logging
logger = create_logger(__name__, logging.ERROR)


class UserServices:

    @staticmethod
    def deny_access(reason: str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=reason,
        )

    @staticmethod
    async def create_user(user: CreateUser, db: AsyncSession, bg_tasks: BackgroundTasks):

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
            confirmation_link = f"http://127.0.0.1:8000/api/v1/auth/verify-account?token={reset_token}"

            bg_tasks.add_task(
                func=send_email,
                recipient=str(new_user.email),
                subject="Activate your Account",
                email_body_data={
                    "greeting": f"Hello {new_user.name},",
                    "message_body": "Click the button below to activate your account",
                },
                redirect_to=confirmation_link,
                button_label="Activate Account",
                email_template="account_verification_email.html",
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
    async def verify_user(token: str, db: AsyncSession):
        email = security.validate_token(token)
        user = await security.get_user(email, db)

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


# instantiate the class
user_services = UserServices()
