"""
Tạo lại dữ liệu mẫu cho RIÊNG tài khoản admin (persona: sinh viên).
Dự án: Càn Khôn Linh Thạch Các

- Giữ nguyên dòng users của admin (mật khẩu, Hồn Đăng, vai trò), lịch sử chat, OCR log,
  Danh Bạ Hộ Đạo và cài đặt cảnh báo.
- Xóa rồi tạo lại: ví, danh mục, giao dịch, hạn mức, giao dịch định kỳ, sổ nợ, mục tiêu.
- Không đụng tới tài khoản khác.
- Dữ liệu trải từ đầu tháng (T-2) tới hôm nay, tính theo ngày chạy script, cố định (seed)
  nên chạy cùng ngày luôn ra cùng kết quả.
- Số dư ví = số dư đầu kỳ + tổng thu − tổng chi, không ví nào bị âm ở bất kỳ thời điểm nào.

Chạy:  python scripts/seed_admin_demo.py            (ghi vào app.db, có backup)
       python scripts/seed_admin_demo.py --dry-run  (chỉ in kết quả, không ghi)
"""

import argparse
import calendar
import datetime
import os
import random
import shutil
import sqlite3
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(ROOT, "app.db")

WALLETS = [  # key, tên, loại, số dư đầu kỳ
    ("cash", "Linh Thạch Tiền Mặt", "cash", 600000),
    ("bank", "Linh Mạch Vietcombank", "bank", 1500000),
    ("momo", "Túi Momo", "e-wallet", 400000),
]

CATEGORIES = [  # key, tên, loại, icon
    ("food", "Ẩm Thực Linh Đan", "EXPENSE", "🍜"),
    ("move", "Phi Kiếm Di Chuyển", "EXPENSE", "🛵"),
    ("rent", "Động Phủ Thuê Trọ", "EXPENSE", "🏠"),
    ("bill", "Tu Luyện Hóa Đơn", "EXPENSE", "⚡"),
    ("study", "Tàng Kinh Các Học Tập", "EXPENSE", "📚"),
    ("shop", "Pháp Khí Mua Sắm", "EXPENSE", "🛍️"),
    ("fun", "Tiêu Dao Giải Trí", "EXPENSE", "🎮"),
    ("health", "Y Dược Đan Phòng", "EXPENSE", "💊"),
    ("goal", "Mục Tiêu Tiết Kiệm", "EXPENSE", "🎯"),  # trùng tên danh mục hệ thống của API nạp mục tiêu
    ("family", "Gia Tộc Chu Cấp", "INCOME", "👨‍👩‍👧"),
    ("job", "Linh Thạch Làm Thêm", "INCOME", "💼"),
    ("gift", "Quà Tặng Đạo Hữu", "INCOME", "🎁"),
]

FOOD_NOTES = [
    "Bánh mì linh đan buổi sáng", "Cơm tấm căng tin", "Bún bò gần trường",
    "Phở bò buổi trưa", "Cơm gà xối mỡ", "Mì cay với đồng môn", "Cơm văn phòng",
    "Xôi gà buổi sáng", "Bánh cuốn nóng", "Hủ tiếu Nam Vang",
]
EXTRA_FOOD_NOTES = ["Trà sữa linh châu", "Cà phê ôn bài", "Đi chợ mua đồ nấu ăn", "Trà chanh với bạn"]


def month_start(d: datetime.date, back: int) -> datetime.date:
    y, m = d.year, d.month - back
    while m <= 0:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return datetime.date(y, m, 1)


def round_k(x: float) -> int:
    return int(round(x / 1000.0)) * 1000


