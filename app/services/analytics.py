import logging
from datetime import date
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from ..models import User, Transaction
from .wallet import get_wallet_info
from ..core import create_logger

logger = create_logger(__name__, logging.ERROR)


class AnalyticServices:
    """
    Services class that provides various analytics and reporting functions for user transactions and spending.

    This class is responsible for calculating spending summaries, fetching transaction data, and providing insights into
    user spending behaviors. It serves as a backend service for operations related to financial analytics within the
    application. It is designed to be used by the `analytics_router` to serve requests related to user spending
    summaries and transaction statements.

    Methods:
        calculate_spending_summary(start: date, end: date, user: User, db: AsyncSession) -> list[dict[str, Any]]:
            Calculates and returns a summary of the user's spending categorized by spending type within the given date range.

        fetch_transactions(start: date, end: date, transaction_type: str | None, category: str | None,
                           user: User, db: AsyncSession):
            Fetches transactions within a specified date range for a user, with optional filtering for transaction type
            and category.
    """

    @staticmethod
    async def calculate_spending_summary(start: date, end: date, user: User, db: AsyncSession) -> list[dict[str, Any]]:
        """
        Calculate the spending summary for a user over a specified date range, grouped by spending category.

        This method retrieves the user's wallet information, and then calculates the total amount spent in each category
        during the provided date range (from `start` to `end`). It filters transactions to include only purchases,
        and groups the results by transaction category.

        Args:
            start (date): The start date for the spending summary (inclusive).
            end (date): The end date for the spending summary (inclusive).
            user (User): The user for whom the spending summary is to be calculated.
            db (AsyncSession): The database session used for querying the database.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each containing a spending category and the total amount spent in that category.

        Raises:
            HTTPException: If an error occurs during the calculation of the spending summary, a 500 HTTP exception is raised.
        """
        # Fetch the wallet information for the user
        wallet = await get_wallet_info(user.id, db)

        try:
            # Query to calculate spending grouped by category
            query = (
                select(
                    Transaction.category,  # Grouping by category
                    func.sum(Transaction.amount).label("amount"),  # Summing amounts
                )
                .filter(
                    and_(
                        Transaction.wallet_id == wallet.id,  # Filter for user's wallet
                        Transaction.type == "Purchase",  # Only purchases
                        func.date(Transaction.created_at) >= start,  # Within start date
                        func.date(Transaction.created_at) <= end,  # Within end date
                    )
                )
                .group_by(Transaction.category)  # Group by category
            )

            result = await db.execute(query)
            transactions = result.all()

            # convert the list of tuples to a list of dicts
            transactions_dict = [
                {"category": category, "amount": amount} for category, amount in transactions
            ]

            # Return the aggregated transactions
            return transactions_dict
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not calculate spending summary. Please contact support.",
            )

    @staticmethod
    async def fetch_transactions(start: date, end: date, transaction_type: str | None, category: str | None,
                                 user: User, db: AsyncSession):
        """
        Fetch a list of transactions for a user over a specified date range, with optional filters for transaction type and category.

        This method retrieves transactions from the user's wallet within the given date range (from `start` to `end`).
        It allows for filtering the results by transaction type (e.g., Purchase, Deposit, Withdrawal) and category (e.g., Rent).
        The transaction type and category filters are optional and only applied if provided.

        Args:
            start (date): The start date for fetching transactions (inclusive).
            end (date): The end date for fetching transactions (inclusive).
            transaction_type (str | None): The type of transaction to filter by (optional). Options include: "Purchase", "Transfer", "Deposit", "Withdrawal".
            category (str | None): The category of transactions to filter by (optional).
            user (User): The user for whom the transactions are being fetched.
            db (AsyncSession): The database session used for querying the database.

        Returns:
            list: A list of transactions matching the specified filters.

        Raises:
            HTTPException: If an error occurs during the fetching of transactions, a 500 HTTP exception is raised.
        """
        wallet = await get_wallet_info(user.id, db)

        try:
            # build query
            query = (
                select(Transaction)
                .filter(
                    and_(
                        Transaction.wallet_id == wallet.id,
                        func.date(Transaction.created_at) >= start,
                        func.date(Transaction.created_at) <= end,
                    )
                )
            )
            # Add option filtering variables if provided
            if transaction_type:
                query = query.filter_by(type=transaction_type)
            if category:
                query = query.filter_by(category=category)

            # execute query
            transactions = await db.execute(query)
            return transactions.scalars().all()
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not fetch transactions. Please contact support.",
            )


analytic_services = AnalyticServices()
