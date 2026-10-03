"""Kết nối SQLite, tạo bảng / migration không phá hủy và seed dữ liệu mẫu."""

import datetime
import os
import secrets
import sqlite3
from contextlib import contextmanager

import bcrypt

from backend.config import DATABASE


# ──────────────────────────────────────────────
# DATABASE HELPERS
# ──────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _seed_secret(env_name: str):
    """Đọc giá trị seed từ .env; nếu trống thì sinh ngẫu nhiên. Trả về (giá_trị, có_phải_tự_sinh)."""
    value = os.getenv(env_name, "").strip()
    if value:
        return value, False
    return secrets.token_urlsafe(9), True


def _print_seed_banner(label: str, value: str, env_name: str):
    print("\n" + "🔑" * 31)
    print(f"  ⚠️  {label.upper()} TÀI KHOẢN ADMIN (sinh ngẫu nhiên)")
    print("  📧  Email:     admin@gmail.com")
    print(f"  🔐  {label}: {value}")
    print(f"  ℹ️  Đặt biến {env_name} trong .env để cố định giá trị này.")
    print("🔑" * 31 + "\n")


def init_db():
    """Tạo các bảng cốt lõi + seed dữ liệu mẫu"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                soul_lamp_hash TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
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

            /* Change 5: Bảng password_reset_tokens */
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            /* Change 8: Bảng recurring_transactions */
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('INCOME','EXPENSE')) NOT NULL,
                frequency TEXT CHECK(frequency IN ('weekly','monthly')) NOT NULL DEFAULT 'monthly',
                next_run_date TEXT NOT NULL,
                note TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (wallet_id) REFERENCES wallets(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            /* Bảng debts (Theo dõi Nợ / Vay mượn) */
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_id INTEGER,
                debt_type TEXT CHECK(debt_type IN ('BORROW','LEND')) NOT NULL,
                person_name TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT DEFAULT '',
                is_settled INTEGER DEFAULT 0,
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (wallet_id) REFERENCES wallets(id)
            );

            /* Bảng saving_goals (Mục Tiêu Tiết Kiệm) */
            CREATE TABLE IF NOT EXISTS saving_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                target_date TEXT DEFAULT '',
                icon TEXT DEFAULT '🎯',
                is_completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            /* Lịch sử chuyển tiền giữa các ví */
            CREATE TABLE IF NOT EXISTS wallet_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                from_wallet_id INTEGER,
                to_wallet_id INTEGER,
                from_wallet_name TEXT NOT NULL,
                to_wallet_name TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            /* Lịch sử nạp / rút mục tiêu tiết kiệm */
            CREATE TABLE IF NOT EXISTS saving_goal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal_id INTEGER NOT NULL,
                action TEXT CHECK(action IN ('DEPOSIT','WITHDRAW')) NOT NULL,
                amount REAL NOT NULL,
                wallet_id INTEGER,
                wallet_name TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        # Migration: Ensure role, is_active, and soul_lamp_hash columns exist on users table
        user_cols = [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "role" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        if "is_active" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
        if "soul_lamp_hash" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN soul_lamp_hash TEXT")

        # Migration: ngày gốc trong tháng của giao dịch định kỳ (tránh trôi ngày 31 -> 28)
        rec_cols = [c[1] for c in conn.execute("PRAGMA table_info(recurring_transactions)").fetchall()]
        if "day_of_month" not in rec_cols:
            conn.execute("ALTER TABLE recurring_transactions ADD COLUMN day_of_month INTEGER")

        # Ensure default admin has role = 'admin', valid hash, and default soul_lamp_hash if NULL
        admin_row = conn.execute("SELECT id, password_hash, soul_lamp_hash FROM users WHERE email = 'admin@gmail.com'").fetchone()
        if admin_row:
            admin_hash = admin_row["password_hash"] or ""
            need_pw_reset = False
            try:
                if not (admin_hash.startswith("$2b$") or admin_hash.startswith("$2a$") or admin_hash.startswith("$2y$")):
                    need_pw_reset = True
                else:
                    bcrypt.checkpw(b"test", admin_hash.encode())
            except Exception:
                need_pw_reset = True

            if need_pw_reset:
                seed_password, generated = _seed_secret("SEED_ADMIN_PASSWORD")
                new_pw_hash = bcrypt.hashpw(seed_password.encode(), bcrypt.gensalt()).decode()
                conn.execute("UPDATE users SET role = 'admin', is_active = 1, password_hash = ? WHERE email = 'admin@gmail.com'", (new_pw_hash,))
                if generated:
                    _print_seed_banner("Mật khẩu", seed_password, "SEED_ADMIN_PASSWORD")
            else:
                conn.execute("UPDATE users SET role = 'admin', is_active = 1 WHERE email = 'admin@gmail.com'")

            # Gán Bản Mệnh Hồn Đăng cho tài khoản Admin nếu đang là NULL
            if admin_row["soul_lamp_hash"] is None or admin_row["soul_lamp_hash"] == "":
                soul_lamp, generated = _seed_secret("SEED_ADMIN_SOUL_LAMP")
                default_soul_lamp_hash = bcrypt.hashpw(soul_lamp.encode(), bcrypt.gensalt()).decode()
                conn.execute("UPDATE users SET soul_lamp_hash = ? WHERE email = 'admin@gmail.com'", (default_soul_lamp_hash,))
                if generated:
                    _print_seed_banner("Bản Mệnh Hồn Đăng", soul_lamp, "SEED_ADMIN_SOUL_LAMP")

        # Change 9: Seed dữ liệu mẫu — mật khẩu an toàn
        user_check = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if not user_check:
            # Đọc mật khẩu từ biến môi trường, hoặc tự sinh ngẫu nhiên
            seed_password, pw_generated = _seed_secret("SEED_ADMIN_PASSWORD")
            seed_soul_lamp, lamp_generated = _seed_secret("SEED_ADMIN_SOUL_LAMP")
            pw_hash = bcrypt.hashpw(seed_password.encode(), bcrypt.gensalt()).decode()
            admin_soul_lamp_hash = bcrypt.hashpw(seed_soul_lamp.encode(), bcrypt.gensalt()).decode()
            conn.execute(
                "INSERT INTO users (email, password_hash, full_name, soul_lamp_hash, role, is_active) VALUES (?, ?, ?, ?, 'admin', 1)",
                ("admin@gmail.com", pw_hash, "Ký Chủ", admin_soul_lamp_hash)
            )
            uid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            # In thông tin sinh ngẫu nhiên ra console (chỉ khi không cấu hình trong .env)
            if pw_generated:
                _print_seed_banner("Mật khẩu", seed_password, "SEED_ADMIN_PASSWORD")
            if lamp_generated:
                _print_seed_banner("Bản Mệnh Hồn Đăng", seed_soul_lamp, "SEED_ADMIN_SOUL_LAMP")

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
                """INSERT INTO transactions
                   (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
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
        else:
            # Update default name from old 'Đạo Hữu Admin' to 'Ký Chủ' if unchanged
            conn.execute(
                "UPDATE users SET full_name = 'Ký Chủ' WHERE email = 'admin@gmail.com' AND full_name = 'Đạo Hữu Admin'"
            )

        # Dọn dẹp dữ liệu mồ côi không gắn user_id hợp lệ
        conn.execute("DELETE FROM transactions WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM wallets WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM categories WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM budgets WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM invoice_ocr_logs WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM chat_sessions WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM wallet_transfers WHERE user_id NOT IN (SELECT id FROM users)")
        conn.execute("DELETE FROM saving_goal_logs WHERE user_id NOT IN (SELECT id FROM users)")

        conn.commit()
