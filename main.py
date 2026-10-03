"""
╔══════════════════════════════════════════════════════════════════╗
║   CÀN KHÔN LINH THẠCH CÁC — HỆ THỐNG QUẢN LÝ CHI TIÊU AI    ║
║   Backend FastAPI + SQLite + Google Gemini AI                    ║
║   Phong cách Tu Tiên (Xianxia Theme)                            ║
╚══════════════════════════════════════════════════════════════════╝

Điểm khởi chạy: tạo app FastAPI và gắn các router trong package backend/.
  backend/config.py    — cấu hình từ .env
  backend/db.py        — kết nối SQLite, tạo bảng, migration, seed
  backend/schemas.py   — Pydantic schemas + kiểm tra dữ liệu đầu vào
  backend/security.py  — JWT, phân quyền, mật khẩu, giới hạn thử sai
  backend/services.py  — nghiệp vụ dùng chung (quyền sở hữu, số dư, định kỳ)
  backend/mailer.py    — gửi mã reset qua SMTP
  backend/gemini.py    — gọi Google Gemini
  backend/routers/     — các nhóm API
"""

import datetime
import os
import sys
from contextlib import asynccontextmanager

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import ALLOWED_ORIGINS
from backend.db import get_db, init_db
from backend.errors import register_error_handlers
from backend.routers import (admin, ai, auth, budgets, categories, debts, goals, recurring, reports, transactions,
                             users, wallets)
from backend.security import create_token

# Re-export cho test_suite.py (main.get_db, main.create_token, main.datetime...)
__all__ = ["app", "get_db", "init_db", "create_token", "datetime"]


@asynccontextmanager
async def lifespan(_app):
    init_db()
    print("=" * 62)
    print("  CAN KHON LINH THACH CAC -- Khai Mo Thanh Cong!")
    print("  Server: http://localhost:8000")
    print("  Docs:   http://localhost:8000/docs")
    print("=" * 62)
    yield


app = FastAPI(title="Càn Khôn Linh Thạch Các API", version="2.3", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)

for module in (auth, wallets, categories, transactions, budgets, reports, recurring, debts, goals, ai, users, admin):
    app.include_router(module.router)


if __name__ == "__main__":
    import uvicorn
    # Mặc định chỉ lắng nghe trên máy cục bộ; đặt HOST=0.0.0.0 nếu muốn mở cho máy khác trong mạng LAN
    uvicorn.run("main:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")),
                reload=True)
