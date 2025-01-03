from datetime import datetime
from sqlalchemy import Column, UUID, String, Boolean, DateTime, ForeignKey, Float, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

# Base class for all db models
Base = declarative_base()


class User(Base):
    """
    Represents a user within the system.

    This model stores the user's personal information, authentication status, and their roles within the system.
    It also defines a relationship to the Wallet model, representing the user's financial assets.

    Attributes:
    - id (UUID): The unique identifier for the user.
    - name (str): The user's full name.
    - email (str): The user's email address, must be unique.
    - password_hash (str): The hashed password for authentication.
    - verified (bool): Indicates if the user has verified their email address.
    - active (bool): Indicates if the user is active and can access the system.
    - role (str): Defines the user's role (e.g., 'user', 'admin').
    - created_at (datetime): The timestamp when the user account was created.

    Relationships:
    - wallets (relationship): A one-to-many relationship with the Wallet model, representing the user's wallets.
    """
    __tablename__ = 'user'

    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    role = Column(String, nullable=False, default='user')
    created_at = Column(DateTime, default=datetime.now)

    wallets = relationship("Wallet", backref="user", cascade="all, delete-orphan")


class Wallet(Base):
    """
    Represents a wallet associated with a user.

    This model stores the user's financial information, including the current balance, currency, and transaction history.

    Attributes:
    - id (UUID): The unique identifier for the wallet.
    - user_id (UUID): The ID of the user associated with this wallet. It is a foreign key referencing the 'user' table.
    - balance (float): The current balance of the wallet. Can be nullable.
    - currency (str): The currency used in the wallet (e.g., 'KES' for Kenyan Shillings). Default is 'KES'.
    - updated_at (datetime): The timestamp of the last update to the wallet.

    Relationships:
    - transactions (relationship): A one-to-many relationship with the Transaction model, representing the wallet's transaction history.
    """
    __tablename__ = 'wallet'

    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID, ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True)
    balance = Column(Float, nullable=True)
    currency = Column(String, nullable=True, default='KES', index=True)
    updated_at = Column(DateTime, default=datetime.now, nullable=True)

    transactions = relationship("Transaction", backref="wallet", cascade="all, delete-orphan")


class Transaction(Base):
    """
    Represents a financial transaction related to a wallet.

    This model stores the details of a transaction, such as the type, amount, and the associated wallet.

    Attributes:
    - id (UUID): The unique identifier for the transaction.
    - wallet_id (UUID): The ID of the wallet associated with the transaction. It is a foreign key referencing the 'wallet' table.
    - type (str): The type of the transaction (e.g., 'Deposit', 'Withdraw', 'Transfer').
    - amount (float): The amount involved in the transaction.
    - category (str): The category of the transaction (optional).
    - created_at (datetime): The timestamp when the transaction was created. It is automatically updated on modification.

    Relationships:
    - wallet (relationship): A many-to-one relationship with the Wallet model, representing the wallet this transaction belongs to.
    """
    __tablename__ = 'transaction'

    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    wallet_id = Column(UUID, ForeignKey('wallet.id', ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AccountRemovalRequest(Base):
    """
    Represents a request for account removal by a user.

    This model stores details about a user's request to remove their account, including the status of the request and any additional details provided.

    Attributes:
    - id (UUID): The unique identifier for the account removal request.
    - user_id (UUID): The ID of the user making the removal request. It is a foreign key referencing the 'user' table.
    - request_timestamp (datetime): The timestamp when the account removal request was made. Defaults to the current time.
    - status (str): The status of the removal request (e.g., "Pending", "Approved", "Rejected"). Defaults to "Pending".
    - details (str): Optional field for additional details about the request (e.g., reason for removal).

    Relationships:
    - user (relationship): A many-to-one relationship with the User model, representing the user who made the request.
    """
    __tablename__ = 'account_removal_request'

    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID, ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    request_timestamp = Column(DateTime, default=datetime.now)
    status = Column(String, nullable=False, default="Pending")
    details = Column(String(100), nullable=True)
