"""Hạn mức chi tiêu theo tháng."""

import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import get_db
from backend.schemas import MONTH_PATTERN, BudgetBody, BudgetUpdateBody
from backend.security import get_current_user
from backend.services import get_owned_category

router = APIRouter()


# ──────────────────────────────────────────────
# BUDGETS ROUTES
# ──────────────────────────────────────────────
@router.get("/api/budgets")
def get_budgets(month_year: Optional[str] = Query(None, pattern=MONTH_PATTERN), user: dict = Depends(get_current_user)):
    if not month_year:
        month_year = datetime.date.today().strftime("%Y-%m")
    with get_db() as conn:
        rows = conn.execute("""
            SELECT b.*, c.category_name, c.icon as category_icon,
                   COALESCE((SELECT SUM(t.amount) FROM transactions t
                             WHERE t.category_id = b.category_id
                             AND t.user_id = b.user_id
                             AND t.transaction_type = 'EXPENSE'
                             AND strftime('%Y-%m', t.transaction_date) = b.month_year), 0) as spent
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ? AND b.month_year = ?
            ORDER BY b.id
        """, (user["user_id"], month_year)).fetchall()
        return [dict(r) for r in rows]


@router.post("/api/budgets")
def create_budget(body: BudgetBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        get_owned_category(conn, body.category_id, user["user_id"], expected_type="EXPENSE")
        existing = conn.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category_id = ? AND month_year = ?",
            (user["user_id"], body.category_id, body.month_year)
        ).fetchone()
        if existing:
            conn.execute("UPDATE budgets SET limit_amount = ? WHERE id = ? AND user_id = ?",
                         (body.limit_amount, existing["id"], user["user_id"]))
            return {"id": existing["id"], "message": "Hạn mức đã cập nhật!"}
        conn.execute(
            "INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
            (user["user_id"], body.category_id, body.limit_amount, body.month_year)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Hạn mức tu luyện đã thiết lập!"}


@router.put("/api/budgets/{budget_id}")
def update_budget(budget_id: int, body: BudgetUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM budgets WHERE id = ? AND user_id = ?",
            (budget_id, user["user_id"])
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Hạn mức không tồn tại hoặc không có quyền!")
        conn.execute("UPDATE budgets SET limit_amount = ? WHERE id = ? AND user_id = ?",
                     (body.limit_amount, budget_id, user["user_id"]))
        return {"message": "Cập nhật thành công!"}


@router.delete("/api/budgets/{budget_id}")
def delete_budget(budget_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, user["user_id"]))
        return {"message": "Hạn mức đã xóa!"}
