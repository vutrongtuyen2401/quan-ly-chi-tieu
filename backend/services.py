"""Nghiệp vụ dùng chung: kiểm tra quyền sở hữu, cập nhật số dư, giao dịch định kỳ."""

import calendar
import datetime
from typing import Optional

from fastapi import HTTPException


# ──────────────────────────────────────────────
# OWNERSHIP HELPERS — đảm bảo ví / danh mục thuộc đúng người dùng
# ──────────────────────────────────────────────
def get_owned_wallet(conn, wallet_id: int, user_id: int):
    wallet = conn.execute("SELECT * FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
    if not wallet:
        raise HTTPException(status_code=404, detail="Túi Càn Khôn không tồn tại hoặc không thuộc quyền sở hữu.")
    return wallet


def get_owned_category(conn, category_id: int, user_id: int, expected_type: Optional[str] = None):
    cat = conn.execute("SELECT * FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id)).fetchone()
    if not cat:
        raise HTTPException(status_code=404, detail="Danh mục không tồn tại hoặc không thuộc quyền sở hữu.")
    if expected_type and cat["category_type"] != expected_type:
        kind = "Thu" if expected_type == "INCOME" else "Chi"
        raise HTTPException(status_code=400, detail=f"Danh mục '{cat['category_name']}' không phải danh mục {kind}.")
    return cat


def apply_wallet_delta(conn, wallet_id: int, user_id: int, txn_type: str, amount: float, reverse: bool = False):
    """Cộng/trừ số dư ví theo loại giao dịch. reverse=True để hoàn tác."""
    sign = 1 if txn_type == "INCOME" else -1
    if reverse:
        sign = -sign
    conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?",
                 (sign * amount, wallet_id, user_id))


# ──────────────────────────────────────────────
# Change 8: RECURRING TRANSACTIONS HELPER
# ──────────────────────────────────────────────
MAX_RECURRING_CATCHUP = 120  # số kỳ tối đa được bù trong 1 lần xử lý


def next_recurring_date(cur_dt: datetime.date, freq: str, day_of_month: int) -> datetime.date:
    if freq == "weekly":
        return cur_dt + datetime.timedelta(days=7)
    year, month = (cur_dt.year + 1, 1) if cur_dt.month == 12 else (cur_dt.year, cur_dt.month + 1)
    last_day = calendar.monthrange(year, month)[1]
    return datetime.date(year, month, min(day_of_month, last_day))


def process_recurring_transactions(conn, user_id: int):
    """Xử lý các giao dịch định kỳ đã đến hạn (bù đủ mọi kỳ bị lỡ) và tự động sinh giao dịch thực tế"""
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    due_sql = "SELECT * FROM recurring_transactions WHERE user_id = ? AND is_active = 1 AND next_run_date <= ?"

    if not conn.execute(due_sql, (user_id, today_str)).fetchone():
        return

    # Khóa ghi trước khi đọc lại để 2 request song song không sinh trùng giao dịch
    if not conn.in_transaction:
        conn.execute("BEGIN IMMEDIATE")
    recurring_items = conn.execute(due_sql, (user_id, today_str)).fetchall()

    for item in recurring_items:
        r_id = item["id"]
        freq = item["frequency"]
        wallet_id = item["wallet_id"]
        amount = item["amount"]
        txn_type = item["transaction_type"]
        note = item["note"] or f"Định kỳ ({'Hàng tuần' if freq == 'weekly' else 'Hàng tháng'})"

        wallet_ok = conn.execute("SELECT 1 FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
        cat_ok = conn.execute("SELECT 1 FROM categories WHERE id = ? AND user_id = ?", (item["category_id"], user_id)).fetchone()
        if not wallet_ok or not cat_ok:
            continue

        stored_date_str = item["next_run_date"]
        try:
            run_dt = datetime.datetime.strptime(stored_date_str, "%Y-%m-%d").date()
        except Exception:
            run_dt = today
        anchor_day = item["day_of_month"] or run_dt.day

        for _ in range(MAX_RECURRING_CATCHUP):
            if run_dt > today:
                break
            next_dt = next_recurring_date(run_dt, freq, anchor_day)
            next_str = next_dt.strftime("%Y-%m-%d")
            claimed = conn.execute(
                "UPDATE recurring_transactions SET next_run_date = ? WHERE id = ? AND next_run_date = ?",
                (next_str, r_id, stored_date_str)
            ).rowcount
            if claimed != 1:
                break

            conn.execute("""
                INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, wallet_id, item["category_id"], amount, txn_type, run_dt.strftime("%Y-%m-%d"), note))
            apply_wallet_delta(conn, wallet_id, user_id, txn_type, amount)

            stored_date_str = next_str
            run_dt = next_dt
