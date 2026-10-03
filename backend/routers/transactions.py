"""Giao dịch thu / chi."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import get_db
from backend.schemas import DATE_PATTERN, TransactionBody, TransactionUpdateBody, TxnType
from backend.security import get_current_user
from backend.services import apply_wallet_delta, get_owned_category, get_owned_wallet

router = APIRouter()


# ──────────────────────────────────────────────
# TRANSACTIONS ROUTES
# ──────────────────────────────────────────────



# Change 4: Tìm kiếm, lọc và phân trang giao dịch
@router.get("/api/transactions")
def get_transactions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = Query(None, pattern=DATE_PATTERN),
    end_date: Optional[str] = Query(None, pattern=DATE_PATTERN),
    category_id: Optional[int] = Query(None),
    wallet_id: Optional[int] = Query(None),
    transaction_type: Optional[TxnType] = Query(None),
    keyword: Optional[str] = Query(None, max_length=100),
    user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        where_clauses = ["t.user_id = ?"]
        params = [user["user_id"]]

        if start_date:
            where_clauses.append("t.transaction_date >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("t.transaction_date <= ?")
            params.append(end_date)
        if category_id:
            where_clauses.append("t.category_id = ?")
            params.append(category_id)
        if wallet_id:
            where_clauses.append("t.wallet_id = ?")
            params.append(wallet_id)
        if transaction_type:
            where_clauses.append("t.transaction_type = ?")
            params.append(transaction_type)
        if keyword:
            escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            where_clauses.append("t.note LIKE ? ESCAPE '\\'")
            params.append(f"%{escaped}%")

        where_sql = " AND ".join(where_clauses)

        # Tổng số kết quả (cho phân trang)
        count_row = conn.execute(f"""
            SELECT COUNT(*) as total FROM transactions t WHERE {where_sql}
        """, params).fetchone()
        total_count = count_row["total"] if count_row else 0

        rows = conn.execute(f"""
            SELECT t.*, w.wallet_name, c.category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN wallets w ON t.wallet_id = w.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE {where_sql}
            ORDER BY t.transaction_date DESC, t.id DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()

        return {
            "data": [dict(r) for r in rows],
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        }


@router.post("/api/transactions")
def create_transaction(body: TransactionBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        get_owned_wallet(conn, body.wallet_id, user["user_id"])
        get_owned_category(conn, body.category_id, user["user_id"], expected_type=body.transaction_type)
        conn.execute(
            """INSERT INTO transactions
               (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user["user_id"], body.wallet_id, body.category_id, body.amount,
             body.transaction_type, body.transaction_date, body.note or "")
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        apply_wallet_delta(conn, body.wallet_id, user["user_id"], body.transaction_type, body.amount)
        return {"id": new_id, "message": "Giao dịch Linh Thạch đã ghi nhận!"}


@router.put("/api/transactions/{txn_id}")
def update_transaction(txn_id: int, body: TransactionUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        old_txn = conn.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                               (txn_id, user["user_id"])).fetchone()
        if not old_txn:
            raise HTTPException(status_code=404, detail="Giao dịch không tồn tại.")

        new_wallet = body.wallet_id if body.wallet_id is not None else old_txn["wallet_id"]
        new_cat = body.category_id if body.category_id is not None else old_txn["category_id"]
        new_amount = body.amount if body.amount is not None else old_txn["amount"]
        new_type = body.transaction_type or old_txn["transaction_type"]
        new_date = body.transaction_date or old_txn["transaction_date"]
        new_note = body.note if body.note is not None else old_txn["note"]

        # Ví & danh mục mới phải thuộc về chính người dùng (chống sửa số dư ví của người khác)
        get_owned_wallet(conn, new_wallet, user["user_id"])
        type_changed = body.category_id is not None or body.transaction_type is not None
        get_owned_category(conn, new_cat, user["user_id"], expected_type=new_type if type_changed else None)

        # Hoàn tác số dư cũ rồi áp dụng số dư mới
        apply_wallet_delta(conn, old_txn["wallet_id"], user["user_id"], old_txn["transaction_type"], old_txn["amount"], reverse=True)
        conn.execute("""
            UPDATE transactions SET wallet_id=?, category_id=?, amount=?,
            transaction_type=?, transaction_date=?, note=? WHERE id=? AND user_id=?
        """, (new_wallet, new_cat, new_amount, new_type, new_date, new_note, txn_id, user["user_id"]))
        apply_wallet_delta(conn, new_wallet, user["user_id"], new_type, new_amount)

        return {"message": "Giao dịch đã cập nhật!"}


@router.delete("/api/transactions/{txn_id}")
def delete_transaction(txn_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        txn = conn.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                           (txn_id, user["user_id"])).fetchone()
        if not txn:
            raise HTTPException(status_code=404, detail="Giao dịch không tồn tại.")
        apply_wallet_delta(conn, txn["wallet_id"], user["user_id"], txn["transaction_type"], txn["amount"], reverse=True)
        conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (txn_id, user["user_id"]))
        return {"message": "Giao dịch đã xóa!"}
