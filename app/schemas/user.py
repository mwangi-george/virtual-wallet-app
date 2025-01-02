
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
    name: str = Field(..., min_length=3, max_length=100)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "David Kai",
            }
        }
