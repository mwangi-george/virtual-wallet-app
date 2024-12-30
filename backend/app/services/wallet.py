import logging
from datetime import datetime
from typing import Type

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import User, Wallet, Transaction
from ..core import create_logger
from ..schemas.wallet import PurchaseRequest, TransferRequest, WithdrawRequest, DepositRequest

logger = create_logger(__name__, log_level=logging.ERROR)


def get_wallet_info(user_id: str, db: Session) -> Type[Wallet]:
    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with user_id {user_id} does not exist"
        )
    return wallet


class WalletServices:

    @staticmethod
    def validate_user_status(user: User):
        """ Restrict access for inactive and unverified users. """
        if not (user.active and user.verified):
            status_detail = "active" if not user.active else "verified"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User is not {status_detail}. Access denied."
            )

    def deposit_funds(self, user: User, data: DepositRequest, db: Session) -> dict:
        self.validate_user_status(user)
        wallet = get_wallet_info(user.id, db)

        new_transaction = Transaction(type="Deposit", amount=data.amount, wallet_id=wallet.id)

        try:
            wallet.balance += data.amount
            wallet.updated_at = datetime.now()
            db.add(new_transaction)
            db.commit()
            db.refresh(wallet)
            return {"amount_deposited": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            db.rollback()
            logger.error("Could not make a deposit. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    def withdraw_funds(self, user: User, data: WithdrawRequest, db: Session) -> dict:
        self.validate_user_status(user)
        wallet = get_wallet_info(user.id, db)

        if data.amount > wallet.balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds to process request. Current wallet balance: {wallet.balance}"
            )

        new_transaction = Transaction(type="Withdraw", amount=data.amount, wallet_id=wallet.id)

        try:
            wallet.balance -= data.amount
            wallet.updated_at = datetime.now()
            db.add(new_transaction)
            db.commit()
            db.refresh(wallet)
            return {"amount_withdrawn": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            db.rollback()
            logger.error("Could not make a withdraw. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    def buy_goods(self, user: User, data: PurchaseRequest, db: Session) -> dict:
        self.validate_user_status(user)
        wallet = get_wallet_info(user.id, db)

        if data.amount > wallet.balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds to process request. Current wallet balance: {wallet.balance}"
            )

        new_transaction = Transaction(type="Purchase", amount=data.amount, wallet_id=wallet.id, category=data.category)

        try:
            wallet.balance -= data.amount
            wallet.updated_at = datetime.now()
            db.add(new_transaction)
            db.commit()
            db.refresh(wallet)
            return {"amount_spent": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            db.rollback()
            logger.error("Couldn't buy goods. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    def transfer_funds(self, user: User, data: TransferRequest, db: Session) -> dict:
        self.validate_user_status(user)
        wallet = get_wallet_info(user.id, db)

        if data.amount > wallet.balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds to process request. Current wallet balance: {wallet.balance}"
            )

        recipient_info = db.query(User).filter_by(id=data.recipient_id).first()
        if recipient_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Couldn't find recipient with user_id {data.recipient_id}"
            )
        if not recipient_info.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Couldn't transfer funds, recipient is no longer active"
            )
        if not recipient_info.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Couldn't transfer funds, recipient is not verified"
            )
        recipient_wallet = get_wallet_info(data.recipient_id, db)

        transaction_data = [
            Transaction(type="Transfer", amount=data.amount, wallet_id=wallet.id, category=data.spending_category),
            Transaction(type="Receive", amount=data.amount, wallet_id=recipient_wallet.id)
        ]
        try:
            wallet.balance -= data.amount
            wallet.updated_at = datetime.now()

            recipient_wallet.balance += data.amount
            recipient_wallet.updated_at = datetime.now()

            db.add_all(transaction_data)
            db.commit()
            db.refresh(wallet)
            return {"amount_transferred": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            db.rollback()
            logger.error("Couldn't transfer funds. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    def get_balance(self, user: User, db: Session) -> dict:
        self.validate_user_status(user)
        wallet = get_wallet_info(user.id, db)
        return {"balance": wallet.balance}


wallet_services = WalletServices()
