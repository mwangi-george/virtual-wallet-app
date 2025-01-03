import bcrypt
import logging

from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from cryptography.fernet import Fernet, InvalidToken

from ..models import User
from .database import get_db
from .logs import create_logger
from .config import settings

logger = create_logger(__name__, log_level=logging.ERROR)


class Security:
    """
    Handles security-related tasks such as token validation, password encryption, and user authentication.

    Attributes:
        JWT_SECRET_KEY (str): The secret key used for JWT encoding/decoding.
        ALGORITHM (str): The algorithm used for JWT encoding/decoding.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The expiration time for access tokens in minutes.
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer for token-based authentication.
        credentials_exception (HTTPException): The exception raised when credentials validation fails.

    Methods:
        get_password_hash(password: str) -> str:
            Hashes a password using bcrypt.

        encrypt_text(text: str) -> str:
            Encrypts a given text using the backend secret key.

        decrypt_text(encrypted_text: str) -> str:
            Decrypts a given encrypted text using the backend secret key.

        verify_password(password: str, hashed_password: str) -> bool:
            Verifies if the provided password matches the hashed password.

        get_user(email: str, db: Session) -> User | None:
            Retrieves a user from the database by email.

        authenticate_user(email: str, password: str, db: Session) -> User | bool:
            Authenticates a user by checking the email and password.

        get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
            Retrieves the current authenticated user from the provided JWT token.

        create_access_token(data: dict) -> str:
            Creates an access token with an expiration time and custom claims.

        validate_token(token: str) -> str:
            Validates a JWT token and returns the associated user's email.
    """

    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )

    @staticmethod
    def get_password_hash(password) -> str:
        """
        Hashes a given password using bcrypt.

        Args:
            password (str): The plain-text password to be hashed.

        Returns:
            str: The bcrypt hashed password.

        Raises:
            HTTPException: If there is an error while hashing the password, a 400 status code error is raised with an appropriate message.
        """
        try:
            pwd_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
            return hashed_password.decode('utf-8')
        except Exception as e:
            msg = f"Unable to hash password: {str(e)}"
            logger.error(msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    @staticmethod
    def generate_encryption_key() -> bytes:
        """Generate a new Fernet key. This should be done once"""
        key = Fernet.generate_key()
        return key

    @staticmethod
    def encrypt_text(text: str) -> str:
        """
        Encrypts a given text using a symmetric encryption method (Fernet).

        Args:
            text (str): The plain-text string to be encrypted.

        Returns:
            str: The encrypted text, encoded in UTF-8.

        Raises:
            ValueError: If the encryption fails, a ValueError is raised with an appropriate error message.
        """
        f = Fernet(settings.BACKEND_SECRET_KEY)
        try:
            encrypted_text = f.encrypt(text.encode('utf-8'))
            return encrypted_text.decode('utf-8')
        except Exception as e:
            logging.error(f"Encryption failed: {e}")
            raise ValueError("Failed to encrypt the text.")

    @staticmethod
    def decrypt_text(encrypted_text: str) -> str:
        """
        Decrypts a given encrypted text using a symmetric decryption method (Fernet).

        Args:
            encrypted_text (str): The encrypted text to be decrypted.

        Returns:
            str: The decrypted text in plain form.

        Raises:
            ValueError: If the decryption fails due to an invalid encryption key, tampered ciphertext,
                        or any other unexpected error during the decryption process.
        """
        f = Fernet(settings.BACKEND_SECRET_KEY)

        try:
            decrypted_text = f.decrypt(encrypted_text)
            return decrypted_text.decode('utf-8')
        except InvalidToken:
            logging.error("Invalid encryption key or tampered ciphertext.")
            raise ValueError("Failed to decrypt the text.")
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            raise ValueError("An unexpected error occurred during decryption.")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifies if a provided password matches a hashed password using bcrypt.

        Args:
            password (str): The plaintext password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches the hashed password, otherwise False.

        Raises:
            HTTPException: If there is an error while verifying the password, such as failure in comparison.
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            msg = f"Could not verify credentials: {str(e)}",
            logger.error(msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    @staticmethod
    async def get_user(email: str, db: Session) -> User | None:
        """
        Fetches a user from the database by their email address.

        Args:
            email (str): The email address of the user to fetch.
            db (Session): The database session to execute the query.

        Returns:
            User | None: The user object if found, or None if no user exists with the provided email.

        """
        results = await db.execute(select(User).filter_by(email=email))
        user = results.scalars().first()
        return user

    async def authenticate_user(self, email: str, password: str, db: Session) -> User | bool:
        """
        Authenticates a user by verifying their email and password.

        Args:
            email (str): The email address of the user attempting to log in.
            password (str): The plain-text password entered by the user.
            db (Session): The database session to query the user information.

        Returns:
            User | bool: The user object if authentication is successful, or False if the credentials are invalid.

        """
        user = await self.get_user(email, db)
        if not user:
            return False
        if not self.verify_password(password, user.password_hash):
            return False
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Fetches the current authenticated user based on the provided JWT token.

        Args:
            token (str, optional): The JWT token passed in the request header.
            db (Session, optional): The database session to retrieve user information.

        Returns:
            User: The authenticated user object based on the decoded token.

        Raises:
            credentials_exception: If the JWT is invalid, expired, or the user does not exist.

        """
        try:
            payload = jwt.decode(token=token, key=self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get('sub')
            if email is None:
                raise self.credentials_exception
        except JWTError:
            raise self.credentials_exception
        user = await self.get_user(email, db)
        if not user:
            raise self.credentials_exception
        return user

    def create_access_token(self, data: dict) -> str:
        """
        Creates an access token (JWT) for the given user data.

        Args:
            data (dict): The data to encode in the JWT token, typically including user-specific information like email.

        Returns:
            str: The encoded JWT access token.

        Raises:
            credentials_exception: If there is an error while generating the access token.

        """
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(claims=to_encode, key=self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Unable to create access token for user {data.get("sub")}: {str(e)}")
            raise self.credentials_exception

    def validate_token(self, token: str) -> str:
        """
        Validates the provided JWT token and extracts the user's email.

        Args:
            token (str): The JWT token to validate.

        Returns:
            str: The email address of the user encoded in the token.

        Raises:
            credentials_exception: If the token is invalid or the email is not found within the token.

        """
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get('sub')
            if not email:
                raise self.credentials_exception
            return email
        except JWTError:
            raise self.credentials_exception


# instantiate the class
security = Security()


class RoleChecker:
    """
    Handles role-based access control for users. Used to restrict access to specific routes based on user roles.

    Attributes:
        allowed_roles (list): A list of roles that are allowed to access the route.

    Methods:
        __call__(user: User = Depends(security.get_current_user)) -> User:
            Checks if the current user's role is in the allowed roles. If not, raises an HTTPException with a 403 Forbidden status.
    """
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    #  make an instance of this class callable,
    def __call__(self, user: User = Depends(security.get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this resource",
            )
        return user
