# -*- coding: utf-8 -*-
"""
test_support_contacts.py
Unit & Integration Test Suite for:
GIAI ĐOẠN 1 (Backend) — Chức năng "Truyền Âm Cầu Viện"
(Danh Bạ Hộ Đạo, Cài Đặt Cảnh Báo, và Tính Toán Chỉ Số Sắp Cạn)

TUYỆT ĐỐI không ghi vào app.db thật: sử dụng database SQLite tạm (tempfile)
và khôi phục main.DATABASE trong tearDown.
"""

import os
import sys
import tempfile
import unittest
import datetime
from fastapi.testclient import TestClient

# Ensure UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import main
from ai_agent.core import AgentCore
from ai_agent.tools import build_default_tool_registry, ToolActionType
from ai_agent.provider import MockAIProvider


class TestSupportContacts(unittest.TestCase):
    def setUp(self):
        # Lưu lại đường dẫn DATABASE thật và trỏ sang file SQLite tạm
        self.orig_db = main.DATABASE
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        main.DATABASE = self.temp_db_path

        # Khởi tạo schema trong database tạm
        main.init_db()

        self.client = TestClient(main.app)

        # Đăng ký User A qua API thật
        resp_a = self.client.post("/api/auth/register", json={
            "email": "user_a@test.com",
            "password": "Password123!",
            "full_name": "Tu Sĩ Tiêu Phong",
            "soul_lamp": "Hồn Đăng A"
        })
        self.assertEqual(resp_a.status_code, 200, resp_a.text)
        data_a = resp_a.json()
        self.token_a = data_a["token"]
        self.user_a_id = data_a["user_id"]
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        # Đăng ký User B qua API thật
        resp_b = self.client.post("/api/auth/register", json={
            "email": "user_b@test.com",
            "password": "Password123!",
            "full_name": "Tu Sĩ Đoàn Dự",
            "soul_lamp": "Hồn Đăng B"
        })
        self.assertEqual(resp_b.status_code, 200, resp_b.text)
        data_b = resp_b.json()
        self.token_b = data_b["token"]
        self.user_b_id = data_b["user_id"]
        self.headers_b = {"Authorization": f"Bearer {self.token_b}"}

    def tearDown(self):
        # Khôi phục DATABASE thật và xóa file tạm
        main.DATABASE = self.orig_db
        try:
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
        except Exception:
            pass

    # =========================================================================
    # 1. AUTHENTICATION & SECURITY ENFORCEMENT
    # =========================================================================
    def test_unauthenticated_requests_blocked(self):
        """Mọi endpoint Truyền Âm Cầu Viện yêu cầu token hợp lệ (401 hoặc 403)"""
        endpoints = [
            ("GET", "/api/support-contacts", None),
            ("POST", "/api/support-contacts", {"contact_name": "Bố", "relationship": "FATHER", "phone": "0912345678"}),
            ("PUT", "/api/support-contacts/1", {"contact_name": "Bố"}),
            ("DELETE", "/api/support-contacts/1", None),
            ("GET", "/api/support-settings", None),
            ("PUT", "/api/support-settings", {"low_balance_threshold": 300000}),
            ("GET", "/api/support/low-funds-status", None),
        ]
        for method, path, json_data in endpoints:
            if method == "GET":
                res = self.client.get(path)
            elif method == "POST":
                res = self.client.post(path, json=json_data)
            elif method == "PUT":
                res = self.client.put(path, json=json_data)
            elif method == "DELETE":
                res = self.client.delete(path)
            self.assertIn(res.status_code, [401, 403], f"Endpoint {method} {path} should require auth, got {res.status_code}")

    # =========================================================================
    # 2. CRUD DANH BẠ & CHUẨN HÓA SỐ ĐIỆN THOẠI
    # =========================================================================
    def test_support_contacts_crud_and_phone_normalization(self):
        """CRUD danh bạ và chuẩn hóa định dạng số điện thoại VN (+84, khoảng trắng, dấu chấm)"""
        # 1. Thêm liên hệ có tiền tố +84 và ký tự phân tách
        create_payload = {
            "contact_name": "Nguyễn Văn Cha",
            "relationship": "FATHER",
            "phone": "+84 912.345.678",
            "priority": 1,
            "note": "Gọi sau giờ tu luyện"
        }
        res_post = self.client.post("/api/support-contacts", json=create_payload, headers=self.headers_a)
        self.assertEqual(res_post.status_code, 200, res_post.text)
        created = res_post.json()
        contact_id = created["id"]
        self.assertEqual(created["phone"], "0912345678", "Số điện thoại phải được chuẩn hóa về dạng 0xxxxxxxxx")
        self.assertEqual(created["relationship_label"], "Bố")
        self.assertEqual(created["contact_name"], "Nguyễn Văn Cha")
        self.assertEqual(created["is_active"], 1)

        # 2. Thêm liên hệ thứ hai với tiền tố 84
        res_post2 = self.client.post("/api/support-contacts", json={
            "contact_name": "Trần Thị Mẹ",
            "relationship": "MOTHER",
            "phone": "84987654321",
            "priority": 2,
            "note": "Dùng Zalo"
        }, headers=self.headers_a)
        self.assertEqual(res_post2.status_code, 200)
        self.assertEqual(res_post2.json()["phone"], "0987654321")

        # 3. GET danh sách: sắp xếp theo priority rồi id
        res_get = self.client.get("/api/support-contacts", headers=self.headers_a)
        self.assertEqual(res_get.status_code, 200)
        contacts = res_get.json()
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]["id"], contact_id)
        self.assertEqual(contacts[0]["priority"], 1)
        self.assertEqual(contacts[1]["priority"], 2)

        # 4. PUT sửa thông tin liên hệ
        update_payload = {
            "contact_name": "Phụ Thân",
            "priority": 5,
            "note": "Gọi buổi tối",
            "is_active": 0
        }
        res_put = self.client.put(f"/api/support-contacts/{contact_id}", json=update_payload, headers=self.headers_a)
        self.assertEqual(res_put.status_code, 200)
        updated = res_put.json()
        self.assertEqual(updated["contact_name"], "Phụ Thân")
        self.assertEqual(updated["priority"], 5)
        self.assertEqual(updated["is_active"], 0)
        self.assertEqual(updated["note"], "Gọi buổi tối")

        # 5. DELETE xóa liên hệ
        res_del = self.client.delete(f"/api/support-contacts/{contact_id}", headers=self.headers_a)
        self.assertEqual(res_del.status_code, 200)

        # 6. GET lại xác nhận chỉ còn 1
        res_get_after = self.client.get("/api/support-contacts", headers=self.headers_a)
        contacts_after = res_get_after.json()
        self.assertEqual(len(contacts_after), 1)
        self.assertEqual(contacts_after[0]["phone"], "0987654321")

    def test_phone_validation_rules(self):
        """Kiểm tra chặn các số điện thoại sai định dạng"""
        invalid_phones = [
            "12345",              # Quá ngắn
            "0212345678",         # Đầu số cố định 02, không phải di động VN (3|5|7|8|9)
            "09123456789",        # 11 số (thừa số)
            "081234567",          # 9 số (thiếu số)
            "+1800123456",        # Mã vùng quốc tế không phải VN
            "abc0912345678",      # Ký tự chữ
            "",                   # Rỗng
        ]
        for p in invalid_phones:
            res = self.client.post("/api/support-contacts", json={
                "contact_name": "Người thân",
                "relationship": "OTHER",
                "phone": p
            }, headers=self.headers_a)
            self.assertEqual(res.status_code, 400, f"Phone '{p}' should return 400, got {res.status_code}")

    def test_duplicate_phone_in_same_account_rejected(self):
        """Trùng số điện thoại trong cùng một tài khoản phải trả về HTTP 400"""
        self.client.post("/api/support-contacts", json={
            "contact_name": "Người thân 1",
            "relationship": "SIBLING",
            "phone": "0912345678"
        }, headers=self.headers_a)

        # Cùng số dạng +84
        res_dup = self.client.post("/api/support-contacts", json={
            "contact_name": "Người thân 2",
            "relationship": "FRIEND",
            "phone": "+84 912.345.678"
        }, headers=self.headers_a)
        self.assertEqual(res_dup.status_code, 400)
        self.assertIn("đã tồn tại", res_dup.json()["detail"].lower())

    def test_max_10_contacts_limit(self):
        """Thêm người thứ 11 trong danh bạ phải bị chặn (HTTP 400)"""
        for i in range(10):
            res = self.client.post("/api/support-contacts", json={
                "contact_name": f"Người thân {i+1}",
                "relationship": "FRIEND",
                "phone": f"091200000{i}"
            }, headers=self.headers_a)
            self.assertEqual(res.status_code, 200)

        # Người thứ 11
        res_11 = self.client.post("/api/support-contacts", json={
            "contact_name": "Người thân 11",
            "relationship": "OTHER",
            "phone": "0912000010"
        }, headers=self.headers_a)
        self.assertEqual(res_11.status_code, 400)
        self.assertIn("tối đa 10", res_11.json()["detail"].lower())

    # =========================================================================
    # 3. DỮ LIỆU ĐỘC LẬP & PHÂN QUYỀN GIỮA CÁC USER
    # =========================================================================
    def test_user_isolation_and_ownership(self):
        """User B không thể xem, sửa hoặc xóa liên hệ của User A (404)"""
        # User A tạo liên hệ
        res_a = self.client.post("/api/support-contacts", json={
            "contact_name": "Bố của A",
            "relationship": "FATHER",
            "phone": "0912345678"
        }, headers=self.headers_a)
        contact_a_id = res_a.json()["id"]

        # User B lấy danh bạ -> không thấy liên hệ của A
        res_b_list = self.client.get("/api/support-contacts", headers=self.headers_b)
        self.assertEqual(res_b_list.status_code, 200)
        self.assertEqual(len(res_b_list.json()), 0)

        # User B thử sửa liên hệ của A -> 404
        res_b_put = self.client.put(f"/api/support-contacts/{contact_a_id}", json={
            "contact_name": "Hacked Name"
        }, headers=self.headers_b)
        self.assertEqual(res_b_put.status_code, 404)

        # User B thử xóa liên hệ của A -> 404
        res_b_del = self.client.delete(f"/api/support-contacts/{contact_a_id}", headers=self.headers_b)
        self.assertEqual(res_b_del.status_code, 404)

        # User B có thể lưu cùng số điện thoại đó cho tài khoản của riêng mình mà không bị chặn
        res_b_create_same_phone = self.client.post("/api/support-contacts", json={
            "contact_name": "Bố của B",
            "relationship": "FATHER",
            "phone": "0912345678"
        }, headers=self.headers_b)
        self.assertEqual(res_b_create_same_phone.status_code, 200)

    # =========================================================================
    # 4. SUPPORT SETTINGS ENDPOINTS
    # =========================================================================
    def test_support_settings_defaults_and_validation(self):
        """GET trả cài đặt mặc định; PUT kiểm tra giới hạn giá trị (threshold, allowance_day)"""
        # 1. GET lần đầu trả giá trị mặc định
        res_get = self.client.get("/api/support-settings", headers=self.headers_a)
        self.assertEqual(res_get.status_code, 200)
        data = res_get.json()
        self.assertEqual(data["enabled"], True)
        self.assertEqual(data["low_balance_threshold"], 500000.0)
        self.assertEqual(data["allowance_day"], 1)
        self.assertEqual(data["message_template"], "")

        # 2. PUT hợp lệ
        res_put = self.client.put("/api/support-settings", json={
            "enabled": 1,
            "low_balance_threshold": 800000.0,
            "allowance_day": 15,
            "message_template": "Chào {xung_ho}, con thiếu {so_tien}"
        }, headers=self.headers_a)
        self.assertEqual(res_put.status_code, 200)
        updated = res_put.json()
        self.assertEqual(updated["low_balance_threshold"], 800000.0)
        self.assertEqual(updated["allowance_day"], 15)
        self.assertEqual(updated["message_template"], "Chào {xung_ho}, con thiếu {so_tien}")

        # 3. PUT allowance_day sai (> 28 hoặc < 1) -> 400
        res_bad_day = self.client.put("/api/support-settings", json={"allowance_day": 31}, headers=self.headers_a)
        self.assertIn(res_bad_day.status_code, [400, 422])

        res_bad_day_zero = self.client.put("/api/support-settings", json={"allowance_day": 0}, headers=self.headers_a)
        self.assertIn(res_bad_day_zero.status_code, [400, 422])

        # 4. PUT threshold âm hoặc vượt 1 tỷ -> 400
        res_neg_thresh = self.client.put("/api/support-settings", json={"low_balance_threshold": -1000}, headers=self.headers_a)
        self.assertIn(res_neg_thresh.status_code, [400, 422])

        res_huge_thresh = self.client.put("/api/support-settings", json={"low_balance_threshold": 1000000001}, headers=self.headers_a)
        self.assertIn(res_huge_thresh.status_code, [400, 422])

        # 5. PUT message_template > 500 ký tự -> 400
        res_huge_tpl = self.client.put("/api/support-settings", json={"message_template": "x" * 501}, headers=self.headers_a)
        self.assertIn(res_huge_tpl.status_code, [400, 422])

    # =========================================================================
    # 5. HÀM TÍNH TOÁN compute_low_funds_status & CÁC TRƯỜNG HỢP TÀI CHÍNH
    # =========================================================================
    def test_compute_low_funds_status_fixed_date(self):
        """Kiểm tra hàm compute_low_funds_status với ngày cố định 2026-10-09 và các mức độ"""
        fixed_today = datetime.date(2026, 10, 9)

        # Thêm 2 người thân cho User A: Bố (FATHER) và Bạn (FRIEND)
        self.client.post("/api/support-contacts", json={
            "contact_name": "Nguyễn Văn Cha",
            "relationship": "FATHER",
            "phone": "0912345678",
            "priority": 1
        }, headers=self.headers_a)
        self.client.post("/api/support-contacts", json={
            "contact_name": "Lê Văn Bạn",
            "relationship": "FRIEND",
            "phone": "0934567890",
            "priority": 2
        }, headers=self.headers_a)

        with main.get_db() as conn:
            # 1. Kiểm tra days_left với allowance_day = 1 -> 23 ngày (09/10 -> 01/11)
            conn.execute("UPDATE support_settings SET allowance_day = 1, low_balance_threshold = 500000 WHERE user_id = ?", (self.user_a_id,))
            status_1 = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_1["days_left"], 23)
            self.assertEqual(status_1["next_allowance_date"], "2026-11-01")

            # 2. Kiểm tra days_left với allowance_day = 15 -> 6 ngày (09/10 -> 15/10)
            conn.execute("UPDATE support_settings SET allowance_day = 15 WHERE user_id = ?", (self.user_a_id,))
            status_15 = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_15["days_left"], 6)
            self.assertEqual(status_15["next_allowance_date"], "2026-10-15")

            # 3. Khi chưa có chi tiêu nào: avg_daily_expense = 0, runway_days = None
            conn.execute("DELETE FROM transactions WHERE user_id = ?", (self.user_a_id,))
            status_no_exp = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_no_exp["avg_daily_expense"], 0.0)
            self.assertIsNone(status_no_exp["runway_days"])

            # 4. Khi today.day >= 7 (ngày 9) và có chi trong tháng: avg = tổng chi tháng / 9
            # Thêm chi tiêu tháng 10: 900.000 ₫ -> avg = 900.000 / 9 = 100.000 ₫/ngày
            wallet_id = conn.execute("SELECT id FROM wallets WHERE user_id = ?", (self.user_a_id,)).fetchone()[0]
            cat_id = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_type = 'EXPENSE'", (self.user_a_id,)).fetchone()[0]

            conn.execute("""
                INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date)
                VALUES (?, ?, ?, 900000, 'EXPENSE', '2026-10-05')
            """, (self.user_a_id, wallet_id, cat_id))

            status_exp = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_exp["avg_daily_expense"], 100000.0)

            # 5. Kiểm tra tính upcoming_fixed:
            # (a) Recurring EXPENSE đang bật trong [09/10, 15/10):
            # recurring weekly 200.000 ₫ next_run 2026-10-10 -> rơi vào khoảng [09/10, 15/10) 1 lần -> +200.000 ₫
            conn.execute("""
                INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, is_active)
                VALUES (?, ?, ?, 200000, 'EXPENSE', 'weekly', '2026-10-10', 1)
            """, (self.user_a_id, wallet_id, cat_id))

            # (b) Khoản nợ BORROW chưa trả có due_date trong khoảng [09/10, 15/10):
            # nợ 300.000 ₫ due 2026-10-12 -> +300.000 ₫
            conn.execute("""
                INSERT INTO debts (user_id, wallet_id, debt_type, person_name, amount, due_date, is_settled)
                VALUES (?, ?, 'BORROW', 'Chủ nợ X', 300000, '2026-10-12', 0)
            """, (self.user_a_id, wallet_id))

            status_fixed = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            # upcoming_fixed = 200.000 + 300.000 = 500.000 ₫
            self.assertEqual(status_fixed["upcoming_fixed"], 500000.0)

            # 6. Kiểm tra các mức SAFE / WARNING / CRITICAL:
            # Đặt allowance_day = 1 (days_left = 23).
            # upcoming_fixed: recurring weekly (10, 17, 24, 31 tháng 10 = 4 lần * 200k = 800k) + borrow 300k = 1.100.000 ₫
            conn.execute("UPDATE support_settings SET allowance_day = 1, low_balance_threshold = 500000 WHERE user_id = ?", (self.user_a_id,))

            # (A) Mức SAFE: Số dư dồi dào 10.000.000 ₫
            conn.execute("UPDATE wallets SET balance = 0 WHERE user_id = ?", (self.user_a_id,))
            conn.execute("UPDATE wallets SET balance = 10000000 WHERE id = ?", (wallet_id,))
            status_safe = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_safe["level"], "SAFE")
            self.assertEqual(status_safe["shortfall"], 0.0)
            self.assertEqual(status_safe["suggested_amount"], 0)

            # (B) Mức WARNING: Số dư 450.000 ₫ (< threshold 500.000 nhưng > threshold * 0.5 = 250.000)
            # Không rơi vào runway < days_left * 0.5 nếu chi ít. Cho avg_expense = 0 để cô lập điều kiện threshold.
            conn.execute("DELETE FROM transactions WHERE user_id = ?", (self.user_a_id,))
            conn.execute("DELETE FROM recurring_transactions WHERE user_id = ?", (self.user_a_id,))
            conn.execute("DELETE FROM debts WHERE user_id = ?", (self.user_a_id,))
            conn.execute("UPDATE wallets SET balance = 0 WHERE user_id = ?", (self.user_a_id,))
            conn.execute("UPDATE wallets SET balance = 450000 WHERE id = ?", (wallet_id,))
            status_warning = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_warning["level"], "WARNING")
            # suggested_amount: max(0, 500000 - 450000) = 50.000 ₫
            self.assertEqual(status_warning["suggested_amount"], 50000)

            # (C) Mức CRITICAL:
            # Điều kiện 1: Số dư cạn kiệt <= 0
            conn.execute("UPDATE wallets SET balance = 0 WHERE id = ?", (wallet_id,))
            status_crit_0 = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_crit_0["level"], "CRITICAL")

            # Điều kiện 2: Số dư < threshold * 0.5 (ví dụ 200.000 < 250.000)
            conn.execute("UPDATE wallets SET balance = 200000 WHERE id = ?", (wallet_id,))
            status_crit_thresh = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_crit_thresh["level"], "CRITICAL")

            # 7. Kiểm tra làm tròn suggested_amount lên bội số 50.000 ₫:
            # Giả sử shortfall = 1.535.000 ₫ -> suggested_amount = 1.550.000 ₫
            # Dựng: days_left = 23, avg_daily_expense = 85.000, balance = 420.000, threshold = 500.000
            # projected_need = 85.000 * 23 + 0 = 1.955.000 ₫
            # shortfall = 1.955.000 - 420.000 = 1.535.000 ₫
            # raw_suggested = max(1.535.000, 500.000 - 420.000) = 1.535.000 ₫
            # suggested_amount = ceil(1.535.000 / 50.000) * 50.000 = 1.550.000 ₫
            conn.execute("UPDATE wallets SET balance = 420000 WHERE id = ?", (wallet_id,))
            # Chi tiêu ngày 1 đến 9: 85.000 * 9 = 765.000 ₫
            conn.execute("""
                INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date)
                VALUES (?, ?, ?, 765000, 'EXPENSE', '2026-10-08')
            """, (self.user_a_id, wallet_id, cat_id))

            status_spec = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_spec["level"], "CRITICAL")  # runway_days = 420000/85000 = 4.9 < 23*0.5 (11.5)
            self.assertEqual(status_spec["runway_days"], 4.9)
            self.assertEqual(status_spec["shortfall"], 1535000.0)
            self.assertEqual(status_spec["suggested_amount"], 1550000)

            # 8. Kiểm tra thay thế placeholder trong message của người thân
            self.assertEqual(len(status_spec["contacts"]), 2)
            c_father = status_spec["contacts"][0]
            c_friend = status_spec["contacts"][1]

            # Người 1: Quan hệ FATHER -> xưng hô "Bố"
            self.assertEqual(c_father["relationship"], "FATHER")
            self.assertIn("Bố ơi", c_father["message"])
            self.assertIn("420.000 ₫", c_father["message"])
            self.assertIn("23 ngày", c_father["message"])
            self.assertIn("1.550.000 ₫", c_father["message"])
            self.assertNotIn("{", c_father["message"], "Toàn bộ placeholder phải được thay thế")

            # Người 2: Quan hệ FRIEND -> xưng hô tên người đó "Lê Văn Bạn"
            self.assertEqual(c_friend["relationship"], "FRIEND")
            self.assertIn("Lê Văn Bạn ơi", c_friend["message"])
            self.assertNotIn("{", c_friend["message"], "Toàn bộ placeholder phải được thay thế")

        # 9. Kiểm tra endpoint GET /api/support/low-funds-status trả đúng dữ liệu (gọi ngoài khối with get_db())
        res_api = self.client.get("/api/support/low-funds-status", headers=self.headers_a)
        self.assertEqual(res_api.status_code, 200)
        json_res = res_api.json()
        self.assertIn("level", json_res)
        self.assertIn("contacts", json_res)
        self.assertIn("reasons", json_res)

    def test_compute_low_funds_status_no_wallets(self):
        """User chưa có ví nào trả level = 'NO_DATA'; user có ví số dư 0 trả 'CRITICAL'"""
        fixed_today = datetime.date(2026, 10, 9)

        # Thêm 1 người thân cho user B
        self.client.post("/api/support-contacts", json={
            "contact_name": "Mẫu Thân",
            "relationship": "MOTHER",
            "phone": "0987654321",
            "priority": 1
        }, headers=self.headers_b)

        with main.get_db() as conn:
            # Xóa sạch ví của user B (mô phỏng tài khoản chưa có ví nào)
            conn.execute("DELETE FROM wallets WHERE user_id = ?", (self.user_b_id,))

            status_no_wallet = main.compute_low_funds_status(conn, self.user_b_id, today=fixed_today)
            self.assertEqual(status_no_wallet["level"], "NO_DATA")
            self.assertEqual(status_no_wallet["reasons"], ["Chưa có ví nào nên chưa thể đánh giá. Hãy tạo ví trong Túi Càn Khôn."])
            self.assertEqual(status_no_wallet["total_balance"], 0.0)
            self.assertIn("days_left", status_no_wallet)
            self.assertIn("next_allowance_date", status_no_wallet)
            # contacts vẫn trả bình thường
            self.assertEqual(len(status_no_wallet["contacts"]), 1)
            self.assertEqual(status_no_wallet["contacts"][0]["relationship_label"], "Mẹ")

            # Ngược lại, user A có ví nhưng số dư = 0 -> vẫn là CRITICAL
            conn.execute("UPDATE wallets SET balance = 0 WHERE user_id = ?", (self.user_a_id,))
            status_zero_bal = main.compute_low_funds_status(conn, self.user_a_id, today=fixed_today)
            self.assertEqual(status_zero_bal["level"], "CRITICAL")
            self.assertIn("cạn kiệt", status_zero_bal["reasons"][0])


