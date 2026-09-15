"""
Script Reset Toàn Bộ Dữ Liệu Mẫu (Clean Sample Data Reset)
Dự án: Càn Khôn Linh Thạch Các — Hệ Thống Quản Lý Chi Tiêu AI
"""

import os
import sys
import sqlite3
import shutil
import datetime
import bcrypt

# Đảm bảo mã hóa UTF-8 cho console Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_PATH = "app.db"
BACKUP_PATH = "app.db.before_reset.bak"

def run_reset():
    print("=" * 70)
    print("🔄 BẮT ĐẦU QUY TRÌNH RESET DỮ LIỆU MẪU SẠCH (CLEAN RESET)")
    print("=" * 70)

    # 1. KIỂM TRA FILE DATABASE & TẠO BACKUP
    if not os.path.exists(DB_PATH):
        print(f"❌ LỖI NGHIÊM TRỌNG: Không tìm thấy file cơ sở dữ liệu '{DB_PATH}'. Dừng reset!")
        sys.exit(1)

    try:
        shutil.copyfile(DB_PATH, BACKUP_PATH)
        print(f"✅ BƯỚC 1: Đã tạo bản sao lưu an toàn -> '{BACKUP_PATH}'")
    except Exception as e:
        print(f"❌ LỖI NGHIÊM TRỌNG: Tạo file backup thất bại ({e}). Dừng ngay để bảo vệ dữ liệu!")
        sys.exit(1)

    # 2. THỰC THI RESET TRONG 1 ATOMIC SQL TRANSACTION
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = conn.cursor()
        print("\n🗑️  BƯỚC 2: Xóa dữ liệu cũ theo đúng thứ tự ràng buộc Foreign Key...")

        # Danh sách các bảng cần xóa dữ liệu mẫu theo thứ tự an toàn
        tables_to_clear = [
            "transactions",
            "recurring_transactions",
            "debts",
            "saving_goals",
            "budgets",
            "invoice_ocr_logs",
            "chat_sessions",
            "password_reset_tokens",
            "categories",
            "wallets",
            "users"
        ]

        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table}")

        # Reset sequence AUTOINCREMENT trong sqlite_sequence
        cursor.execute("DELETE FROM sqlite_sequence")
        print("  -> Đã xóa toàn bộ dữ liệu cũ và reset AUTOINCREMENT ID về 1.")

        print("\n🌱 BƯỚC 3: Tạo tài khoản Admin và User demo...")
        # Hash mật khẩu an toàn theo bcrypt chuẩn project
        admin_pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        admin_soul_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode()
        
        user_pw_hash = bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode()
        user_soul_hash = bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode()

        cursor.execute("""
            INSERT INTO users (id, email, password_hash, full_name, soul_lamp_hash, role, is_active)
            VALUES (1, 'admin@gmail.com', ?, 'Ký Chủ', ?, 'admin', 1)
        """, (admin_pw_hash, admin_soul_hash))

        cursor.execute("""
            INSERT INTO users (id, email, password_hash, full_name, soul_lamp_hash, role, is_active)
            VALUES (2, 'user@gmail.com', ?, 'Đạo Hữu User', ?, 'user', 1)
        """, (user_pw_hash, user_soul_hash))

        print("  -> Admin: admin@gmail.com | Password: admin123 | Role: admin (ID: 1)")
        print("  -> User:  user@gmail.com  | Password: user123  | Role: user  (ID: 2)")

        print("\n💳 BƯỚC 4: Khởi tạo danh sách Ví Linh Thạch mẫu...")
        # Admin: Đúng 3 ví chính
        # Initial balances: Cash = 5M, Vietcombank = 15M, Momo = 20M
        admin_wallets = [
            (1, 1, "Linh Thạch Tiền Mặt", 5000000.0, "cash"),
            (2, 1, "Linh Mạch Vietcombank", 15000000.0, "bank"),
            (3, 1, "Túi Momo", 20000000.0, "e-wallet"),
        ]
        user_wallets = [
            (4, 2, "Linh Thạch Tiền Mặt", 3000000.0, "cash"),
            (5, 2, "Linh Mạch Vietcombank", 10000000.0, "bank"),
            (6, 2, "Túi Momo", 2000000.0, "e-wallet"),
        ]
        cursor.executemany("INSERT INTO wallets (id, user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?, ?)", admin_wallets + user_wallets)
        print("  -> Admin có đúng 3 ví (Cash: 5M, Vietcombank: 15M, Momo: 20M).")
        print("  -> User demo có đúng 3 ví (Cash: 3M, Vietcombank: 10M, Momo: 2M).")

        print("\n🏷️  BƯỚC 5: Khởi tạo Danh mục Thu/Chi...")
        admin_cats = [
            (1, 1, "Ẩm Thực Linh Đan", "EXPENSE", "🍕"),
            (2, 1, "Pháp Khí Mua Sắm", "EXPENSE", "🛍️"),
            (3, 1, "Phi Kiếm Di Chuyển", "EXPENSE", "🚗"),
            (4, 1, "Linh Thạch Lương Bổng", "INCOME", "💵"),
            (5, 1, "Quà Tặng Đạo Hữu", "INCOME", "🎁"),
            (6, 1, "Tu Luyện Hóa Đơn", "EXPENSE", "⚡"),
        ]
        user_cats = [
            (7, 2, "Ẩm Thực Linh Đan", "EXPENSE", "🍕"),
            (8, 2, "Pháp Khí Mua Sắm", "EXPENSE", "🛍️"),
            (9, 2, "Phi Kiếm Di Chuyển", "EXPENSE", "🚗"),
            (10, 2, "Linh Thạch Lương Bổng", "INCOME", "💵"),
            (11, 2, "Quà Tặng Đạo Hữu", "INCOME", "🎁"),
        ]
        cursor.executemany("INSERT INTO categories (id, user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?, ?)", admin_cats + user_cats)

        print("\n💸 BƯỚC 6: Tạo 25 giao dịch thực tế cho Admin & 5 giao dịch cho User...")
        today = datetime.date.today()
        
        # 25 giao dịch Admin
        # Wallet 1 (Cash - Initial 5M): 6 EXPENSES (1.325M), 2 INCOMES (3M) -> Net: +1.675M -> Final Bal: 6.675M
        # Wallet 2 (Bank - Initial 15M): 7 EXPENSES (5.2M), 3 INCOMES (40M) -> Net: +34.8M -> Final Bal: 49.8M
        # Wallet 3 (Momo - Initial 20M): 5 EXPENSES (1.25M), 2 INCOMES (4.5M) -> Net: +3.25M -> Final Bal: 23.25M
        admin_txs = [
            # Wallet 1 (Cash)
            (1, 1, 1, 150000.0, "EXPENSE", str(today - datetime.timedelta(days=1)), "Mua linh đan phở bò gia truyền"),
            (1, 1, 1, 85000.0, "EXPENSE", str(today - datetime.timedelta(days=2)), "Cơm trưa Linh Đan quán"),
            (1, 1, 1, 220000.0, "EXPENSE", str(today - datetime.timedelta(days=3)), "Mua đạn dược y tế cảm cúm"),
            (1, 1, 1, 120000.0, "EXPENSE", str(today - datetime.timedelta(days=4)), "Uống linh trà chiều với đồng môn"),
            (1, 1, 2, 300000.0, "EXPENSE", str(today - datetime.timedelta(days=5)), "Mua nến thơm tu luyện"),
            (1, 1, 1, 450000.0, "EXPENSE", str(today - datetime.timedelta(days=6)), "Ăn lẩu linh miêu cuối tuần"),
            (1, 1, 5, 2000000.0, "INCOME", str(today - datetime.timedelta(days=7)), "Bán đan dược tự chế"),
            (1, 1, 4, 1000000.0, "INCOME", str(today - datetime.timedelta(days=8)), "Trợ cấp sinh hoạt tông môn"),

            # Wallet 2 (Vietcombank)
            (1, 2, 4, 20000000.0, "INCOME", str(today - datetime.timedelta(days=1)), "Lương tháng 8 từ Tông Môn"),
            (1, 2, 4, 15000000.0, "INCOME", str(today - datetime.timedelta(days=10)), "Thưởng dự án Trận Pháp Khí"),
            (1, 2, 4, 5000000.0, "INCOME", str(today - datetime.timedelta(days=15)), "Tiền làm thêm Trợ Giảng"),
            (1, 2, 2, 1200000.0, "EXPENSE", str(today - datetime.timedelta(days=2)), "Pháp bảo tai nghe không dây"),
            (1, 2, 2, 500000.0, "EXPENSE", str(today - datetime.timedelta(days=4)), "Mua pháp khí trang phục mới"),
            (1, 2, 6, 350000.0, "EXPENSE", str(today - datetime.timedelta(days=5)), "Thanh toán mạng linh cáp Internet"),
            (1, 2, 6, 800000.0, "EXPENSE", str(today - datetime.timedelta(days=7)), "Nộp linh thạch điện nước tháng này"),
            (1, 2, 6, 250000.0, "EXPENSE", str(today - datetime.timedelta(days=9)), "Nạp tiền điện thoại Viettel"),
            (1, 2, 1, 1500000.0, "EXPENSE", str(today - datetime.timedelta(days=11)), "Mua linh dược dưỡng nhan"),
            (1, 2, 2, 600000.0, "EXPENSE", str(today - datetime.timedelta(days=13)), "Đăng ký khóa học Linh Trận"),

            # Wallet 3 (Momo)
            (1, 3, 5, 3000000.0, "INCOME", str(today - datetime.timedelta(days=3)), "Nhận tiền chuyển khoản bạn bè"),
            (1, 3, 5, 1500000.0, "INCOME", str(today - datetime.timedelta(days=9)), "Linh thạch lì xì sinh nhật"),
            (1, 3, 3, 200000.0, "EXPENSE", str(today - datetime.timedelta(days=1)), "Phi kiếm Grab đi làm"),
            (1, 3, 2, 180000.0, "EXPENSE", str(today - datetime.timedelta(days=3)), "Xem phim rạp Cinema Xianxia"),
            (1, 3, 1, 320000.0, "EXPENSE", str(today - datetime.timedelta(days=6)), "Đặt trà sữa ShopeeFood"),
            (1, 3, 6, 150000.0, "EXPENSE", str(today - datetime.timedelta(days=8)), "Thanh toán ví trả sau Momo"),
            (1, 3, 2, 400000.0, "EXPENSE", str(today - datetime.timedelta(days=12)), "Mua sách Linh Thư Các"),
        ]

        # 5 giao dịch User Demo (user_id = 2)
        user_txs = [
            (2, 4, 7, 100000.0, "EXPENSE", str(today - datetime.timedelta(days=1)), "Cơm trưa bình dân"),
            (2, 4, 9, 20000.0, "EXPENSE", str(today - datetime.timedelta(days=2)), "Gửi xe máy"),
            (2, 5, 10, 15000000.0, "INCOME", str(today - datetime.timedelta(days=5)), "Lương công ty"),
            (2, 5, 8, 1000000.0, "EXPENSE", str(today - datetime.timedelta(days=3)), "Mua quần áo mới"),
            (2, 6, 7, 150000.0, "EXPENSE", str(today - datetime.timedelta(days=4)), "Nạp thẻ game"),
        ]

        cursor.executemany("""
            INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, admin_txs + user_txs)

        print("\n📊 BƯỚC 7: Cập nhật chính xác số dư ví theo công thức toán học...")
        # Công thức: Balance = Initial Balance + Sum(INCOME) - Sum(EXPENSE)
        initial_map = {
            1: 5000000.0,
            2: 15000000.0,
            3: 20000000.0,
            4: 3000000.0,
            5: 10000000.0,
            6: 2000000.0,
        }
        all_wallets = cursor.execute("SELECT id, user_id, wallet_name FROM wallets").fetchall()
        for w in all_wallets:
            wid = w["id"]
            init_bal = initial_map.get(wid, 0.0)
            inc = cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE wallet_id = ? AND transaction_type = 'INCOME'", (wid,)).fetchone()[0]
            exp = cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE wallet_id = ? AND transaction_type = 'EXPENSE'", (wid,)).fetchone()[0]
            
            calc_bal = init_bal + inc - exp
            cursor.execute("UPDATE wallets SET balance = ? WHERE id = ?", (calc_bal, wid))
            print(f"  -> Ví ID {wid} ({w['wallet_name']}): Số dư chuẩn = {calc_bal:,.0f}đ (Gốc={init_bal:,.0f}đ, Thu={inc:,.0f}đ, Chi={exp:,.0f}đ)")

        print("\n📌 BƯỚC 8: Khởi tạo dữ liệu mẫu cho các bảng phụ thuộc...")
        # Budgets
        cur_month = today.strftime("%Y-%m")
        cursor.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (1, 1, 3000000.0, ?)", (cur_month,))
        cursor.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (1, 2, 5000000.0, ?)", (cur_month,))

        # Saving Goals
        cursor.execute("""
            INSERT INTO saving_goals (user_id, target_name, target_amount, current_amount, target_date, icon, is_completed)
            VALUES (1, 'Mua Linh Bảo Laptop', 30000000.0, 10000000.0, '2026-12-31', '🎯', 0)
        """)

        # Recurring Transactions
        next_m = (today + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note, is_active)
            VALUES (1, 2, 6, 500000.0, 'EXPENSE', 'monthly', ?, 'Tự động đóng linh thạch Internet', 1)
        """, (next_m,))

        # Debts
        cursor.execute("""
            INSERT INTO debts (user_id, wallet_id, debt_type, person_name, amount, due_date, is_settled, note)
            VALUES (1, 1, 'BORROW', 'Hàn Lập', 1000000.0, '2026-10-01', 0, 'Mượn mua thêm đan dược')
        """)

        # Commit toàn bộ transaction
        conn.commit()
        print("\n💾 ĐÃ COMMIT DỮ LIỆU THÀNH CÔNG VÀO DATABASE!")

    except Exception as err:
        conn.rollback()
        conn.close()
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH RESET: {err}")
        print("  -> Đã thực hiện ROLLBACK transaction. Dữ liệu chưa bị thay đổi!")
        sys.exit(1)

    # 4. KIỂM TRA & TỰ ĐỘNG ĐÁNH GIÁ INTEGRITY SAU RESET
    print("\n" + "=" * 70)
    print("🔍 BƯỚC 9: KIỂM TRA INTEGRITY & ĐÁNH GIÁ CHẤT LƯỢNG DỮ LIỆU MỚI")
    print("=" * 70)

    test_results = {}

    # Check Admin
    admin_row = cursor.execute("SELECT id, email, role FROM users WHERE email = 'admin@gmail.com'").fetchone()
    test_results["Admin login"] = "PASS" if (admin_row and admin_row["role"] == "admin" and admin_row["id"] == 1) else "FAIL"

    # Check Wallet count
    admin_wallets_count = cursor.execute("SELECT COUNT(*) FROM wallets WHERE user_id = 1").fetchone()[0]
    test_results["Wallet count"] = "PASS" if admin_wallets_count == 3 else "FAIL"

    # Check Duplicates
    dup_wallets = cursor.execute("SELECT user_id, wallet_name, COUNT(*) FROM wallets GROUP BY user_id, wallet_name HAVING COUNT(*) > 1").fetchall()
    dup_users = cursor.execute("SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1").fetchall()
    test_results["Duplicate seed test"] = "PASS" if (len(dup_wallets) == 0 and len(dup_users) == 0) else "FAIL"

    # Check Transactions
    admin_tx_count = cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 1").fetchone()[0]
    test_results["Transaction integrity"] = "PASS" if (20 <= admin_tx_count <= 30) else "FAIL"

    # Check Foreign Keys
    orphan_tx = cursor.execute("""
        SELECT COUNT(*) FROM transactions t
        LEFT JOIN users u ON t.user_id = u.id
        LEFT JOIN wallets w ON t.wallet_id = w.id
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE u.id IS NULL OR w.id IS NULL OR c.id IS NULL
    """).fetchone()[0]
    test_results["Foreign key integrity"] = "PASS" if orphan_tx == 0 else "FAIL"

    # Check Balance Calculation Accuracy
    balance_discrepancy = False
    for w in cursor.execute("SELECT id, balance FROM wallets").fetchall():
        wid = w["id"]
        stored_bal = w["balance"]
        init_b = initial_map.get(wid, 0.0)
        inc = cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE wallet_id = ? AND transaction_type = 'INCOME'", (wid,)).fetchone()[0]
        exp = cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE wallet_id = ? AND transaction_type = 'EXPENSE'", (wid,)).fetchone()[0]
        calc_b = init_b + inc - exp
        if abs(stored_bal - calc_b) > 0.01:
            balance_discrepancy = True
            print(f"❌ Discrepancy in Wallet {wid}: Stored={stored_bal}, Calc={calc_b}")

    test_results["Balance integrity"] = "PASS" if not balance_discrepancy else "FAIL"

    conn.close()

    # Summarize final test status
    all_pass = all(val == "PASS" for val in test_results.values())
    final_status = "RESET SUCCESSFUL" if all_pass else "RESET FAILED"

    print("\n--- KẾT QUẢ KIỂM THỬ TỰ ĐỘNG ---")
    for k, v in test_results.items():
        print(f"  [{v}] {k}")

    print(f"\n👉 KẾT LUẬN CUỐI CÙNG: {final_status}")
    print("=" * 70)

if __name__ == "__main__":
    run_reset()
