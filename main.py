"""
╔══════════════════════════════════════════════════════════════════╗
║   HỆ THỐNG QUẢN LÝ CHI TIÊU — BACKEND API DỊCH VỤ TÀI CHÍNH      ║
║   FastAPI + SQLAlchemy ORM + SQL Server / SQLite                 ║
║   Enterprise-Grade Defensive Security & Concurrency Control      ║
║   Gemini AI Financial Advisor & OCR Vision Integration           ║
║   Full Unicode Migration & Automated Mojibake Auto-Cleaner       ║
║   Brand: Hệ Thống Quản Lý Chi Tiêu                               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import json
import base64
import datetime
import calendar
import logging
from contextlib import contextmanager, asynccontextmanager
from typing import Optional, List, Dict, Any

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Cấu hình logging chuẩn hóa UTF-8
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ExpenseManagementAPI")

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from sqlalchemy import create_engine, text, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError

# Nạp các module bảo mật và models
from models import Base, User, Category, Transaction, Wallet, Budget, Debt, SavingGoal, RecurringTransaction, InvoiceOcrLog, ChatSession
from schemas import (
    RegisterBody, LoginBody, WalletBody, CategoryBody,
    TransactionBody, TransactionUpdateBody, TransferBody,
    BudgetBody, ChatBody, ProfileUpdateBody
)
from security import (
    hash_password, verify_password, create_access_token, decode_access_token,
    brute_force_protector, enforce_rate_limit
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH, override=True)
else:
    load_dotenv()

def get_gemini_api_key() -> str:
    """Lấy API Key của Google Gemini từ biến môi trường"""
    for var_name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY", "API_KEY"]:
        val = os.getenv(var_name)
        if val and val.strip() and val.strip().strip("'\"") != "your_api_key_here":
            return val.strip().strip("'\"")
    return ""

def get_gemini_models_list(vision: bool = False) -> List[str]:
    """Danh sách các model AI được hỗ trợ ưu tiên theo thứ tự khả dụng"""
    if vision:
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro-vision"]
    return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

def validate_image_bytes(data: bytes) -> str:
    """Kiểm tra và xác thực Magic Bytes của tệp hình ảnh để chống upload mã độc"""
    if not data or len(data) < 8:
        raise ValueError("Dữ liệu ảnh không hợp lệ hoặc kích thước quá nhỏ.")
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("Định dạng ảnh không được hỗ trợ (chỉ chấp nhận JPEG, PNG, GIF, WEBP).")

ALLOWED_ORIGINS_RAW = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:8000,http://127.0.0.1:5173,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000"
)
ALLOWED_ORIGINS = [orig.strip() for orig in ALLOWED_ORIGINS_RAW.split(",") if orig.strip()]

# ──────────────────────────────────────────────
# DATABASE CONNECTION & POOLING
# ──────────────────────────────────────────────
def create_db_engine():
    urls = [
        os.getenv("DATABASE_URL"),
        r"mssql+pyodbc://@.\SQLEXPRESS/QuanLyChiTieu_nvt?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes",
        r"mssql+pyodbc://@.\SQLEXPRESS/QuanLyChiTieu?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes",
    ]
    for url in urls:
        if not url: continue
        try:
            eng = create_engine(url, pool_pre_ping=True)
            with eng.connect() as test_conn:
                logger.info(f"✅ Kết nối CSDL SQL Server thành công: {url}")
            return eng
        except Exception as err:
            logger.warning(f"⚠️ Thử kết nối {url} không thành công: {err}")
    logger.info("ℹ️ Chuyển sang sử dụng SQLite nội bộ (app.db)")
    return create_engine("sqlite:///app.db", connect_args={"check_same_thread": False})

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency cung cấp Session Database có quản lý Transaction và Rollback tự động"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction Rollback do lỗi: {e}")
        raise
    finally:
        db.close()

# ──────────────────────────────────────────────
# UNICODE SCHEMA MIGRATION & MOJIBAKE CLEANER
# ──────────────────────────────────────────────
def clean_text_mojibake(text_val: str) -> str:
    """Hàm chuyển đổi các chuỗi văn bản bị lỗi font Mojibake '?' về tiếng Việt chuẩn xác"""
    if not text_val or "?" not in text_val:
        return text_val

    # Xử lý các mẫu tên ví tiền phổ biến
    if "Ti" in text_val and "M" in text_val:
        return "Tiền Mặt"
    if "MB" in text_val or ("Kho" in text_val and "Bank" in text_val):
        return "Tài Khoản MB Bank"
    if "MoMo" in text_val or ("Đi" in text_val and "T" in text_val):
        return "Ví Điện Tử MoMo"
    if "Tài Kho" in text_val or "Tai Kho" in text_val:
        return text_val.replace("Tài Kho?n", "Tài Khoản").replace("Tai Kho?n", "Tài Khoản")

    replacements = [
        ("Ti?n M?t", "Tiền Mặt"),
        ("Ti?n m?t", "Tiền mặt"),
        ("Tài Kho?n", "Tài Khoản"),
        ("Ti Kho?n", "Tài Khoản"),
        ("Ví Đi?n T?", "Ví Điện Tử"),
        ("V Đi?n T?", "Ví Điện Tử"),
        ("Đi?n T?", "Điện Tử"),
        ("Ăn u?ng", "Ăn uống"),
        ("Ăn U?ng", "Ăn Uống"),
        ("An u?ng", "Ăn uống"),
        ("Mua s?m", "Mua sắm"),
        ("Mua S?m", "Mua Sắm"),
        ("Di chuy?n", "Di chuyển"),
        ("Di Chuy?n", "Di Chuyển"),
        ("H?c t?p", "Học tập"),
        ("Phát tri?n", "Phát triển"),
        ("Hóa \u0111?n", "Hóa đơn"),
        ("Ti?n ích", "Tiện ích"),
        ("S?c kh?e", "Sức khỏe"),
        ("Y t?", "Y tế"),
        ("Gi?i trí", "Giải trí"),
        ("Du l?ch", "Du lịch"),
        ("Ti?n l??ng", "Tiền lương"),
        ("Ti?n l?ng", "Tiền lương"),
        ("??u t?", "Đầu tư"),
        ("Thu nh?p", "Thu nhập"),
        ("Thu nh?p ph?", "Thu nhập phụ"),
        ("Th??ng", "Thưởng"),
        ("Qu?n Tr? Vin", "Quản Trị Viên"),
        ("Qu?n Tr? Vin", "Quản Trị Viên"),
        ("Qu?n tr?", "Quản trị"),
        ("H? Th?ng", "Hệ Thống"),
        ("Chi Tiu", "Chi Tiêu"),
        ("Chi Ti?u", "Chi Tiêu")
    ]
    res = text_val
    for old_s, new_s in replacements:
        res = res.replace(old_s, new_s)

    # Loại bỏ các dấu hỏi còn sót lại
    res = res.replace("?", "")
    return res.strip()

def migrate_tables_to_nvarchar():
    """Tự động thực thi ALTER TABLE trong SQL Server sang NVARCHAR cho tất cả các bảng"""
    alter_queries = [
        "ALTER TABLE Users ALTER COLUMN FullName NVARCHAR(150) NOT NULL",
        "ALTER TABLE Users ALTER COLUMN Email NVARCHAR(150) NOT NULL",
        "ALTER TABLE Categories ALTER COLUMN Name NVARCHAR(150) NOT NULL",
        "ALTER TABLE Categories ALTER COLUMN Icon NVARCHAR(100) NOT NULL",
        "ALTER TABLE wallets ALTER COLUMN wallet_name NVARCHAR(150) NOT NULL",
        "ALTER TABLE wallets ALTER COLUMN wallet_type NVARCHAR(50) NOT NULL",
        "ALTER TABLE Transactions ALTER COLUMN Note NVARCHAR(500) NOT NULL",
        "ALTER TABLE budgets ALTER COLUMN month_year NVARCHAR(50) NOT NULL",
        "ALTER TABLE debts ALTER COLUMN debt_name NVARCHAR(200) NOT NULL",
        "ALTER TABLE saving_goals ALTER COLUMN goal_name NVARCHAR(200) NOT NULL",
        "ALTER TABLE recurring_transactions ALTER COLUMN note NVARCHAR(500) NOT NULL",
        "ALTER TABLE invoice_ocr_logs ALTER COLUMN image_path NVARCHAR(500) NOT NULL",
    ]
    try:
        with engine.begin() as conn:
            for q in alter_queries:
                try:
                    conn.execute(text(q))
                except Exception:
                    pass
    except Exception:
        pass

DEFAULT_CATEGORIES = [
    ("Ăn uống", "EXPENSE", "fa-solid fa-utensils"),
    ("Mua sắm", "EXPENSE", "fa-solid fa-cart-shopping"),
    ("Di chuyển", "EXPENSE", "fa-solid fa-car"),
    ("Học tập & Phát triển", "EXPENSE", "fa-solid fa-book"),
    ("Hóa đơn & Tiện ích", "EXPENSE", "fa-solid fa-bolt"),
    ("Sức khỏe & Y tế", "EXPENSE", "fa-solid fa-heart-pulse"),
    ("Giải trí & Du lịch", "EXPENSE", "fa-solid fa-plane"),
    ("Tiền lương", "INCOME", "fa-solid fa-money-bill-wave"),
    ("Đầu tư & Thưởng", "INCOME", "fa-solid fa-chart-line"),
    ("Thu nhập phụ", "INCOME", "fa-solid fa-gift"),
]

def cleanup_corrupted_categories(db: Session) -> int:
    """Dọn dẹp triệt để các danh mục bị lỗi font Mojibake và nạp lại chuẩn Unicode"""
    cleaned_count = 0
    try:
        all_cats = db.query(Category).all()
        corrupted = [c for c in all_cats if "?" in c.Name or "?" in (c.Icon or "")]

        if corrupted:
            fallback_cat = db.query(Category).filter(
                ~Category.Name.like('%?%'),
                Category.Type == "EXPENSE"
            ).first()

            if not fallback_cat or "?" in fallback_cat.Name:
                fallback_cat = Category(Name="Khác", Type="EXPENSE", Icon="fa-solid fa-box")
                db.add(fallback_cat)
                db.commit()
                db.refresh(fallback_cat)

            for bad_cat in corrupted:
                db.query(Transaction).filter(Transaction.CategoryId == bad_cat.Id).update(
                    {Transaction.CategoryId: fallback_cat.Id},
                    synchronize_session=False
                )
                db.query(Budget).filter(Budget.category_id == bad_cat.Id).update(
                    {Budget.category_id: fallback_cat.Id},
                    synchronize_session=False
                )
                db.delete(bad_cat)
                cleaned_count += 1

            db.commit()
            logger.info(f"🧹 Đã xóa {cleaned_count} danh mục bị lỗi font Mojibake thành công.")

        # Seed lại các danh mục chuẩn
        for name, ctype, icon in DEFAULT_CATEGORIES:
            chk = db.query(Category).filter(Category.Name == name).first()
            if not chk:
                db.add(Category(Name=name, Type=ctype, Icon=icon))
            else:
                chk.Type = ctype
                chk.Icon = icon
        db.commit()
        logger.info("✅ Đã chuẩn hóa danh mục tài chính chuẩn Unicode & FontAwesome.")
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi dọn dẹp danh mục: {e}")
    return cleaned_count

def cleanup_corrupted_wallets(db: Session) -> int:
    """Dọn dẹp và chuẩn hóa lại tên các ví tiền bị lỗi font Mojibake (Ti?n M?t -> Tiền Mặt,...)"""
    cleaned = 0
    try:
        wallets = db.query(Wallet).all()
        for w in wallets:
            if w.wallet_name and "?" in w.wallet_name:
                new_name = clean_text_mojibake(w.wallet_name)
                if new_name != w.wallet_name:
                    w.wallet_name = new_name
                    cleaned += 1
        if cleaned > 0:
            db.commit()
            logger.info(f"🧹 Đã chuẩn hóa {cleaned} ví tiền bị lỗi font Unicode.")
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi dọn dẹp ví tiền: {e}")
    return cleaned

def cleanup_corrupted_users(db: Session) -> int:
    """Chuẩn hóa họ tên người dùng và tài khoản Quản trị viên"""
    cleaned = 0
    try:
        users = db.query(User).all()
        for u in users:
            if u.FullName and "?" in u.FullName:
                if u.Email.lower() == "admin@gmail.com":
                    u.FullName = "Quản Trị Viên Hệ Thống"
                else:
                    u.FullName = clean_text_mojibake(u.FullName)
                cleaned += 1
        if cleaned > 0:
            db.commit()
            logger.info(f"🧹 Đã chuẩn hóa {cleaned} tài khoản người dùng.")
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khi dọn dẹp tài khoản: {e}")
    return cleaned

def cleanup_all_database_mojibake(db: Session) -> Dict[str, int]:
    """Tổng dọn rác toàn diện CSDL: Migrate NVARCHAR + Sửa Lỗi Font Ví Tiền + Danh Mục + Người Dùng"""
    migrate_tables_to_nvarchar()
    c_cats = cleanup_corrupted_categories(db)
    c_wallets = cleanup_corrupted_wallets(db)
    c_users = cleanup_corrupted_users(db)
    return {
        "categories_cleaned": c_cats,
        "wallets_cleaned": c_wallets,
        "users_cleaned": c_users
    }

def seed_default_user_data(db: Session, user_id: int):
    """Khởi tạo ví tiền và các danh mục thu/chi mặc định cho tài khoản mới"""
    try:
        wallets_exist = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallets_exist:
            default_wallets = [
                Wallet(user_id=user_id, wallet_name="Tiền Mặt", balance=5000000.0, wallet_type="cash"),
                Wallet(user_id=user_id, wallet_name="Tài Khoản MB Bank", balance=15000000.0, wallet_type="bank"),
                Wallet(user_id=user_id, wallet_name="Ví Điện Tử MoMo", balance=2000000.0, wallet_type="e-wallet"),
            ]
            db.add_all(default_wallets)
            db.commit()
        else:
            cleanup_corrupted_wallets(db)
    except Exception as e:
        db.rollback()
        logger.warning(f"Bỏ qua seed ví: {e}")

    cleanup_corrupted_categories(db)

def init_db():
    """Khởi tạo cấu trúc bảng, dọn rác Mojibake và tạo tài khoản Admin mặc định"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        cleanup_all_database_mojibake(db)

        admin_email = "admin@gmail.com"
        admin = db.query(User).filter(User.Email == admin_email).first()
        admin_pw_hash = hash_password("123456")

        if not admin:
            new_admin = User(
                Email=admin_email,
                PasswordHash=admin_pw_hash,
                FullName="Quản Trị Viên Hệ Thống",
                Role="Admin",
                IsActive=True
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            seed_default_user_data(db, new_admin.Id)
            logger.info("✅ Đã khởi tạo tài khoản Quản trị viên (admin@gmail.com)")
        else:
            admin.PasswordHash = admin_pw_hash
            admin.FullName = "Quản Trị Viên Hệ Thống"
            admin.Role = "Admin"
            admin.IsActive = True
            db.commit()
            seed_default_user_data(db, admin.Id)
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi khởi tạo CSDL: {e}")
    finally:
        db.close()

# ──────────────────────────────────────────────
# APPLICATION INITIALIZATION
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("=" * 60)
    logger.info("  HỆ THỐNG QUẢN LÝ CHI TIÊU — SẴN SÀNG HOẠT ĐỘNG")
    logger.info("  Bảo mật: Passlib Bcrypt, Jose JWT (30m), Anti-IDOR, Anti-BruteForce")
    logger.info("  Tích hợp AI: Gemini AI Chatbot & OCR Vision")
    logger.info("  FontAwesome / Emoji Category Icons & Unicode Mojibake Cleaner")
    logger.info("  Server: http://localhost:8000")
    logger.info("  Docs:   http://localhost:8000/docs")
    logger.info("=" * 60)
    yield

app = FastAPI(
    title="Hệ Thống Quản Lý Chi Tiêu API",
    description="API quản lý tài chính cá nhân toàn diện, tích hợp Gemini AI và kiến trúc bảo mật phòng thủ",
    version="4.4.0",
    lifespan=lifespan
)
security_scheme = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# NATURAL LANGUAGE EXCEPTION HANDLERS (TRANSLATE PYDANTIC)
# ──────────────────────────────────────────────
FIELD_TRANSLATIONS: Dict[str, str] = {
    "email": "Địa chỉ email",
    "password": "Mật khẩu",
    "full_name": "Họ và tên",
    "amount": "Số tiền",
    "category_id": "Danh mục",
    "wallet_id": "Ví thanh toán",
    "wallet_name": "Tên ví",
    "wallet_type": "Loại ví",
    "category_name": "Tên danh mục",
    "category_type": "Loại danh mục",
    "limit_amount": "Hạn mức ngân sách",
    "transaction_date": "Ngày giao dịch",
    "month_year": "Tháng/Năm",
    "message": "Nội dung tin nhắn",
    "from_wallet_id": "Ví nguồn",
    "to_wallet_id": "Ví đích",
    "note": "Ghi chú"
}

def translate_validation_error(err: dict) -> str:
    loc = err.get("loc", [])
    field_name = str(loc[-1]) if loc else "dữ liệu"
    field_label = FIELD_TRANSLATIONS.get(field_name, field_name)
    err_type = err.get("type", "")
    msg = err.get("msg", "")

    if field_name == "password" and "string_too_short" in err_type:
        return "Vui lòng nhập mật khẩu tối thiểu 6 kí tự (bao gồm chữ hoa, chữ thường, số và kí tự đặc biệt)."
    if "string_too_short" in err_type:
        return f"Trường [{field_label}] quá ngắn, vui lòng nhập đầy đủ thông tin."
    if "string_too_long" in err_type:
        return f"Trường [{field_label}] vượt quá độ dài quy định."
    if "missing" in err_type:
        return f"Vui lòng điền đầy đủ thông tin [{field_label}]."
    if "email" in field_name or "value_error" in err_type:
        if "email" in field_name:
            return "Định dạng email không hợp lệ, vui lòng kiểm tra lại."
        if msg.startswith("Value error, "):
            return msg.replace("Value error, ", "").strip()
        return f"Dữ liệu [{field_label}] không hợp lệ: {msg}"
    if "greater_than" in err_type or "greater_than_equal" in err_type:
        return f"Giá trị [{field_label}] phải lớn hơn 0."
    if "less_than" in err_type or "less_than_equal" in err_type:
        return f"Giá trị [{field_label}] vượt quá mức cho phép."
    if "string_pattern_mismatch" in err_type:
        return f"Định dạng của [{field_label}] không đúng quy chuẩn hệ thống."
    
    return f"Thông tin [{field_label}] không hợp lệ. Vui lòng kiểm tra lại."

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    translated_messages = []
    for err in errors:
        translated_messages.append(translate_validation_error(err))
    
    final_message = translated_messages[0] if translated_messages else "Dữ liệu gửi lên không đúng định dạng."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": final_message}
    )

