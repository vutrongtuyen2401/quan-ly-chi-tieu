"""Ví (Túi Càn Khôn) và chuyển tiền giữa các ví."""

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import get_db
from backend.schemas import TransferBody, WalletBody, WalletUpdateBody
from backend.security import get_current_user
from backend.services import get_owned_wallet
from backend.utils import vnd

router = APIRouter()


# ──────────────────────────────────────────────
# WALLETS ROUTES
# ──────────────────────────────────────────────
@router.get("/api/wallets")
def get_wallets(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM wallets WHERE user_id = ? ORDER BY id", (user["user_id"],)).fetchall()
        return [dict(r) for r in rows]


@router.post("/api/wallets")
def create_wallet(body: WalletBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
            (user["user_id"], body.wallet_name, body.balance, body.wallet_type)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Túi Càn Khôn đã được khai mở!"}


# Change 3: Sửa ví
@router.put("/api/wallets/{wallet_id}")
def update_wallet(wallet_id: int, body: WalletUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        wallet = get_owned_wallet(conn, wallet_id, user["user_id"])
        new_name = body.wallet_name if body.wallet_name is not None else wallet["wallet_name"]
        new_type = body.wallet_type if body.wallet_type is not None else wallet["wallet_type"]
        conn.execute("UPDATE wallets SET wallet_name = ?, wallet_type = ? WHERE id = ? AND user_id = ?",
                     (new_name, new_type, wallet_id, user["user_id"]))
        return {"message": "Túi Càn Khôn đã được cập nhật!", "wallet_name": new_name, "wallet_type": new_type}


@router.delete("/api/wallets/{wallet_id}")
def delete_wallet(wallet_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        wallet = get_owned_wallet(conn, wallet_id, user["user_id"])
        txn_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE wallet_id = ? AND user_id = ?",
                                 (wallet_id, user["user_id"])).fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM recurring_transactions WHERE wallet_id = ? AND user_id = ?",
                                 (wallet_id, user["user_id"])).fetchone()[0]
        if txn_count or rec_count:
            parts = []
            if txn_count:
                parts.append(f"{txn_count} giao dịch")
            if rec_count:
                parts.append(f"{rec_count} giao dịch định kỳ")
            raise HTTPException(
                status_code=400,
                detail=f"Không thể hủy túi '{wallet['wallet_name']}' vì đang gắn với {' và '.join(parts)}. "
                       f"Hãy chuyển sang ví khác hoặc xóa chúng trước."
            )
        # Khoản nợ chỉ tham chiếu ví để ghi chú → gỡ liên kết thay vì chặn xóa
        conn.execute("UPDATE debts SET wallet_id = NULL WHERE wallet_id = ? AND user_id = ?", (wallet_id, user["user_id"]))
        conn.execute("DELETE FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user["user_id"]))
        return {"message": "Túi Càn Khôn đã bị hủy!"}


# ──────────────────────────────────────────────
# WALLET TRANSFER
# ──────────────────────────────────────────────
@router.get("/api/wallets/transfers")
def get_wallet_transfers(limit: int = Query(20, ge=1, le=100), user: dict = Depends(get_current_user)):
    """Lịch sử chuyển Linh Thạch giữa các ví (mới nhất trước)"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM wallet_transfers WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user["user_id"], limit)
        ).fetchall()
        return [dict(r) for r in rows]


@router.post("/api/wallets/transfer")
def transfer_between_wallets(body: TransferBody, user: dict = Depends(get_current_user)):
    """Chuyển Linh Thạch giữa các Túi Càn Khôn"""
    if body.from_wallet_id == body.to_wallet_id:
        raise HTTPException(status_code=400, detail="Không thể chuyển cho chính mình!")

    with get_db() as conn:
        from_wallet = conn.execute(
            "SELECT * FROM wallets WHERE id = ? AND user_id = ?",
            (body.from_wallet_id, user["user_id"])
        ).fetchone()
        to_wallet = conn.execute(
            "SELECT * FROM wallets WHERE id = ? AND user_id = ?",
            (body.to_wallet_id, user["user_id"])
        ).fetchone()

        if not from_wallet or not to_wallet:
            raise HTTPException(status_code=404, detail="Túi Càn Khôn không tồn tại.")
        if from_wallet["balance"] < body.amount:
            raise HTTPException(status_code=400, detail="Linh Thạch không đủ để chuyển!")

        conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?",
                     (body.amount, body.from_wallet_id, user["user_id"]))
        conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?",
                     (body.amount, body.to_wallet_id, user["user_id"]))
        conn.execute(
            """INSERT INTO wallet_transfers (user_id, from_wallet_id, to_wallet_id, from_wallet_name, to_wallet_name, amount, note)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user["user_id"], body.from_wallet_id, body.to_wallet_id,
             from_wallet["wallet_name"], to_wallet["wallet_name"], body.amount, body.note or "")
        )

        return {
            "message": f"Đã chuyển {vnd(body.amount)} Linh Thạch từ '{from_wallet['wallet_name']}' sang '{to_wallet['wallet_name']}'!",
            "from_wallet": from_wallet["wallet_name"],
            "to_wallet": to_wallet["wallet_name"],
            "amount": body.amount,
        }
