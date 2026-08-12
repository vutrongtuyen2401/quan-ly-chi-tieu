"""
╔══════════════════════════════════════════════════════════════════╗
║   CÀN KHÔN LINH THẠCH CÁC — HỆ THỐNG QUẢN LÝ CHI TIÊU AI    ║
║   Backend FastAPI + SQLite + Google Gemini AI                    ║
║   Phong cách Tu Tiên (Xianxia Theme)                            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sqlite3
import json
import base64
import datetime
import hashlib
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from dotenv import load_dotenv

import jwt
import bcrypt

load_dotenv()

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
DATABASE = "app.db"
JWT_SECRET = os.getenv("JWT_SECRET", "xianxia_cankhon_default_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

app = FastAPI(title="Càn Khôn Linh Thạch Các API", version="2.1")
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# DATABASE HELPERS
# ──────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Tạo 7 bảng cốt lõi + seed dữ liệu mẫu"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_name TEXT NOT NULL,
                balance REAL DEFAULT 0,
                wallet_type TEXT DEFAULT 'cash',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_name TEXT NOT NULL,
                category_type TEXT CHECK(category_type IN ('INCOME','EXPENSE')) NOT NULL,
                icon TEXT DEFAULT '📦',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('INCOME','EXPENSE')) NOT NULL,
                transaction_date TEXT NOT NULL,
                note TEXT DEFAULT '',
                image_url TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (wallet_id) REFERENCES wallets(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                limit_amount REAL NOT NULL,
                month_year TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS invoice_ocr_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image_path TEXT DEFAULT '',
                extracted_json TEXT DEFAULT '{}',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                prompt_question TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        # Seed dữ liệu mẫu nếu chưa có user
        user_check = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if not user_check:
            # Admin user: admin@gmail.com / 123456
            pw_hash = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
            conn.execute(
                "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
                ("admin@gmail.com", pw_hash, "Đạo Hữu Admin")
            )
            uid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            # 3 Ví Linh Thạch
            wallets_data = [
                (uid, "Linh Thạch Tiền Mặt", 5000000, "cash"),
                (uid, "Linh Mạch Vietcombank", 15000000, "bank"),
                (uid, "Túi Momo", 2000000, "e-wallet"),
            ]
            conn.executemany(
                "INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                wallets_data
            )

            # 5 Danh Mục
            categories_data = [
                (uid, "Ẩm Thực Linh Đan", "EXPENSE", "🍕"),
                (uid, "Pháp Khí Mua Sắm", "EXPENSE", "🛍️"),
                (uid, "Phi Kiếm Di Chuyển", "EXPENSE", "🚗"),
                (uid, "Linh Thạch Lương Bổng", "INCOME", "💵"),
                (uid, "Quà Tặng Đạo Hữu", "INCOME", "🎁"),
            ]
            conn.executemany(
                "INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
                categories_data
            )

            # Giao dịch mẫu
            today = datetime.date.today()
            transactions_data = [
                (uid, 1, 1, 150000, "EXPENSE", str(today - datetime.timedelta(days=1)), "Mua linh đan phở bò"),
                (uid, 1, 2, 500000, "EXPENSE", str(today - datetime.timedelta(days=2)), "Mua pháp khí áo mới"),
                (uid, 2, 3, 200000, "EXPENSE", str(today - datetime.timedelta(days=3)), "Phi kiếm Grab đi làm"),
                (uid, 2, 4, 20000000, "INCOME", str(today - datetime.timedelta(days=5)), "Lương tháng 8 từ Tông Môn"),
                (uid, 3, 5, 1000000, "INCOME", str(today - datetime.timedelta(days=7)), "Quà tặng từ Sư Huynh"),
                (uid, 1, 1, 85000, "EXPENSE", str(today), "Mua cơm trưa Linh Đan quán"),
                (uid, 2, 2, 1200000, "EXPENSE", str(today - datetime.timedelta(days=4)), "Pháp bảo tai nghe mới"),
            ]
            conn.executemany(
                "INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                transactions_data
            )

            # Budget mẫu
            month_year = today.strftime("%Y-%m")
            budgets_data = [
                (uid, 1, 3000000, month_year),
                (uid, 2, 2000000, month_year),
                (uid, 3, 1000000, month_year),
            ]
            conn.executemany(
                "INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                budgets_data
            )

        conn.commit()


# ──────────────────────────────────────────────
# PYDANTIC MODELS
# ──────────────────────────────────────────────
class RegisterBody(BaseModel):
    email: str
    password: str
    full_name: str

class LoginBody(BaseModel):
    email: str
    password: str

class WalletBody(BaseModel):
    wallet_name: str
    balance: float = 0
    wallet_type: str = "cash"

class CategoryBody(BaseModel):
    category_name: str
    category_type: str  # INCOME or EXPENSE
    icon: str = "📦"

class TransactionBody(BaseModel):
    wallet_id: int
    category_id: int
    amount: float
    transaction_type: str  # INCOME or EXPENSE
    transaction_date: str
    note: str = ""

class TransactionUpdateBody(BaseModel):
    wallet_id: Optional[int] = None
    category_id: Optional[int] = None
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[str] = None
    note: Optional[str] = None

class BudgetBody(BaseModel):
    category_id: int
    limit_amount: float
    month_year: str

class ChatBody(BaseModel):
    message: str


# ──────────────────────────────────────────────
# AUTH HELPERS
# ──────────────────────────────────────────────
def create_token(user_id: int, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"user_id": payload["user_id"], "email": payload["email"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn. Hãy đăng nhập lại.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")


# ──────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────
@app.post("/api/auth/register")
def register(body: RegisterBody):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (body.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email đã tồn tại trong Tông Môn.")
        pw_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
            (body.email, pw_hash, body.full_name)
        )
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        token = create_token(user_id, body.email)
        return {"token": token, "user_id": user_id, "full_name": body.full_name, "email": body.email}


@app.post("/api/auth/login")
def login(body: LoginBody):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (body.email,)).fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Đạo Tâm không tồn tại.")
        if not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
            raise HTTPException(status_code=401, detail="Mật khẩu sai. Đạo Tâm bị phong ấn.")
        token = create_token(user["id"], user["email"])
        return {"token": token, "user_id": user["id"], "full_name": user["full_name"], "email": user["email"]}


# ──────────────────────────────────────────────
# WALLETS ROUTES
# ──────────────────────────────────────────────
@app.get("/api/wallets")
def get_wallets(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM wallets WHERE user_id = ? ORDER BY id", (user["user_id"],)).fetchall()
        return [dict(r) for r in rows]


@app.post("/api/wallets")
def create_wallet(body: WalletBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
            (user["user_id"], body.wallet_name, body.balance, body.wallet_type)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Túi Càn Khôn đã được khai mở!"}


@app.delete("/api/wallets/{wallet_id}")
def delete_wallet(wallet_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user["user_id"]))
        return {"message": "Túi Càn Khôn đã bị hủy!"}


# ──────────────────────────────────────────────
# CATEGORIES ROUTES
# ──────────────────────────────────────────────
@app.get("/api/categories")
def get_categories(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY id", (user["user_id"],)).fetchall()
        return [dict(r) for r in rows]


@app.post("/api/categories")
def create_category(body: CategoryBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
            (user["user_id"], body.category_name, body.category_type, body.icon)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Danh mục mới đã khai mở!"}


@app.delete("/api/categories/{cat_id}")
def delete_category(cat_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", (cat_id, user["user_id"]))
        return {"message": "Danh mục đã bị hủy!"}


# ──────────────────────────────────────────────
# TRANSACTIONS ROUTES
# ──────────────────────────────────────────────
@app.get("/api/transactions")
def get_transactions(
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT t.*, w.wallet_name, c.category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN wallets w ON t.wallet_id = w.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.transaction_date DESC, t.id DESC
            LIMIT ?
        """, (user["user_id"], limit)).fetchall()
        return [dict(r) for r in rows]