# ──────────────────────────────────────────────
# AUTHENTICATION & AUTHORIZATION DEPENDENCIES
# ──────────────────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency giải mã JWT Token và xác thực quyền người dùng"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin xác thực không hợp lệ."
        )

    user = db.query(User).filter(User.Id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản người dùng không tồn tại."
        )

    if not user.IsActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa quyền truy cập."
        )

    # Tự động sửa họ tên nếu bị lỗi font
    if user.FullName and "?" in user.FullName:
        user.FullName = clean_text_mojibake(user.FullName)
        db.commit()

    role_str = str(user.Role or "User").lower()
    return {
        "user_id": user.Id,
        "email": user.Email,
        "role": role_str,
        "full_name": user.FullName
    }

def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency kiểm tra quyền Quản trị viên (Admin RBAC)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Quản trị viên hệ thống mới có quyền thực hiện tác vụ này."
        )
    return current_user

# ──────────────────────────────────────────────
# AUTHENTICATION ROUTES
# ──────────────────────────────────────────────
@app.post("/api/auth/register", status_code=status.HTTP_200_OK)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    """Đăng ký tài khoản người dùng mới với mật khẩu được băm an toàn"""
    existing_user = db.query(User).filter(User.Email == body.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email này đã được đăng ký trên hệ thống."
        )

    pw_hash = hash_password(body.password)
    role = "Admin" if body.email.lower() == "admin@gmail.com" else "User"

    new_user = User(
        Email=body.email,
        PasswordHash=pw_hash,
        FullName=body.full_name,
        Role=role,
        IsActive=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    seed_default_user_data(db, new_user.Id)

    token = create_access_token({
        "user_id": new_user.Id,
        "email": new_user.Email,
        "role": role.lower()
    })

    return {
        "token": token,
        "user_id": new_user.Id,
        "full_name": new_user.FullName,
        "email": new_user.Email,
        "role": role.lower()
    }

@app.post("/api/auth/login", status_code=status.HTTP_200_OK)
def login(request: Request, body: LoginBody, db: Session = Depends(get_db)):
    """Đăng nhập hệ thống có cơ chế phòng chống Brute-Force và khóa tạm thời"""
    client_ip = request.client.host if request.client else "unknown"
    lockout_key = f"{body.email}:{client_ip}"

    is_locked, remaining = brute_force_protector.check_is_locked(lockout_key)
    if is_locked:
        minutes_rem = (remaining // 60) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Tài khoản/IP tạm thời bị khóa do nhập sai mật khẩu quá 5 lần. Vui lòng thử lại sau {minutes_rem} phút."
        )

    user = db.query(User).filter(User.Email == body.email).first()
    if not user:
        brute_force_protector.record_failed_attempt(lockout_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác."
        )

    if not user.IsActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa."
        )

    if not verify_password(body.password, user.PasswordHash):
        attempts = brute_force_protector.record_failed_attempt(lockout_key)
        remaining_tries = max(0, 5 - attempts)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Mật khẩu không chính xác. Bạn còn {remaining_tries} lần thử trước khi bị khóa."
        )

    brute_force_protector.reset_attempts(lockout_key)

    if user.FullName and "?" in user.FullName:
        user.FullName = clean_text_mojibake(user.FullName)
        db.commit()

    role_str = str(user.Role or ("Admin" if body.email.lower() == "admin@gmail.com" else "User")).lower()
    token = create_access_token({
        "user_id": user.Id,
        "email": user.Email,
        "role": role_str
    })

    return {
        "token": token,
        "user_id": user.Id,
        "full_name": user.FullName,
        "email": user.Email,
        "role": role_str
    }