def build_plan(today: datetime.date):
    """Sinh danh sách giao dịch (ngày, ví, danh mục, số tiền, loại, ghi chú) + dữ liệu phụ."""
    rng = random.Random(today.toordinal())
    start = month_start(today, 2)
    txs = []

    def add(day, wallet, cat, amount, ttype, note):
        txs.append((day, wallet, cat, int(amount), ttype, note))

    d = start
    while d <= today:
        last_day = calendar.monthrange(d.year, d.month)[1]
        mlabel = f"tháng {d.month}"
        # Thu nhập cố định
        if d.day == 1:
            add(d, "bank", "family", 5000000, "INCOME", f"Bố mẹ gửi tiền sinh hoạt {mlabel}")
        if d.day == 10:
            add(d, "momo", "job", 1800000, "INCOME", f"Lương làm thêm quán cà phê {mlabel}")
        # Chi cố định
        if d.day == 2:
            add(d, "bank", "rent", 1800000, "EXPENSE", f"Tiền phòng trọ {mlabel}")
        if d.day == 5:
            add(d, "bank", "bill", round_k(rng.uniform(210000, 290000)), "EXPENSE", f"Tiền điện nước {mlabel}")
        if d.day == 15:
            add(d, "momo", "bill", 120000, "EXPENSE", "Gia hạn gói cước 4G")
        if d.day == 20:
            add(d, "bank", "goal", 300000, "EXPENSE", "Tích lũy mục tiêu: Mua laptop học tập")
        # Ăn uống hằng ngày
        add(d, "cash", "food", round_k(rng.uniform(30000, 65000)), "EXPENSE", rng.choice(FOOD_NOTES))
        if rng.random() < 0.55:
            add(d, "momo", "food", round_k(rng.uniform(25000, 70000)), "EXPENSE", rng.choice(EXTRA_FOOD_NOTES))
        # Đi lại
        if d.day % 4 == 0:
            add(d, "cash", "move", round_k(rng.uniform(50000, 80000)), "EXPENSE", "Đổ xăng xe máy")
        elif rng.random() < 0.12:
            add(d, "momo", "move", round_k(rng.uniform(25000, 60000)), "EXPENSE", "Đặt Grab đi học")
        # Cuối tuần giải trí
        if d.weekday() == 5 and rng.random() < 0.7:
            add(d, "momo", "fun", round_k(rng.uniform(60000, 120000)), "EXPENSE",
                rng.choice(["Xem phim cuối tuần", "Đi hát karaoke với lớp", "Nạp game giải trí"]))
        # Học tập / mua sắm / sức khỏe: vài lần mỗi tháng
        if d.day in (7, 22):
            add(d, "cash", "study", round_k(rng.uniform(30000, 90000)), "EXPENSE", "Photo tài liệu, mua bút vở")
        if d.day == 12:
            add(d, "bank", "study", round_k(rng.uniform(120000, 220000)), "EXPENSE", "Mua giáo trình môn chuyên ngành")
        if d.day == 18:
            add(d, "momo", "shop", round_k(rng.uniform(150000, 350000)), "EXPENSE",
                rng.choice(["Mua áo thun mới", "Mua tai nghe", "Mua đồ dùng phòng trọ"]))
        if d.day == 25 and d.month % 2 == 0:
            add(d, "cash", "health", round_k(rng.uniform(60000, 150000)), "EXPENSE", "Mua thuốc cảm cúm")
        if d.day == last_day and d.month % 2 == 1:
            add(d, "momo", "gift", 300000, "INCOME", "Bạn bè gửi quà sinh nhật")
        d += datetime.timedelta(days=1)

    return start, txs


def simulate_balances(txs):
    """Giữ ví không bao giờ âm: nếu ví dự định không đủ tiền thì chuyển khoản chi sang ví khác đủ tiền."""
    bal = {k: v for k, _, _, v in WALLETS}
    out = []
    for day, wallet, cat, amount, ttype, note in sorted(txs, key=lambda t: (t[0], t[4] != "INCOME")):
        if ttype == "EXPENSE" and bal[wallet] < amount:
            alt = [w for w in ("momo", "bank", "cash") if bal[w] >= amount]
            if not alt:
                continue  # thực tế sinh viên sẽ không chi được khoản này
            wallet = alt[0]
        bal[wallet] += amount if ttype == "INCOME" else -amount
        out.append((day, wallet, cat, amount, ttype, note))
    return out, bal


