"""Mục tiêu tiết kiệm."""

import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import get_db
from backend.schemas import SavingGoalCreateBody, SavingGoalDepositBody, SavingGoalUpdateBody
from backend.security import get_current_user
from backend.services import get_owned_wallet
from backend.utils import vnd

router = APIRouter()


# ──────────────────────────────────────────────
# SAVING GOALS ROUTES (MỤC TIÊU TIẾT KIỆM)
# ──────────────────────────────────────────────
@router.get("/api/saving-goals")
def get_saving_goals(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM saving_goals
            WHERE user_id = ?
            ORDER BY is_completed ASC, target_date ASC, id DESC
        """, (user["user_id"],)).fetchall()

        goals = []
        today = datetime.date.today()
        for r in rows:
            g = dict(r)
            t_amt = g["target_amount"] or 1
            c_amt = g["current_amount"] or 0
            g["percent"] = round(min((c_amt / t_amt) * 100, 100), 1)
            g["remaining_amount"] = max(t_amt - c_amt, 0)

            if g.get("target_date"):
                try:
                    t_date = datetime.date.fromisoformat(g["target_date"])
                    g["days_left"] = (t_date - today).days
                except Exception:
                    g["days_left"] = None
            else:
                g["days_left"] = None
            goals.append(g)

        # Summary
        total_target = sum(g["target_amount"] for g in goals)
        total_saved = sum(g["current_amount"] for g in goals)
        completed_count = sum(1 for g in goals if g["is_completed"])
        active_count = len(goals) - completed_count

        return {
            "goals": goals,
            "summary": {
                "total_target": total_target,
                "total_saved": total_saved,
                "completed_count": completed_count,
                "active_count": active_count,
                "overall_percent": round((total_saved / total_target * 100) if total_target > 0 else 0, 1)
            }
        }


@router.post("/api/saving-goals")
def create_saving_goal(body: SavingGoalCreateBody, user: dict = Depends(get_current_user)):
    if not body.target_name.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên mục tiêu tiết kiệm.")
    if body.target_amount <= 0:
        raise HTTPException(status_code=400, detail="Số tiền mục tiêu phải lớn hơn 0.")

    curr = max(body.current_amount or 0, 0)
    is_comp = 1 if curr >= body.target_amount else 0

    with get_db() as conn:
        conn.execute("""
            INSERT INTO saving_goals (user_id, target_name, target_amount, current_amount, target_date, icon, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user["user_id"], body.target_name.strip(), body.target_amount, curr, body.target_date or "", body.icon or "🎯", is_comp))
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Mục tiêu tiết kiệm đã được thiết lập!"}