@app.post("/api/transactions")
def create_transaction(body: TransactionBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO transactions
               (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user["user_id"], body.wallet_id, body.category_id, body.amount,
             body.transaction_type, body.transaction_date, body.note)
        )
        # Cập nhật số dư ví
        if body.transaction_type == "INCOME":
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?",
                         (body.amount, body.wallet_id, user["user_id"]))
        else:
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?",
                         (body.amount, body.wallet_id, user["user_id"]))
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Giao dịch Linh Thạch đã ghi nhận!"}


@app.put("/api/transactions/{txn_id}")
def update_transaction(txn_id: int, body: TransactionUpdateBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        old_txn = conn.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                               (txn_id, user["user_id"])).fetchone()
        if not old_txn:
            raise HTTPException(status_code=404, detail="Giao dịch không tồn tại.")

        # Rollback old balance
        if old_txn["transaction_type"] == "INCOME":
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ?",
                         (old_txn["amount"], old_txn["wallet_id"]))
        else:
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ?",
                         (old_txn["amount"], old_txn["wallet_id"]))

        # Apply update
        new_wallet = body.wallet_id or old_txn["wallet_id"]
        new_cat = body.category_id or old_txn["category_id"]
        new_amount = body.amount if body.amount is not None else old_txn["amount"]
        new_type = body.transaction_type or old_txn["transaction_type"]
        new_date = body.transaction_date or old_txn["transaction_date"]
        new_note = body.note if body.note is not None else old_txn["note"]

        conn.execute("""
            UPDATE transactions SET wallet_id=?, category_id=?, amount=?,
            transaction_type=?, transaction_date=?, note=? WHERE id=? AND user_id=?
        """, (new_wallet, new_cat, new_amount, new_type, new_date, new_note, txn_id, user["user_id"]))

        # Apply new balance
        if new_type == "INCOME":
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ?", (new_amount, new_wallet))
        else:
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ?", (new_amount, new_wallet))

        return {"message": "Giao dịch đã cập nhật!"}


