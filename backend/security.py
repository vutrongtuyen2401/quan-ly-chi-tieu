"""JWT, phân quyền, kiểm tra mật khẩu và giới hạn số lần thử sai."""

import datetime
import hashlib
import secrets
import time

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import JWT_ALGORITHM, JWT_EXPIRATION_HOURS, JWT_SECRET, LOGIN_LOCKOUT_SECONDS, RECOVERY_MAX_ATTEMPTS
from backend.db import get_db

security = HTTPBearer()

# Rate limiting đăng nhập — {email: {"count": int, "first_attempt": float}}
login_attempts = {}
# Khôi phục mật khẩu — {(bucket, email): {"count": int, "first_attempt": float}}
recovery_attempts = {}


# ──────────────────────────────────────────────
# AUTH HELPERS
# ──────────────────────────────────────────────
def create_token(user_id: int, email: str, role: str = "user") -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": (role or "user").lower(),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        token_user_id = int(payload["user_id"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn. Hãy đăng nhập lại.")
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")

    # Đọc lại trạng thái & vai trò từ DB: khóa tài khoản / đổi quyền có hiệu lực ngay, không chờ token hết hạn
    with get_db() as conn:
        row = conn.execute("SELECT id, email, role, is_active FROM users WHERE id = ?", (token_user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Tài khoản không còn tồn tại. Hãy đăng nhập lại.")
    if row["is_active"] == 0:
        raise HTTPException(status_code=401, detail="Tài khoản này đã bị phong ấn (khóa). Vui lòng liên hệ Chưởng Môn (Admin).")
    return {
        "user_id": row["id"],
        "email": row["email"],
        "role": str(row["role"] or "user").lower(),
    }


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if str(user.get("role", "")).lower() != "admin":
        raise HTTPException(status_code=403, detail="Quyền hạn không đủ! Chỉ Chưởng Môn (Admin) mới có quyền truy cập.")
    return user


def verify_password(plain: str, stored_hash: str) -> bool:
    """So khớp mật khẩu với hash bcrypt (hỗ trợ hash sha256/plaintext cũ để tự nâng cấp)."""
    if not stored_hash:
        return False
    try:
        if stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
            return bcrypt.checkpw(plain.encode("utf-8"), stored_hash.encode("utf-8"))
        stored = stored_hash.encode("utf-8")
        sha256_hash = hashlib.sha256(plain.encode("utf-8")).hexdigest().encode("utf-8")
        return secrets.compare_digest(stored, sha256_hash) or secrets.compare_digest(stored, plain.encode("utf-8"))
    except Exception:
        return False


def _recovery_blocked(bucket: str, email: str) -> bool:
    key = (bucket, email)
    attempt = recovery_attempts.get(key)
    if not attempt:
        return False
    if time.time() - attempt["first_attempt"] > LOGIN_LOCKOUT_SECONDS:
        del recovery_attempts[key]
        return False
    return attempt["count"] >= RECOVERY_MAX_ATTEMPTS


def _recovery_fail(bucket: str, email: str):
    key = (bucket, email)
    now_ts = time.time()
    if len(recovery_attempts) > 1000:
        for k in [k for k, v in recovery_attempts.items() if now_ts - v["first_attempt"] > LOGIN_LOCKOUT_SECONDS]:
            recovery_attempts.pop(k, None)
    attempt = recovery_attempts.setdefault(key, {"count": 0, "first_attempt": now_ts})
    attempt["count"] += 1


def _recovery_clear(bucket: str, email: str):
    recovery_attempts.pop((bucket, email), None)


TOO_MANY_RECOVERY = "Thao tác sai quá nhiều lần. Vui lòng thử lại sau 15 phút."