@router.put("/api/saving-goals/{goal_id}")
def update_saving_goal(goal_id: int, body: SavingGoalUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        goal = conn.execute("SELECT * FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user["user_id"])).fetchone()
        if not goal:
            raise HTTPException(status_code=404, detail="Mục tiêu không tồn tại.")

        name = body.target_name.strip() if body.target_name else goal["target_name"]
        t_amt = body.target_amount if body.target_amount is not None and body.target_amount > 0 else goal["target_amount"]
        c_amt = body.current_amount if body.current_amount is not None and body.current_amount >= 0 else goal["current_amount"]
        t_date = body.target_date if body.target_date is not None else goal["target_date"]
        icon = body.icon if body.icon else goal["icon"]
        amounts_changed = t_amt != goal["target_amount"] or c_amt != goal["current_amount"]
        if c_amt >= t_amt:
            is_comp = 1
        elif body.is_completed is not None and not amounts_changed:
            is_comp = body.is_completed  # người dùng tự đánh dấu hoàn thành / chưa hoàn thành
        else:
            is_comp = 0

        conn.execute("""
            UPDATE saving_goals SET target_name=?, target_amount=?, current_amount=?, target_date=?, icon=?, is_completed=?
            WHERE id=? AND user_id=?
        """, (name, t_amt, c_amt, t_date, icon, is_comp, goal_id, user["user_id"]))

        return {"message": "Mục tiêu tiết kiệm đã được cập nhật!"}


@router.post("/api/saving-goals/{goal_id}/deposit")
def deposit_saving_goal(goal_id: int, body: SavingGoalDepositBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        goal = conn.execute("SELECT * FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user["user_id"])).fetchone()
        if not goal:
            raise HTTPException(status_code=404, detail="Mục tiêu không tồn tại.")

        if body.wallet_id:
            w = conn.execute("SELECT * FROM wallets WHERE id = ? AND user_id = ?", (body.wallet_id, user["user_id"])).fetchone()
            if not w:
                raise HTTPException(status_code=404, detail="Túi Càn Khôn không tồn tại.")
            if w["balance"] < body.amount:
                raise HTTPException(status_code=400, detail=f"Số dư ví không đủ (Còn {vnd(w['balance'])} VNĐ).")
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?",
                         (body.amount, body.wallet_id, user["user_id"]))

        log_goal_action(conn, user["user_id"], goal_id, "DEPOSIT", body.amount, w if body.wallet_id else None)
        new_amt = goal["current_amount"] + body.amount
        is_comp = 1 if new_amt >= goal["target_amount"] else goal["is_completed"]

        conn.execute("UPDATE saving_goals SET current_amount = ?, is_completed = ? WHERE id = ? AND user_id = ?",
                     (new_amt, is_comp, goal_id, user["user_id"]))

        msg = "🎉 Chúc mừng đạo hữu đã hoàn thành mục tiêu tiết kiệm!" if is_comp and not goal["is_completed"] else "Đã tích lũy thêm thành công!"
        return {"current_amount": new_amt, "is_completed": is_comp, "message": msg}


@router.post("/api/saving-goals/{goal_id}/withdraw")
def withdraw_saving_goal(goal_id: int, body: SavingGoalDepositBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        goal = conn.execute("SELECT * FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user["user_id"])).fetchone()
        if not goal:
            raise HTTPException(status_code=404, detail="Mục tiêu không tồn tại.")
        if goal["current_amount"] < body.amount:
            raise HTTPException(status_code=400, detail=f"Số dư mục tiêu không đủ (Hiện có {vnd(goal['current_amount'])} VNĐ).")

        wallet = None
        if body.wallet_id:
            wallet = get_owned_wallet(conn, body.wallet_id, user["user_id"])
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?",
                         (body.amount, body.wallet_id, user["user_id"]))

        log_goal_action(conn, user["user_id"], goal_id, "WITHDRAW", body.amount, wallet)
        new_amt = goal["current_amount"] - body.amount
        is_comp = 1 if new_amt >= goal["target_amount"] else 0

        conn.execute("UPDATE saving_goals SET current_amount = ?, is_completed = ? WHERE id = ? AND user_id = ?",
                     (new_amt, is_comp, goal_id, user["user_id"]))

        return {"current_amount": new_amt, "is_completed": is_comp, "message": "Đã rút linh thạch khỏi mục tiêu!"}


@router.delete("/api/saving-goals/{goal_id}")
def delete_saving_goal(goal_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM saving_goal_logs WHERE goal_id = ? AND user_id = ?", (goal_id, user["user_id"]))
        conn.execute("DELETE FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user["user_id"]))
        return {"message": "Đã xóa mục tiêu tiết kiệm!"}


def log_goal_action(conn, user_id: int, goal_id: int, action: str, amount: float, wallet=None):
    conn.execute(
        "INSERT INTO saving_goal_logs (user_id, goal_id, action, amount, wallet_id, wallet_name) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, goal_id, action, amount, wallet["id"] if wallet else None, wallet["wallet_name"] if wallet else "")
    )


@router.get("/api/saving-goals/{goal_id}/logs")
def get_saving_goal_logs(goal_id: int, limit: int = Query(20, ge=1, le=100), user: dict = Depends(get_current_user)):
    with get_db() as conn:
        goal = conn.execute("SELECT id FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user["user_id"])).fetchone()
        if not goal:
            raise HTTPException(status_code=404, detail="Mục tiêu không tồn tại.")
        rows = conn.execute(
            "SELECT * FROM saving_goal_logs WHERE goal_id = ? AND user_id = ? ORDER BY id DESC LIMIT ?",
            (goal_id, user["user_id"], limit)
        ).fetchall()
        return [dict(r) for r in rows]
