"""Giao dịch định kỳ."""

from fastapi import APIRouter, Depends, HTTPException

from backend.db import get_db
from backend.schemas import RecurringTransactionBody, RecurringTransactionUpdateBody
from backend.security import get_current_user
from backend.services import get_owned_category, get_owned_wallet, process_recurring_transactions

router = APIRouter()


# ──────────────────────────────────────────────
# Change 8: RECURRING TRANSACTIONS ROUTES
# ──────────────────────────────────────────────
@router.get("/api/recurring-transactions")
def get_recurring_transactions(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        process_recurring_transactions(conn, user["user_id"])
        rows = conn.execute("""
            SELECT r.*, w.wallet_name, c.category_name, c.icon as category_icon
            FROM recurring_transactions r
            LEFT JOIN wallets w ON r.wallet_id = w.id
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.user_id = ?
            ORDER BY r.id DESC
        """, (user["user_id"],)).fetchall()
        return [dict(r) for r in rows]


@router.post("/api/recurring-transactions")
def create_recurring_transaction(body: RecurringTransactionBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        get_owned_wallet(conn, body.wallet_id, user["user_id"])
        get_owned_category(conn, body.category_id, user["user_id"], expected_type=body.transaction_type)
        day_of_month = int(body.next_run_date[8:10])
        conn.execute("""
            INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note, day_of_month)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user["user_id"], body.wallet_id, body.category_id, body.amount, body.transaction_type, body.frequency,
              body.next_run_date, body.note or "", day_of_month))
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        process_recurring_transactions(conn, user["user_id"])
        return {"id": new_id, "message": "Giao dịch định kỳ đã được thiết lập!"}


@router.put("/api/recurring-transactions/{rec_id}")
def update_recurring_transaction(rec_id: int, body: RecurringTransactionUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rec = conn.execute("SELECT * FROM recurring_transactions WHERE id = ? AND user_id = ?", (rec_id, user["user_id"])).fetchone()
        if not rec:
            raise HTTPException(status_code=404, detail="Giao dịch định kỳ không tồn tại.")

        w_id = body.wallet_id if body.wallet_id is not None else rec["wallet_id"]
        c_id = body.category_id if body.category_id is not None else rec["category_id"]
        amt = body.amount if body.amount is not None else rec["amount"]
        t_type = body.transaction_type if body.transaction_type is not None else rec["transaction_type"]
        freq = body.frequency if body.frequency is not None else rec["frequency"]
        n_date = body.next_run_date if body.next_run_date is not None else rec["next_run_date"]
        note = body.note if body.note is not None else rec["note"]
        active = body.is_active if body.is_active is not None else rec["is_active"]
        # Đổi ngày chạy → cập nhật luôn ngày gốc trong tháng
        day_of_month = rec["day_of_month"]
        if body.next_run_date is not None and body.next_run_date != rec["next_run_date"]:
            day_of_month = int(body.next_run_date[8:10])

        get_owned_wallet(conn, w_id, user["user_id"])
        type_changed = body.category_id is not None or body.transaction_type is not None
        get_owned_category(conn, c_id, user["user_id"], expected_type=t_type if type_changed else None)

        conn.execute("""
            UPDATE recurring_transactions SET wallet_id=?, category_id=?, amount=?,
            transaction_type=?, frequency=?, next_run_date=?, note=?, is_active=?, day_of_month=?
            WHERE id=? AND user_id=?
        """, (w_id, c_id, amt, t_type, freq, n_date, note, active, day_of_month, rec_id, user["user_id"]))

        process_recurring_transactions(conn, user["user_id"])
        return {"message": "Giao dịch định kỳ đã được cập nhật!"}


@router.delete("/api/recurring-transactions/{rec_id}")
def delete_recurring_transaction(rec_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM recurring_transactions WHERE id = ? AND user_id = ?", (rec_id, user["user_id"]))
        return {"message": "Giao dịch định kỳ đã được xóa!"}
