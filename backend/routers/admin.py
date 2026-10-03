"""Quản trị: thống kê hệ thống, khóa tài khoản, phân quyền."""

from fastapi import APIRouter, Depends, HTTPException

from backend.db import get_db
from backend.schemas import RoleUpdateBody
from backend.security import require_admin

router = APIRouter()


# ──────────────────────────────────────────────
# ADMIN ROUTES (QUẢN TRỊ TÔNG MÔN)
# ──────────────────────────────────────────────
@router.get("/api/admin/stats")
def get_admin_stats(admin: dict = Depends(require_admin)):
    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0]
        locked_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 0").fetchone()[0]
        total_wallets = conn.execute("SELECT COUNT(*) FROM wallets").fetchone()[0]
        total_txns = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        total_income = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type = 'INCOME'").fetchone()[0]
        total_expense = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type = 'EXPENSE'").fetchone()[0]
        total_balance = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM wallets").fetchone()[0]
        total_debts = conn.execute("SELECT COUNT(*) FROM debts").fetchone()[0]
        total_goals = conn.execute("SELECT COUNT(*) FROM saving_goals").fetchone()[0]

        return {
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
            "total_wallets": total_wallets,
            "total_transactions": total_txns,
            "total_income": total_income,
            "total_expense": total_expense,
            "total_system_cashflow": total_income + total_expense,
            "total_balance": total_balance,
            "total_debts": total_debts,
            "total_goals": total_goals,
        }


@router.get("/api/admin/users")
def get_admin_users(admin: dict = Depends(require_admin)):
    with get_db() as conn:
        users = conn.execute("""
            SELECT
                u.id, u.email, u.full_name, u.role, u.is_active, u.created_at,
                COUNT(DISTINCT w.id) as wallet_count,
                COALESCE(SUM(w.balance), 0) as total_balance,
                (SELECT COUNT(*) FROM transactions t WHERE t.user_id = u.id) as txn_count
            FROM users u
            LEFT JOIN wallets w ON w.user_id = u.id
            GROUP BY u.id
            ORDER BY u.id ASC
        """).fetchall()
        return [dict(u) for u in users]


@router.put("/api/admin/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, admin: dict = Depends(require_admin)):
    if user_id == admin["user_id"]:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản của chính mình!")
    with get_db() as conn:
        target = conn.execute("SELECT id, is_active, email FROM users WHERE id = ?", (user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
        new_status = 0 if target["is_active"] == 1 else 1
        conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
        msg = f"Đã mở khóa tài khoản {target['email']}!" if new_status == 1 else f"Đã phong ấn (khóa) tài khoản {target['email']}!"
        return {"message": msg, "user_id": user_id, "is_active": new_status}


@router.put("/api/admin/users/{user_id}/role")
def change_user_role(user_id: int, body: RoleUpdateBody, admin: dict = Depends(require_admin)):
    if user_id == admin["user_id"] and body.role != "admin":
        raise HTTPException(status_code=400, detail="Không thể tự giáng chức của chính mình!")
    with get_db() as conn:
        target = conn.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (body.role, user_id))
        return {"message": f"Đã cập nhật vai trò của {target['email']} thành {body.role}!", "user_id": user_id, "role": body.role}
