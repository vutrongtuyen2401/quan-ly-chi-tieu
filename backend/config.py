"""Cấu hình đọc từ biến môi trường (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv("DATABASE_PATH", "app.db")

# JWT_SECRET bắt buộc — dừng server nếu thiếu
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError(
        "\n" + "=" * 62 + "\n"
        "  ❌ LỖI NGHIÊM TRỌNG: Biến môi trường JWT_SECRET chưa được đặt!\n"
        "  Hãy thêm JWT_SECRET vào file .env trước khi khởi động server.\n"
        "  Ví dụ: JWT_SECRET=my_super_secret_key_here\n"
        + "=" * 62
    )

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gửi mã reset mật khẩu qua email (SMTP)
# APP_ENV=production: bắt buộc cấu hình SMTP, KHÔNG BAO GIỜ trả mã reset trong response.
# APP_ENV=development (mặc định): nếu chưa cấu hình SMTP thì trả mã trực tiếp để test.
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or 587)
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "").strip() or SMTP_USER
# SMTP_SECURITY: starttls (cổng 587, mặc định) | ssl (cổng 465) | none
SMTP_SECURITY = os.getenv("SMTP_SECURITY", "starttls").strip().lower()
RESET_TOKEN_EXPIRE_MINUTES = 30

# CORS an toàn — đọc danh sách origins từ biến môi trường
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

# Rate limiting đăng nhập / khôi phục mật khẩu
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60  # 15 phút
RECOVERY_MAX_ATTEMPTS = 5

OCR_MAX_BYTES = 8 * 1024 * 1024  # 8 MB
