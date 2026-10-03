"""Hồ sơ người dùng."""

import bcrypt
from fastapi import APIRouter, Depends, HTTPException

from backend.db import get_db
from backend.schemas import ProfileUpdateBody, SoulLampUpdateBody
from backend.security import get_current_user, verify_password

router = APIRouter()


# ──────────────────────────────────────────────
# USER PROFILE ROUTES
# ──────────────────────────────────────────────
@router.get("/api/user/profile")
def get_user_profile(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        u = conn.execute("SELECT id, email, full_name, role, is_active, created_at FROM users WHERE id = ?", (user["user_id"],)).fetchone()
        if not u:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đạo hữu.")
        return dict(u)


@router.put("/api/user/profile")
def update_user_profile(body: ProfileUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (body.full_name, user["user_id"]))
        return {"message": "Cập nhật đạo hiệu thành công!", "full_name": body.full_name}


@router.put("/api/user/soul-lamp")
def update_soul_lamp(body: SoulLampUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        u = conn.execute("SELECT id, password_hash FROM users WHERE id = ?", (user["user_id"],)).fetchone()
        if not u:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

        if not verify_password(body.current_password, u["password_hash"]):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác.")

        new_hash = bcrypt.hashpw(body.new_soul_lamp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn.execute("UPDATE users SET soul_lamp_hash = ? WHERE id = ?", (new_hash, user["user_id"]))

        return {"message": "Đã cập nhật Bản Mệnh Hồn Đăng thành công!"}
