import logging
from datetime import date
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import User, Transaction
from .wallet import get_wallet_info
from ..core import create_logger

logger = create_logger(__name__, logging.ERROR)


class AnalyticServices:

    @staticmethod
    def calculate_spending_summary(start: date, end: date, user: User, db: Session):
        # Fetch the wallet information for the user
        wallet = get_wallet_info(user.id, db)

        try:
            # Query to calculate spending grouped by category
            transactions = (
                db.query(
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
                .all()  # Execute the query
            )

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
    def fetch_transactions(start: date, end: date, transaction_type: str | None, category: str | None,
                           user: User, db: Session):
        wallet = get_wallet_info(user.id, db)

        try:
            # build query
            query = (
                db.query(Transaction)
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
            transactions = query.all()
            return transactions
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not fetch transactions. Please contact support.",
            )


analytic_services = AnalyticServices()
