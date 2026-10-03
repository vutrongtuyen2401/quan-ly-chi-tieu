"""Sổ nợ / cho vay."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import get_db
from backend.schemas import DebtCreateBody, DebtUpdateBody
from backend.security import get_current_user
from backend.services import get_owned_wallet

router = APIRouter()


# ──────────────────────────────────────────────
# DEBTS ROUTES (THEO DÕI SỔ NỢ / VAY MƯỢN)
# ──────────────────────────────────────────────
@router.get("/api/debts")
def get_debts(debt_type: Optional[str] = Query(None), is_settled: Optional[int] = Query(None), user: dict = Depends(get_current_user)):
    with get_db() as conn:
        where_clauses = ["d.user_id = ?"]
        params = [user["user_id"]]

        if debt_type and debt_type in ("BORROW", "LEND"):
            where_clauses.append("d.debt_type = ?")
            params.append(debt_type)

        if is_settled is not None:
            where_clauses.append("d.is_settled = ?")
            params.append(is_settled)

        where_sql = " AND ".join(where_clauses)
        rows = conn.execute(f"""
            SELECT d.*, w.wallet_name
            FROM debts d
            LEFT JOIN wallets w ON d.wallet_id = w.id
            WHERE {where_sql}
            ORDER BY d.is_settled ASC, d.due_date ASC, d.id DESC
        """, params).fetchall()

        # Thống kê tổng hợp nợ
        stats = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN debt_type = 'BORROW' AND is_settled = 0 THEN amount ELSE 0 END), 0) as total_borrow_unsettled,
                COALESCE(SUM(CASE WHEN debt_type = 'LEND' AND is_settled = 0 THEN amount ELSE 0 END), 0) as total_lend_unsettled,
                COALESCE(SUM(CASE WHEN debt_type = 'BORROW' AND is_settled = 1 THEN amount ELSE 0 END), 0) as total_borrow_settled,
                COALESCE(SUM(CASE WHEN debt_type = 'LEND' AND is_settled = 1 THEN amount ELSE 0 END), 0) as total_lend_settled
            FROM debts
            WHERE user_id = ?
        """, (user["user_id"],)).fetchone()

        return {
            "debts": [dict(r) for r in rows],
            "summary": {
                "total_borrow_unsettled": stats["total_borrow_unsettled"],
                "total_lend_unsettled": stats["total_lend_unsettled"],
                "total_borrow_settled": stats["total_borrow_settled"],
                "total_lend_settled": stats["total_lend_settled"],
            }
        }


@router.post("/api/debts")
def create_debt(body: DebtCreateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        if body.wallet_id is not None:
            get_owned_wallet(conn, body.wallet_id, user["user_id"])
        conn.execute("""
            INSERT INTO debts (user_id, wallet_id, debt_type, person_name, amount, due_date, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user["user_id"], body.wallet_id, body.debt_type, body.person_name.strip(), body.amount, body.due_date or "", body.note or ""))
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Đã ghi nhận vào Sổ Nợ!"}


@router.put("/api/debts/{debt_id}")
def update_debt(debt_id: int, body: DebtUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ? AND user_id = ?", (debt_id, user["user_id"])).fetchone()
        if not debt:
            raise HTTPException(status_code=404, detail="Khoản nợ không tồn tại.")

        # wallet_id gửi lên là null → gỡ liên kết ví; không gửi → giữ nguyên
        w_id = body.wallet_id if "wallet_id" in body.model_fields_set else debt["wallet_id"]
        if w_id is not None:
            get_owned_wallet(conn, w_id, user["user_id"])
        d_type = body.debt_type or debt["debt_type"]
        p_name = body.person_name or debt["person_name"]
        amt = body.amount if body.amount is not None else debt["amount"]
        d_date = body.due_date if body.due_date is not None else debt["due_date"]
        note = body.note if body.note is not None else debt["note"]
        settled = body.is_settled if body.is_settled is not None else debt["is_settled"]

        conn.execute("""
            UPDATE debts SET wallet_id=?, debt_type=?, person_name=?, amount=?, due_date=?, note=?, is_settled=?
            WHERE id=? AND user_id=?
        """, (w_id, d_type, p_name, amt, d_date, note, settled, debt_id, user["user_id"]))

        return {"message": "Khoản nợ đã được cập nhật!"}


@router.post("/api/debts/{debt_id}/settle")
def toggle_settle_debt(debt_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        debt = conn.execute("SELECT * FROM debts WHERE id = ? AND user_id = ?", (debt_id, user["user_id"])).fetchone()
        if not debt:
            raise HTTPException(status_code=404, detail="Khoản nợ không tồn tại.")

        new_settled = 0 if debt["is_settled"] == 1 else 1
        conn.execute("UPDATE debts SET is_settled = ? WHERE id = ? AND user_id = ?", (new_settled, debt_id, user["user_id"]))
        msg = "Khoản nợ đã được tất toán thành công!" if new_settled == 1 else "Đã hoàn tác trạng thái chưa tất toán."
        return {"is_settled": new_settled, "message": msg}


@router.delete("/api/debts/{debt_id}")
def delete_debt(debt_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM debts WHERE id = ? AND user_id = ?", (debt_id, user["user_id"]))
        return {"message": "Đã xóa khoản nợ khỏi sổ!"}