@app.delete("/api/transactions/{txn_id}")
def delete_transaction(txn_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        txn = conn.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                           (txn_id, user["user_id"])).fetchone()
        if not txn:
            raise HTTPException(status_code=404, detail="Giao dịch không tồn tại.")
        # Rollback balance
        if txn["transaction_type"] == "INCOME":
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ?", (txn["amount"], txn["wallet_id"]))
        else:
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ?", (txn["amount"], txn["wallet_id"]))
        conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        return {"message": "Giao dịch đã xóa!"}


# ──────────────────────────────────────────────
# BUDGETS ROUTES
# ──────────────────────────────────────────────
@app.get("/api/budgets")
def get_budgets(month_year: str = Query(None), user: dict = Depends(get_current_user)):
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


@app.post("/api/budgets")
def create_budget(body: BudgetBody, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category_id = ? AND month_year = ?",
            (user["user_id"], body.category_id, body.month_year)
        ).fetchone()
        if existing:
            conn.execute("UPDATE budgets SET limit_amount = ? WHERE id = ?",
                         (body.limit_amount, existing["id"]))
            return {"id": existing["id"], "message": "Hạn mức đã cập nhật!"}
        conn.execute(
            "INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
            (user["user_id"], body.category_id, body.limit_amount, body.month_year)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": new_id, "message": "Hạn mức tu luyện đã thiết lập!"}


@app.delete("/api/budgets/{budget_id}")
def delete_budget(budget_id: int, user: dict = Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, user["user_id"]))
        return {"message": "Hạn mức đã xóa!"}


