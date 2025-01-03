import logging
from datetime import datetime
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from ..models import User, Wallet, Transaction
from ..core import create_logger
from ..schemas.wallet import PurchaseRequest, TransferRequest, WithdrawRequest, DepositRequest

logger = create_logger(__name__, log_level=logging.ERROR)


async def get_wallet_info(user_id: str, db: AsyncSession) -> Wallet:
    """
    Retrieves the wallet associated with the specified user.

    This function queries the database to fetch the wallet for the given user. If no wallet is found,
    it raises an HTTP 404 error. It is commonly used by various services that interact with user wallets
    (e.g., deposit, withdrawal, transfer).

    Args:
        user_id (str): The ID of the user whose wallet is being retrieved.
        db (AsyncSession): The database session for querying wallet information.

    Returns:
        Wallet: The wallet associated with the given user.

    Raises:
        HTTPException: If no wallet is found for the specified user, an HTTP 404 error is raised.
    """
    results = await db.execute(select(Wallet).filter_by(user_id=user_id))
    wallet = results.scalars().first()
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with user_id {user_id} does not exist"
        )
    return wallet


class WalletServices:
    """
        WalletServices handles operations related to a user's wallet, including depositing funds,
        withdrawing funds, transferring funds, and checking the wallet balance.

        This class includes methods to validate user status, perform wallet transactions, and maintain
        wallet integrity by ensuring users have the necessary permissions (active and verified status)
        before any transactions are processed.

        Methods:
            - validate_user_status: Ensures the user is active and verified before performing any wallet operations.
            - deposit_funds: Adds funds to the user's wallet.
            - withdraw_funds: Deducts funds from the user's wallet.
            - transfer_funds: Transfers funds from one user's wallet to another.
            - get_balance: Returns the current balance of the user's wallet.
    """

    @staticmethod
    def validate_user_status(user: User) -> None:
        """
            Validates if a user is active and verified.

            This method checks if the user's account is both active and verified. If the user is either inactive
            or unverified, an HTTP exception is raised, denying access and providing a detailed reason for the denial.

            Args:
                user (User): The user whose status is being checked.

            Raises:
                HTTPException: If the user is inactive or unverified, an HTTP 403 Forbidden error is raised
                                with a specific detail message indicating the reason for denial (either "active"
                                or "verified").
        """

        if not (user.active and user.verified):
            status_detail = "active" if not user.active else "verified"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User is not {status_detail}. Access denied."
            )

    async def deposit_funds(self, user: User, data: DepositRequest, db: AsyncSession) -> dict:
        """
            Deposits funds into the user's wallet.

            This method processes a deposit request by updating the user's wallet balance and creating a corresponding
            transaction record for the deposit. It also ensures that the user is both active and verified before processing
            the deposit. If the transaction is successful, the new wallet balance is returned.

            Args:
                user (User): The user who is making the deposit.
                data (DepositRequest): The data containing the deposit amount.
                db (AsyncSession): The database session for committing changes.

            Returns:
                dict: A dictionary containing the deposited amount and the updated wallet balance.

            Raises:
                HTTPException: If the user is not active or verified, or if there is an error during the deposit
                                process (such as a database issue), an HTTPException is raised with an appropriate error message.
        """

        self.validate_user_status(user)
        wallet = await get_wallet_info(user.id, db)

        new_transaction = Transaction(type="Deposit", amount=data.amount, wallet_id=wallet.id)

        try:
            wallet.balance += data.amount
            wallet.updated_at = datetime.now()
            db.add(new_transaction)
            await db.commit()
            await db.refresh(wallet)
            return {"amount_deposited": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            await db.rollback()
            logger.error("Could not make a deposit. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    async def withdraw_funds(self, user: User, data: WithdrawRequest, db: AsyncSession) -> dict:
        """
            Withdraws funds from the user's wallet.

            This method processes a withdrawal request by ensuring the user has sufficient funds in their wallet.
            It also validates that the user is active and verified before proceeding. If the withdrawal request
            is successful, the user's wallet balance is updated, and a new transaction record is created.

            Args:
                user (User): The user who is making the withdrawal.
                data (WithdrawRequest): The data containing the withdrawal amount.
                db (AsyncSession): The database session for committing changes.

            Returns:
                dict: A dictionary containing the withdrawn amount and the updated wallet balance.

            Raises:
                HTTPException: If the user is not active or verified, or if the withdrawal amount exceeds the
                                wallet balance, or if there is an error during the withdrawal process,
                                an HTTPException is raised with an appropriate error message.
        """
        self.validate_user_status(user)
        wallet = await get_wallet_info(user.id, db)

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
            await db.commit()
            await db.refresh(wallet)
            return {"amount_withdrawn": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            await db.rollback()
            logger.error("Could not make a withdraw. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    async def buy_goods(self, user: User, data: PurchaseRequest, db: AsyncSession) -> dict:
        self.validate_user_status(user)
        wallet = await get_wallet_info(user.id, db)

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
            await db.commit()
            await db.refresh(wallet)
            return {"amount_spent": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            await db.rollback()
            logger.error("Couldn't buy goods. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    async def transfer_funds(self, user: User, data: TransferRequest, db: AsyncSession) -> dict:
        """
            Transfers funds from the user's wallet to another user's wallet.

            This method handles the transfer of funds between two users, ensuring both users are active and verified.
            It validates the sender's and recipient's wallet balances, checks the recipient's status, and performs
            the transfer by updating both users' wallet balances. A transaction record is created for both the sender
            and the recipient. If any error occurs, the transaction is rolled back.

            Args:
                user (User): The user who is initiating the transfer.
                data (TransferRequest): The data containing transfer details such as recipient ID, amount, and spending category.
                db (AsyncSession): The database session for committing changes.

            Returns:
                dict: A dictionary containing the transferred amount and the updated wallet balance of the sender.

            Raises:
                HTTPException: If the user is not active or verified, if the recipient is not found, is inactive,
                                or is not verified, if the sender does not have sufficient funds, or if there is
                                an error during the transaction process, an HTTPException is raised with an appropriate error message.
        """
        self.validate_user_status(user)
        wallet = await get_wallet_info(user.id, db)

        if data.amount > wallet.balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds to process request. Current wallet balance: {wallet.balance}"
            )

        recipient_info_results = await db.execute(select(User).filter_by(id=data.recipient_id))
        recipient_info = recipient_info_results.scalars().first()
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
        recipient_wallet = await get_wallet_info(data.recipient_id, db)

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
            await db.commit()
            await db.refresh(wallet)
            return {"amount_transferred": data.amount, "wallet_balance": wallet.balance}
        except Exception as e:
            await db.rollback()
            logger.error("Couldn't transfer funds. Error: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request! Please try again."
            )

    async def get_balance(self, user: User, db: AsyncSession) -> dict:
        """
            Retrieves the balance of the user's wallet.

            This method checks the user's status to ensure they are active and verified, then retrieves
            the balance of their wallet. It returns the wallet balance in a dictionary format.

            Args:
                user (User): The user whose wallet balance is being retrieved.
                db (AsyncSession): The database session for querying wallet information.

            Returns:
                dict: A dictionary containing the user's wallet balance.

            Raises:
                HTTPException: If the user is not active or verified, an HTTPException is raised.
        """
        self.validate_user_status(user)
        wallet = await get_wallet_info(user.id, db)
        return {"balance": wallet.balance}


wallet_services = WalletServices()
