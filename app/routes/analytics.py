from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User
from ..core import security, get_db
from ..services.analytics import analytic_services
from ..schemas.analytics import StatementSummaryResponse, SpendingSummaryResponse


def create_analytics_router() -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/analytics",
        tags=["Spending Analytics"],
    )

    @router.get("/spending-summary", status_code=status.HTTP_200_OK)
    async def get_spending_summary(start_date: date = Query(date.today() - timedelta(days=90)),
                                   end_date: date = Query(date.today()),
                                   user: User = Depends(security.get_current_user), db: AsyncSession = Depends(get_db)):
        transactions = await analytic_services.calculate_spending_summary(start_date, end_date, user, db)
        summary = SpendingSummaryResponse(summary=transactions)
        return summary

    @router.get("/request-statement", response_model=StatementSummaryResponse, status_code=status.HTTP_200_OK)
    async def get_statement(start_date: date = Query(date.today() - timedelta(days=90)),
                            end_date: date = Query(date.today()),
                            transaction_type: str = Query(
                                default=None,
                                description=f"Type of the Transaction, Options include: "
                                            f"Purchase, Transfer, Deposit, Withdrawal"),
                            category: str = Query(None, description="Spending Category, e.g. Rent"),
                            user: User = Depends(security.get_current_user), db: AsyncSession = Depends(get_db)):
        transactions = await analytic_services.fetch_transactions(start_date, end_date, transaction_type, category, user, db)
        statement = StatementSummaryResponse(transactions=transactions)
        return statement

    return router