# ──────────────────────────────────────────────
# REPORTS ROUTES
# ──────────────────────────────────────────────
@app.get("/api/reports/summary")
def get_reports_summary(month_year: str = Query(None), user: dict = Depends(get_current_user)):
    if not month_year:
        month_year = datetime.date.today().strftime("%Y-%m")
    with get_db() as conn:
        income = conn.execute("""
            SELECT COALESCE(SUM(amount), 0) as total FROM transactions
            WHERE user_id = ? AND transaction_type = 'INCOME'
            AND strftime('%Y-%m', transaction_date) = ?
        """, (user["user_id"], month_year)).fetchone()["total"]

        expense = conn.execute("""
            SELECT COALESCE(SUM(amount), 0) as total FROM transactions
            WHERE user_id = ? AND transaction_type = 'EXPENSE'
            AND strftime('%Y-%m', transaction_date) = ?
        """, (user["user_id"], month_year)).fetchone()["total"]

        total_balance = conn.execute("""
            SELECT COALESCE(SUM(balance), 0) as total FROM wallets WHERE user_id = ?
        """, (user["user_id"],)).fetchone()["total"]

        # Chi tiêu theo danh mục
        by_category = conn.execute("""
            SELECT c.category_name, c.icon, SUM(t.amount) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.transaction_type = 'EXPENSE'
            AND strftime('%Y-%m', t.transaction_date) = ?
            GROUP BY t.category_id
            ORDER BY total DESC
        """, (user["user_id"], month_year)).fetchall()

        return {
            "month_year": month_year,
            "total_income": income,
            "total_expense": expense,
            "net_savings": income - expense,
            "total_balance": total_balance,
            "expense_by_category": [dict(r) for r in by_category],
        }


