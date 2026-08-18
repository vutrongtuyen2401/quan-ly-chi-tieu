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
        self.assertIn("reset_token", data)

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
        self.assertIn("reset_token", res.json())

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
        self.assertIn("reset_token", res_new.json())

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
        token = forgot.json()["reset_token"]

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

        # 3. Admin can access stats
        stats_res = self.client.get("/api/admin/stats", headers=admin_headers)
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertIn("total_users", stats)
        self.assertIn("total_wallets", stats)
        self.assertIn("total_system_cashflow", stats)

        # 4. Admin can list all users
        users_res = self.client.get("/api/admin/users", headers=admin_headers)
        self.assertEqual(users_res.status_code, 200)
        users = users_res.json()
        self.assertGreaterEqual(len(users), 1)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