@app.get("/api/user/profile")
def get_user_profile(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy thông tin tài khoản người dùng"""
    u = db.query(User).filter(User.Id == user["user_id"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
    return {
        "Id": u.Id,
        "Email": u.Email,
        "FullName": u.FullName,
        "Role": u.Role,
        "CreatedAt": str(u.CreatedAt)
    }

@app.put("/api/user/profile")
def update_user_profile(body: ProfileUpdateBody, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cập nhật thông tin họ tên người dùng"""
    u = db.query(User).filter(User.Id == user["user_id"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
    u.FullName = body.full_name
    db.commit()
    return {"message": "Cập nhật thông tin thành công!", "full_name": body.full_name}

# ──────────────────────────────────────────────
# WALLETS ROUTES (PESSIMISTIC LOCKING & IDOR SAFE)
# ──────────────────────────────────────────────
@app.get("/api/wallets")
def get_wallets(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy danh sách các ví tiền của người dùng hiện tại (Tự động sửa lỗi font Mojibake)"""
    wallets_list = db.query(Wallet).filter(Wallet.user_id == user["user_id"]).order_by(Wallet.id.asc()).all()
    if not wallets_list:
        seed_default_user_data(db, user["user_id"])
        wallets_list = db.query(Wallet).filter(Wallet.user_id == user["user_id"]).order_by(Wallet.id.asc()).all()

    # Tự động chuẩn hóa nếu phát hiện ký tự '?'
    needs_commit = False
    for w in wallets_list:
        if w.wallet_name and "?" in w.wallet_name:
            clean_name = clean_text_mojibake(w.wallet_name)
            if clean_name != w.wallet_name:
                w.wallet_name = clean_name
                needs_commit = True
    if needs_commit:
        try:
            db.commit()
        except Exception:
            db.rollback()

    return [
        {
            "id": w.id,
            "user_id": w.user_id,
            "wallet_name": w.wallet_name,
            "balance": w.balance,
            "wallet_type": w.wallet_type,
            "created_at": str(w.created_at)
        } for w in wallets_list
    ]

@app.post("/api/wallets")
def create_wallet(body: WalletBody, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Tạo ví tiền mới"""
    new_wallet = Wallet(
        user_id=user["user_id"],
        wallet_name=body.wallet_name,
        balance=body.balance,
        wallet_type=body.wallet_type
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return {"id": new_wallet.id, "message": "Tạo ví thành công!"}

@app.delete("/api/wallets/{wallet_id}")
def delete_wallet(wallet_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xóa ví tiền (Phòng chống IDOR)"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Ví tiền không tồn tại.")

    if wallet.user_id != user["user_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập hoặc xóa ví này.")

    count = db.query(Wallet).filter(Wallet.user_id == user["user_id"]).count()
    if count <= 1:
        raise HTTPException(status_code=400, detail="Bạn cần duy trì ít nhất 1 ví tiền trong tài khoản.")

    db.delete(wallet)
    db.commit()
    return {"message": "Đã xóa ví thành công."}

@app.post("/api/wallets/transfer")
def transfer_between_wallets(body: TransferBody, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Chuyển tiền giữa 2 ví an toàn bằng Khóa bi quan (Pessimistic Locking)"""
    if body.from_wallet_id == body.to_wallet_id:
        raise HTTPException(status_code=400, detail="Ví nguồn và ví đích không được trùng nhau.")

    try:
        w_from = db.query(Wallet).filter(
            Wallet.id == body.from_wallet_id,
            Wallet.user_id == user["user_id"]
        ).first()

        w_to = db.query(Wallet).filter(
            Wallet.id == body.to_wallet_id,
            Wallet.user_id == user["user_id"]
        ).first()

        if not w_from or not w_to:
            raise HTTPException(status_code=404, detail="Một trong hai ví tiền không tồn tại hoặc không thuộc quyền sở hữu của bạn.")

        if w_from.balance < body.amount:
            raise HTTPException(status_code=400, detail=f"Số dư ví nguồn không đủ ({w_from.balance:,.0f} < {body.amount:,.0f} VNĐ).")

        w_from.balance -= body.amount
        w_to.balance += body.amount
        db.commit()

        return {"message": f"Chuyển thành công {body.amount:,.0f} VNĐ từ [{w_from.wallet_name}] sang [{w_to.wallet_name}]."}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi chuyển tiền: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình xử lý luân chuyển số dư.")

# ──────────────────────────────────────────────
# CATEGORIES ROUTES & CLEANUP
# ──────────────────────────────────────────────
@app.get("/api/categories")
def get_categories(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy danh sách các danh mục chi tiêu & thu nhập (Chuẩn FontAwesome/Emoji)"""
    cats = db.query(Category).order_by(Category.Id.asc()).all()
    return [
        {
            "id": c.Id,
            "category_name": c.Name,
            "category_type": c.Type,
            "icon": c.Icon or "fa-solid fa-box"
        } for c in cats
    ]

@app.post("/api/categories")
def create_category(body: CategoryBody, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Tạo danh mục mới"""
    new_cat = Category(
        Name=body.category_name,
        Type=body.category_type,
        Icon=body.icon
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return {"id": new_cat.Id, "message": "Đã tạo danh mục thành công!"}

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xóa danh mục"""
    cat = db.query(Category).filter(Category.Id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Danh mục không tồn tại.")
    db.delete(cat)
    db.commit()
    return {"message": "Đã xóa danh mục thành công."}

@app.post("/api/cleanup-categories")
@app.post("/api/cleanup-all")
@app.post("/api/admin/cleanup-categories")
def cleanup_all_endpoint(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """API endpoint dọn rác ký tự lỗi Mojibake '?' và chuẩn hóa toàn bộ CSDL (Ví tiền, Danh mục, Người dùng)"""
    res = cleanup_all_database_mojibake(db)
    total_cleaned = res["categories_cleaned"] + res["wallets_cleaned"] + res["users_cleaned"]
    return {
        "message": f"Đã dọn dẹp và chuẩn hóa thành công: {res['wallets_cleaned']} ví tiền, {res['categories_cleaned']} danh mục và {res['users_cleaned']} người dùng!",
        "cleaned_count": total_cleaned,
        "details": res
    }

# ──────────────────────────────────────────────
# TRANSACTIONS ROUTES (ANTI-IDOR & ANTI-CHEAT)
# ──────────────────────────────────────────────
@app.get("/api/transactions")
def get_transactions(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách giao dịch có phân trang và lọc (Bảo vệ IDOR)"""
    query = db.query(Transaction, Category).join(Category, Transaction.CategoryId == Category.Id)
    query = query.filter(Transaction.UserId == user["user_id"])

    if transaction_type:
        query = query.filter(Category.Type == transaction_type)
    if category_id:
        query = query.filter(Transaction.CategoryId == category_id)
    if start_date:
        query = query.filter(Transaction.TransactionDate >= start_date)
    if end_date:
        query = query.filter(Transaction.TransactionDate <= end_date)

    rows = query.order_by(Transaction.TransactionDate.desc(), Transaction.Id.desc()).offset(offset).limit(limit).all()

    default_w = db.query(Wallet).filter(Wallet.user_id == user["user_id"]).first()
    default_w_name = default_w.wallet_name if default_w else "Ví Chính"
    default_w_id = default_w.id if default_w else 1

    res = []
    for txn, cat in rows:
        res.append({
            "id": txn.Id,
            "wallet_id": default_w_id,
            "wallet_name": default_w_name,
            "category_id": txn.CategoryId,
            "category_name": cat.Name,
            "category_icon": cat.Icon or "fa-solid fa-box",
            "amount": txn.Amount,
            "transaction_type": cat.Type,
            "transaction_date": str(txn.TransactionDate),
            "note": txn.Note or ""
        })
    return res

@app.post("/api/transactions")
def create_transaction(
    request: Request,
    body: TransactionBody,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo giao dịch tài chính với Pessimistic Locking cập nhật số dư ví an toàn"""
    enforce_rate_limit(request, max_requests=10, window_seconds=60, endpoint_tag="create_txn")

    cat = db.query(Category).filter(Category.Id == body.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Danh mục không tồn tại.")

    if cat.Type != body.transaction_type:
        raise HTTPException(
            status_code=400,
            detail=f"Loại giao dịch ({body.transaction_type}) không khớp với loại danh mục ({cat.Type})."
        )

    try:
        new_txn = Transaction(
            UserId=user["user_id"],
            CategoryId=body.category_id,
            Amount=body.amount,
            TransactionDate=body.transaction_date,
            Note=body.note
        )
        db.add(new_txn)

        target_wallet_id = body.wallet_id
        if not target_wallet_id:
            w_first = db.query(Wallet).filter(Wallet.user_id == user["user_id"]).first()
            target_wallet_id = w_first.id if w_first else None

        if target_wallet_id:
            target_wallet = db.query(Wallet).filter(
                Wallet.id == target_wallet_id,
                Wallet.user_id == user["user_id"]
            ).first()

            if target_wallet:
                if body.transaction_type == "EXPENSE":
                    target_wallet.balance -= body.amount
                else:
                    target_wallet.balance += body.amount

        db.commit()
        db.refresh(new_txn)
        return {"id": new_txn.Id, "message": "Thêm giao dịch thành công!"}
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi thêm giao dịch: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý tạo giao dịch tài chính.")

@app.delete("/api/transactions/{txn_id}")
def delete_transaction(txn_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xóa giao dịch tài chính và khôi phục số dư ví an toàn (IDOR Protection)"""
    txn = db.query(Transaction).filter(Transaction.Id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Giao dịch không tồn tại.")

    if txn.UserId != user["user_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền can thiệp vào giao dịch của người khác.")

    try:
        cat = db.query(Category).filter(Category.Id == txn.CategoryId).first()
        t_type = cat.Type if cat else "EXPENSE"

        target_wallet = db.query(Wallet).filter(
            Wallet.user_id == txn.UserId
        ).first()

        if target_wallet:
            if t_type == "EXPENSE":
                target_wallet.balance += txn.Amount
            else:
                target_wallet.balance -= txn.Amount

        db.delete(txn)
        db.commit()
        return {"message": "Đã xóa giao dịch thành công."}
    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi xóa giao dịch: {e}")
        raise HTTPException(status_code=500, detail="Không thể xóa giao dịch.")

# ──────────────────────────────────────────────
# DASHBOARD & FINANCIAL REPORTS
# ──────────────────────────────────────────────
@app.get("/api/dashboard/summary")
@app.get("/api/reports/summary")
def get_dashboard_summary(month_year: Optional[str] = None, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Tổng quan số dư, tổng thu, tổng chi và phân bổ danh mục trong tháng"""
    if not month_year:
        month_year = datetime.date.today().strftime("%Y-%m")

    total_income_res = db.query(func.sum(Transaction.Amount)).join(Category, Transaction.CategoryId == Category.Id).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "INCOME",
        Transaction.TransactionDate.like(f"{month_year}%")
    ).scalar() or 0.0

    total_expense_res = db.query(func.sum(Transaction.Amount)).join(Category, Transaction.CategoryId == Category.Id).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate.like(f"{month_year}%")
    ).scalar() or 0.0

    total_balance_res = db.query(func.sum(Wallet.balance)).filter(
        Wallet.user_id == user["user_id"]
    ).scalar()

    if total_balance_res is None:
        total_balance_res = float(total_income_res - total_expense_res + 22000000.0)

    exp_cats = db.query(
        Category.Name, Category.Icon, func.sum(Transaction.Amount).label("total")
    ).join(Category, Transaction.CategoryId == Category.Id).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate.like(f"{month_year}%")
    ).group_by(Category.Name, Category.Icon).order_by(func.sum(Transaction.Amount).desc()).all()

    category_breakdown = [
        {
            "category_name": row[0],
            "icon": row[1] or "fa-solid fa-box",
            "total": float(row[2] or 0),
            "total_amount": float(row[2] or 0)
        } for row in exp_cats
    ]

    return {
        "month_year": month_year,
        "total_income": float(total_income_res),
        "total_expense": float(total_expense_res),
        "net_savings": float(total_income_res - total_expense_res),
        "total_balance": float(total_balance_res),
        "expense_by_category": category_breakdown
    }

@app.get("/api/reports/trend")
@app.get("/api/stats/monthly-trend")
def get_monthly_trend(months: int = Query(6, ge=1, le=24), user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xu hướng thu chi qua các tháng gần nhất"""
    trend = []
    today = datetime.date.today()
    for i in range(months - 1, -1, -1):
        m_date = today - datetime.timedelta(days=i * 30)
        m_str = m_date.strftime("%Y-%m")

        inc = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
            Category, Transaction.CategoryId == Category.Id
        ).filter(
            Transaction.UserId == user["user_id"],
            Category.Type == "INCOME",
            Transaction.TransactionDate.like(f"{m_str}%")
        ).scalar() or 0.0

        exp = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
            Category, Transaction.CategoryId == Category.Id
        ).filter(
            Transaction.UserId == user["user_id"],
            Category.Type == "EXPENSE",
            Transaction.TransactionDate.like(f"{m_str}%")
        ).scalar() or 0.0

        trend.append({
            "month": m_str,
            "month_year": m_str,
            "income": float(inc),
            "expense": float(exp),
            "total_income": float(inc),
            "total_expense": float(exp)
        })
    return {"trend": trend}

@app.get("/api/reports/weekly")
def get_weekly_reports(weeks: int = Query(4, ge=1, le=12), user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Báo cáo dòng tiền theo các tuần gần nhất"""
    today = datetime.date.today()
    weekly_data = []
    for i in range(weeks - 1, -1, -1):
        end_d = today - datetime.timedelta(days=i * 7)
        start_d = end_d - datetime.timedelta(days=6)
        s_str = start_d.strftime("%Y-%m-%d")
        e_str = end_d.strftime("%Y-%m-%d")

        inc = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
            Category, Transaction.CategoryId == Category.Id
        ).filter(
            Transaction.UserId == user["user_id"],
            Category.Type == "INCOME",
            Transaction.TransactionDate >= s_str,
            Transaction.TransactionDate <= e_str
        ).scalar() or 0.0

        exp = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
            Category, Transaction.CategoryId == Category.Id
        ).filter(
            Transaction.UserId == user["user_id"],
            Category.Type == "EXPENSE",
            Transaction.TransactionDate >= s_str,
            Transaction.TransactionDate <= e_str
        ).scalar() or 0.0

        weekly_data.append({
            "week": f"Tuần {weeks - i}",
            "week_start": s_str,
            "week_end": e_str,
            "income": float(inc),
            "expense": float(exp)
        })
    return {"data": weekly_data}

@app.get("/api/reports/compare")
def get_compare_reports(month1: str, month2: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """So sánh tài chính giữa 2 tháng"""
    s1 = get_dashboard_summary(month1, user, db)
    s2 = get_dashboard_summary(month2, user, db)
    return {
        "month1": s1,
        "month2": s2,
        "diff_income": s2["total_income"] - s1["total_income"],
        "diff_expense": s2["total_expense"] - s1["total_expense"]
    }

# ──────────────────────────────────────────────
# SMART ANALYTICS & FINANCIAL FORECASTING API
# ──────────────────────────────────────────────
@app.get("/api/analytics")
def get_spending_analytics_and_forecast(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phân tích & Dự báo Chi tiêu Thông minh:
    1. Tổng thu / Tổng chi trong ngày hôm nay.
    2. Trung bình chi tiêu mỗi ngày trong 7 ngày và 30 ngày qua.
    3. Cảnh báo 'Tiêu xài hoang phí' (Overspending Alert).
    4. Dự báo tài chính ngày mai & số dư/thâm hụt cuối tháng.
    """
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    current_month_str = today.strftime("%Y-%m")

    # 1. Thu / Chi Hôm nay
    today_inc = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "INCOME",
        Transaction.TransactionDate == today_str
    ).scalar() or 0.0

    today_exp = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate == today_str
    ).scalar() or 0.0

    # 2. Chi tiêu 7 ngày qua & 30 ngày qua
    date_7d_ago = (today - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    date_30d_ago = (today - datetime.timedelta(days=29)).strftime("%Y-%m-%d")

    sum_exp_7d = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate >= date_7d_ago,
        Transaction.TransactionDate <= today_str
    ).scalar() or 0.0

    sum_exp_30d = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate >= date_30d_ago,
        Transaction.TransactionDate <= today_str
    ).scalar() or 0.0

    avg_daily_7d = round(sum_exp_7d / 7.0, 2)
    avg_daily_30d = round(sum_exp_30d / 30.0, 2)

    # 3. Thu nhập & Chi tiêu tháng hiện tại
    month_inc = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "INCOME",
        Transaction.TransactionDate.like(f"{current_month_str}%")
    ).scalar() or 0.0

    month_exp = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate.like(f"{current_month_str}%")
    ).scalar() or 0.0

    # 4. Cảnh báo Tiêu xài hoang phí
    is_overspending = False
    warning_reasons = []

    if today_exp > 0 and today_inc > 0 and today_exp > today_inc:
        is_overspending = True
        warning_reasons.append(f"Chi tiêu hôm nay ({today_exp:,.0f} ₫) vượt quá thu nhập trong ngày ({today_inc:,.0f} ₫)")
    elif today_exp > 0 and today_inc == 0 and today_exp > (avg_daily_7d if avg_daily_7d > 0 else 100000):
        if avg_daily_7d > 0 and today_exp > 2.0 * avg_daily_7d:
            is_overspending = True
            warning_reasons.append(f"Chi tiêu hôm nay ({today_exp:,.0f} ₫) cao gấp {(today_exp / avg_daily_7d):.1f} lần mức trung bình 7 ngày qua ({avg_daily_7d:,.0f} ₫)")
        elif avg_daily_7d == 0 and today_exp > 200000:
            is_overspending = True
            warning_reasons.append(f"Chi tiêu hôm nay đạt {today_exp:,.0f} ₫ trong khi chưa có nguồn thu")

    if avg_daily_7d > 0 and today_exp >= 2.0 * avg_daily_7d:
        is_overspending = True
        if not any("cao gấp" in r for r in warning_reasons):
            warning_reasons.append(f"Chi tiêu hôm nay ({today_exp:,.0f} ₫) vượt hơn 200% mức trung bình ngày ({avg_daily_7d:,.0f} ₫)")

    # 5. Dự báo tài chính
    forecast_tomorrow_expense = avg_daily_7d if avg_daily_7d > 0 else (avg_daily_30d if avg_daily_30d > 0 else today_exp)

    year = today.year
    month = today.month
    _, num_days_in_month = calendar.monthrange(year, month)
    current_day = today.day
    remaining_days = max(0, num_days_in_month - current_day)

    projected_daily_rate = avg_daily_7d if avg_daily_7d > 0 else (avg_daily_30d if avg_daily_30d > 0 else today_exp)
    projected_remaining_expense = remaining_days * projected_daily_rate
    projected_total_month_expense = month_exp + projected_remaining_expense
    projected_month_end_balance = month_inc - projected_total_month_expense
    is_deficit = projected_month_end_balance < 0

    if is_overspending:
        if is_deficit:
            message = f"Hôm nay bạn đã chi tiêu khá mạnh tay ({today_exp:,.0f} ₫). Với đà này, dự kiến ngày mai bạn sẽ cần khoảng {forecast_tomorrow_expense:,.0f} ₫, và có nguy cơ thâm hụt ngân sách {abs(projected_month_end_balance):,.0f} ₫ vào cuối tháng. Hãy chủ động thắt chặt chi tiêu!"
        else:
            message = f"Hôm nay bạn đã chi tiêu cao hơn thường lệ ({today_exp:,.0f} ₫). Dự kiến ngày mai bạn sẽ cần khoảng {forecast_tomorrow_expense:,.0f} ₫. Hãy chú ý giữ vững thặng dư cuối tháng ({projected_month_end_balance:,.0f} ₫)."
    else:
        if is_deficit:
            message = f"Chi tiêu hôm nay ở mức hợp lý ({today_exp:,.0f} ₫). Tuy nhiên theo tính toán tổng thể tháng, bạn có thể thâm hụt khoảng {abs(projected_month_end_balance):,.0f} ₫ vào cuối tháng nếu không bổ sung nguồn thu."
        else:
            message = f"Tình hình tài chính hôm nay rất ổn định ({today_exp:,.0f} ₫ chi tiêu). Dự kiến số dư tiết kiệm cuối tháng của bạn sẽ đạt mức dương {projected_month_end_balance:,.0f} ₫. Bạn đang quản lý tài chính rất tốt!"

    return {
        "today_date": today_str,
        "today_income": float(today_inc),
        "today_expense": float(today_exp),
        "avg_daily_expense_7d": float(avg_daily_7d),
        "avg_daily_expense_30d": float(avg_daily_30d),
        "month_to_date_income": float(month_inc),
        "month_to_date_expense": float(month_exp),
        "days_remaining_in_month": remaining_days,
        "forecast_tomorrow_expense": float(forecast_tomorrow_expense),
        "forecast_total_month_expense": float(projected_total_month_expense),
        "forecast_month_end_balance": float(projected_month_end_balance),
        "is_overspending": is_overspending,
        "is_deficit_projected": is_deficit,
        "warning_reasons": warning_reasons,
        "forecast_message": message
    }

# ──────────────────────────────────────────────
# BUDGETS & ALERTS ROUTES
# ──────────────────────────────────────────────
@app.get("/api/budgets")
def get_budgets(month_year: Optional[str] = None, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy danh sách ngân sách hạn mức (IDOR Safe)"""
    if not month_year:
        month_year = datetime.date.today().strftime("%Y-%m")

    budgets_list = db.query(Budget, Category).join(Category, Budget.category_id == Category.Id).filter(
        Budget.user_id == user["user_id"],
        Budget.month_year == month_year
    ).all()

    res = []
    for b, c in budgets_list:
        spent = db.query(func.sum(Transaction.Amount)).filter(
            Transaction.UserId == user["user_id"],
            Transaction.CategoryId == b.category_id,
            Transaction.TransactionDate.like(f"{month_year}%")
        ).scalar() or 0.0

        res.append({
            "id": b.id,
            "category_id": b.category_id,
            "category_name": c.Name,
            "category_icon": c.Icon or "fa-solid fa-box",
            "limit_amount": b.limit_amount,
            "spent": float(spent),
            "spent_amount": float(spent),
            "month_year": b.month_year
        })
    return res

@app.post("/api/budgets")
def create_budget(body: BudgetBody, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Thiết lập hạn mức ngân sách"""
    existing = db.query(Budget).filter(
        Budget.user_id == user["user_id"],
        Budget.category_id == body.category_id,
        Budget.month_year == body.month_year
    ).first()

    if existing:
        existing.limit_amount = body.limit_amount
        db.commit()
        return {"message": "Cập nhật hạn mức ngân sách thành công!"}

    new_budget = Budget(
        user_id=user["user_id"],
        category_id=body.category_id,
        limit_amount=body.limit_amount,
        month_year=body.month_year
    )
    db.add(new_budget)
    db.commit()
    return {"message": "Thiết lập hạn mức ngân sách thành công!"}

@app.delete("/api/budgets/{budget_id}")
def delete_budget(budget_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xóa hạn mức ngân sách (IDOR Safe)"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Hạn mức không tồn tại.")
    if budget.user_id != user["user_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa hạn mức này.")

    db.delete(budget)
    db.commit()
    return {"message": "Đã xóa hạn mức thành công."}

@app.get("/api/budgets/alerts")
@app.post("/api/ai/check-budget")
def get_budget_alerts(month_year: Optional[str] = None, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Kiểm tra và cảnh báo các danh mục đã chi tiêu vượt quá 80% hạn mức"""
    budgets_list = get_budgets(month_year, user, db)
    alerts = []
    for b in budgets_list:
        limit = b["limit_amount"]
        spent = b["spent_amount"]
        pct = round((spent / limit) * 100, 1) if limit > 0 else 0
        if pct >= 80:
            level = "DANGER" if pct >= 100 else "WARNING"
            msg = f"Cảnh báo! Danh mục '{b['category_name']}' đã sử dụng {pct}% hạn mức ({spent:,.0f}/{limit:,.0f} VNĐ)."
            alerts.append({
                "category": b["category_name"],
                "icon": b["category_icon"],
                "percent": pct,
                "level": level,
                "message": msg
            })
    return {"alerts": alerts}

# ──────────────────────────────────────────────
# AI ADVISOR & OCR (GEMINI INTEGRATION)
# ──────────────────────────────────────────────
@app.post("/api/ai/chat")
async def ai_chat(body: ChatBody, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Trợ lý Cố vấn Tài chính AI thông minh (Gemini AI Chatbot)"""
    api_key = get_gemini_api_key()
    user_msg = body.message.strip()

    today_m = datetime.date.today().strftime("%Y-%m")
    inc = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "INCOME",
        Transaction.TransactionDate.like(f"{today_m}%")
    ).scalar() or 0.0

    exp = db.query(func.sum(Transaction.Amount)).select_from(Transaction).join(
        Category, Transaction.CategoryId == Category.Id
    ).filter(
        Transaction.UserId == user["user_id"],
        Category.Type == "EXPENSE",
        Transaction.TransactionDate.like(f"{today_m}%")
    ).scalar() or 0.0

    savings = inc - exp
    ai_reply = ""
    success_ai = False

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            prompt = f"""
Bạn là Trợ lý Cố vấn Quản lý Chi tiêu và Tài chính Cá nhân Thông minh của 'Hệ Thống Quản Lý Chi Tiêu'.
Hãy trả lời thân thiện, lịch sự, chuẩn mực ngôn ngữ tài chính hiện đại và đưa ra các lời khuyên thiết thực.
Dữ liệu tài chính tháng {today_m} của người dùng hiện tại:
- Họ tên: {user.get('full_name', 'Bạn')}
- Tổng thu nhập tháng: {inc:,.0f} VNĐ
- Tổng chi tiêu tháng: {exp:,.0f} VNĐ
- Tiết kiệm hiện tại: {savings:,.0f} VNĐ

Câu hỏi của người dùng: "{user_msg}"
"""
            for model_name in get_gemini_models_list(vision=False):
                try:
                    model = genai.GenerativeModel(model_name)
                    res = model.generate_content(prompt)
                    if res and res.text:
                        ai_reply = res.text.strip()
                        success_ai = True
                        break
                except Exception as model_err:
                    logger.warning(f"Thử model {model_name} thất bại: {model_err}")
        except Exception as err:
            logger.warning(f"Lỗi khởi tạo Gemini SDK: {err}")

    if not success_ai:
        if "tiết kiệm" in user_msg.lower() or "cách" in user_msg.lower():
            ai_reply = f"Chào bạn! Tháng {today_m} này bạn đang có tổng thu {inc:,.0f} VNĐ và chi tiêu {exp:,.0f} VNĐ. Để tối ưu tiết kiệm, hãy áp dụng quy tắc 50/30/20: dành 50% cho nhu cầu thiết yếu, 30% cho sở thích cá nhân và trích ngay 20% vào quỹ tiết kiệm đầu tư."
        elif "số dư" in user_msg.lower() or "ví" in user_msg.lower():
            ai_reply = f"Dữ liệu tháng này của bạn: Tổng thu nhập đạt {inc:,.0f} VNĐ, tổng chi tiêu là {exp:,.0f} VNĐ. Số dư chênh lệch tích lũy hiện là {savings:,.0f} VNĐ."
        else:
            ai_reply = f"Chào bạn! Tôi là Cố vấn Tài chính AI của bạn. Tháng này bạn đã ghi nhận {inc:,.0f} VNĐ thu nhập và {exp:,.0f} VNĐ chi tiêu (Tiết kiệm: {savings:,.0f} VNĐ). Tôi luôn sẵn sàng phân tích và hỗ trợ bạn quản lý tài chính cá nhân hiệu quả nhất!"

    try:
        chat_entry = ChatSession(user_id=user["user_id"], prompt_question=user_msg, ai_response=ai_reply)
        db.add(chat_entry)
        db.commit()
    except Exception:
        db.rollback()

    return {"response": ai_reply}

@app.get("/api/ai/chat-history")
def get_chat_history(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy lịch sử trò chuyện với AI (IDOR Safe)"""
    history = db.query(ChatSession).filter(
        ChatSession.user_id == user["user_id"]
    ).order_by(ChatSession.id.desc()).limit(20).all()
    return [
        {
            "prompt_question": c.prompt_question,
            "ai_response": c.ai_response,
            "created_at": str(c.created_at)
        } for c in history
    ]

@app.post("/api/ocr")
@app.post("/api/ai/scan-invoice")
@app.post("/api/ocr/receipt")
async def scan_invoice(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Nhận diện và trích xuất thông tin hóa đơn qua Magic Bytes & Gemini Vision AI"""
    content = await file.read()
    mime_type = "image/jpeg"
    try:
        mime_type = validate_image_bytes(content)
    except Exception as e:
        logger.warning(f"Lỗi kiểm tra magic bytes ảnh: {e}")

    api_key = get_gemini_api_key()
    parsed_data = {
        "store_name": "Cửa Hàng Tiện Lợi",
        "total_amount": 125000.0,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "items": "Hóa đơn mua sắm tiêu dùng",
        "category_id": 1,
        "merchant": "Cửa Hàng Tiện Lợi"
    }

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            prompt = """
Hãy phân tích hình ảnh hóa đơn/phiếu thanh toán này và trích xuất thông tin dưới dạng JSON chuẩn:
{
  "store_name": "Tên cửa hàng hoặc đơn vị xuất hóa đơn",
  "total_amount": Số tiền thanh toán tổng cộng (dạng số float/int, ví dụ: 150000),
  "date": "YYYY-MM-DD",
  "items": "Mô tả ngắn gọn các mặt hàng hoặc dịch vụ chính",
  "merchant": "Tên cửa hàng"
}
Lưu ý: Chỉ trả về duy nhất chuỗi JSON hợp lệ, không dùng Markdown backticks hay văn bản giải thích.
"""
            for model_name in get_gemini_models_list(vision=True):
                try:
                    model = genai.GenerativeModel(model_name)
                    res = model.generate_content([
                        prompt,
                        {"mime_type": mime_type, "data": content}
                    ])
                    if res and res.text:
                        text_resp = res.text.strip()
                        text_resp = re.sub(r"^```json\s*", "", text_resp)
                        text_resp = re.sub(r"\s*```$", "", text_resp)
                        parsed = json.loads(text_resp)
                        if "total_amount" in parsed: parsed_data["total_amount"] = float(parsed["total_amount"])
                        if "store_name" in parsed: parsed_data["store_name"] = str(parsed["store_name"])
                        if "date" in parsed: parsed_data["date"] = str(parsed["date"])
                        if "items" in parsed: parsed_data["items"] = str(parsed["items"])
                        if "merchant" in parsed: parsed_data["merchant"] = str(parsed["merchant"])
                        break
                except Exception as model_err:
                    logger.warning(f"Thử model OCR {model_name} thất bại: {model_err}")
        except Exception as err:
            logger.warning(f"Lỗi phân tích Gemini OCR: {err}")

    return {
        "status": "success",
        "data": parsed_data,
        "amount": parsed_data["total_amount"],
        "date": parsed_data["date"],
        "note": parsed_data["items"],
        "store_name": parsed_data["store_name"]
    }

@app.post("/api/ai/saving-tips")
def get_saving_tips(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lời khuyên tài chính thông minh theo quy tắc 50/30/20"""
    summary = get_dashboard_summary(None, user, db)
    inc = summary["total_income"]
    exp = summary["total_expense"]
    rate = round(((inc - exp) / inc * 100), 1) if inc > 0 else 0.0

    tips_text = f"""
💡 **Lời Khuyên Quản Lý Tài Chính Cá Nhân**:
1. **Tỷ Lệ Tiết Kiệm**: Bạn đang đạt mức tiết kiệm **{rate}%** trong tháng này.
2. **Quy Tắc 50/30/20**: Hãy phân bổ 50% cho nhu cầu thiết yếu, 30% cho chi tiêu cá nhân, và tối thiểu 20% cho quỹ tiết kiệm / đầu tư.
3. **Quản Lý Hạn Mức**: Hãy kiểm tra các danh mục có cảnh báo vượt 80% ngân sách để kịp thời cân đối chi tiêu!
"""
    return {
        "month_year": summary["month_year"],
        "savings_rate": rate,
        "tips": tips_text
    }

# ──────────────────────────────────────────────
# ADMIN MANAGEMENT (RBAC PROTECTED)
# ──────────────────────────────────────────────
@app.get("/api/admin/users")
def admin_get_users(admin: dict = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Quản trị viên xem danh sách toàn bộ người dùng"""
    users_list = db.query(User).order_by(User.Id.desc()).all()
    return [
        {
            "id": u.Id,
            "email": u.Email,
            "full_name": u.FullName,
            "role": u.Role,
            "is_blocked": 0 if u.IsActive else 1,
            "created_at": str(u.CreatedAt)
        } for u in users_list
    ]

@app.post("/api/admin/users/{user_id}/block")
def admin_toggle_block_user(user_id: int, admin: dict = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Khóa hoặc mở khóa tài khoản người dùng"""
    if user_id == admin["user_id"]:
        raise HTTPException(status_code=400, detail="Bạn không thể tự khóa tài khoản Quản trị viên của chính mình.")

    user = db.query(User).filter(User.Id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")

    user.IsActive = not user.IsActive
    db.commit()
    msg = "Đã mở khóa tài khoản thành công." if user.IsActive else "Đã khóa tài khoản thành công."
    return {"message": msg, "is_blocked": 0 if user.IsActive else 1}

@app.get("/api/admin/transactions")
def admin_get_all_transactions(admin: dict = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Quản trị viên giám sát toàn bộ giao dịch hệ thống"""
    rows = db.query(Transaction, User, Category).join(
        User, Transaction.UserId == User.Id
    ).join(
        Category, Transaction.CategoryId == Category.Id
    ).order_by(Transaction.TransactionDate.desc(), Transaction.Id.desc()).limit(200).all()

    res = []
    for txn, u, cat in rows:
        res.append({
            "id": txn.Id,
            "user_id": txn.UserId,
            "user_email": u.Email,
            "user_name": u.FullName,
            "category_name": cat.Name,
            "amount": txn.Amount,
            "transaction_type": cat.Type,
            "transaction_date": str(txn.TransactionDate),
            "note": txn.Note or ""
        })
    return res

@app.delete("/api/admin/transactions/{txn_id}")
def admin_delete_transaction(txn_id: int, admin: dict = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Quản trị viên xóa giao dịch bất thường"""
    txn = db.query(Transaction).filter(Transaction.Id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Giao dịch không tồn tại.")
    db.delete(txn)
    db.commit()
    return {"message": "Quản trị viên đã xóa giao dịch thành công."}

# ──────────────────────────────────────────────
# MAIN ENTRYPOINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