# ──────────────────────────────────────────────
# AI ROUTES (Google Gemini)
# ──────────────────────────────────────────────
def get_gemini_model(vision=False):
    """Initialize Gemini model"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY chưa được cấu hình. Hãy thêm vào file .env")
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model_name = "gemini-1.5-flash" if vision else "gemini-1.5-flash"
        return genai.GenerativeModel(model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khởi tạo Gemini: {str(e)}")


@app.post("/api/ai/scan-invoice")
async def scan_invoice(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Linh Nhãn AI OCR — quét hóa đơn từ ảnh"""
    model = get_gemini_model(vision=True)
    contents = await file.read()
    b64_data = base64.b64encode(contents).decode()

    prompt = """Bạn là trợ lý AI tài chính. Hãy phân tích hóa đơn/receipt trong ảnh này.
    Trả về JSON với format:
    {
        "store_name": "Tên cửa hàng",
        "total_amount": 0,
        "items": [{"name": "Tên sản phẩm", "price": 0, "quantity": 1}],
        "date": "YYYY-MM-DD",
        "currency": "VND"
    }
    Chỉ trả về JSON, không giải thích thêm."""

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": file.content_type or "image/jpeg", "data": b64_data}
        ])
        response_text = response.text.strip()
        # Try to parse JSON from response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        extracted = json.loads(response_text)

        # Log OCR result
        with get_db() as conn:
            conn.execute(
                "INSERT INTO invoice_ocr_logs (user_id, image_path, extracted_json) VALUES (?, ?, ?)",
                (user["user_id"], file.filename, json.dumps(extracted, ensure_ascii=False))
            )

        return {"success": True, "data": extracted}
    except json.JSONDecodeError:
        return {"success": True, "data": {"raw_text": response.text, "store_name": "", "total_amount": 0, "items": []}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi OCR: {str(e)}")


@app.post("/api/ai/check-budget")
def check_budget(user: dict = Depends(get_current_user)):
    """Cảnh Báo Tẩu Hỏa Nhập Ma — kiểm tra ngân sách"""
    month_year = datetime.date.today().strftime("%Y-%m")
    with get_db() as conn:
        budgets = conn.execute("""
            SELECT b.*, c.category_name, c.icon,
                   COALESCE((SELECT SUM(t.amount) FROM transactions t
                             WHERE t.category_id = b.category_id
                             AND t.user_id = b.user_id
                             AND t.transaction_type = 'EXPENSE'
                             AND strftime('%Y-%m', t.transaction_date) = b.month_year), 0) as spent
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ? AND b.month_year = ?
        """, (user["user_id"], month_year)).fetchall()

        alerts = []
        for b in budgets:
            b = dict(b)
            pct = (b["spent"] / b["limit_amount"] * 100) if b["limit_amount"] > 0 else 0
            if pct >= 100:
                alerts.append({
                    "category": b["category_name"],
                    "icon": b["icon"],
                    "spent": b["spent"],
                    "limit": b["limit_amount"],
                    "percent": round(pct, 1),
                    "level": "DANGER",
                    "message": f"🔥 TẨU HỎA NHẬP MA! {b['category_name']} đã vượt hạn mức ({round(pct,1)}%)"
                })
            elif pct >= 80:
                alerts.append({
                    "category": b["category_name"],
                    "icon": b["icon"],
                    "spent": b["spent"],
                    "limit": b["limit_amount"],
                    "percent": round(pct, 1),
                    "level": "WARNING",
                    "message": f"⚠️ CẢNH BÁO TÂM MA! {b['category_name']} đã dùng {round(pct,1)}% hạn mức"
                })

        return {"month_year": month_year, "alerts": alerts, "total_budgets": len(budgets)}


@app.post("/api/ai/chat")
def ai_chat(body: ChatBody, user: dict = Depends(get_current_user)):
    """Khí Linh Tiên Trí — trợ lý AI Gemini tư vấn tài chính"""
    model = get_gemini_model()

    # Lấy context tài chính của user
    month_year = datetime.date.today().strftime("%Y-%m")
    with get_db() as conn:
        summary = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type='INCOME' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN transaction_type='EXPENSE' THEN amount ELSE 0 END), 0) as expense
            FROM transactions WHERE user_id = ? AND strftime('%Y-%m', transaction_date) = ?
        """, (user["user_id"], month_year)).fetchone()

        total_balance = conn.execute(
            "SELECT COALESCE(SUM(balance), 0) as total FROM wallets WHERE user_id = ?",
            (user["user_id"],)
        ).fetchone()["total"]

    context = f"""Bạn là "Khí Linh Tiên Trí" — trợ lý AI tài chính phong cách tu tiên.
    Hãy trả lời câu hỏi của đạo hữu bằng giọng văn tu tiên huyền huyễn nhưng vẫn chính xác về mặt tài chính.

    Thông tin tài chính tháng {month_year} của đạo hữu:
    - Tổng thu nhập (Khai Thác Linh Mạch): {summary['income']:,.0f} VNĐ
    - Tổng chi tiêu (Tiêu Hao Linh Thạch): {summary['expense']:,.0f} VNĐ
    - Tiết kiệm thuần: {summary['income'] - summary['expense']:,.0f} VNĐ
    - Tổng số dư tất cả ví (Túi Càn Khôn): {total_balance:,.0f} VNĐ

    Câu hỏi của đạo hữu: {body.message}"""

    try:
        response = model.generate_content(context)
        ai_answer = response.text

        # Lưu lịch sử chat
        with get_db() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (user_id, prompt_question, ai_response) VALUES (?, ?, ?)",
                (user["user_id"], body.message, ai_answer)
            )

        return {"response": ai_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tiên Trí gặp trở ngại: {str(e)}")


@app.get("/api/ai/chat-history")
def get_chat_history(user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 30",
            (user["user_id"],)
        ).fetchall()
        return [dict(r) for r in rows]


# ──────────────────────────────────────────────
# STARTUP
# ──────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()
    print("=" * 62)
    print("  CAN KHON LINH THACH CAC -- Khai Mo Thanh Cong!")
    print("  Server: http://localhost:8000")
    print("  Docs:   http://localhost:8000/docs")
    print("=" * 62)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
