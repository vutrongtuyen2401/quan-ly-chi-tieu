"""Pydantic schemas kèm kiểm tra dữ liệu đầu vào."""

import datetime
import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal, Optional

from pydantic import AfterValidator, BaseModel, Field, StringConstraints


# ──────────────────────────────────────────────
# PYDANTIC SCHEMAS (kèm kiểm tra dữ liệu đầu vào)
# ──────────────────────────────────────────────
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
MAX_AMOUNT = 1e13  # 10 nghìn tỷ — chặn số vô lý / tràn số


def _check_date(v: str) -> str:
    v = v.strip()
    try:
        datetime.datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Ngày không hợp lệ (định dạng đúng: YYYY-MM-DD).")
    return v


def _check_optional_date(v: Optional[str]) -> Optional[str]:
    if v is None or v.strip() == "":
        return v.strip() if v is not None else None
    return _check_date(v)


def _check_month(v: str) -> str:
    v = v.strip()
    if not MONTH_RE.match(v):
        raise ValueError("Tháng không hợp lệ (định dạng đúng: YYYY-MM).")
    return v


def _check_email(v: str) -> str:
    v = v.strip().lower()
    if not EMAIL_RE.match(v) or len(v) > 254:
        raise ValueError("Email không hợp lệ.")
    return v


DateStr = Annotated[str, AfterValidator(_check_date)]
OptionalDateStr = Annotated[Optional[str], AfterValidator(_check_optional_date)]
MonthStr = Annotated[str, AfterValidator(_check_month)]
EmailStr = Annotated[str, AfterValidator(_check_email)]
def _round_vnd(v: float) -> float:
    """VNĐ không có phần lẻ: làm tròn về đồng (0.5 làm tròn lên) để mọi phép cộng số dư luôn chính xác."""
    return float(Decimal(str(v)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _round_positive_vnd(v: float) -> float:
    v = _round_vnd(v)
    if v <= 0:
        raise ValueError("Số tiền phải từ 1 đồng trở lên.")
    return v


# Cột tiền trong SQLite là REAL; chỉ lưu giá trị nguyên nên không có sai số dấu phẩy động
PositiveAmount = Annotated[float, Field(gt=0, le=MAX_AMOUNT, allow_inf_nan=False), AfterValidator(_round_positive_vnd)]
NonNegativeAmount = Annotated[float, Field(ge=0, le=MAX_AMOUNT, allow_inf_nan=False), AfterValidator(_round_vnd)]
Balance = Annotated[float, Field(ge=-MAX_AMOUNT, le=MAX_AMOUNT, allow_inf_nan=False), AfterValidator(_round_vnd)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Note = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
Icon = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=16)]
Password = Annotated[str, StringConstraints(min_length=6, max_length=128)]
SoulLamp = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=128)]
Flag = Annotated[int, Field(ge=0, le=1)]
TxnType = Literal["INCOME", "EXPENSE"]
WalletType = Literal["cash", "bank", "e-wallet"]
Frequency = Literal["weekly", "monthly"]
DebtType = Literal["BORROW", "LEND"]


class RegisterBody(BaseModel):
    email: EmailStr
    password: Password
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)] = ""
    soul_lamp: SoulLamp

class LoginBody(BaseModel):
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=254)]
    password: Annotated[str, StringConstraints(max_length=128)]

class ForgotPasswordBody(BaseModel):
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=254)]
    soul_lamp: Annotated[str, StringConstraints(max_length=128)]

class ResetPasswordBody(BaseModel):
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=254)]
    token: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]
    new_password: Password

class SoulLampUpdateBody(BaseModel):
    current_password: Annotated[str, StringConstraints(max_length=128)]
    new_soul_lamp: SoulLamp

class ProfileUpdateBody(BaseModel):
    full_name: Name

class WalletBody(BaseModel):
    wallet_name: Name
    balance: Balance = 0
    wallet_type: WalletType = "cash"

class WalletUpdateBody(BaseModel):
    wallet_name: Optional[Name] = None
    wallet_type: Optional[WalletType] = None

class TransferBody(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: PositiveAmount
    note: Optional[Note] = None

class CategoryBody(BaseModel):
    category_name: Name
    category_type: TxnType
    icon: Icon = "📦"

class CategoryUpdateBody(BaseModel):
    category_name: Optional[Name] = None
    icon: Optional[Icon] = None

class TransactionBody(BaseModel):
    wallet_id: int
    category_id: int
    amount: PositiveAmount
    transaction_type: TxnType
    transaction_date: DateStr
    note: Optional[Note] = None

class TransactionUpdateBody(BaseModel):
    wallet_id: Optional[int] = None
    category_id: Optional[int] = None
    amount: Optional[PositiveAmount] = None
    transaction_type: Optional[TxnType] = None
    transaction_date: Optional[DateStr] = None
    note: Optional[Note] = None

class BudgetBody(BaseModel):
    category_id: int
    limit_amount: PositiveAmount
    month_year: MonthStr

class BudgetUpdateBody(BaseModel):
    limit_amount: PositiveAmount

class RecurringBody(BaseModel):
    wallet_id: int
    category_id: int
    amount: PositiveAmount
    transaction_type: TxnType = "EXPENSE"
    frequency: Frequency = "monthly"
    next_run_date: DateStr
    note: Optional[Note] = None

class RecurringUpdateBody(BaseModel):
    wallet_id: Optional[int] = None
    category_id: Optional[int] = None
    amount: Optional[PositiveAmount] = None
    transaction_type: Optional[TxnType] = None
    frequency: Optional[Frequency] = None
    next_run_date: Optional[DateStr] = None
    note: Optional[Note] = None
    is_active: Optional[Flag] = None

RecurringTransactionBody = RecurringBody
RecurringTransactionUpdateBody = RecurringUpdateBody

class ChatBody(BaseModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]

class DebtCreateBody(BaseModel):
    debt_type: DebtType
    person_name: Name
    amount: PositiveAmount
    due_date: OptionalDateStr = None
    note: Optional[Note] = None
    wallet_id: Optional[int] = None

class DebtUpdateBody(BaseModel):
    debt_type: Optional[DebtType] = None
    person_name: Optional[Name] = None
    amount: Optional[PositiveAmount] = None
    due_date: OptionalDateStr = None
    note: Optional[Note] = None
    wallet_id: Optional[int] = None
    is_settled: Optional[Flag] = None

class SavingGoalCreateBody(BaseModel):
    target_name: Name
    target_amount: PositiveAmount
    current_amount: Optional[NonNegativeAmount] = 0.0
    target_date: OptionalDateStr = None
    icon: Optional[Icon] = "🎯"

class SavingGoalUpdateBody(BaseModel):
    target_name: Optional[Name] = None
    target_amount: Optional[PositiveAmount] = None
    current_amount: Optional[NonNegativeAmount] = None
    target_date: OptionalDateStr = None
    icon: Optional[Icon] = None
    is_completed: Optional[Flag] = None

class SavingGoalDepositBody(BaseModel):
    amount: PositiveAmount
    wallet_id: Optional[int] = None

class RoleUpdateBody(BaseModel):
    role: Literal["user", "admin"]


# Pattern dùng cho tham số Query
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"
