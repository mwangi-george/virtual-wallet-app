import os
import bcrypt
import logging

from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from ..models import User
from .database import get_db
from .logs import create_logger

load_dotenv()

logger = create_logger(__name__, log_level=logging.ERROR)


class Security:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )

    @staticmethod
    def get_password_hash(password) -> str:
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
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            msg = f"Could not verify credentials: {str(e)}",
            logger.error(msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    @staticmethod
    async def get_user(email: str, db: Session) -> User | None:
        results = await db.execute(select(User).filter_by(email=email))
        user = results.scalars().first()
        return user

    async def authenticate_user(self, email: str, password: str, db: Session) -> User | bool:
        user = await self.get_user(email, db)
        if not user:
            return False
        if not self.verify_password(password, user.password_hash):
            return False
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
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
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get('sub')
            if email is None:
                raise self.credentials_exception
            return email
        except JWTError:
            raise self.credentials_exception


# instantiate the class
security = Security()


class RoleChecker:
    """ Admin class injected in admin routes"""
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
