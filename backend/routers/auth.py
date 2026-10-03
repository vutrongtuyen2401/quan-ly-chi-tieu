"""Đăng ký, đăng nhập, quên / đặt lại mật khẩu."""

import datetime
import secrets
import time

import bcrypt
from fastapi import APIRouter, HTTPException

from backend import mailer
from backend.config import LOGIN_LOCKOUT_SECONDS, LOGIN_MAX_ATTEMPTS, RESET_TOKEN_EXPIRE_MINUTES
from backend.db import get_db
from backend.schemas import ForgotPasswordBody, LoginBody, RegisterBody, ResetPasswordBody
from backend.security import (TOO_MANY_RECOVERY, _recovery_blocked, _recovery_clear, _recovery_fail, create_token,
                              login_attempts, verify_password)

router = APIRouter()


# ──────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────
@router.post("/api/auth/register")
@router.post("/api/register")
@router.post("/register")
def register(body: RegisterBody):
    full_name = body.full_name or "Ký Chủ"
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE lower(email) = ?", (body.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email đã tồn tại trong Tông Môn.")
        pw_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
        soul_lamp_hash = bcrypt.hashpw(body.soul_lamp.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (email, password_hash, full_name, soul_lamp_hash, role, is_active) VALUES (?, ?, ?, ?, 'user', 1)",
            (body.email, pw_hash, full_name, soul_lamp_hash)
        )
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Khởi tạo Ví và Danh mục mặc định cho user mới
        wallets_data = [
            (user_id, "Linh Thạch Tiền Mặt", 5000000, "cash"),
            (user_id, "Linh Mạch Vietcombank", 15000000, "bank"),
            (user_id, "Túi Momo", 2000000, "e-wallet"),
        ]
        conn.executemany(
            "INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
            wallets_data
        )

        categories_data = [
            (user_id, "Ẩm Thực Linh Đan", "EXPENSE", "🍕"),
            (user_id, "Pháp Khí Mua Sắm", "EXPENSE", "🛍️"),
            (user_id, "Phi Kiếm Di Chuyển", "EXPENSE", "🚗"),
            (user_id, "Linh Thạch Lương Bổng", "INCOME", "💵"),
            (user_id, "Quà Tặng Đạo Hữu", "INCOME", "🎁"),
        ]
        conn.executemany(
            "INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
            categories_data
        )

        token = create_token(user_id, body.email, role="user")
        return {"token": token, "user_id": user_id, "full_name": full_name, "email": body.email, "role": "user"}


@router.post("/api/auth/login")
@router.post("/api/login")
@router.post("/login")
def login(body: LoginBody):
    # Change 6: Rate limiting — kiểm tra số lần đăng nhập sai
    email_lower = body.email.lower().strip()
    now_ts = time.time()

    # Dọn các bản ghi đã hết hạn để bộ đếm không phình to theo thời gian
    if len(login_attempts) > 1000:
        for key in [k for k, v in login_attempts.items() if now_ts - v["first_attempt"] > LOGIN_LOCKOUT_SECONDS]:
            login_attempts.pop(key, None)

    if email_lower in login_attempts:
        attempt = login_attempts[email_lower]
        elapsed = now_ts - attempt["first_attempt"]
        if elapsed > LOGIN_LOCKOUT_SECONDS:
            del login_attempts[email_lower]
        elif attempt["count"] >= LOGIN_MAX_ATTEMPTS:
            remaining = int(LOGIN_LOCKOUT_SECONDS - elapsed)
            raise HTTPException(
                status_code=429,
                detail=f"Tài khoản tạm khóa do đăng nhập sai quá nhiều lần. Vui lòng thử lại sau {max(remaining // 60, 1)} phút."
            )

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email_lower,)).fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")
        if user["is_active"] == 0:
            raise HTTPException(status_code=403, detail="Tài khoản này đã bị phong ấn (khóa). Vui lòng liên hệ Chưởng Môn (Admin).")

        stored_hash = user["password_hash"] or ""
        is_pw_valid = verify_password(body.password, stored_hash)
        if is_pw_valid and not stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
            # Tự nâng cấp hash cũ (sha256 / plaintext) lên bcrypt
            new_pw_hash = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_pw_hash, user["id"]))

        if not is_pw_valid:
            if email_lower not in login_attempts:
                login_attempts[email_lower] = {"count": 1, "first_attempt": now_ts}
            else:
                login_attempts[email_lower]["count"] += 1
            remaining_attempts = LOGIN_MAX_ATTEMPTS - login_attempts[email_lower]["count"]
            if remaining_attempts <= 0:
                raise HTTPException(
                    status_code=429,
                    detail="Tài khoản tạm khóa do đăng nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút."
                )
            raise HTTPException(status_code=401, detail=f"Mật khẩu sai. Đạo Tâm bị phong ấn. (Còn {remaining_attempts} lần thử)")

        # Đăng nhập thành công → reset bộ đếm
        login_attempts.pop(email_lower, None)

        user_role = user["role"] or "user"
        token = create_token(user["id"], user["email"], role=user_role)
        return {
            "token": token,
            "user_id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user_role
        }


# ──────────────────────────────────────────────
# Change 5: FORGOT / RESET PASSWORD
# ──────────────────────────────────────────────
RESET_TOKEN_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # bỏ ký tự dễ nhầm O/0, I/1
RESET_TOKEN_LENGTH = 8
INVALID_RECOVERY_MSG = "Thông tin xác thực không chính xác, vui lòng kiểm tra lại"


