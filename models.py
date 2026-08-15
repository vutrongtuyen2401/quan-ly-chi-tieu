"""
╔══════════════════════════════════════════════════════════════════╗
║   HỆ THỐNG QUẢN LÝ CHI TIÊU — CƠ SỞ DỮ LIỆU & ORM MODELS         ║
║   SQLAlchemy ORM Entities matching production schema             ║
║   Full Unicode (NVARCHAR) & FontAwesome (String 100) Support     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Unicode, UnicodeText
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(Unicode(150), unique=True, nullable=False, index=True)
    PasswordHash = Column(String(255), nullable=False)
    FullName = Column(Unicode(150), nullable=False)
    Role = Column(String(50), default="User", nullable=False)
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class Category(Base):
    __tablename__ = "Categories"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(Unicode(150), nullable=False, index=True)
    Type = Column(String(50), nullable=False)  # INCOME / EXPENSE
    Icon = Column(Unicode(100), default="fa-solid fa-box", nullable=False)
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class Transaction(Base):
    __tablename__ = "Transactions"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, nullable=False, index=True)
    CategoryId = Column(Integer, nullable=False, index=True)
    Amount = Column(Float, nullable=False)
    TransactionDate = Column(String(50), nullable=False, index=True)
    Note = Column(Unicode(500), default="", nullable=False)
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    wallet_name = Column(Unicode(150), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    wallet_type = Column(String(50), default="cash", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    category_id = Column(Integer, nullable=False, index=True)
    limit_amount = Column(Float, nullable=False)
    month_year = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    debt_name = Column(Unicode(200), nullable=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0, nullable=False)
    duration_months = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class SavingGoal(Base):
    __tablename__ = "saving_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    goal_name = Column(Unicode(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0, nullable=False)
    auto_save_percentage = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    wallet_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    note = Column(Unicode(500), default="", nullable=False)
    recurring_day = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class InvoiceOcrLog(Base):
    __tablename__ = "invoice_ocr_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    image_path = Column(Unicode(500), default="", nullable=False)
    extracted_json = Column(UnicodeText, default="{}", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    prompt_question = Column(UnicodeText, nullable=False)
    ai_response = Column(UnicodeText, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