def seed(db_path: str, email: str, dry_run: bool, today: datetime.date):
    if not os.path.exists(db_path):
        sys.exit(f"Không tìm thấy database: {db_path}")

    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    admin = conn.execute("SELECT id, email FROM users WHERE email = ?", (email,)).fetchone()
    if not admin:
        sys.exit(f"Không tìm thấy tài khoản {email}")
    uid = admin["id"]

    start, raw = build_plan(today)
    txs, final_bal = simulate_balances(raw)

    print(f"Tài khoản: {email} (id={uid}) — dữ liệu từ {start} đến {today}")
    print(f"Số giao dịch sẽ tạo: {len(txs)}")
    for k, name, _, init in WALLETS:
        print(f"  {name}: đầu kỳ {init:,} → cuối kỳ {final_bal[k]:,}")

    if dry_run:
        print("--dry-run: không ghi gì vào database.")
        conn.close()
        return

    backup = db_path + ".before_admin_reseed.bak"
    conn.execute("PRAGMA wal_checkpoint(FULL)")
    shutil.copyfile(db_path, backup)
    print(f"Đã sao lưu: {backup}")

    try:
        conn.execute("BEGIN")
        for table in ("transactions", "recurring_transactions", "budgets", "debts", "saving_goals"):
            conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM categories WHERE user_id = ?", (uid,))
        conn.execute("DELETE FROM wallets WHERE user_id = ?", (uid,))

        wallet_ids = {}
        for k, name, wtype, _ in WALLETS:
            cur = conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                               (uid, name, final_bal[k], wtype))
            wallet_ids[k] = cur.lastrowid

        cat_ids = {}
        for k, name, ctype, icon in CATEGORIES:
            cur = conn.execute("INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
                               (uid, name, ctype, icon))
            cat_ids[k] = cur.lastrowid

        conn.executemany("""
            INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [(uid, wallet_ids[w], cat_ids[c], a, t, day.isoformat(), n) for day, w, c, a, t, n in txs])

        # Hạn mức cho 3 tháng
        for back in (2, 1, 0):
            my = month_start(today, back).strftime("%Y-%m")
            for k, limit in (("food", 2500000), ("fun", 300000), ("shop", 400000), ("move", 400000)):
                conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                             (uid, cat_ids[k], limit, my))

        # Giao dịch định kỳ: lần chạy kế tiếp đều ở tương lai để không tự sinh thêm giao dịch
        def next_monthly(day):
            cand = datetime.date(today.year, today.month, day)
            return cand if cand > today else month_start(today, -1).replace(day=day)
        conn.executemany("""
            INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type,
                                                frequency, next_run_date, note, is_active)
            VALUES (?, ?, ?, ?, ?, 'monthly', ?, ?, 1)
        """, [
            (uid, wallet_ids["momo"], cat_ids["bill"], 120000, "EXPENSE", next_monthly(15).isoformat(), "Gia hạn gói cước 4G"),
            (uid, wallet_ids["bank"], cat_ids["rent"], 1800000, "EXPENSE", next_monthly(2).isoformat(), "Tiền phòng trọ"),
            (uid, wallet_ids["bank"], cat_ids["family"], 5000000, "INCOME", next_monthly(1).isoformat(), "Bố mẹ gửi tiền sinh hoạt"),
        ])

        # Sổ nợ
        conn.executemany("""
            INSERT INTO debts (user_id, wallet_id, debt_type, person_name, amount, due_date, is_settled, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (uid, wallet_ids["cash"], "BORROW", "Minh (bạn cùng phòng)", 500000,
             (today + datetime.timedelta(days=11)).isoformat(), 0, "Mượn tiền đóng học phí phụ"),
            (uid, wallet_ids["momo"], "LEND", "Lan (bạn cùng lớp)", 200000,
             (today + datetime.timedelta(days=26)).isoformat(), 0, "Cho mượn mua vé xe về quê"),
            (uid, wallet_ids["cash"], "BORROW", "Anh Tuấn (khóa trên)", 300000,
             (start + datetime.timedelta(days=20)).isoformat(), 1, "Đã trả xong"),
        ])

        # Mục tiêu tiết kiệm: số tiền hiện có = 2.000.000 đã có từ trước + các lần tích lũy đã ghi giao dịch
        goal_deposits = sum(a for _, _, c, a, _, _ in txs if c == "goal")
        conn.executemany("""
            INSERT INTO saving_goals (user_id, target_name, target_amount, current_amount, target_date, icon, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (uid, "Mua laptop học tập", 15000000, 2000000 + goal_deposits, f"{today.year + 1}-06-30", "💻", 0),
            (uid, "Vé xe về quê dịp Tết", 1200000, 1200000, f"{today.year + 1}-01-15", "🚌", 1),
        ])

        conn.commit()
    except Exception as err:
        conn.rollback()
        conn.close()
        sys.exit(f"Lỗi, đã rollback, dữ liệu không đổi: {err}")

    # Kiểm tra lại
    bad = conn.execute("""
        SELECT COUNT(*) FROM transactions t
        LEFT JOIN wallets w ON w.id = t.wallet_id AND w.user_id = t.user_id
        LEFT JOIN categories c ON c.id = t.category_id AND c.user_id = t.user_id AND c.category_type = t.transaction_type
        WHERE t.user_id = ? AND (w.id IS NULL OR c.id IS NULL)
    """, (uid,)).fetchone()[0]
    print("Giao dịch sai ví/danh mục:", bad)
    print("integrity_check:", conn.execute("PRAGMA integrity_check").fetchone()[0])
    conn.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=DEFAULT_DB)
    p.add_argument("--email", default="admin@gmail.com")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    seed(a.db, a.email, a.dry_run, datetime.date.today())
