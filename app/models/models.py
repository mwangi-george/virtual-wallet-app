from datetime import datetime
from sqlalchemy import Column, UUID, String, Boolean, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

# Base class for all db models
Base = declarative_base()


class User(Base):
    """ Represents a user """
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
    """ Represents a wallet """
    __tablename__ = 'wallet'

    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID, ForeignKey('user.id', ondelete="CASCADE"), nullable=False, index=True)
    balance = Column(Float, nullable=True)
    currency = Column(String, nullable=True, default='KES', index=True)
    updated_at = Column(DateTime, default=datetime.now, nullable=True)

    transactions = relationship("Transaction", backref="wallet", cascade="all, delete-orphan")


class Transaction(Base):
    """ Represents a transaction """
    __tablename__ = 'transaction'

    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    wallet_id = Column(UUID, ForeignKey('wallet.id', ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Task(Base):
    """ Represents a task: Used to manage long-running tasks """
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String, nullable=False)
    triggered_by = Column(Integer, nullable=False)
    task_name = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
