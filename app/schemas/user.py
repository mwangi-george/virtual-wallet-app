
from pydantic import BaseModel, Field


class RemoveAccountRequest(BaseModel):
    details: str | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "details": "Do not want to use VWS app anymore"
            }
        }


class UpdateProfileRequest(BaseModel):
    updated_name: str = Field(..., min_length=3, max_length=100)
    updated_password: str = Field(..., min_length=4, max_length=100)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "updated_name": "David Kai",
                "updated_password": "nmlp",
            }
        }
