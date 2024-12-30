from typing import Type
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models import User
from ..core import create_logger
from ..schemas.admin import StatusChangeRequest, RoleChangeRequest
import logging

logger = create_logger(__name__, logging.ERROR)


class AdminServices:
    """ Services class that defines what Admins can do """

    @staticmethod
    def fetch_users_paginated(db: Session, start: int = 0, limit: int = 20) -> [User]:
        users = db.query(User).offset(start).limit(limit).all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        return users

    @staticmethod
    def fetch_user_by_email(email: str, db: Session) -> Type[User] | None:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")
        return user

    def modify_user_status(self, data: StatusChangeRequest, db: Session):
        user = self.fetch_user_by_email(data.email, db)
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
        db.commit()
        db.refresh(user)
        return user

    def delete_user_by_email(self, email: str, db: Session):
        user = self.fetch_user_by_email(email, db)
        if user.role in ["admin", "master-admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot delete {user.email} since they have admin rights",
            )
        db.delete(user)
        db.commit()
        return f"User {email} deleted successfully"

    def modify_user_role(self, data: RoleChangeRequest, db: Session):
        user = self.fetch_user_by_email(data.email, db)
        if data.new_role == user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{user.email} already has {data.new_role} rights",
            )
        user.role = data.new_role
        db.commit()
        db.refresh(user)
        return user


admin_services = AdminServices()
