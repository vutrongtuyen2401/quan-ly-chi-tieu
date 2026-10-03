"""Error handlers — trả lỗi dạng {"detail": "<chuỗi tiếng Việt>"} để frontend hiển thị được."""

import sqlite3

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.utils import vnd


# ──────────────────────────────────────────────
# ERROR HANDLERS — trả lỗi dạng {"detail": "<chuỗi tiếng Việt>"} để frontend hiển thị được
# ──────────────────────────────────────────────
FIELD_LABELS = {
    "email": "Email", "password": "Mật khẩu", "new_password": "Mật khẩu mới",
    "full_name": "Đạo hiệu", "soul_lamp": "Bản Mệnh Hồn Đăng", "new_soul_lamp": "Bản Mệnh Hồn Đăng mới",
    "wallet_name": "Tên ví", "wallet_type": "Loại ví", "balance": "Số dư",
    "category_name": "Tên danh mục", "category_type": "Loại danh mục", "icon": "Biểu tượng",
    "wallet_id": "Túi Càn Khôn", "category_id": "Danh mục", "amount": "Số tiền",
    "transaction_type": "Loại giao dịch", "transaction_date": "Ngày giao dịch", "note": "Ghi chú",
    "limit_amount": "Hạn mức", "month_year": "Tháng", "frequency": "Tần suất",
    "next_run_date": "Ngày chạy kế tiếp", "debt_type": "Loại nợ", "person_name": "Tên đối tác",
    "due_date": "Hạn trả", "target_name": "Tên mục tiêu", "target_amount": "Số tiền mục tiêu",
    "current_amount": "Số tiền hiện có", "target_date": "Ngày mục tiêu", "message": "Tin nhắn",
    "from_wallet_id": "Ví nguồn", "to_wallet_id": "Ví đích", "role": "Vai trò", "token": "Mã xác thực",
}


def _fmt_limit(value) -> str:
    return vnd(value) if isinstance(value, (int, float)) and float(value).is_integer() else str(value)


def _format_validation_error(err: dict) -> str:
    loc = [str(p) for p in err.get("loc", []) if p not in ("body", "query", "path")]
    field = loc[-1] if loc else ""
    label = FIELD_LABELS.get(field, field or "Dữ liệu")
    err_type = err.get("type", "")
    ctx = err.get("ctx") or {}
    if err_type == "missing":
        return f"{label} là bắt buộc."
    if err_type == "value_error":
        return str(ctx.get("error") or err.get("msg", "")).removeprefix("Value error, ")
    if err_type == "greater_than":
        return f"{label} phải lớn hơn {_fmt_limit(ctx.get('gt'))}."
    if err_type == "greater_than_equal":
        return f"{label} không được nhỏ hơn {_fmt_limit(ctx.get('ge'))}."
    if err_type in ("less_than", "less_than_equal"):
        return f"{label} vượt quá giới hạn cho phép."
    if err_type == "string_too_short":
        min_len = ctx.get("min_length", 1)
        return f"{label} không được để trống." if min_len <= 1 else f"{label} phải có ít nhất {min_len} ký tự."
    if err_type == "string_too_long":
        return f"{label} quá dài (tối đa {ctx.get('max_length')} ký tự)."
    if err_type in ("literal_error", "enum"):
        return f"{label} không hợp lệ."
    if err_type.startswith(("float_", "int_", "finite_number")):
        return f"{label} phải là số hợp lệ."
    if err_type == "string_pattern_mismatch":
        return f"{label} không đúng định dạng."
    return f"{label}: {err.get('msg', 'không hợp lệ')}"


async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = _format_validation_error(errors[0]) if errors else "Dữ liệu không hợp lệ."
    return JSONResponse(status_code=422, content={"detail": message})


async def integrity_exception_handler(_request: Request, exc: sqlite3.IntegrityError):
    print(f"[DB IntegrityError] {exc}", flush=True)
    return JSONResponse(status_code=400, content={"detail": "Dữ liệu đang được sử dụng ở nơi khác hoặc không hợp lệ."})


async def unhandled_exception_handler(_request: Request, exc: Exception):
    print(f"[Unhandled Error] {exc!r}", flush=True)
    return JSONResponse(status_code=500, content={"detail": "Hệ thống gặp trở ngại ngoài ý muốn. Vui lòng thử lại sau."})


def register_error_handlers(app):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(sqlite3.IntegrityError, integrity_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
