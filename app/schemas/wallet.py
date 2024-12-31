from pydantic import BaseModel, Field


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)  # amount must be greater than zero

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount": 2000,
            }
        }


class DepositResponse(BaseModel):
    amount_deposited: float = Field(..., gt=0)
    wallet_balance: float


class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount": 2000,
            }
        }


class WithdrawalResponse(BaseModel):
    amount_withdrawn: float = Field(..., gt=0)
    wallet_balance: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount_withdrawn": 2000,
                "wallet_balance": 432000,
            }
        }


class PurchaseRequest(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=3, max_length=100)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount": 40000,
                "category": "Rent",
            }
        }


class PurchaseResponse(BaseModel):
    amount_spent: float = Field(..., gt=0)
    wallet_balance: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount_spent": 40000,
                "wallet_balance": 432000,
            }
        }


class TransferRequest(BaseModel):
    amount: float = Field(..., gt=0)
    recipient_id: str
    spending_category: str = Field(..., min_length=3, max_length=100)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount": 2000,
                "recipient_id": "0be69ca0-6084-41d6-9efa-8ecd99811075",
                "spending_category": "Family",
            }
        }


class TransferResponse(BaseModel):
    amount_transferred: float = Field(..., gt=0)
    wallet_balance: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "amount_transferred": 2000,
                "wallet_balance": 432000,
            }
        }


class BalanceResponse(BaseModel):
    balance: float