@router.post("/api/auth/forgot-password")
def forgot_password(body: ForgotPasswordBody):
    """Tạo mã reset mật khẩu — Yêu cầu xác thực Email + Bản Mệnh Hồn Đăng"""
    email = body.email.lower()
    if not email or not body.soul_lamp:
        raise HTTPException(status_code=400, detail=INVALID_RECOVERY_MSG)
    if _recovery_blocked("forgot", email):
        raise HTTPException(status_code=429, detail=TOO_MANY_RECOVERY)

    use_email = mailer.smtp_configured()
    if mailer.IS_PRODUCTION and not use_email:
        print("  ❌ forgot-password: APP_ENV=production nhưng chưa cấu hình SMTP_HOST/SMTP_FROM")
        raise HTTPException(status_code=503, detail="Chức năng khôi phục mật khẩu tạm thời không khả dụng. Vui lòng liên hệ quản trị viên.")

    with get_db() as conn:
        user = conn.execute("SELECT id, email, soul_lamp_hash FROM users WHERE lower(email) = ?", (email,)).fetchone()

        is_valid = False
        if user and user["soul_lamp_hash"]:
            try:
                is_valid = bcrypt.checkpw(body.soul_lamp.strip().encode("utf-8"), user["soul_lamp_hash"].encode("utf-8"))
            except Exception:
                is_valid = False

        if not is_valid:
            # QUAN TRỌNG VỀ BẢO MẬT: Trả về CÙNG MỘT thông báo lỗi chung cho cả 3 trường hợp:
            # 1. Email không tồn tại
            # 2. Bản Mệnh Hồn Đăng sai
            # 3. User chưa từng đặt Bản Mệnh Hồn Đăng (soul_lamp_hash là NULL)
            _recovery_fail("forgot", email)
            raise HTTPException(status_code=400, detail=INVALID_RECOVERY_MSG)

        _recovery_clear("forgot", email)

        # Tạo mã reset 8 ký tự, hạn 30 phút; vô hiệu hóa các mã cũ chưa dùng
        reset_token = "".join(secrets.choice(RESET_TOKEN_ALPHABET) for _ in range(RESET_TOKEN_LENGTH))
        expires_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)).isoformat()

        conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE lower(email) = ? AND used = 0", (email,))
        cur = conn.execute(
            "INSERT INTO password_reset_tokens (email, token, expires_at) VALUES (?, ?, ?)",
            (email, reset_token, expires_at)
        )
        token_id = cur.lastrowid
        recipient = user["email"]

    if use_email:
        try:
            mailer.send_reset_email(recipient, reset_token)
        except Exception as e:
            print(f"  ❌ forgot-password: gửi email thất bại: {type(e).__name__}: {e}")
            # Vô hiệu hóa mã vừa tạo vì người dùng không nhận được
            with get_db() as conn:
                conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE id = ?", (token_id,))
            raise HTTPException(status_code=503, detail="Không gửi được email khôi phục. Vui lòng thử lại sau.")
        return {
            "message": "Mã xác thực đã được gửi tới email của bạn.",
            "email_sent": True,
            "expires_in_minutes": RESET_TOKEN_EXPIRE_MINUTES,
        }

    # Chế độ phát triển (APP_ENV != production và chưa cấu hình SMTP): trả mã trực tiếp
    return {
        "message": "Mã reset đã được tạo. (Chế độ phát triển: mã hiển thị trực tiếp)",
        "email_sent": False,
        "reset_token": reset_token,
        "expires_in_minutes": RESET_TOKEN_EXPIRE_MINUTES,
        "note": "⚠️ DEV MODE: Cấu hình SMTP_* trong .env để gửi mã qua email; đặt APP_ENV=production để tắt chế độ này."
    }


@router.post("/api/auth/reset-password")
def reset_password(body: ResetPasswordBody):
    """Đặt lại mật khẩu bằng mã reset"""
    email = body.email.lower()
    if _recovery_blocked("reset", email):
        raise HTTPException(status_code=429, detail=TOO_MANY_RECOVERY)

    with get_db() as conn:
        token_row = conn.execute(
            "SELECT * FROM password_reset_tokens WHERE lower(email) = ? AND token = ? AND used = 0 ORDER BY id DESC LIMIT 1",
            (email, body.token.upper())
        ).fetchone()

        if not token_row:
            _recovery_fail("reset", email)
            raise HTTPException(status_code=400, detail="Mã reset không hợp lệ hoặc đã được sử dụng.")

        # Kiểm tra hết hạn
        expires_at = datetime.datetime.fromisoformat(token_row["expires_at"])
        if datetime.datetime.now(datetime.timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="Mã reset đã hết hạn. Vui lòng yêu cầu mã mới.")

        # Cập nhật mật khẩu mới
        pw_hash = bcrypt.hashpw(body.new_password.encode(), bcrypt.gensalt()).decode()
        conn.execute("UPDATE users SET password_hash = ? WHERE lower(email) = ?", (pw_hash, email))

        # Đánh dấu token đã sử dụng
        conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE id = ?", (token_row["id"],))

    _recovery_clear("reset", email)
    login_attempts.pop(email, None)
    return {"message": "Mật khẩu đã được đặt lại thành công! Hãy đăng nhập bằng mật khẩu mới."}
