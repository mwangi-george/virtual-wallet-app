
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class UserData(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    verified: bool
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "0be69ca0-6084-41d6-9efa-8ecd99811075",
                "name": "John Doe",
                "email": "john_doe@gmail.com",
                "role": "user",
                "verified": True,
                "active": True,
                "created_at": "2021-02-18T00:00:00Z",
            }
        }


class Users(BaseModel):
    users: list[UserData]


class StatusChangeRequest(BaseModel):
    email: str
    new_status: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "john_doe@gmail.com",
                "new_status": True,
            }
        }


class RoleChangeRequest(BaseModel):
    email: str
    new_role: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "john_doe@gmail.com",
                "new_role": "user",
            }
        }
