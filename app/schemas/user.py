
from pydantic import BaseModel


class RemoveAccountRequest(BaseModel):
    details: str | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "details": "Do not want to use VWS app anymore"
            }
        }
