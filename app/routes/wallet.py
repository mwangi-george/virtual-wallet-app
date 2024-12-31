from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import get_db, security
from ..models import User
from ..schemas.wallet import (
    DepositRequest, DepositResponse,
    WithdrawRequest, WithdrawalResponse,
    PurchaseRequest, PurchaseResponse,
    TransferRequest, TransferResponse,
    BalanceResponse,
)
from ..services.wallet import wallet_services


def create_wallet_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/wallet", tags=["Transactions"])

    @router.post("/deposit", response_model=DepositResponse, status_code=status.HTTP_201_CREATED,
                 name="Deposit", description="Deposit Funds to user's wallet")
    async def deposit(data: DepositRequest,
                      user: User = Depends(security.get_current_user),
                      db: AsyncSession = Depends(get_db)):
        """ Deposit money into the wallet"""
        response = await wallet_services.deposit_funds(user, data, db)
        return response

    @router.post("/withdraw", response_model=WithdrawalResponse, status_code=status.HTTP_200_OK,
                 name="Withdraw", description="Withdraw Funds from user's wallet")
    async def withdraw(data: WithdrawRequest,
                       user: User = Depends(security.get_current_user),
                       db: AsyncSession = Depends(get_db)):
        """ Withdraw money from the wallet"""
        response = await wallet_services.withdraw_funds(user, data, db)
        return response

    @router.post("/transfer", response_model=TransferResponse, status_code=status.HTTP_201_CREATED,
                 name="Transfer", description="Transfer Funds from user's wallet to another user's wallet")
    async def transfer(data: TransferRequest,
                       user: User = Depends(security.get_current_user),
                       db: AsyncSession = Depends(get_db)):
        """ Transfer money to another user"""
        response = await wallet_services.transfer_funds(user, data, db)
        return response

    @router.post("/transact", response_model=PurchaseResponse, status_code=status.HTTP_200_OK,
                 name="Transact", description="Perform a transaction")
    async def transact(data: PurchaseRequest,
                       user: User = Depends(security.get_current_user),
                       db: AsyncSession = Depends(get_db)):
        """ Perform a transaction on the wallet, e.g. pay rent"""
        response = await wallet_services.buy_goods(user, data, db)
        return response

    @router.get("/balance", response_model=BalanceResponse, status_code=status.HTTP_200_OK,
                name="Check balance", description="Get user's wallet balance")
    async def check_account_balance(user: User = Depends(security.get_current_user),
                                    db: AsyncSession = Depends(get_db)):
        """ Check the balance of the user's wallet"""
        response = await wallet_services.get_balance(user, db)
        return response

    return router
