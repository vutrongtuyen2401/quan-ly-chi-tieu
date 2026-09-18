"""
Bộ Test Tự Động Toàn Diện Cho Dự Án Quản Lý Chi Tiêu (Càn Khôn Linh Thạch Các)
Bao gồm toàn bộ 8 nhóm chức năng:
1. Auth & User Profile (Đăng ký, Đăng nhập, Profile, Quên/Đổi mật khẩu)
2. Wallets (Túi Càn Khôn, Số dư, Chuyển tiền liên ví)
3. Categories (Danh mục Thu/Chi)
4. Transactions (Ghi nhận Thu/Chi, Lọc, Phân trang, Xóa)
5. Budgets & Recurring (Hạn mức & Giao dịch định kỳ)
6. Debts Tracking - Sổ Nợ (Vay/Cho vay, Tất toán tự động, Thống kê nợ)
7. Saving Goals - Mục Tiêu Tiết Kiệm (Nạp/Rút linh thạch, Tiến độ %, Hoàn thành)
8. Admin Management - Phân Quyền (Thống kê hệ thống, Khóa/Mở khóa tài khoản, Đổi vai trò)
9. Reports & Exports (Tổng quan, Xu hướng 6 tháng, Theo tuần, So sánh 2 tháng, Xuất CSV/Excel)
"""

import os
import json
import io
import datetime
import unittest
import sqlite3
import tempfile
from fastapi.testclient import TestClient

# Thiết lập biến môi trường test trước khi import main
os.environ["JWT_SECRET"] = "test_jwt_secret_key_for_unit_tests_12345"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_123"

import main
from main import app, init_db, create_token


class ComprehensiveTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tạo file database tạm cho test suite
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()

        main.DATABASE = cls.db_path
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Dọn dẹp file test db
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except Exception:
                pass

    def setUp(self):
        main.login_attempts.clear()
        main.forgot_password_attempts.clear()

    # ──────────────────────────────────────────────
    # 1. AUTH & USER PROFILE TESTS
    # ──────────────────────────────────────────────
    def test_01_register_user_success(self):
        payload = {
            "email": "tu_si_1@gmail.com",
            "password": "password123",
            "full_name": "Bạch Tiểu Thuần",
            "soul_lamp": "BiMatDaoTam123"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.assertEqual(data["email"], payload["email"])
        self.assertEqual(data["role"], "user")

    def test_02_register_duplicate_email(self):
        payload = {
            "email": "tu_si_1@gmail.com",
            "password": "password123",
            "full_name": "Bạch Tiểu Thuần Trùng",
            "soul_lamp": "BiMatDaoTam123"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Email đã tồn tại", res.json()["detail"])

    def test_03_login_success_and_fail(self):
        # Wrong password
        res_fail = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "wrong_password"})
        self.assertEqual(res_fail.status_code, 401)

        # Right password
        res_ok = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        self.assertEqual(res_ok.status_code, 200)
        self.assertIn("token", res_ok.json())

    def test_04_user_profile_crud(self):
        # Login
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get profile
        res_prof = self.client.get("/api/user/profile", headers=headers)
        self.assertEqual(res_prof.status_code, 200)
        self.assertEqual(res_prof.json()["email"], "tu_si_1@gmail.com")

        # Update profile name
        res_update = self.client.put("/api/user/profile", json={"full_name": "Bạch Đại Lão"}, headers=headers)
        self.assertEqual(res_update.status_code, 200)

        # Check again
        res_prof2 = self.client.get("/api/user/profile", headers=headers)
        self.assertEqual(res_prof2.json()["full_name"], "Bạch Đại Lão")

    # ──────────────────────────────────────────────
    # 1B. BẢN MỆNH HỒN ĐĂNG (8 STEPS VERIFICATION)
    # ──────────────────────────────────────────────
    def test_04b_soul_lamp_step1_register_and_db_hash(self):
        """Bước 1: Đăng ký tài khoản mới với Bản Mệnh Hồn Đăng, xác nhận băm bcrypt trong DB (không lưu plaintext)"""
        email = "soul_lamp_user@gmail.com"
        plain_soul_lamp = "MatMaThienDinh789"
        res = self.client.post("/api/auth/register", json={
            "email": email,
            "password": "password123",
            "full_name": "Lâm Động",
            "soul_lamp": plain_soul_lamp
        })
        self.assertEqual(res.status_code, 200)

        # Kiểm tra trực tiếp trong DB
        with main.get_db() as conn:
            user = conn.execute("SELECT soul_lamp_hash FROM users WHERE email = ?", (email,)).fetchone()
            self.assertIsNotNone(user)
            db_hash = user["soul_lamp_hash"]
            self.assertIsNotNone(db_hash)
            self.assertNotEqual(db_hash, plain_soul_lamp)
            self.assertTrue(db_hash.startswith("$2b$") or db_hash.startswith("$2a$") or db_hash.startswith("$2y$"))

    def test_04c_soul_lamp_step2_forgot_password_success(self):
        """Bước 2: Quên mật khẩu với email ĐÚNG + Bản Mệnh Hồn Đăng ĐÚNG -> cấp mã reset"""
        res = self.client.post("/api/auth/forgot-password", json={
            "email": "soul_lamp_user@gmail.com",
            "soul_lamp": "MatMaThienDinh789"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertNotIn("reset_token", data)
        with main.get_db() as conn:
            row = conn.execute("SELECT token FROM password_reset_tokens WHERE email = 'soul_lamp_user@gmail.com' AND used = 0 ORDER BY id DESC LIMIT 1").fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(len(row["token"]), 6)

    def test_04d_soul_lamp_step3_forgot_password_wrong_soul_lamp(self):
        """Bước 3: Quên mật khẩu với email ĐÚNG + Bản Mệnh Hồn Đăng SAI -> bị từ chối với thông báo chung chung"""
        res = self.client.post("/api/auth/forgot-password", json={
            "email": "soul_lamp_user@gmail.com",
            "soul_lamp": "GiaTriSaiHoanToan"
        })
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["detail"], "Thông tin xác thực không chính xác, vui lòng kiểm tra lại")
        self.assertNotIn("reset_token", data)

    def test_04e_soul_lamp_step4_forgot_password_nonexistent_email(self):
        """Bước 4: Quên mật khẩu với email KHÔNG tồn tại -> CÙNG thông báo lỗi như bước 3 (chống user enumeration)"""
        res_step3 = self.client.post("/api/auth/forgot-password", json={
            "email": "soul_lamp_user@gmail.com",
            "soul_lamp": "GiaTriSaiHoanToan"
        })
        res_step4 = self.client.post("/api/auth/forgot-password", json={
            "email": "nonexistent_email_9999@gmail.com",
            "soul_lamp": "MatMaThienDinh789"
        })
        self.assertEqual(res_step4.status_code, 400)
        self.assertEqual(res_step3.json()["detail"], res_step4.json()["detail"])
        self.assertEqual(res_step4.json()["detail"], "Thông tin xác thực không chính xác, vui lòng kiểm tra lại")

    def test_04f_soul_lamp_step5_admin_forgot_password(self):
        """Bước 5: Admin mặc định admin@gmail.com + soul_lamp 'admin' -> cấp mã reset thành công"""
        res = self.client.post("/api/auth/forgot-password", json={
            "email": "admin@gmail.com",
            "soul_lamp": "admin"
        })
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("reset_token", res.json())
        with main.get_db() as conn:
            row = conn.execute("SELECT token FROM password_reset_tokens WHERE email = 'admin@gmail.com' AND used = 0 ORDER BY id DESC LIMIT 1").fetchone()
            self.assertIsNotNone(row)

    def test_04g_soul_lamp_step6_and_7_update_and_verify_new_soul_lamp(self):
        """Bước 6 & 7: Đổi Bản Mệnh Hồn Đăng qua API profile, sau đó thử lại luồng quên mật khẩu với giá trị MỚI và CŨ"""
        # Login
        login_res = self.client.post("/api/auth/login", json={"email": "soul_lamp_user@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 6.1 Thử đổi với mật khẩu hiện tại SAI
        res_wrong_pw = self.client.put("/api/user/soul-lamp", json={
            "current_password": "wrong_password",
            "new_soul_lamp": "GiaTriMoiVuaDoi123"
        }, headers=headers)
        self.assertEqual(res_wrong_pw.status_code, 400)

        # 6.2 Đổi với mật khẩu hiện tại ĐÚNG
        res_ok = self.client.put("/api/user/soul-lamp", json={
            "current_password": "password123",
            "new_soul_lamp": "GiaTriMoiVuaDoi123"
        }, headers=headers)
        self.assertEqual(res_ok.status_code, 200)

        # 7.1 Thử quên mật khẩu bằng giá trị CŨ -> phải THẤT BẠI
        res_old = self.client.post("/api/auth/forgot-password", json={
            "email": "soul_lamp_user@gmail.com",
            "soul_lamp": "MatMaThienDinh789"
        })
        self.assertEqual(res_old.status_code, 400)
        self.assertEqual(res_old.json()["detail"], "Thông tin xác thực không chính xác, vui lòng kiểm tra lại")

        # 7.2 Thử quên mật khẩu bằng giá trị MỚI -> phải THÀNH CÔNG
        res_new = self.client.post("/api/auth/forgot-password", json={
            "email": "soul_lamp_user@gmail.com",
            "soul_lamp": "GiaTriMoiVuaDoi123"
        })
        self.assertEqual(res_new.status_code, 200)
        self.assertNotIn("reset_token", res_new.json())

    def test_04h_soul_lamp_step8_full_auth_and_reset_flow(self):
        """Bước 8: Kiểm tra toàn bộ luồng đăng ký, đăng nhập, quên mật khẩu & reset mật khẩu hoàn chỉnh"""
        email = "full_flow_user@gmail.com"
        soul_lamp = "FullFlowLamp999"
        new_pass = "brand_new_pass_456"

        # Register
        reg = self.client.post("/api/auth/register", json={
            "email": email,
            "password": "old_pass_123",
            "full_name": "Tiêu Viêm",
            "soul_lamp": soul_lamp
        })
        self.assertEqual(reg.status_code, 200)

        # Forgot password -> token
        forgot = self.client.post("/api/auth/forgot-password", json={"email": email, "soul_lamp": soul_lamp})
        self.assertEqual(forgot.status_code, 200)
        self.assertNotIn("reset_token", forgot.json())
        with main.get_db() as conn:
            token_row = conn.execute("SELECT token FROM password_reset_tokens WHERE email = ? AND used = 0 ORDER BY id DESC LIMIT 1", (email,)).fetchone()
            token = token_row["token"]

        # Reset password
        reset = self.client.post("/api/auth/reset-password", json={
            "email": email,
            "token": token,
            "new_password": new_pass
        })
        self.assertEqual(reset.status_code, 200)

        # Login with new password
        login_new = self.client.post("/api/auth/login", json={"email": email, "password": new_pass})
        self.assertEqual(login_new.status_code, 200)
        self.assertIn("token", login_new.json())

    # ──────────────────────────────────────────────
    # 2. WALLETS TESTS
    # ──────────────────────────────────────────────
    def test_05_wallets_crud_and_transfer(self):
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # User defaults to 3 wallets
        res = self.client.get("/api/wallets", headers=headers)
        self.assertEqual(res.status_code, 200)
        wallets = res.json()
        self.assertGreaterEqual(len(wallets), 2)
        w1_id, w2_id = wallets[0]["id"], wallets[1]["id"]
        w1_init_bal = wallets[0]["balance"]
        w2_init_bal = wallets[1]["balance"]

        # Create new custom wallet
        new_w = self.client.post("/api/wallets", json={"wallet_name": "Nhẫn Trữ Vật", "balance": 1000000, "wallet_type": "cash"}, headers=headers)
        self.assertEqual(new_w.status_code, 200)
        new_w_id = new_w.json()["id"]

        # Transfer 500,000 from w1 to w2
        transfer_res = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w1_id,
            "to_wallet_id": w2_id,
            "amount": 500000,
            "note": "Chuyển linh thạch sang tài khoản ngân hàng"
        }, headers=headers)
        self.assertEqual(transfer_res.status_code, 200)

        # Verify balances
        wallets_after = self.client.get("/api/wallets", headers=headers).json()
        w1_after = next(w for w in wallets_after if w["id"] == w1_id)
        w2_after = next(w for w in wallets_after if w["id"] == w2_id)
        self.assertEqual(w1_after["balance"], w1_init_bal - 500000)
        self.assertEqual(w2_after["balance"], w2_init_bal + 500000)

        # Delete custom wallet
        del_res = self.client.delete(f"/api/wallets/{new_w_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

    # ──────────────────────────────────────────────
    # 3. CATEGORIES & TRANSACTIONS TESTS
    # ──────────────────────────────────────────────
    def test_06_categories_and_transactions_flow(self):
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Category
        cat_res = self.client.post("/api/categories", json={
            "category_name": "Luyện Đan Chi Phí",
            "category_type": "EXPENSE",
            "icon": "🧪"
        }, headers=headers)
        self.assertEqual(cat_res.status_code, 200)
        cat_id = cat_res.json()["id"]

        # 2. Get wallet
        wallets = self.client.get("/api/wallets", headers=headers).json()
        w_id = wallets[0]["id"]
        bal_before = wallets[0]["balance"]

        # 3. Create Expense Transaction
        txn_res = self.client.post("/api/transactions", json={
            "wallet_id": w_id,
            "category_id": cat_id,
            "amount": 250000,
            "transaction_type": "EXPENSE",
            "transaction_date": "2026-08-15",
            "note": "Mua thảo dược Bách Thảo Các"
        }, headers=headers)
        self.assertEqual(txn_res.status_code, 200)
        txn_id = txn_res.json()["id"]

        # 4. Verify wallet balance decreased
        wallets_after = self.client.get("/api/wallets", headers=headers).json()
        w_after = next(w for w in wallets_after if w["id"] == w_id)
        self.assertEqual(w_after["balance"], bal_before - 250000)

        # 5. Filter & pagination check
        txns_page = self.client.get(f"/api/transactions?category_id={cat_id}&limit=10&offset=0", headers=headers)
        self.assertEqual(txns_page.status_code, 200)
        self.assertGreaterEqual(txns_page.json()["total_count"], 1)

        # 6. Delete transaction and verify wallet refunded
        del_txn = self.client.delete(f"/api/transactions/{txn_id}", headers=headers)
        self.assertEqual(del_txn.status_code, 200)
        wallets_refund = self.client.get("/api/wallets", headers=headers).json()
        w_refund = next(w for w in wallets_refund if w["id"] == w_id)
        self.assertEqual(w_refund["balance"], bal_before)

    # ──────────────────────────────────────────────
    # 4. BUDGETS & RECURRING TRANSACTIONS
    # ──────────────────────────────────────────────
    def test_07_budgets_and_recurring(self):
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        cats = self.client.get("/api/categories", headers=headers).json()
        cat_id = cats[0]["id"]
        wallets = self.client.get("/api/wallets", headers=headers).json()
        w_id = wallets[0]["id"]

        # Budget Create
        b_res = self.client.post("/api/budgets", json={
            "category_id": cat_id,
            "limit_amount": 1000000,
            "month_year": "2026-08"
        }, headers=headers)
        self.assertEqual(b_res.status_code, 200)

        # Recurring Create
        rec_res = self.client.post("/api/recurring-transactions", json={
            "wallet_id": w_id,
            "category_id": cat_id,
            "amount": 150000,
            "transaction_type": "EXPENSE",
            "frequency": "monthly",
            "next_run_date": "2026-09-01",
            "note": "Phí thuê động phủ hàng tháng"
        }, headers=headers)
        self.assertEqual(rec_res.status_code, 200)
        rec_id = rec_res.json()["id"]

        # Recurring Toggle
        toggle_res = self.client.put(f"/api/recurring-transactions/{rec_id}", json={"is_active": 0}, headers=headers)
        self.assertEqual(toggle_res.status_code, 200)

        # Recurring Delete
        del_rec = self.client.delete(f"/api/recurring-transactions/{rec_id}", headers=headers)
        self.assertEqual(del_rec.status_code, 200)

    # ──────────────────────────────────────────────
    # 5. FEATURE 1: DEBTS TRACKING TESTS
    # ──────────────────────────────────────────────
    def test_08_debts_tracking_full_flow(self):
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create BORROW debt
        d1 = self.client.post("/api/debts", json={
            "debt_type": "BORROW",
            "person_name": "Lý Hắc Ma",
            "amount": 2000000,
            "due_date": "2026-09-15",
            "note": "Vay linh thạch mua đan dược"
        }, headers=headers).json()

        # 2. Create LEND debt
        d2 = self.client.post("/api/debts", json={
            "debt_type": "LEND",
            "person_name": "Hàn Lập",
            "amount": 5000000,
            "due_date": "2026-10-01",
            "note": "Cho vay mua bảo kiếm"
        }, headers=headers).json()

        # 3. Get Debts & Summary
        debts_res = self.client.get("/api/debts", headers=headers).json()
        self.assertGreaterEqual(len(debts_res["debts"]), 2)
        self.assertEqual(debts_res["summary"]["total_borrow_unsettled"], 2000000)
        self.assertEqual(debts_res["summary"]["total_lend_unsettled"], 5000000)

        # 4. Settle Borrow debt
        settle_res = self.client.post(f"/api/debts/{d1['id']}/settle", headers=headers)
        self.assertEqual(settle_res.status_code, 200)
        self.assertEqual(settle_res.json()["is_settled"], 1)

        # Check summary updated
        debts_res2 = self.client.get("/api/debts", headers=headers).json()
        self.assertEqual(debts_res2["summary"]["total_borrow_unsettled"], 0)
        self.assertEqual(debts_res2["summary"]["total_borrow_settled"], 2000000)

        # 5. Delete debt
        del_res = self.client.delete(f"/api/debts/{d2['id']}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

    # ──────────────────────────────────────────────
    # 6. FEATURE 2: SAVING GOALS TESTS
    # ──────────────────────────────────────────────
    def test_09_saving_goals_full_flow(self):
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        wallets = self.client.get("/api/wallets", headers=headers).json()
        w_id = wallets[0]["id"]
        w_bal_start = wallets[0]["balance"]

        # 1. Create Saving Goal
        g_res = self.client.post("/api/saving-goals", json={
            "target_name": "Tậu Phi Kiếm Cửu Tiêu",
            "target_amount": 10000000,
            "current_amount": 2000000,
            "target_date": "2026-12-31",
            "icon": "⚔️"
        }, headers=headers)
        self.assertEqual(g_res.status_code, 200)
        goal_id = g_res.json()["id"]

        # 2. Deposit 3,000,000 from wallet
        dep_res = self.client.post(f"/api/saving-goals/{goal_id}/deposit", json={
            "amount": 3000000,
            "wallet_id": w_id
        }, headers=headers)
        self.assertEqual(dep_res.status_code, 200)
        self.assertEqual(dep_res.json()["current_amount"], 5000000)

        # Check wallet deducted
        w_bal_after_dep = next(w for w in self.client.get("/api/wallets", headers=headers).json() if w["id"] == w_id)["balance"]
        self.assertEqual(w_bal_after_dep, w_bal_start - 3000000)

        # 3. Withdraw 1,000,000 back to wallet
        with_res = self.client.post(f"/api/saving-goals/{goal_id}/withdraw", json={
            "amount": 1000000,
            "wallet_id": w_id
        }, headers=headers)
        self.assertEqual(with_res.status_code, 200)
        self.assertEqual(with_res.json()["current_amount"], 4000000)

        # Check wallet refunded
        w_bal_after_with = next(w for w in self.client.get("/api/wallets", headers=headers).json() if w["id"] == w_id)["balance"]
        self.assertEqual(w_bal_after_with, w_bal_after_dep + 1000000)

        # 4. Check Goals List & Progress Calculation
        goals_data = self.client.get("/api/saving-goals", headers=headers).json()
        my_goal = next(g for g in goals_data["goals"] if g["id"] == goal_id)
        self.assertEqual(my_goal["percent"], 40.0)
        self.assertEqual(my_goal["remaining_amount"], 6000000)

        # 5. Delete Goal
        del_g = self.client.delete(f"/api/saving-goals/{goal_id}", headers=headers)
        self.assertEqual(del_g.status_code, 200)

    # ──────────────────────────────────────────────
    # 7. FEATURE 3: ADMIN PERMISSIONS & MANAGEMENT
    # ──────────────────────────────────────────────
    def test_10_admin_roles_and_management(self):
        # 1. Normal user cannot access admin stats -> 403
        login_user = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"}).json()
        user_headers = {"Authorization": f"Bearer {login_user['token']}"}
        res_forbidden = self.client.get("/api/admin/stats", headers=user_headers)
        self.assertEqual(res_forbidden.status_code, 403)

        # 2. Create Admin Token directly for admin@gmail.com
        admin_token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 3. Admin can access stats (strictly account metrics, NO financial metrics)
        stats_res = self.client.get("/api/admin/stats", headers=admin_headers)
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertIn("total_users", stats)
        self.assertIn("active_users", stats)
        self.assertIn("locked_users", stats)
        # Privacy boundary: must NOT contain financial fields
        for field in ["total_wallets", "total_transactions", "total_income", "total_expense", "total_system_cashflow", "total_balance", "total_debts", "total_goals"]:
            self.assertNotIn(field, stats, f"Privacy violation: {field} must not be in admin stats")

        # 4. Admin can list all users (strictly identity fields, NO financial fields)
        users_res = self.client.get("/api/admin/users", headers=admin_headers)
        self.assertEqual(users_res.status_code, 200)
        users = users_res.json()
        self.assertGreaterEqual(len(users), 1)
        for u in users:
            for field in ["wallet_count", "total_balance", "txn_count"]:
                self.assertNotIn(field, u, f"Privacy violation: {field} must not be in user row for admin")

        # 5. Admin locks normal user
        target_uid = login_user["user_id"]
        lock_res = self.client.put(f"/api/admin/users/{target_uid}/toggle-active", headers=admin_headers)
        self.assertEqual(lock_res.status_code, 200)
        self.assertEqual(lock_res.json()["is_active"], 0)

        # 6. Locked user is forbidden to login -> 403
        login_locked = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        self.assertEqual(login_locked.status_code, 403)

        # 7. Admin unlocks normal user
        unlock_res = self.client.put(f"/api/admin/users/{target_uid}/toggle-active", headers=admin_headers)
        self.assertEqual(unlock_res.status_code, 200)
        self.assertEqual(unlock_res.json()["is_active"], 1)

        # 8. Admin promotes user to admin
        role_res = self.client.put(f"/api/admin/users/{target_uid}/role", json={"role": "admin"}, headers=admin_headers)
        self.assertEqual(role_res.status_code, 200)
        self.assertEqual(role_res.json()["role"], "admin")

    # ──────────────────────────────────────────────
    # 8. REPORTS & EXPORTS
    # ──────────────────────────────────────────────
    def test_11_reports_and_export_endpoints(self):
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Summary
        sum_res = self.client.get("/api/reports/summary", headers=headers)
        self.assertEqual(sum_res.status_code, 200)
        self.assertIn("total_income", sum_res.json())

        # Trend (6 months)
        trend_res = self.client.get("/api/reports/trend?months=6", headers=headers)
        self.assertEqual(trend_res.status_code, 200)

        # Weekly
        weekly_res = self.client.get("/api/reports/weekly?weeks=4", headers=headers)
        self.assertEqual(weekly_res.status_code, 200)

        # Compare 2 months
        compare_res = self.client.get("/api/reports/compare?month1=2026-07&month2=2026-08", headers=headers)
        self.assertEqual(compare_res.status_code, 200)

        # Export CSV
        csv_res = self.client.get("/api/reports/export?format=csv", headers=headers)
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn("text/csv", csv_res.headers.get("content-type", ""))

        # Export Excel
        excel_res = self.client.get("/api/reports/export?format=excel", headers=headers)
        self.assertEqual(excel_res.status_code, 200)

    # ──────────────────────────────────────────────
    # 9. BATCH-01: JWT LIVE DB & DEACTIVATION
    # ──────────────────────────────────────────────
    def test_12_jwt_live_db_validation_and_deactivation(self):
        """Kiểm tra token bị từ chối ngay khi tài khoản bị vô hiệu hóa trong DB, và token user không tồn tại bị 401"""
        email = "live_check_user@gmail.com"
        reg = self.client.post("/api/auth/register", json={
            "email": email,
            "password": "pass_live_123",
            "full_name": "Lăng Thanh Trúc",
            "soul_lamp": "SoulLampLive123"
        })
        self.assertEqual(reg.status_code, 200)
        token = reg.json()["token"]
        user_id = reg.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Gọi profile thành công
        p1 = self.client.get("/api/user/profile", headers=headers)
        self.assertEqual(p1.status_code, 200)

        # 2. Khóa user trực tiếp trong SQLite
        with main.get_db() as conn:
            conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))

        # 3. Thử gọi lại API bằng token còn hạn 24h -> PHẢI BỊ 403 Forbidden
        p2 = self.client.get("/api/user/profile", headers=headers)
        self.assertEqual(p2.status_code, 403)
        self.assertIn("phong ấn", p2.json()["detail"])

        # 4. Thử gọi API tài chính bằng token bị khóa -> 403
        w_res = self.client.get("/api/wallets", headers=headers)
        self.assertEqual(w_res.status_code, 403)

        # 5. Mở khóa lại trong DB -> gọi API thành công
        with main.get_db() as conn:
            conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
        p3 = self.client.get("/api/user/profile", headers=headers)
        self.assertEqual(p3.status_code, 200)

        # 6. Token chứa user_id không tồn tại trong DB -> 401
        ghost_token = create_token(user_id=999999, email="ghost@gmail.com", role="user")
        ghost_res = self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {ghost_token}"})
        self.assertEqual(ghost_res.status_code, 401)

    # ──────────────────────────────────────────────
    # 10. BATCH-01: CROSS-USER IDOR PROTECTION
    # ──────────────────────────────────────────────
    def test_13_cross_user_resource_ownership_and_idor(self):
        """Kiểm tra triệt để: Không user nào có thể thao tác tài nguyên của user khác qua ID (IDOR)"""
        # Tạo User A
        reg_a = self.client.post("/api/auth/register", json={
            "email": "user_idor_a@gmail.com",
            "password": "password_a",
            "full_name": "Đạo Hữu A",
            "soul_lamp": "SoulLampA123"
        }).json()
        headers_a = {"Authorization": f"Bearer {reg_a['token']}"}
        wallets_a = self.client.get("/api/wallets", headers=headers_a).json()
        cats_a = self.client.get("/api/categories", headers=headers_a).json()
        w_a = wallets_a[0]["id"]
        c_a = cats_a[0]["id"]

        # Tạo User B
        reg_b = self.client.post("/api/auth/register", json={
            "email": "user_idor_b@gmail.com",
            "password": "password_b",
            "full_name": "Đạo Hữu B",
            "soul_lamp": "SoulLampB123"
        }).json()
        headers_b = {"Authorization": f"Bearer {reg_b['token']}"}
        wallets_b = self.client.get("/api/wallets", headers=headers_b).json()
        cats_b = self.client.get("/api/categories", headers=headers_b).json()
        w_b = wallets_b[0]["id"]
        c_b = cats_b[0]["id"]

        # 1. User A cố sửa/xóa ví của User B -> 404
        self.assertEqual(self.client.put(f"/api/wallets/{w_b}", json={"wallet_name": "Hack Ví B"}, headers=headers_a).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/wallets/{w_b}", headers=headers_a).status_code, 404)

        # 2. User A cố sửa/xóa danh mục của User B -> 404
        self.assertEqual(self.client.put(f"/api/categories/{c_b}", json={"category_name": "Hack Cat B"}, headers=headers_a).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/categories/{c_b}", headers=headers_a).status_code, 404)

        # 3. User A cố tạo giao dịch gắn vào ví của User B -> 404
        bad_txn_w = self.client.post("/api/transactions", json={
            "wallet_id": w_b,
            "category_id": c_a,
            "amount": 100000,
            "transaction_type": "EXPENSE",
            "transaction_date": "2026-09-17"
        }, headers=headers_a)
        self.assertEqual(bad_txn_w.status_code, 404)

        # 4. User A cố tạo giao dịch gắn vào danh mục của User B -> 404
        bad_txn_c = self.client.post("/api/transactions", json={
            "wallet_id": w_a,
            "category_id": c_b,
            "amount": 100000,
            "transaction_type": "EXPENSE",
            "transaction_date": "2026-09-17"
        }, headers=headers_a)
        self.assertEqual(bad_txn_c.status_code, 404)

        # 5. User A tạo 1 giao dịch hợp lệ của mình
        valid_txn = self.client.post("/api/transactions", json={
            "wallet_id": w_a,
            "category_id": c_a,
            "amount": 100000,
            "transaction_type": "EXPENSE",
            "transaction_date": "2026-09-17"
        }, headers=headers_a).json()
        txn_id_a = valid_txn["id"]

        # 6. User A cố sửa giao dịch của mình nhưng đổi ví sang ví của User B -> 404
        hack_w_update = self.client.put(f"/api/transactions/{txn_id_a}", json={
            "wallet_id": w_b
        }, headers=headers_a)
        self.assertEqual(hack_w_update.status_code, 404)

        # 7. User B cố sửa/xóa giao dịch của User A -> 404
        self.assertEqual(self.client.put(f"/api/transactions/{txn_id_a}", json={"amount": 200000}, headers=headers_b).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/transactions/{txn_id_a}", headers=headers_b).status_code, 404)

        # 8. User A cố tạo ngân sách bằng danh mục của User B -> 404
        bad_budget = self.client.post("/api/budgets", json={
            "category_id": c_b,
            "limit_amount": 5000000,
            "month_year": "2026-09"
        }, headers=headers_a)
        self.assertEqual(bad_budget.status_code, 404)

        # User A tạo ngân sách hợp lệ
        valid_b = self.client.post("/api/budgets", json={
            "category_id": c_a,
            "limit_amount": 5000000,
            "month_year": "2026-09"
        }, headers=headers_a).json()
        b_id_a = valid_b["id"]

        # User B cố sửa hoặc xóa ngân sách của User A -> 404
        self.assertEqual(self.client.put(f"/api/budgets/{b_id_a}", json={"limit_amount": 1000000}, headers=headers_b).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/budgets/{b_id_a}", headers=headers_b).status_code, 404)

        # 9. User A cố tạo giao dịch định kỳ bằng ví hoặc danh mục của User B -> 404
        self.assertEqual(self.client.post("/api/recurring-transactions", json={
            "wallet_id": w_b,
            "category_id": c_a,
            "amount": 200000,
            "next_run_date": "2026-10-01"
        }, headers=headers_a).status_code, 404)
        self.assertEqual(self.client.post("/api/recurring-transactions", json={
            "wallet_id": w_a,
            "category_id": c_b,
            "amount": 200000,
            "next_run_date": "2026-10-01"
        }, headers=headers_a).status_code, 404)

        # User A tạo định kỳ hợp lệ
        rec_a = self.client.post("/api/recurring-transactions", json={
            "wallet_id": w_a,
            "category_id": c_a,
            "amount": 200000,
            "next_run_date": "2026-10-01"
        }, headers=headers_a).json()["id"]
        # User B cố sửa/xóa định kỳ của User A -> 404
        self.assertEqual(self.client.put(f"/api/recurring-transactions/{rec_a}", json={"amount": 300000}, headers=headers_b).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/recurring-transactions/{rec_a}", headers=headers_b).status_code, 404)

        # 10. User A tạo khoản nợ gắn ví của User B -> 404
        bad_debt = self.client.post("/api/debts", json={
            "debt_type": "BORROW",
            "person_name": "Người Vay",
            "amount": 500000,
            "wallet_id": w_b
        }, headers=headers_a)
        self.assertEqual(bad_debt.status_code, 404)

        # User A tạo khoản nợ hợp lệ
        debt_a = self.client.post("/api/debts", json={
            "debt_type": "BORROW",
            "person_name": "Người Vay",
            "amount": 500000,
            "wallet_id": w_a
        }, headers=headers_a).json()["id"]
        # User B cố tất toán / xóa nợ của User A -> 404
        self.assertEqual(self.client.post(f"/api/debts/{debt_a}/settle", headers=headers_b).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/debts/{debt_a}", headers=headers_b).status_code, 404)

        # 11. User A tạo mục tiêu tiết kiệm
        goal_a = self.client.post("/api/saving-goals", json={
            "target_name": "Mua Linh Thạch Đan",
            "target_amount": 5000000
        }, headers=headers_a).json()["id"]

        # User B cố nạp / rút / xóa mục tiêu tiết kiệm của User A -> 404
        self.assertEqual(self.client.post(f"/api/saving-goals/{goal_a}/deposit", json={"amount": 500000}, headers=headers_b).status_code, 404)
        self.assertEqual(self.client.post(f"/api/saving-goals/{goal_a}/withdraw", json={"amount": 500000}, headers=headers_b).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/saving-goals/{goal_a}", headers=headers_b).status_code, 404)

        # User A rút tiền tiết kiệm vào ví của User B -> 404
        self.client.post(f"/api/saving-goals/{goal_a}/deposit", json={"amount": 1000000}, headers=headers_a)
        bad_goal_withdraw = self.client.post(f"/api/saving-goals/{goal_a}/withdraw", json={
            "amount": 500000,
            "wallet_id": w_b
        }, headers=headers_a)
        self.assertEqual(bad_goal_withdraw.status_code, 404)

        # 12. User A chuyển tiền từ ví B sang ví A -> 404
        steal_transfer = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w_b,
            "to_wallet_id": w_a,
            "amount": 100000
        }, headers=headers_a)
        self.assertEqual(steal_transfer.status_code, 404)

        # User A chuyển tiền từ ví A sang ví B -> 404
        send_to_foreign = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w_a,
            "to_wallet_id": w_b,
            "amount": 100000
        }, headers=headers_a)
        self.assertEqual(send_to_foreign.status_code, 404)

    # ──────────────────────────────────────────────
    # 11. BATCH-01: FINANCIAL DATA INTEGRITY VALIDATION
    # ──────────────────────────────────────────────
    def test_14_financial_data_integrity_and_validation(self):
        """Kiểm tra chặn số tiền âm hoặc bằng 0 trên mọi endpoint tài chính"""
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        wallets = self.client.get("/api/wallets", headers=headers).json()
        w_id = wallets[0]["id"]
        cats = self.client.get("/api/categories", headers=headers).json()
        c_id = cats[0]["id"]

        # 1. Giao dịch amount <= 0 -> 400
        self.assertEqual(self.client.post("/api/transactions", json={
            "wallet_id": w_id, "category_id": c_id, "amount": 0, "transaction_type": "EXPENSE", "transaction_date": "2026-09-17"
        }, headers=headers).status_code, 400)
        self.assertEqual(self.client.post("/api/transactions", json={
            "wallet_id": w_id, "category_id": c_id, "amount": -10000, "transaction_type": "EXPENSE", "transaction_date": "2026-09-17"
        }, headers=headers).status_code, 400)

        # 2. Giao dịch loại không hợp lệ -> 400
        self.assertEqual(self.client.post("/api/transactions", json={
            "wallet_id": w_id, "category_id": c_id, "amount": 50000, "transaction_type": "INVALID_TYPE", "transaction_date": "2026-09-17"
        }, headers=headers).status_code, 400)

        # 3. Chuyển tiền amount <= 0 -> 400
        if len(wallets) >= 2:
            self.assertEqual(self.client.post("/api/wallets/transfer", json={
                "from_wallet_id": wallets[0]["id"], "to_wallet_id": wallets[1]["id"], "amount": 0
            }, headers=headers).status_code, 400)
            self.assertEqual(self.client.post("/api/wallets/transfer", json={
                "from_wallet_id": wallets[0]["id"], "to_wallet_id": wallets[1]["id"], "amount": -5000
            }, headers=headers).status_code, 400)

        # 4. Ngân sách limit_amount <= 0 -> 400
        self.assertEqual(self.client.post("/api/budgets", json={
            "category_id": c_id, "limit_amount": 0, "month_year": "2026-09"
        }, headers=headers).status_code, 400)
        self.assertEqual(self.client.post("/api/budgets", json={
            "category_id": c_id, "limit_amount": -1000, "month_year": "2026-09"
        }, headers=headers).status_code, 400)

        # 5. Định kỳ amount <= 0 -> 400
        self.assertEqual(self.client.post("/api/recurring-transactions", json={
            "wallet_id": w_id, "category_id": c_id, "amount": 0, "next_run_date": "2026-10-01"
        }, headers=headers).status_code, 400)

        # 6. Sổ nợ amount <= 0 -> 400
        self.assertEqual(self.client.post("/api/debts", json={
            "debt_type": "BORROW", "person_name": "Test", "amount": 0
        }, headers=headers).status_code, 400)

        # 7. Mục tiêu tiết kiệm target_amount <= 0 -> 400
        self.assertEqual(self.client.post("/api/saving-goals", json={
            "target_name": "Test", "target_amount": 0
        }, headers=headers).status_code, 400)

    # ──────────────────────────────────────────────
    # 12. BATCH-01: OCR FAILURE DOES NOT FABRICATE DATA
    # ──────────────────────────────────────────────
    def test_15_ocr_failure_does_not_fabricate_data(self):
        """Kiểm tra khi OCR thất bại, tuyệt đối không trả về thành công với dữ liệu bịa đặt (150,000đ)"""
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Gửi file ảnh giả/rỗng mà Gemini không thể parse được hóa đơn
        fake_image = io.BytesIO(b"fake_corrupted_image_content_not_real_receipt")
        files = {"file": ("corrupted.jpg", fake_image, "image/jpeg")}

        res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        # Phải trả về lỗi 422 hoặc tương đương, TUYỆT ĐỐI KHÔNG trả về success=True với 150000đ mẫu
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertIn("detail", data)
        self.assertNotIn("Cửa Hàng Linh Đan (Trích xuất mẫu)", str(data))

        # Kiểm tra trong DB không có bản ghi fake bị insert vào invoice_ocr_logs
        with main.get_db() as conn:
            fake_log = conn.execute(
                "SELECT * FROM invoice_ocr_logs WHERE extracted_json LIKE '%Cửa Hàng Linh Đan (Trích xuất mẫu)%'"
            ).fetchone()
            self.assertIsNone(fake_log)

    # ──────────────────────────────────────────────
    # 13. BATCH-01 MICRO-FIX: FINDING 1.1 ADMIN FINANCIAL PRIVACY
    # ──────────────────────────────────────────────
    def test_16_admin_financial_privacy_boundary(self):
        """Kiểm tra Admin stats và user list tuyệt đối không rò rỉ dữ liệu tài chính của người dùng"""
        admin_token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Admin stats must only contain account/admin metrics
        stats_res = self.client.get("/api/admin/stats", headers=admin_headers)
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertIn("total_users", stats)
        self.assertIn("active_users", stats)
        self.assertIn("locked_users", stats)

        forbidden_stat_keys = [
            "total_wallets", "total_transactions", "total_income", "total_expense",
            "total_system_cashflow", "total_balance", "total_debts", "total_goals"
        ]
        for key in forbidden_stat_keys:
            self.assertNotIn(key, stats, f"Security Violation: {key} must NOT exist in admin stats!")

        # 2. Admin users list must not contain any personal financial aggregates
        users_res = self.client.get("/api/admin/users", headers=admin_headers)
        self.assertEqual(users_res.status_code, 200)
        users = users_res.json()
        self.assertGreaterEqual(len(users), 1)

        forbidden_user_keys = ["wallet_count", "total_balance", "txn_count"]
        allowed_user_keys = {"id", "email", "full_name", "role", "is_active", "created_at"}
        for u in users:
            for key in forbidden_user_keys:
                self.assertNotIn(key, u, f"Privacy Violation: {key} must NOT be in admin user row!")
            self.assertTrue(set(u.keys()).issubset(allowed_user_keys))

    # ──────────────────────────────────────────────
    # 14. BATCH-01 MICRO-FIX: FINDING 1.2 DEPENDENT RECORDS ON DELETE
    # ──────────────────────────────────────────────
    def test_17_delete_wallet_category_with_dependent_records_returns_400(self):
        """Kiểm tra xóa ví hoặc danh mục có bản ghi phụ thuộc phải trả về HTTP 400 rõ ràng, không sập 500"""
        login_res = self.client.post("/api/auth/login", json={"email": "tu_si_1@gmail.com", "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Tạo ví và danh mục thử nghiệm
        w_res = self.client.post("/api/wallets", json={"wallet_name": "Ví Ràng Buộc", "balance": 1000000, "wallet_type": "cash"}, headers=headers)
        w_id = w_res.json()["id"]

        c_res = self.client.post("/api/categories", json={"category_name": "DM Ràng Buộc", "category_type": "EXPENSE", "icon": "🔒"}, headers=headers)
        c_id = c_res.json()["id"]

        # Case 1: Ví và Danh mục liên kết với Giao dịch
        txn_res = self.client.post("/api/transactions", json={
            "wallet_id": w_id, "category_id": c_id, "amount": 50000,
            "transaction_type": "EXPENSE", "transaction_date": "2026-09-18", "note": "Giao dịch test khóa ngoại"
        }, headers=headers)
        self.assertEqual(txn_res.status_code, 200)
        txn_id = txn_res.json()["id"]

        # Thử xóa ví -> Phải trả về 400 (Client error), TUYỆT ĐỐI KHÔNG trả về 500
        del_w_err = self.client.delete(f"/api/wallets/{w_id}", headers=headers)
        self.assertEqual(del_w_err.status_code, 400)
        self.assertIn("giao dịch", del_w_err.json()["detail"].lower())

        # Thử xóa danh mục -> Phải trả về 400 (Client error), TUYỆT ĐỐI KHÔNG trả về 500
        del_c_err = self.client.delete(f"/api/categories/{c_id}", headers=headers)
        self.assertEqual(del_c_err.status_code, 400)
        self.assertIn("giao dịch", del_c_err.json()["detail"].lower())

        # Xóa giao dịch vừa tạo
        self.assertEqual(self.client.delete(f"/api/transactions/{txn_id}", headers=headers).status_code, 200)

        # Case 2: Danh mục liên kết với Ngân sách (Budget)
        b_res = self.client.post("/api/budgets", json={"category_id": c_id, "limit_amount": 200000, "month_year": "2026-09"}, headers=headers)
        self.assertEqual(b_res.status_code, 200)
        b_id = b_res.json()["id"]

        # Thử xóa danh mục đang có budget -> 400
        del_c_b_err = self.client.delete(f"/api/categories/{c_id}", headers=headers)
        self.assertEqual(del_c_b_err.status_code, 400)
        self.assertIn("hạn mức", del_c_b_err.json()["detail"].lower())

        # Xóa budget
        self.assertEqual(self.client.delete(f"/api/budgets/{b_id}", headers=headers).status_code, 200)

        # Case 3: Ví liên kết với Sổ nợ (Debt)
        d_res = self.client.post("/api/debts", json={"debt_type": "BORROW", "person_name": "Sư Huynh", "amount": 300000, "wallet_id": w_id}, headers=headers)
        self.assertEqual(d_res.status_code, 200)
        d_id = d_res.json()["id"]

        # Thử xóa ví đang có debt -> 400
        del_w_d_err = self.client.delete(f"/api/wallets/{w_id}", headers=headers)
        self.assertEqual(del_w_d_err.status_code, 400)
        self.assertIn("nợ", del_w_d_err.json()["detail"].lower())

        # Xóa debt
        self.assertEqual(self.client.delete(f"/api/debts/{d_id}", headers=headers).status_code, 200)

        # Case 4: Ví và Danh mục liên kết với Định kỳ (Recurring)
        r_res = self.client.post("/api/recurring-transactions", json={
            "wallet_id": w_id, "category_id": c_id, "amount": 100000,
            "transaction_type": "EXPENSE", "frequency": "monthly", "next_run_date": "2026-10-18"
        }, headers=headers)
        self.assertEqual(r_res.status_code, 200)
        r_id = r_res.json()["id"]

        # Thử xóa ví -> 400
        self.assertEqual(self.client.delete(f"/api/wallets/{w_id}", headers=headers).status_code, 400)
        # Thử xóa danh mục -> 400
        self.assertEqual(self.client.delete(f"/api/categories/{c_id}", headers=headers).status_code, 400)

        # Xóa recurring
        self.assertEqual(self.client.delete(f"/api/recurring-transactions/{r_id}", headers=headers).status_code, 200)

        # Case 5: Sau khi xóa hết liên kết, xóa ví và danh mục thành công -> 200
        self.assertEqual(self.client.delete(f"/api/wallets/{w_id}", headers=headers).status_code, 200)
        self.assertEqual(self.client.delete(f"/api/categories/{c_id}", headers=headers).status_code, 200)

    # ──────────────────────────────────────────────
    # 13. BATCH-02.1: FINDING 2.3 — FORGOT-PASSWORD SECURITY & RATE LIMITING
    # ──────────────────────────────────────────────
    def test_18_forgot_password_security_and_rate_limiting(self):
        """Kiểm tra Finding 2.3:
        1. Yêu cầu bình thường thành công, không làm lộ reset_token qua HTTP response
        2. Chống lạm dụng / rate limiting: tối đa 5 lần trong 15 phút, lần thứ 6 trả về 429
        3. Luồng reset mật khẩu vẫn hoạt động trơn tru qua token hợp lệ lưu trong DB
        4. Chống dò tìm tài khoản (account enumeration): email không tồn tại trả về cùng lỗi 400 và cùng bị rate limit
        """
        email = "hardening_forgot_user@gmail.com"
        soul_lamp = "HardeningSoulLamp123"

        # 1. Đăng ký tài khoản
        reg = self.client.post("/api/auth/register", json={
            "email": email,
            "password": "initial_password_123",
            "full_name": "Tu Sĩ Bảo Mật",
            "soul_lamp": soul_lamp
        })
        self.assertEqual(reg.status_code, 200)

        # 2. Yêu cầu quên mật khẩu hợp lệ lần 1
        res1 = self.client.post("/api/auth/forgot-password", json={
            "email": email,
            "soul_lamp": soul_lamp
        })
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertNotIn("reset_token", data1, "Reset token KHÔNG được phép lộ trong normal response")
        self.assertIn("message", data1)
        self.assertEqual(data1.get("expires_in_minutes"), 30)

        # Kiểm tra token đã được lưu an toàn trong SQLite
        with main.get_db() as conn:
            token_row = conn.execute(
                "SELECT token FROM password_reset_tokens WHERE email = ? AND used = 0 ORDER BY id DESC LIMIT 1",
                (email,)
            ).fetchone()
            self.assertIsNotNone(token_row)
            valid_token = token_row["token"]
            self.assertEqual(len(valid_token), 6)

        # 3. Yêu cầu tiếp 4 lần nữa (tổng cộng 5 lần)
        for i in range(2, 6):
            res_i = self.client.post("/api/auth/forgot-password", json={
                "email": email,
                "soul_lamp": soul_lamp
            })
            self.assertEqual(res_i.status_code, 200)
            self.assertNotIn("reset_token", res_i.json())

        # 4. Lần thứ 6 -> Bị chặn bởi rate limiting (HTTP 429)
        res6 = self.client.post("/api/auth/forgot-password", json={
            "email": email,
            "soul_lamp": soul_lamp
        })
        self.assertEqual(res6.status_code, 429, "Lần thứ 6 trong 15 phút phải trả về HTTP 429")
        self.assertIn("quá nhiều lần", res6.json()["detail"].lower())

        # 5. Kiểm tra account enumeration: email không tồn tại trả về cùng lỗi 400
        fake_email = "nonexistent_victim_user_999@gmail.com"
        for j in range(1, 6):
            fake_res = self.client.post("/api/auth/forgot-password", json={
                "email": fake_email,
                "soul_lamp": "AnyRandomAnswer"
            })
            self.assertEqual(fake_res.status_code, 400)
            self.assertEqual(fake_res.json()["detail"], "Thông tin xác thực không chính xác, vui lòng kiểm tra lại")
            self.assertNotIn("reset_token", fake_res.json())

        # Lần thứ 6 với fake email cũng bị 429 (ngăn chặn kẻ tấn công dò tìm)
        fake_res6 = self.client.post("/api/auth/forgot-password", json={
            "email": fake_email,
            "soul_lamp": "AnyRandomAnswer"
        })
        self.assertEqual(fake_res6.status_code, 429)

        # 6. Luồng reset mật khẩu bằng valid_token vẫn hoàn thành xuất sắc
        new_pw = "new_hardened_pw_789"
        reset_res = self.client.post("/api/auth/reset-password", json={
            "email": email,
            "token": valid_token,
            "new_password": new_pw
        })
        self.assertEqual(reset_res.status_code, 200)

        # Đăng nhập với mật khẩu mới -> thành công
        login_res = self.client.post("/api/auth/login", json={
            "email": email,
            "password": new_pw
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("token", login_res.json())

    # ──────────────────────────────────────────────
    # 14. BATCH-02.1: FINDING 3.1 — JWT INVALIDATION AFTER PASSWORD CHANGE/RESET
    # ──────────────────────────────────────────────
    def test_19_jwt_invalidation_after_password_reset_and_change(self):
        """Kiểm tra Finding 3.1:
        1. JWT cấp trước khi reset mật khẩu bị vô hiệu hóa (401)
        2. JWT của user khác KHÔNG bị ảnh hưởng (vẫn 200)
        3. JWT mới cấp sau khi reset mật khẩu hoạt động bình thường (200)
        4. JWT cấp trước khi đổi mật khẩu (PUT /api/user/password) bị vô hiệu hóa (401)
        5. JWT mới cấp sau khi đổi mật khẩu hoạt động bình thường (200)
        """
        email_a = "user_invalidation_a@gmail.com"
        email_b = "user_invalidation_b@gmail.com"
        lamp_a = "LampSecretA_123"
        lamp_b = "LampSecretB_456"
        pw_a = "initial_pass_a_111"
        pw_b = "initial_pass_b_222"

        # 1. Tạo 2 người dùng A và B
        reg_a = self.client.post("/api/auth/register", json={
            "email": email_a, "password": pw_a, "full_name": "User A", "soul_lamp": lamp_a
        })
        self.assertEqual(reg_a.status_code, 200)
        token_a_old = reg_a.json()["token"]

        reg_b = self.client.post("/api/auth/register", json={
            "email": email_b, "password": pw_b, "full_name": "User B", "soul_lamp": lamp_b
        })
        self.assertEqual(reg_b.status_code, 200)
        token_b = reg_b.json()["token"]

        # Cả 2 token ban đầu đều truy cập được
        self.assertEqual(self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_a_old}"}).status_code, 200)
        self.assertEqual(self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_b}"}).status_code, 200)

        # 2. Reset mật khẩu của User A
        self.client.post("/api/auth/forgot-password", json={"email": email_a, "soul_lamp": lamp_a})
        with main.get_db() as conn:
            token_row = conn.execute(
                "SELECT token FROM password_reset_tokens WHERE email = ? AND used = 0 ORDER BY id DESC LIMIT 1",
                (email_a,)
            ).fetchone()
            reset_token_a = token_row["token"]

        pw_a_reset = "pass_a_after_reset_333"
        reset_res = self.client.post("/api/auth/reset-password", json={
            "email": email_a,
            "token": reset_token_a,
            "new_password": pw_a_reset
        })
        self.assertEqual(reset_res.status_code, 200)

        # KIỂM TRA 3.1.A: Token cũ của User A bị 401
        res_old_after_reset = self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_a_old}"})
        self.assertEqual(res_old_after_reset.status_code, 401)
        self.assertIn("hết hiệu lực", res_old_after_reset.json()["detail"].lower())

        # KIỂM TRA 3.1.B: Token của User B KHÔNG bị ảnh hưởng (vẫn 200)
        res_b_after_reset = self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(res_b_after_reset.status_code, 200)

        # KIỂM TRA 3.1.C: Đăng nhập mới User A với mật khẩu mới -> Token mới hoạt động bình thường (200)
        login_a1 = self.client.post("/api/auth/login", json={"email": email_a, "password": pw_a_reset})
        self.assertEqual(login_a1.status_code, 200)
        token_a_new1 = login_a1.json()["token"]
        self.assertEqual(self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_a_new1}"}).status_code, 200)

        # 3. Đổi mật khẩu chủ động qua API PUT /api/user/password
        pw_a_changed = "pass_a_after_change_444"
        # Đổi mật khẩu với mật khẩu hiện tại sai -> 400
        fail_change = self.client.put("/api/user/password", json={
            "current_password": "wrong_current_pass",
            "new_password": pw_a_changed
        }, headers={"Authorization": f"Bearer {token_a_new1}"})
        self.assertEqual(fail_change.status_code, 400)

        # Đổi mật khẩu với mật khẩu hiện tại đúng -> 200
        ok_change = self.client.put("/api/user/password", json={
            "current_password": pw_a_reset,
            "new_password": pw_a_changed
        }, headers={"Authorization": f"Bearer {token_a_new1}"})
        self.assertEqual(ok_change.status_code, 200)

        # KIỂM TRA 3.1.D: Token trước khi đổi mật khẩu bị 401
        res_old_after_change = self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_a_new1}"})
        self.assertEqual(res_old_after_change.status_code, 401)
        self.assertIn("hết hiệu lực", res_old_after_change.json()["detail"].lower())

        # KIỂM TRA 3.1.E: Token của User B vẫn không bị ảnh hưởng (200)
        self.assertEqual(self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_b}"}).status_code, 200)

        # KIỂM TRA 3.1.F: User A đăng nhập lại với pw_a_changed -> token mới hoạt động bình thường (200)
        login_a2 = self.client.post("/api/auth/login", json={"email": email_a, "password": pw_a_changed})
        self.assertEqual(login_a2.status_code, 200)
        token_a_new2 = login_a2.json()["token"]
        self.assertEqual(self.client.get("/api/user/profile", headers={"Authorization": f"Bearer {token_a_new2}"}).status_code, 200)

    # ──────────────────────────────────────────────
    # 15. BATCH-02.2: FINDING 2.2 — RECURRING TRANSACTION ROBUSTNESS
    # ──────────────────────────────────────────────
    def test_20_recurring_transaction_multiple_overdue_cycles_and_safety_limit(self):
        """Kiểm tra Finding 2.2:
        1. Xử lý toàn bộ các chu kỳ đã đến hạn trong cùng một lần gọi (multi-cycle processing).
        2. Cập nhật ngày thực thi tiếp theo chính xác sau mỗi chu kỳ.
        3. Không sinh trùng lặp giao dịch cho cùng một chu kỳ nếu chạy lại processor (idempotency).
        4. Áp dụng giới hạn an toàn tối đa 12 chu kỳ / lần gọi.
        """
        email = "recurring_multi_cycle_user@gmail.com"
        reg = self.client.post("/api/auth/register", json={
            "email": email, "password": "password123", "full_name": "Đạo Hữu Chu Kỳ", "soul_lamp": "SoulLampRec123"
        })
        self.assertEqual(reg.status_code, 200)
        token = reg.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg.json()["user_id"]

        # Lấy ví mặc định và danh mục mặc định
        w_res = self.client.get("/api/wallets", headers=headers)
        wallet = w_res.json()[0]
        w_id = wallet["id"]
        initial_balance = wallet["balance"]

        c_res = self.client.get("/api/categories", headers=headers)
        cat = [c for c in c_res.json() if c["category_type"] == "EXPENSE"][0]
        c_id = cat["id"]

        # 1. Tạo giao dịch định kỳ bị trễ đúng 3 tháng:
        today = datetime.date.today()
        y = today.year
        m = today.month - 3
        if m <= 0:
            m += 12
            y -= 1
        overdue_3_months_date = f"{y:04d}-{m:02d}-01"

        amount = 100000.0
        with main.get_db() as conn:
            conn.execute("""
                INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note)
                VALUES (?, ?, ?, ?, 'EXPENSE', 'monthly', ?, 'Thuê phòng tập tu')
            """, (user_id, w_id, c_id, amount, overdue_3_months_date))
            rec_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Gọi API trigger xử lý: GET /api/recurring-transactions
        res_rec = self.client.get("/api/recurring-transactions", headers=headers)
        self.assertEqual(res_rec.status_code, 200)

        # Kiểm tra: Tất cả các chu kỳ quá hạn đã được xử lý trong cùng 1 lần gọi
        with main.get_db() as conn:
            txns = conn.execute("""
                SELECT * FROM transactions WHERE user_id = ? AND note = 'Thuê phòng tập tu' ORDER BY transaction_date ASC
            """, (user_id,)).fetchall()
            num_cycles = len(txns)
            self.assertGreaterEqual(num_cycles, 3)

            # Số dư ví phải giảm tương ứng với số chu kỳ đã xử lý
            updated_wallet = conn.execute("SELECT balance FROM wallets WHERE id = ?", (w_id,)).fetchone()
            expected_balance = initial_balance - (num_cycles * amount)
            self.assertEqual(updated_wallet["balance"], expected_balance)

            # next_run_date trong recurring_transactions phải được đẩy vào tương lai (> today)
            rec_row = conn.execute("SELECT next_run_date FROM recurring_transactions WHERE id = ?", (rec_id,)).fetchone()
            self.assertGreater(rec_row["next_run_date"], today.strftime("%Y-%m-%d"))

        # 2. Kiểm tra tính IDEMPOTENT (không sinh trùng lặp nếu chạy lại):
        res_rec_2 = self.client.get("/api/recurring-transactions", headers=headers)
        self.assertEqual(res_rec_2.status_code, 200)
        with main.get_db() as conn:
            txns_after = conn.execute("""
                SELECT * FROM transactions WHERE user_id = ? AND note = 'Thuê phòng tập tu'
            """, (user_id,)).fetchall()
            self.assertEqual(len(txns_after), num_cycles, "Không được sinh giao dịch trùng lặp khi chạy lại processor")

        # 3. Kiểm tra GIỚI HẠN AN TOÀN TỐI ĐA 12 CHU KỲ (Safety Limit):
        very_old_date = f"{today.year - 2:04d}-{today.month:02d}-01"
        with main.get_db() as conn:
            conn.execute("""
                INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note)
                VALUES (?, ?, ?, 50000, 'EXPENSE', 'monthly', ?, 'Phí gia hạn thẻ 2 năm')
            """, (user_id, w_id, c_id, very_old_date))
            limit_rec_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Gọi xử lý
        self.assertEqual(self.client.get("/api/recurring-transactions", headers=headers).status_code, 200)

        with main.get_db() as conn:
            limit_txns = conn.execute("""
                SELECT * FROM transactions WHERE user_id = ? AND note = 'Phí gia hạn thẻ 2 năm'
            """, (user_id,)).fetchall()
            self.assertEqual(len(limit_txns), 12, "Giới hạn an toàn tối đa 12 chu kỳ phải được thực thi nghiêm ngặt")

    def test_21_recurring_transaction_foreign_key_fault_tolerance_and_reports_stability(self):
        """Kiểm tra Finding 2.2:
        1. Một bản ghi định kỳ có khóa ngoại sai/stale (wallet_id hoặc category_id không tồn tại)
           tuyệt đối KHÔNG làm sập tiến trình (không sinh HTTP 500).
        2. Các bản ghi định kỳ hợp lệ khác vẫn được xử lý bình thường.
        3. Các endpoint báo cáo/dashboard (GET /api/reports/summary, GET /api/recurring-transactions)
           vẫn ổn định và trả về HTTP 200.
        4. Foreign keys của SQLite tiếp tục được bảo toàn và thực thi nghiêm ngặt.
        """
        email = "recurring_fault_tolerant_user@gmail.com"
        reg = self.client.post("/api/auth/register", json={
            "email": email, "password": "password123", "full_name": "Đạo Hữu Chịu Lỗi", "soul_lamp": "SoulLampFault123"
        })
        self.assertEqual(reg.status_code, 200)
        token = reg.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg.json()["user_id"]

        w_res = self.client.get("/api/wallets", headers=headers)
        valid_wallet_id = w_res.json()[0]["id"]
        c_res = self.client.get("/api/categories", headers=headers)
        valid_cat_id = c_res.json()[0]["id"]

        today_str = datetime.date.today().strftime("%Y-%m-%d")

        # 1. Chèn trực tiếp một bản ghi định kỳ CÓ KHÓA NGOẠI KHÔNG HỢP LỆ (wallet_id 999999 không tồn tại)
        # Tạm thời tắt foreign keys chỉ để chèn bản ghi lỗi mô phỏng dữ liệu cũ/hỏng trong DB
        with main.get_db() as conn:
            conn.execute("PRAGMA foreign_keys=OFF")
            conn.execute("""
                INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note)
                VALUES (?, 999999, ?, 200000, 'EXPENSE', 'monthly', ?, 'Bản ghi định kỳ lỗi khóa ngoại')
            """, (user_id, valid_cat_id, today_str))
            conn.execute("PRAGMA foreign_keys=ON")

            # Đồng thời có một bản ghi định kỳ HỢP LỆ
            conn.execute("""
                INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note)
                VALUES (?, ?, ?, 77000, 'INCOME', 'weekly', ?, 'Lương hợp lệ hàng tuần')
            """, (user_id, valid_wallet_id, valid_cat_id, today_str))

        # 2. Gọi GET /api/reports/summary: KHÔNG ĐƯỢC CRASH HTTP 500
        rep_res = self.client.get("/api/reports/summary", headers=headers)
        self.assertEqual(rep_res.status_code, 200, "Báo cáo không được sập 500 do bản ghi định kỳ hỏng")
        rep_data = rep_res.json()
        self.assertIn("total_income", rep_data)

        # 3. Gọi GET /api/recurring-transactions: KHÔNG ĐƯỢC CRASH HTTP 500
        rec_list_res = self.client.get("/api/recurring-transactions", headers=headers)
        self.assertEqual(rec_list_res.status_code, 200, "API danh sách định kỳ không được sập 500")

        # 4. Xác nhận bản ghi HỢP LỆ đã được xử lý thành công
        with main.get_db() as conn:
            valid_txn = conn.execute("""
                SELECT * FROM transactions WHERE user_id = ? AND note = 'Lương hợp lệ hàng tuần'
            """, (user_id,)).fetchone()
            self.assertIsNotNone(valid_txn, "Bản ghi hợp lệ phải được xử lý thành công ngay cả khi có bản ghi khác bị lỗi")
            self.assertEqual(valid_txn["amount"], 77000)

            # Bản ghi lỗi không tạo giao dịch (không làm sai lệch dữ liệu tài chính)
            invalid_txn = conn.execute("""
                SELECT * FROM transactions WHERE user_id = ? AND note = 'Bản ghi định kỳ lỗi khóa ngoại'
            """, (user_id,)).fetchone()
            self.assertIsNone(invalid_txn, "Bản ghi lỗi không được phép sinh giao dịch rác")

            # Kiểm tra foreign keys vẫn đang được bật trên SQLite
            fk_state = conn.execute("PRAGMA foreign_keys").fetchone()[0]
            self.assertEqual(fk_state, 1, "Ràng buộc khóa ngoại của SQLite phải luôn được duy trì bật (ON)")

    # ──────────────────────────────────────────────
    # 15. BATCH-03.1: FINDING 2.1 — TRANSFER & SAVING GOAL AUDIT TRAIL
    # ──────────────────────────────────────────────
    def test_22_transfer_audit_trail_and_balance_integrity(self):
        """Kiểm tra Finding 2.1:
        1. Chuyển tiền giữa 2 ví cập nhật chính xác số dư cả 2 ví.
        2. Tự động sinh đầy đủ 2 bản ghi lịch sử giao dịch (1 EXPENSE từ ví nguồn, 1 INCOME tới ví đích).
        3. Phân biệt ngữ nghĩa xuất/nhập tiền, liên kết đúng danh mục và ghi chú ví đối ứng.
        4. Danh sách GET /api/transactions hiển thị đúng các bản ghi chuyển tiền.
        """
        email = "transfer_audit_user@gmail.com"
        reg = self.client.post("/api/auth/register", json={
            "email": email, "password": "password123", "full_name": "Đạo Hữu Chuyển Linh", "soul_lamp": "SoulLampXfer123"
        })
        self.assertEqual(reg.status_code, 200)
        token = reg.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg.json()["user_id"]

        wallets = self.client.get("/api/wallets", headers=headers).json()
        w_from = wallets[0]
        w_to = wallets[1]
        w_from_init = w_from["balance"]
        w_to_init = w_to["balance"]
        transfer_amount = 350000

        # Thực hiện chuyển tiền có note và operation_id
        op_id = "op-transfer-audit-001"
        res = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w_from["id"],
            "to_wallet_id": w_to["id"],
            "amount": transfer_amount,
            "note": "Mua đan dược Bách Thảo",
            "operation_id": op_id
        }, headers=headers)
        self.assertEqual(res.status_code, 200)
        res_data = res.json()
        self.assertIn("message", res_data)
        self.assertEqual(res_data["amount"], transfer_amount)

        # 1. Kiểm tra số dư ví được cập nhật chính xác
        wallets_after = self.client.get("/api/wallets", headers=headers).json()
        w_from_after = next(w for w in wallets_after if w["id"] == w_from["id"])
        w_to_after = next(w for w in wallets_after if w["id"] == w_to["id"])
        self.assertEqual(w_from_after["balance"], w_from_init - transfer_amount)
        self.assertEqual(w_to_after["balance"], w_to_init + transfer_amount)

        # 2. Kiểm tra bản ghi trong bảng transactions (2 chiều đầy đủ)
        with main.get_db() as conn:
            txns = conn.execute("""
                SELECT t.*, c.category_name, c.category_type as cat_type
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.operation_id = ?
                ORDER BY t.id ASC
            """, (user_id, op_id)).fetchall()

            self.assertEqual(len(txns), 2, "Chuyển tiền phải tạo đúng 2 bản ghi giao dịch (chiều xuất và chiều nhập)")

            # Chiều xuất tiền (EXPENSE)
            t_out = txns[0]
            self.assertEqual(t_out["wallet_id"], w_from["id"])
            self.assertEqual(t_out["amount"], transfer_amount)
            self.assertEqual(t_out["transaction_type"], "EXPENSE")
            self.assertEqual(t_out["cat_type"], "EXPENSE")
            self.assertIn(w_to["wallet_name"], t_out["note"])
            self.assertIn("Mua đan dược Bách Thảo", t_out["note"])

            # Chiều nhập tiền (INCOME)
            t_in = txns[1]
            self.assertEqual(t_in["wallet_id"], w_to["id"])
            self.assertEqual(t_in["amount"], transfer_amount)
            self.assertEqual(t_in["transaction_type"], "INCOME")
            self.assertEqual(t_in["cat_type"], "INCOME")
            self.assertIn(w_from["wallet_name"], t_in["note"])
            self.assertIn("Mua đan dược Bách Thảo", t_in["note"])

        # 3. Kiểm tra GET /api/transactions trả về đúng
        list_res = self.client.get("/api/transactions", headers=headers)
        self.assertEqual(list_res.status_code, 200)
        items = list_res.json()["data"]
        op_items = [i for i in items if i.get("operation_id") == op_id]
        self.assertEqual(len(op_items), 2)

    def test_23_transfer_idempotency_and_duplicate_prevention(self):
        """Kiểm tra Finding 2.1:
        1. Gọi lại API chuyển tiền với cùng operation_id không làm trừ/cộng thêm số dư.
        2. Không tạo thêm giao dịch trùng lặp trong cơ sở dữ liệu.
        3. Chống lặp nhanh (rapid duplicate invocation) khi không có operation_id.
        """
        email = "transfer_idempotent_user@gmail.com"
        reg = self.client.post("/api/auth/register", json={
            "email": email, "password": "password123", "full_name": "Đạo Hữu Chống Trùng", "soul_lamp": "SoulLampIdemp123"
        })
        self.assertEqual(reg.status_code, 200)
        token = reg.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg.json()["user_id"]

        wallets = self.client.get("/api/wallets", headers=headers).json()
        w1_id, w2_id = wallets[0]["id"], wallets[1]["id"]
        op_key = "idemp-transfer-unique-999"

        # Lần gọi 1
        res1 = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w1_id, "to_wallet_id": w2_id, "amount": 100000,
            "note": "Chuyển tiền thử nghiệm", "operation_id": op_key
        }, headers=headers)
        self.assertEqual(res1.status_code, 200)

        w1_bal_after_1 = next(w for w in self.client.get("/api/wallets", headers=headers).json() if w["id"] == w1_id)["balance"]

        # Lần gọi 2 (retry với cùng operation_id)
        res2 = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w1_id, "to_wallet_id": w2_id, "amount": 100000,
            "note": "Chuyển tiền thử nghiệm", "operation_id": op_key
        }, headers=headers)
        self.assertEqual(res2.status_code, 200)

        # Số dư không được thay đổi thêm
        w1_bal_after_2 = next(w for w in self.client.get("/api/wallets", headers=headers).json() if w["id"] == w1_id)["balance"]
        self.assertEqual(w1_bal_after_1, w1_bal_after_2, "Gọi lại cùng operation_id không được trừ tiền ví lần 2")

        # Số giao dịch với op_key này vẫn là 2
        with main.get_db() as conn:
            cnt = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ? AND operation_id = ?", (user_id, op_key)).fetchone()[0]
            self.assertEqual(cnt, 2, "Gọi lại cùng operation_id không được nhân bản lịch sử giao dịch")

        # Test chống lặp nhanh khi không truyền operation_id
        res_fast1 = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w1_id, "to_wallet_id": w2_id, "amount": 50000, "note": "Chuyển nhanh"
        }, headers=headers)
        self.assertEqual(res_fast1.status_code, 200)

        # Ngay lập tức gọi lại cùng payload
        res_fast2 = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w1_id, "to_wallet_id": w2_id, "amount": 50000, "note": "Chuyển nhanh"
        }, headers=headers)
        self.assertEqual(res_fast2.status_code, 200)

        with main.get_db() as conn:
            fast_txns = conn.execute("""
                SELECT COUNT(*) FROM transactions WHERE user_id = ? AND note LIKE '%Chuyển nhanh%'
            """, (user_id,)).fetchone()[0]
            self.assertEqual(fast_txns, 2, "Thao tác gửi liên tiếp ngay lập tức không được tạo bản ghi trùng lặp")

    def test_24_saving_goal_deposit_audit_trail_and_balance_integrity(self):
        """Kiểm tra Finding 2.1:
        1. Nạp tiền vào mục tiêu tiết kiệm trừ số dư ví và tăng current_amount.
        2. Tự động sinh bản ghi lịch sử giao dịch EXPENSE cho ví nạp với danh mục Mục Tiêu Tiết Kiệm.
        3. Chống trùng lặp (Idempotency) khi nạp tiền lặp lại cùng operation_id.
        """
        email = "goal_audit_user@gmail.com"
        reg = self.client.post("/api/auth/register", json={
            "email": email, "password": "password123", "full_name": "Đạo Hữu Tiết Kiệm", "soul_lamp": "SoulLampGoalAudit123"
        })
        self.assertEqual(reg.status_code, 200)
        token = reg.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg.json()["user_id"]

        wallets = self.client.get("/api/wallets", headers=headers).json()
        w = wallets[0]
        w_init = w["balance"]

        # Tạo mục tiêu tiết kiệm
        goal_res = self.client.post("/api/saving-goals", json={
            "target_name": "Tích lũy mua Đan Lò Cực Phẩm",
            "target_amount": 10000000,
            "current_amount": 1000000
        }, headers=headers)
        self.assertEqual(goal_res.status_code, 200)
        goal_id = goal_res.json()["id"]

        dep_amt = 1500000
        op_dep_id = "op-dep-goal-001"

        # Nạp tiền từ ví
        dep_res = self.client.post(f"/api/saving-goals/{goal_id}/deposit", json={
            "amount": dep_amt,
            "wallet_id": w["id"],
            "operation_id": op_dep_id
        }, headers=headers)
        self.assertEqual(dep_res.status_code, 200)
        self.assertEqual(dep_res.json()["current_amount"], 2500000)

        # Kiểm tra ví bị trừ tiền
        w_after = next(x for x in self.client.get("/api/wallets", headers=headers).json() if x["id"] == w["id"])
        self.assertEqual(w_after["balance"], w_init - dep_amt)

        # Kiểm tra bản ghi trong bảng transactions
        with main.get_db() as conn:
            txn = conn.execute("""
                SELECT t.*, c.category_name, c.icon as cat_icon
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.operation_id = ?
            """, (user_id, op_dep_id)).fetchone()

            self.assertIsNotNone(txn, "Phải ghi nhận 1 bản ghi giao dịch EXPENSE khi nạp tiền vào mục tiêu từ ví")
            self.assertEqual(txn["wallet_id"], w["id"])
            self.assertEqual(txn["amount"], dep_amt)
            self.assertEqual(txn["transaction_type"], "EXPENSE")
            self.assertEqual(txn["category_name"], "Mục Tiêu Tiết Kiệm")
            self.assertEqual(txn["cat_icon"], "🎯")
            self.assertIn("Tích lũy mua Đan Lò Cực Phẩm", txn["note"])

        # Kiểm tra gọi lại với cùng operation_id không làm tăng thêm tiền hoặc tạo thêm giao dịch
        dep_res2 = self.client.post(f"/api/saving-goals/{goal_id}/deposit", json={
            "amount": dep_amt,
            "wallet_id": w["id"],
            "operation_id": op_dep_id
        }, headers=headers)
        self.assertEqual(dep_res2.status_code, 200)
        self.assertEqual(dep_res2.json()["current_amount"], 2500000)

        w_after2 = next(x for x in self.client.get("/api/wallets", headers=headers).json() if x["id"] == w["id"])
        self.assertEqual(w_after2["balance"], w_init - dep_amt, "Gọi lại cùng operation_id không được trừ tiền ví lần nữa")

    def test_25_transfer_and_deposit_security_ownership_and_atomic_rollback(self):
        """Kiểm tra Finding 2.1:
        1. User A không thể chuyển tiền từ hoặc đến ví của User B (chống IDOR).
        2. User A không thể nạp tiền từ ví của User B vào mục tiêu của mình.
        3. Số tiền <= 0 hoặc vượt quá số dư bị từ chối với HTTP 400, không thay đổi số dư và không sinh giao dịch.
        4. Tính nguyên tử (Atomicity): Lỗi giữa chừng (rollback) không để lại dữ liệu dở dang.
        5. Lịch sử giao dịch thông thường và báo cáo tiếp tục hoạt động hoàn hảo.
        """
        # Đăng ký User A
        reg_a = self.client.post("/api/auth/register", json={
            "email": "user_a_xfer@gmail.com", "password": "password123", "full_name": "User A", "soul_lamp": "SoulLampA"
        })
        headers_a = {"Authorization": f"Bearer {reg_a.json()['token']}"}
        w_a = self.client.get("/api/wallets", headers=headers_a).json()[0]["id"]

        # Đăng ký User B
        reg_b = self.client.post("/api/auth/register", json={
            "email": "user_b_xfer@gmail.com", "password": "password123", "full_name": "User B", "soul_lamp": "SoulLampB"
        })
        headers_b = {"Authorization": f"Bearer {reg_b.json()['token']}"}
        w_b = self.client.get("/api/wallets", headers=headers_b).json()[0]["id"]
        w_b_init_bal = self.client.get("/api/wallets", headers=headers_b).json()[0]["balance"]

        # 1. User A cố chuyển tiền từ ví của User B -> 404
        idor_res_1 = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w_b, "to_wallet_id": w_a, "amount": 100000
        }, headers=headers_a)
        self.assertEqual(idor_res_1.status_code, 404)

        # 2. User A cố chuyển tiền vào ví của User B -> 404
        idor_res_2 = self.client.post("/api/wallets/transfer", json={
            "from_wallet_id": w_a, "to_wallet_id": w_b, "amount": 100000
        }, headers=headers_a)
        self.assertEqual(idor_res_2.status_code, 404)

        # Số dư User B không đổi
        self.assertEqual(self.client.get("/api/wallets", headers=headers_b).json()[0]["balance"], w_b_init_bal)

        # 3. User A cố nạp tiền từ ví User B vào mục tiêu của User A -> 404
        goal_a = self.client.post("/api/saving-goals", json={"target_name": "Goal A", "target_amount": 1000000}, headers=headers_a).json()["id"]
        idor_dep = self.client.post(f"/api/saving-goals/{goal_a}/deposit", json={"amount": 100000, "wallet_id": w_b}, headers=headers_a)
        self.assertEqual(idor_dep.status_code, 404)

        # 4. Kiểm tra số tiền không hợp lệ:
        err_amt_0 = self.client.post("/api/wallets/transfer", json={"from_wallet_id": w_a, "to_wallet_id": w_a, "amount": 100000}, headers=headers_a)
        self.assertEqual(err_amt_0.status_code, 400, "Không được chuyển cho chính mình")

        err_amt_neg = self.client.post("/api/wallets/transfer", json={"from_wallet_id": w_a, "to_wallet_id": w_b, "amount": -100}, headers=headers_a)
        self.assertEqual(err_amt_neg.status_code, 400, "Số tiền âm phải bị từ chối")

        err_dep_neg = self.client.post(f"/api/saving-goals/{goal_a}/deposit", json={"amount": -50, "wallet_id": w_a}, headers=headers_a)
        self.assertEqual(err_dep_neg.status_code, 400, "Số tiền nạp âm phải bị từ chối")

        err_dep_exceed = self.client.post(f"/api/saving-goals/{goal_a}/deposit", json={"amount": 9999999999, "wallet_id": w_a}, headers=headers_a)
        self.assertEqual(err_dep_exceed.status_code, 400, "Nạp vượt quá số dư ví phải bị từ chối")

        # 5. Kiểm tra tính nguyên tử (Atomicity & Rollback):
        # Giả lập lỗi DB giữa chừng và xác nhận conn.rollback() trong get_db bảo toàn số dư
        with self.assertRaises(Exception):
            with main.get_db() as conn:
                conn.execute("UPDATE wallets SET balance = balance - 123456 WHERE id = ?", (w_a,))
                # Gây lỗi cưỡng bức
                raise RuntimeError("Mô phỏng lỗi đột ngột giữa chừng")

        # Số dư sau exception phải giữ nguyên hoàn toàn (đã rollback)
        current_w_a_bal = next(w for w in self.client.get("/api/wallets", headers=headers_a).json() if w["id"] == w_a)["balance"]
        self.assertNotEqual(current_w_a_bal, w_b_init_bal - 123456)

    # ──────────────────────────────────────────────
    # 14. BATCH-03.2: OCR / AI HARDENING (FINDING 3.2)
    # ──────────────────────────────────────────────
    def test_26_ocr_upload_valid_success(self):
        """1. Valid supported OCR upload succeeds, parses schema, and persists to DB."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        valid_ai_response = json.dumps({
            "store_name": "Nhà Thuốc Vạn Thọ Đường",
            "total_amount": 250000,
            "date": "2026-03-20",
            "currency": "VND",
            "items": [
                {"name": "Linh Thảo Tiên Đan", "price": 250000, "quantity": 1}
            ]
        })

        image_bytes = io.BytesIO(b"\xff\xd8\xff\xe0" + b"fake_valid_jpeg_payload")
        files = {"file": ("receipt.jpg", image_bytes, "image/jpeg")}

        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = valid_ai_response
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["store_name"], "Nhà Thuốc Vạn Thọ Đường")
        self.assertEqual(data["data"]["total_amount"], 250000)
        self.assertEqual(data["data"]["date"], "2026-03-20")
        self.assertEqual(len(data["data"]["items"]), 1)

        # Kiểm tra bản ghi đã được ghi vào invoice_ocr_logs
        with main.get_db() as conn:
            log = conn.execute(
                "SELECT * FROM invoice_ocr_logs WHERE user_id = 1 AND image_path = 'receipt.jpg' ORDER BY id DESC LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(log)
            self.assertIn("Nhà Thuốc Vạn Thọ Đường", log["extracted_json"])

    def test_27_ocr_upload_size_limit_early_rejection(self):
        """2. Oversized OCR upload is rejected with HTTP 413, no DB records created."""
        from unittest.mock import patch
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        # Giả lập MAX_OCR_FILE_SIZE = 1024 bytes (1 KB)
        with patch.dict(os.environ, {"MAX_OCR_FILE_SIZE": "1024"}):
            oversized_bytes = io.BytesIO(b"A" * 2048)
            files = {"file": ("huge_receipt.png", oversized_bytes, "image/png")}
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 413)
        self.assertIn("vượt quá giới hạn", res.json()["detail"])

        # Kiểm tra không có log nào trong DB
        with main.get_db() as conn:
            log = conn.execute(
                "SELECT * FROM invoice_ocr_logs WHERE image_path = 'huge_receipt.png'"
            ).fetchone()
            self.assertIsNone(log)

    def test_28_ocr_unsupported_mime_and_extension_rejected(self):
        """3. Unsupported MIME / file types are rejected with HTTP 415."""
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. PDF file
        pdf_file = io.BytesIO(b"%PDF-1.4...")
        res_pdf = self.client.post("/api/ai/scan-invoice", files={"file": ("invoice.pdf", pdf_file, "application/pdf")}, headers=headers)
        self.assertEqual(res_pdf.status_code, 415)

        # 2. EXE file disguised as octet-stream
        exe_file = io.BytesIO(b"MZ...")
        res_exe = self.client.post("/api/ai/scan-invoice", files={"file": ("invoice.exe", exe_file, "application/octet-stream")}, headers=headers)
        self.assertEqual(res_exe.status_code, 415)

        # 3. TXT file disguised as image/jpeg
        txt_file = io.BytesIO(b"Text file content")
        res_txt = self.client.post("/api/ai/scan-invoice", files={"file": ("invoice.txt", txt_file, "image/jpeg")}, headers=headers)
        self.assertEqual(res_txt.status_code, 415)

        # 4. PNG file with text/plain MIME type
        png_txt = io.BytesIO(b"dummy")
        res_png_txt = self.client.post("/api/ai/scan-invoice", files={"file": ("invoice.png", png_txt, "text/plain")}, headers=headers)
        self.assertEqual(res_png_txt.status_code, 415)

    def test_29_ocr_empty_file_rejected(self):
        """4. Empty (0-byte) upload is rejected with HTTP 400."""
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        empty_file = io.BytesIO(b"")
        res = self.client.post("/api/ai/scan-invoice", files={"file": ("empty.jpg", empty_file, "image/jpeg")}, headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn("không được rỗng", res.json()["detail"])

    def test_30_ocr_malformed_gemini_json_rejected(self):
        """5. Malformed Gemini JSON is rejected with HTTP 422, zero DB records."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        image_bytes = io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy")
        files = {"file": ("malformed.jpg", image_bytes, "image/jpeg")}

        # Test case A: Broken JSON string
        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = "```json\n{ store_name: invalid json without closing"
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 422)

        # Test case B: Empty string response from Gemini
        files["file"] = ("malformed.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")
        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = ""
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 422)

        # Verify no record created
        with main.get_db() as conn:
            log = conn.execute("SELECT * FROM invoice_ocr_logs WHERE image_path = 'malformed.jpg'").fetchone()
            self.assertIsNone(log)

    def test_31_ocr_semantic_not_a_receipt_rejected(self):
        """6. Semantic non-receipt statuses such as {"status": "not a receipt"} are rejected with HTTP 422."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        invalid_payloads = [
            json.dumps({"status": "not a receipt"}),
            json.dumps({"status": "not_receipt"}),
            json.dumps({"status": "invalid"}),
            json.dumps({"is_receipt": False}),
            json.dumps({"is_invoice": False}),
            json.dumps({"error": "No receipt detected in image"}),
            json.dumps({"status": "not a receipt", "store_name": "Quán Trà", "total_amount": 50000, "date": "2026-03-20", "items": []})
        ]

        for payload in invalid_payloads:
            files = {"file": ("not_receipt.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}
            with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
                mock_gemini.return_value = payload
                res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

            self.assertEqual(res.status_code, 422, f"Failed for payload: {payload}")

        with main.get_db() as conn:
            log = conn.execute("SELECT * FROM invoice_ocr_logs WHERE image_path = 'not_receipt.jpg'").fetchone()
            self.assertIsNone(log, "Semantic rejection must never persist a database record")

    def test_32_ocr_missing_required_fields_rejected(self):
        """7. Missing required OCR fields (store_name, total_amount, date, items) return HTTP 422."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        # Missing store_name
        p_no_store = json.dumps({"total_amount": 100000, "date": "2026-03-20", "items": []})
        # Missing total_amount
        p_no_amount = json.dumps({"store_name": "Tiệm Thuốc", "date": "2026-03-20", "items": []})
        # Missing date
        p_no_date = json.dumps({"store_name": "Tiệm Thuốc", "total_amount": 100000, "items": []})
        # Missing items
        p_no_items = json.dumps({"store_name": "Tiệm Thuốc", "total_amount": 100000, "date": "2026-03-20"})

        for payload in [p_no_store, p_no_amount, p_no_date, p_no_items]:
            files = {"file": ("missing.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}
            with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
                mock_gemini.return_value = payload
                res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)
            self.assertEqual(res.status_code, 422)

        with main.get_db() as conn:
            log = conn.execute("SELECT * FROM invoice_ocr_logs WHERE image_path = 'missing.jpg'").fetchone()
            self.assertIsNone(log)

    def test_33_ocr_wrong_field_types_rejected(self):
        """8. Incorrect data types (string amount, boolean amount, negative amount, bad date) return HTTP 422."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        bad_type_payloads = [
            # String amount instead of number
            {"store_name": "Tiệm Thuốc", "total_amount": "hai tram ngan", "date": "2026-03-20", "items": []},
            # Boolean amount (isinstance(True, int) is True in Python, must be explicitly guarded)
            {"store_name": "Tiệm Thuốc", "total_amount": True, "date": "2026-03-20", "items": []},
            # Negative amount
            {"store_name": "Tiệm Thuốc", "total_amount": -50000, "date": "2026-03-20", "items": []},
            # Invalid date string
            {"store_name": "Tiệm Thuốc", "total_amount": 50000, "date": "ngay-mai-2026", "items": []},
            # Items is not a list
            {"store_name": "Tiệm Thuốc", "total_amount": 50000, "date": "2026-03-20", "items": "mot goi thuoc"},
            # Item element is not a dict or missing name
            {"store_name": "Tiệm Thuốc", "total_amount": 50000, "date": "2026-03-20", "items": ["invalid_item"]},
            # Item element has negative price
            {"store_name": "Tiệm Thuốc", "total_amount": 50000, "date": "2026-03-20", "items": [{"name": "Gói A", "price": -100, "quantity": 1}]},
        ]

        for p in bad_type_payloads:
            files = {"file": ("bad_type.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}
            with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
                mock_gemini.return_value = json.dumps(p)
                res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)
            self.assertEqual(res.status_code, 422, f"Failed for bad payload: {p}")

        with main.get_db() as conn:
            log = conn.execute("SELECT * FROM invoice_ocr_logs WHERE image_path = 'bad_type.jpg'").fetchone()
            self.assertIsNone(log)

    def test_34_ocr_gemini_api_failure_handled_safely(self):
        """9. Gemini / API failure does not leak internal secrets and does not create DB records."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        files = {"file": ("api_fail.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}

        # Simulate exception from Gemini API with sensitive key in message
        secret_leak_msg = "Google API call failed: 403 Forbidden, key=AIzaSySecretApiKey12345, internal endpoint https://internal.google.com"
        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.side_effect = RuntimeError(secret_leak_msg)
            res = self.client.post("/api/ai/scan-invoice", files=files, headers=headers)

        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertNotIn("AIzaSySecretApiKey12345", str(data), "Internal API secrets must never leak to client")
        self.assertNotIn("https://internal.google.com", str(data), "Internal URLs must never leak to client")

        with main.get_db() as conn:
            log = conn.execute("SELECT * FROM invoice_ocr_logs WHERE image_path = 'api_fail.jpg'").fetchone()
            self.assertIsNone(log)

    def test_35_ocr_authentication_required(self):
        """10. Unauthenticated OCR request is rejected with HTTP 401."""
        files = {"file": ("auth_test.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}
        res = self.client.post("/api/ai/scan-invoice", files=files)
        self.assertEqual(res.status_code, 401)

    def test_36_ocr_persists_only_on_valid_result(self):
        """11. Verify DB record count for invoice_ocr_logs increases strictly by 1 on success and 0 on failure."""
        from unittest.mock import patch, AsyncMock
        token = create_token(user_id=1, email="admin@gmail.com", role="admin")
        headers = {"Authorization": f"Bearer {token}"}

        with main.get_db() as conn:
            count_before = conn.execute("SELECT COUNT(*) FROM invoice_ocr_logs").fetchone()[0]

        # 1. Failed request -> count does not change
        files_fail = {"file": ("fail_count.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}
        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = json.dumps({"status": "not a receipt"})
            res_fail = self.client.post("/api/ai/scan-invoice", files=files_fail, headers=headers)
        self.assertEqual(res_fail.status_code, 422)

        with main.get_db() as conn:
            count_after_fail = conn.execute("SELECT COUNT(*) FROM invoice_ocr_logs").fetchone()[0]
        self.assertEqual(count_after_fail, count_before)

        # 2. Successful request -> count increases by exactly 1
        valid_json = json.dumps({
            "store_name": "Tiệm Bánh Ngọt Trúc Diệp",
            "total_amount": 88000,
            "date": "2026-03-21",
            "currency": "VND",
            "items": [{"name": "Bánh Trà Xanh", "price": 88000, "quantity": 1}]
        })
        files_ok = {"file": ("ok_count.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"dummy"), "image/jpeg")}
        with patch("main.generate_gemini_content_async", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = valid_json
            res_ok = self.client.post("/api/ai/scan-invoice", files=files_ok, headers=headers)
        self.assertEqual(res_ok.status_code, 200)

        with main.get_db() as conn:
            count_after_ok = conn.execute("SELECT COUNT(*) FROM invoice_ocr_logs").fetchone()[0]
        self.assertEqual(count_after_ok, count_before + 1)

    # ──────────────────────────────────────────────
    # 12. AI AGENT & FINANCIAL TOOLS TESTS (P0 & P1)
    # ──────────────────────────────────────────────
    def _setup_ai_agent_test_env(self):
        """Helper khởi tạo môi trường thử nghiệm độc lập cho AI Agent"""
        from ai_agent import AgentCore, MockAIProvider, build_default_tool_registry
        with main.get_db() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (99, 'ai_tester@gmail.com', 'dummy_hash', 'Tu Sĩ AI', 'user')")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (991, 99, 'Ví Tiền Mặt', 'CASH', 2000000)")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (992, 99, 'Ví Ngân Hàng', 'BANK', 5000000)")
            conn.execute("INSERT OR REPLACE INTO saving_goals (id, user_id, target_name, target_amount, current_amount) VALUES (991, 99, 'Mua Laptop', 20000000, 2000000)")

        token = create_token(user_id=99, email="ai_tester@gmail.com", role="user")
        headers = {"Authorization": f"Bearer {token}"}
        mock_provider = MockAIProvider(default_response="Tiên Trí đã lắng nghe đạo hữu.")
        test_core = AgentCore(provider=mock_provider, registry=build_default_tool_registry())
        main.set_agent_core(test_core)
        return headers, test_core

    def test_37_ai_read_requests(self):
        """1. AI Agent: Tra cứu số dư ví qua Read Tool (get_wallets)"""
        headers, _ = self._setup_ai_agent_test_env()
        res = self.client.post("/api/ai/chat", json={"message": "Ví còn bao nhiêu tiền?"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "get_wallets")
        self.assertIn("Ví Tiền Mặt", str(data["tool_result"]))

    def test_38_ai_expense_creation_confirmation_flow(self):
        """2 & 6. AI Agent: Ghi nhận chi tiêu qua luồng xác nhận bắt buộc"""
        headers, _ = self._setup_ai_agent_test_env()
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]

        # Bước 1: Yêu cầu chi tiêu -> Trạng thái CONFIRMING
        res1 = self.client.post("/api/ai/chat", json={"message": "Tôi vừa ăn sáng hết 50 nghìn."}, headers=headers)
        self.assertEqual(res1.status_code, 200)
        d1 = res1.json()
        self.assertEqual(d1["state"], "CONFIRMING")
        self.assertIn("create_expense", str(d1["pending_confirmation"]))
        self.assertIn("Xác nhận", d1["response"])

        # Số dư trong DB chưa được đổi
        with main.get_db() as conn:
            w_mid = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]
        self.assertEqual(w_mid, w_before)

        # Bước 2: Người dùng xác nhận -> Trạng thái SUCCESS
        res2 = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=headers)
        self.assertEqual(res2.status_code, 200)
        d2 = res2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "create_expense")

        # Số dư trong DB đã được trừ 50,000
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]
            txn = conn.execute("SELECT * FROM transactions WHERE user_id = 99 AND amount = 50000 ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(w_after, w_before - 50000)
        self.assertIsNotNone(txn)
        self.assertEqual(txn["transaction_type"], "EXPENSE")

    def test_39_ai_income_creation_flow(self):
        """3. AI Agent: Ghi nhận thu nhập qua luồng xác nhận"""
        headers, _ = self._setup_ai_agent_test_env()
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]

        res1 = self.client.post("/api/ai/chat", json={"message": "Nhận được tiền thưởng 2 triệu."}, headers=headers)
        d1 = res1.json()
        self.assertEqual(d1["state"], "CONFIRMING")

        res2 = self.client.post("/api/ai/chat", json={"message": "Đồng ý"}, headers=headers)
        d2 = res2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "create_income")

        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]
        self.assertEqual(w_after, w_before + 2000000)

    def test_40_ai_transfer_money_flow(self):
        """4. AI Agent: Chuyển tiền liên ví có xác nhận và audit trail"""
        headers, _ = self._setup_ai_agent_test_env()
        with main.get_db() as conn:
            w1_before = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]
            w2_before = conn.execute("SELECT balance FROM wallets WHERE id = 992").fetchone()["balance"]

        res1 = self.client.post("/api/ai/chat", json={"message": "Chuyển 500 nghìn từ ví Tiền Mặt sang ví Ngân Hàng"}, headers=headers)
        d1 = res1.json()
        self.assertEqual(d1["state"], "CONFIRMING")
        self.assertEqual(d1["pending_confirmation"]["tool_name"], "transfer_money")

        res2 = self.client.post("/api/ai/chat", json={"message": "Tiến hành"}, headers=headers)
        d2 = res2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "transfer_money")

        with main.get_db() as conn:
            w1_after = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]
            w2_after = conn.execute("SELECT balance FROM wallets WHERE id = 992").fetchone()["balance"]
        self.assertEqual(w1_after, w1_before - 500000)
        self.assertEqual(w2_after, w2_before + 500000)

    def test_41_ai_saving_goal_deposit_flow(self):
        """5. AI Agent: Nạp tiền mục tiêu tiết kiệm có xác nhận"""
        headers, _ = self._setup_ai_agent_test_env()
        with main.get_db() as conn:
            goal_before = conn.execute("SELECT current_amount FROM saving_goals WHERE id = 991").fetchone()["current_amount"]

        res1 = self.client.post("/api/ai/chat", json={"message": "Đưa 1 triệu vào mục tiêu mua laptop"}, headers=headers)
        d1 = res1.json()
        self.assertEqual(d1["state"], "CONFIRMING")
        self.assertEqual(d1["pending_confirmation"]["tool_name"], "saving_goal_deposit")

        res2 = self.client.post("/api/ai/chat", json={"message": "Lưu đi"}, headers=headers)
        d2 = res2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "saving_goal_deposit")

        with main.get_db() as conn:
            goal_after = conn.execute("SELECT current_amount FROM saving_goals WHERE id = 991").fetchone()["current_amount"]
        self.assertEqual(goal_after, goal_before + 1000000)

    def test_42_ai_cancellation_flow(self):
        """7. AI Agent: Hủy bỏ thao tác khi đang ở trạng thái CONFIRMING"""
        headers, _ = self._setup_ai_agent_test_env()
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]

        res1 = self.client.post("/api/ai/chat", json={"message": "Chi 300k ăn tối"}, headers=headers)
        self.assertEqual(res1.json()["state"], "CONFIRMING")

        # Người dùng đổi ý: "Hủy bỏ, đừng lưu"
        res2 = self.client.post("/api/ai/chat", json={"message": "Hủy bỏ, đừng lưu"}, headers=headers)
        d2 = res2.json()
        self.assertEqual(d2["state"], "IDLE")
        self.assertIn("hủy bỏ", d2["response"].lower())

        # Số dư không suy suyển
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 991").fetchone()["balance"]
        self.assertEqual(w_after, w_before)

    def test_43_ai_ambiguous_request_asks_clarification(self):
        """8. AI Agent: Yêu cầu mơ hồ -> Agent yêu cầu làm rõ, không tự ý đoán"""
        headers, _ = self._setup_ai_agent_test_env()
        # Thiếu ví nguồn/đích
        res = self.client.post("/api/ai/chat", json={"message": "Chuyển tiền 200 nghìn"}, headers=headers)
        d = res.json()
        self.assertIn("chưa rõ", d["response"].lower())
        self.assertIsNone(d.get("pending_confirmation"))

    def test_44_ai_invalid_amount_rejected(self):
        """9. AI Agent: Số tiền không hợp lệ (0 hoặc âm) -> Bị từ chối an toàn"""
        headers, _ = self._setup_ai_agent_test_env()
        res = self.client.post("/api/ai/chat", json={"message": "Chi 0 đồng tiền trà đá"}, headers=headers)
        d = res.json()
        self.assertIn("số tiền phải lớn hơn 0", d["response"].lower())

    def test_45_ai_unauthenticated_request_rejected(self):
        """10. AI Agent: Yêu cầu không có Token xác thực -> HTTP 401"""
        res = self.client.post("/api/ai/chat", json={"message": "Số dư còn bao nhiêu?"})
        self.assertEqual(res.status_code, 401)

    def test_46_ai_tool_failure_handled_truthfully(self):
        """11 & 12. AI Agent: Thao tác thất bại (vượt số dư) -> Báo ERROR, không tuyên bố thành công giả mạo"""
        headers, _ = self._setup_ai_agent_test_env()
        # Chuyển 999 tỷ (vượt quá số dư)
        res1 = self.client.post("/api/ai/chat", json={"message": "Chuyển 999 tỷ từ ví Tiền Mặt sang ví Ngân Hàng"}, headers=headers)
        self.assertEqual(res1.json()["state"], "CONFIRMING")

        res2 = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=headers)
        d2 = res2.json()
        self.assertEqual(d2["state"], "ERROR")
        self.assertIn("thất bại", d2["response"].lower())
        self.assertNotIn("thành công", d2["response"].lower())

    def test_47_ai_p1_read_tools(self):
        """P1: Kiểm tra các công cụ tra cứu mở rộng (overview, budget, debts, categories, recent)"""
        headers, _ = self._setup_ai_agent_test_env()
        for msg, expected_tool in [
            ("Tổng quan tài chính tháng này", "get_financial_overview"),
            ("Hạn mức chi tiêu thế nào?", "get_budget_status"),
            ("Xem sổ nợ", "get_debts"),
            ("Xem danh mục chi tiêu", "get_categories"),
            ("Giao dịch gần đây", "get_recent_transactions")
        ]:
            res = self.client.post("/api/ai/chat", json={"message": msg}, headers=headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["state"], "SUCCESS", f"Failed for {msg}")
            self.assertEqual(data["tool_executed"], expected_tool, f"Wrong tool for {msg}")

    def test_48_ai_p1_conversational_queries(self):
        """P1: Kiểm tra các câu hỏi đàm đạo tự nhiên (Ví tiền mặt còn bao nhiêu, Tháng này tiêu bao nhiêu, Tìm giao dịch)"""
        headers, _ = self._setup_ai_agent_test_env()

        # 1. "Ví tiền mặt còn bao nhiêu?"
        res1 = self.client.post("/api/ai/chat", json={"message": "Ví tiền mặt còn bao nhiêu?"}, headers=headers)
        self.assertEqual(res1.status_code, 200)
        d1 = res1.json()
        self.assertEqual(d1["state"], "SUCCESS")
        self.assertEqual(d1["tool_executed"], "get_wallets")
        self.assertIn("Ví Tiền Mặt", d1["response"])

        # 2. "Tháng này tôi tiêu bao nhiêu?"
        res2 = self.client.post("/api/ai/chat", json={"message": "Tháng này tôi tiêu bao nhiêu?"}, headers=headers)
        self.assertEqual(res2.status_code, 200)
        d2 = res2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "get_financial_overview")

        # 3. "Tìm giao dịch ăn sáng"
        res3 = self.client.post("/api/ai/chat", json={"message": "Tìm giao dịch ăn sáng"}, headers=headers)
        self.assertEqual(res3.status_code, 200)
        d3 = res3.json()
        self.assertEqual(d3["state"], "SUCCESS")
        self.assertEqual(d3["tool_executed"], "search_transactions")

    def test_49_ai_p2_followup_modification_and_retry_hints(self):
        """P2: Kiểm tra hội thoại follow-up sửa đổi số tiền trước khi xác nhận và gợi ý thử lại khi lỗi"""
        headers, _ = self._setup_ai_agent_test_env()

        # 1. Tạo yêu cầu ban đầu 50k
        res1 = self.client.post("/api/ai/chat", json={"message": "Chi 50k tiền ăn sáng"}, headers=headers)
        self.assertEqual(res1.json()["state"], "CONFIRMING")
        self.assertEqual(res1.json()["pending_confirmation"]["args"]["amount"], 50000)

        # 2. Follow-up sửa đổi: "Sửa thành 65 nghìn"
        res2 = self.client.post("/api/ai/chat", json={"message": "Sửa thành 65 nghìn"}, headers=headers)
        self.assertEqual(res2.json()["state"], "CONFIRMING")
        self.assertEqual(res2.json()["pending_confirmation"]["args"]["amount"], 65000)
        self.assertIn("65,000", res2.json()["response"])

        # 3. Xác nhận sau khi sửa
        res3 = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=headers)
        self.assertEqual(res3.json()["state"], "SUCCESS")
        with main.get_db() as conn:
            txn = conn.execute("SELECT * FROM transactions WHERE user_id = 99 AND amount = 65000 ORDER BY id DESC LIMIT 1").fetchone()
        self.assertIsNotNone(txn)

        # 4. Gợi ý thử lại với số dư tối đa khi thất bại
        res_fail = self.client.post("/api/ai/chat", json={"message": "Chuyển 500 triệu từ ví Tiền Mặt sang ví Ngân Hàng"}, headers=headers)
        self.assertEqual(res_fail.json()["state"], "CONFIRMING")
        res_fail_conf = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=headers)
        d_fail = res_fail_conf.json()
        self.assertEqual(d_fail["state"], "ERROR")
        self.assertIn("tối đa", d_fail["response"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