class TestSupportContactsAIAgent(unittest.IsolatedAsyncioTestCase):
    """Kiểm thử tích hợp Khí Linh AI Agent (MockAIProvider) với chức năng Truyền Âm Cầu Viện"""

    async def asyncSetUp(self):
        self.orig_db = main.DATABASE
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        main.DATABASE = self.temp_db_path
        main.init_db()

        self.client = TestClient(main.app)

        # Đăng ký User A
        resp_a = self.client.post("/api/auth/register", json={
            "email": "user_a@test.com",
            "password": "Password123!",
            "full_name": "Tu Sĩ Tiêu Phong",
            "soul_lamp": "Hồn Đăng A"
        })
        self.assertEqual(resp_a.status_code, 200)
        data_a = resp_a.json()
        self.token_a = data_a["token"]
        self.user_a_id = data_a["user_id"]
        self.headers_a = {"Authorization": f"Bearer {self.token_a}"}

        # Đăng ký User B
        resp_b = self.client.post("/api/auth/register", json={
            "email": "user_b@test.com",
            "password": "Password123!",
            "full_name": "Tu Sĩ Đoàn Dự",
            "soul_lamp": "Hồn Đăng B"
        })
        self.assertEqual(resp_b.status_code, 200)
        data_b = resp_b.json()
        self.token_b = data_b["token"]
        self.user_b_id = data_b["user_id"]
        self.headers_b = {"Authorization": f"Bearer {self.token_b}"}

        # Thêm người thân cho User A
        self.client.post("/api/support-contacts", json={
            "contact_name": "Phụ Thân Tiêu Viễn Sơn",
            "relationship": "FATHER",
            "phone": "0988111222",
            "note": "Xin linh thạch tu luyện"
        }, headers=self.headers_a)

        # User A có ví tiền số dư thấp
        self.client.post("/api/wallets", json={
            "wallet_name": "Ví Tiền Mặt",
            "balance": 50000,
            "wallet_type": "cash"
        }, headers=self.headers_a)

        # Cài đặt ngưỡng cảnh báo cho User A
        self.client.put("/api/support-settings", json={
            "enabled": True,
            "low_balance_threshold": 500000,
            "allowance_day": 15
        }, headers=self.headers_a)

        self.registry = build_default_tool_registry()
        self.agent = AgentCore(provider=MockAIProvider(), registry=self.registry)

    async def asyncTearDown(self):
        main.DATABASE = self.orig_db
        try:
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
        except Exception:
            pass

    async def test_low_funds_support_agent_query(self):
        """'cuối tháng sắp hết tiền thì gọi ai' -> gọi đúng tool low_funds_support (READ), không tool ghi; user B không thấy người thân user A"""
        # User A hỏi
        resp_a = await self.agent.process_request(
            user_id=self.user_a_id,
            user_message="cuối tháng sắp hết tiền thì gọi ai"
        )
        self.assertEqual(resp_a.tool_executed, "low_funds_support")
        self.assertIsNotNone(resp_a.tool_result)
        self.assertTrue(resp_a.tool_result.get("success", False))

        # Đảm bảo tool được thực thi là READ (LOW risk), không cần xác nhận, không có tool ghi nào được gọi
        tool_obj = self.registry.get(resp_a.tool_executed)
        self.assertEqual(tool_obj.action_type, ToolActionType.READ)
        self.assertEqual(tool_obj.risk_level.value, "LOW")
        self.assertFalse(tool_obj.requires_confirmation)

        # User A nhìn thấy người thân của mình trong câu trả lời
        self.assertIn("Tiêu Viễn Sơn", resp_a.text)
        self.assertIn("0988111222", resp_a.text)

        # User B hỏi câu tương tự:
        resp_b = await self.agent.process_request(
            user_id=self.user_b_id,
            user_message="cuối tháng sắp hết tiền thì gọi ai"
        )
        self.assertEqual(resp_b.tool_executed, "low_funds_support")
        # User B TUYỆT ĐỐI không nhìn thấy thông tin người thân của User A
        self.assertNotIn("Tiêu Viễn Sơn", resp_b.text)
        self.assertNotIn("0988111222", resp_b.text)
        # Vì User B chưa có người thân nên nhận được hướng dẫn thêm vào Hồ Sơ > Danh Bạ Hộ Đạo
        self.assertIn("Danh Bạ Hộ Đạo", resp_b.text)

    async def test_low_funds_support_phrases_routing(self):
        """Kiểm tra toàn bộ các câu khẩu lệnh chỉ định được định tuyến chuẩn tới low_funds_support"""
        phrases = [
            "sắp hết tiền",
            "hết tiền rồi",
            "cuối tháng hết tiền",
            "xin tiền bố mẹ",
            "gọi ai xin tiền",
            "số điện thoại người thân",
            "danh bạ hộ đạo"
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                resp = await self.agent.process_request(
                    user_id=self.user_a_id,
                    user_message=phrase
                )
                self.assertEqual(
                    resp.tool_executed,
                    "low_funds_support",
                    f"Câu '{phrase}' không được định tuyến tới low_funds_support mà tới '{resp.tool_executed}'"
                )
                self.assertIsNotNone(resp.tool_result)
                self.assertTrue(resp.tool_result.get("success", False))
                # Không được có tool ghi
                tool_def = self.registry.get(resp.tool_executed)
                self.assertEqual(tool_def.action_type, ToolActionType.READ)


if __name__ == "__main__":
    unittest.main()

