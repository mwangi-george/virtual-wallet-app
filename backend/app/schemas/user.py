from pydantic import BaseModel, Field, EmailStr


class CreateUser(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=100)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john_doe@gmail.com",
                "password": "zxcv",
            }
        }


class TokenData(BaseModel):
    access_token: str
    token_type: str


class ConfirmAction(BaseModel):
    message: str | None
