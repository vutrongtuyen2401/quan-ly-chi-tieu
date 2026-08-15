"""
╔══════════════════════════════════════════════════════════════════╗
║   HỆ THỐNG QUẢN LÝ CHI TIÊU — PYDANTIC SCHEMAS & VALIDATION      ║
║   Strict Data Validation & Defensive Input Sanitation            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import re
import html
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"
MONTH_YEAR_REGEX = r"^\d{4}-\d{2}$"

def sanitize_text(value: str) -> str:
    """Loại bỏ khoảng trắng thừa và escape HTML để ngăn chặn XSS"""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    return html.escape(stripped)

class RegisterBody(BaseModel):
    email: str = Field(..., description="Địa chỉ email đăng ký")
    password: str = Field(..., min_length=6, max_length=128, description="Mật khẩu tối thiểu 6 ký tự")
    full_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên người dùng")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Định dạng email không hợp lệ.")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = sanitize_text(v)
        if not v:
            raise ValueError("Họ tên không được để trống.")
        return v

class LoginBody(BaseModel):
    email: str = Field(..., description="Địa chỉ email đăng nhập")
    password: str = Field(..., min_length=1, max_length=128, description="Mật khẩu tài khoản")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Định dạng email không hợp lệ.")
        return v

class WalletBody(BaseModel):
    wallet_name: str = Field(..., min_length=1, max_length=100, description="Tên ví tiền")
    balance: float = Field(0.0, ge=0.0, le=1_000_000_000_000.0, description="Số dư ban đầu")
    wallet_type: str = Field("cash", pattern="^(cash|bank|e-wallet)$", description="Loại ví: cash, bank, e-wallet")

    @field_validator("wallet_name")
    @classmethod
    def sanitize_wallet_name(cls, v: str) -> str:
        v = sanitize_text(v)
        if not v:
            raise ValueError("Tên ví không được để trống.")
        return v

class CategoryBody(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100, description="Tên danh mục chi tiêu/thu nhập")
    category_type: str = Field(..., pattern="^(INCOME|EXPENSE)$", description="Loại: INCOME hoặc EXPENSE")
    icon: str = Field("📦", max_length=20, description="Icon biểu tượng")

    @field_validator("category_name")
    @classmethod
    def sanitize_category_name(cls, v: str) -> str:
        v = sanitize_text(v)
        if not v:
            raise ValueError("Tên danh mục không được để trống.")
        return v

class TransactionBody(BaseModel):
    wallet_id: Optional[int] = Field(None, description="ID ví tiền thực hiện giao dịch")
    category_id: int = Field(..., gt=0, description="ID danh mục")
    amount: float = Field(..., gt=0.0, le=1_000_000_000_000.0, description="Số tiền giao dịch (phải lớn hơn 0)")
    transaction_type: str = Field(..., pattern="^(INCOME|EXPENSE)$", description="Loại giao dịch: INCOME hoặc EXPENSE")
    transaction_date: str = Field(..., pattern=DATE_REGEX, description="Ngày giao dịch định dạng YYYY-MM-DD")
    note: str = Field("", max_length=500, description="Ghi chú giao dịch")

    @field_validator("note")
    @classmethod
    def sanitize_note(cls, v: str) -> str:
        return sanitize_text(v)

class TransactionUpdateBody(BaseModel):
    wallet_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    amount: Optional[float] = Field(None, gt=0.0, le=1_000_000_000_000.0)
    transaction_type: Optional[str] = Field(None, pattern="^(INCOME|EXPENSE)$")
    transaction_date: Optional[str] = Field(None, pattern=DATE_REGEX)
    note: Optional[str] = Field(None, max_length=500)

    @field_validator("note")
    @classmethod
    def sanitize_update_note(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_text(v) if v is not None else None

class TransferBody(BaseModel):
    from_wallet_id: int = Field(..., gt=0, description="ID ví nguồn")
    to_wallet_id: int = Field(..., gt=0, description="ID ví đích")
    amount: float = Field(..., gt=0.0, le=1_000_000_000_000.0, description="Số tiền chuyển")
    note: str = Field("", max_length=500, description="Ghi chú chuyển tiền")

    @field_validator("note")
    @classmethod
    def sanitize_transfer_note(cls, v: str) -> str:
        return sanitize_text(v)

class BudgetBody(BaseModel):
    category_id: int = Field(..., gt=0, description="ID danh mục áp dụng hạn mức")
    limit_amount: float = Field(..., gt=0.0, le=1_000_000_000_000.0, description="Hạn mức ngân sách tối đa")
    month_year: str = Field(..., pattern=MONTH_YEAR_REGEX, description="Tháng áp dụng định dạng YYYY-MM")

class ChatBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Nội dung câu hỏi gửi tới Trợ lý AI")

    @field_validator("message")
    @classmethod
    def sanitize_chat_msg(cls, v: str) -> str:
        v = sanitize_text(v)
        if not v:
            raise ValueError("Nội dung tin nhắn không được để trống.")
        return v

class ProfileUpdateBody(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên mới")

    @field_validator("full_name")
    @classmethod
    def sanitize_profile_name(cls, v: str) -> str:
        v = sanitize_text(v)
        if not v:
            raise ValueError("Họ tên không được để trống.")
        return v
