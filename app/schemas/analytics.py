from datetime import date, datetime, timedelta
from uuid import UUID
from pydantic import BaseModel
from fastapi import Query


class SpendingSummaryItem(BaseModel):
    category: str
    amount: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category": "Rent",
                "amount": 3000,
            }
        }


class SpendingSummaryResponse(BaseModel):
    summary: list[SpendingSummaryItem]


class StatementSummaryItem(BaseModel):
    id: UUID
    type: str
    amount: float
    category: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "8b22952d-ce0b-417d-b28b-80162a5e2c4a",
                "type": "Purchase",
                "amount": 3000,
                "category": "Rent",
                "created_at": "2024-12-30 09:22:42.652482",
            }
        }


class StatementSummaryResponse(BaseModel):
    transactions: list[StatementSummaryItem]
