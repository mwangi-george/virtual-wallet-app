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


class UpdateUserPassword(BaseModel):
    token: str
    new_password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "token": f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnZW9yZ2VfbXdhbmdpQGluc3VwcGx5aGVhbHRoLmN"
                         f"vbSIsImV4cCI6MTczNTg2NDYxNn0.UQl3Efa0pU1nncJfUz7qoRvgo3t4BcdiqFw8011sZ0e",
                "new_password": "zxcv",
            }
        }
