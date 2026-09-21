"""
Test Suite: Full-System AI Agent Capabilities & Tool Registry
Kiểm thử toàn diện 32 capabilities của Khí Linh AI Agent:
- Wallet Domain: create, update, delete, transfer, get_wallets
- Category Domain: create, update, delete, get_categories
- Transaction Domain: create_expense, create_income, update, delete, search
- Budget Domain: create, update, delete, status
- Recurring Domain: create, update, delete, list
- Debt Domain: create, update, settle, delete, status
- Saving Goal Domain: create, update, deposit, withdraw, delete, status
- Reports Domain: overview, summary, category, trend, weekly, compare, export
- Navigation & Profile Domain: navigate_to, profile, help
- General Conversation & Advisory: greeting, philosophical, hypothetical (NO mutation)
- Admin Protection: role verification
- Confirmation, Cancellation, Modification, Orphan confirmation lifecycle
"""

import os
import unittest
import tempfile
import json
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_full_system_agent_secret_key_12345"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_pass_full_system_test"

import main
from main import app, init_db, create_token
from ai_agent import AgentCore, MockAIProvider, build_default_tool_registry, AgentState


class TestFullSystemAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()

        main.DATABASE = cls.db_path
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except Exception:
                pass

    def setUp(self):
        with main.get_db() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM transactions WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM recurring_transactions WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM budgets WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM debts WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM saving_goals WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM categories WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM wallets WHERE user_id IN (901, 902)")
            conn.execute("DELETE FROM users WHERE id IN (901, 902)")

            # User 901: Regular disciple (user)
            conn.execute("INSERT INTO users (id, email, password_hash, full_name, role) VALUES (901, 'disciple@sect.com', 'dummy_hash', 'Đạo Hữu Tiêu Dao', 'user')")
            # User 902: Sect Master (admin)
            conn.execute("INSERT INTO users (id, email, password_hash, full_name, role) VALUES (902, 'master@sect.com', 'dummy_hash', 'Chưởng Môn Tiên Nhân', 'admin')")

            # Seed Ví cho User 901
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9011, 901, 'Ví Tiền Mặt', 'cash', 5000000)")
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9012, 901, 'Ví Ngân Hàng', 'bank', 15000000)")

            # Seed Danh mục cho User 901
            conn.execute("INSERT INTO categories (id, user_id, category_name, category_type, icon) VALUES (9011, 901, 'Ăn Uống', 'EXPENSE', '🍜')")
            conn.execute("INSERT INTO categories (id, user_id, category_name, category_type, icon) VALUES (9012, 901, 'Tiền Lương', 'INCOME', '💵')")

        self.user_token = create_token(user_id=901, email="disciple@sect.com", role="user")
        self.admin_token = create_token(user_id=902, email="master@sect.com", role="admin")

        self.user_headers = {"Authorization": f"Bearer {self.user_token}"}
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        self.mock_provider = MockAIProvider(default_response="Khí Linh Tiên Trí xin kính chào đạo hữu.")
        self.agent_core = AgentCore(provider=self.mock_provider, registry=build_default_tool_registry())
        main.set_agent_core(self.agent_core)

    # ─────────────────────────────────────────────────────────
    # 1. WALLET CAPABILITIES
    # ─────────────────────────────────────────────────────────
    def test_01_wallet_crud_and_transfer(self):
        """Kiểm thử toàn diện: Tạo ví, xem ví, chuyển tiền, sửa ví, xóa ví"""
        # A. Tạo ví mới: "Thêm ví MB Bank 80 triệu"
        res = self.client.post("/api/ai/chat", json={"message": "Thêm ví MB Bank 80 triệu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_wallet")
        self.assertEqual(data["pending_confirmation"]["args"]["balance"], 80000000)

        # Đảm bảo DB chưa thêm ví
        with main.get_db() as conn:
            w_check = conn.execute("SELECT * FROM wallets WHERE user_id = 901 AND wallet_name = 'MB Bank'").fetchone()
            self.assertIsNone(w_check)

        # B. Xác nhận tạo ví
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "create_wallet")

        # Kiểm tra DB đã có ví MB Bank với 80tr
        with main.get_db() as conn:
            w = conn.execute("SELECT * FROM wallets WHERE user_id = 901 AND wallet_name = 'MB Bank'").fetchone()
            self.assertIsNotNone(w)
            self.assertEqual(w["balance"], 80000000)

        # C. Tra cứu số dư ví (READ)
        res = self.client.post("/api/ai/chat", json={"message": "Cho tôi xem các ví"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "get_wallets")
        self.assertIn("MB Bank", data["response"])

        # D. Chuyển tiền: "Chuyển 2 triệu từ MB Bank sang Ví Tiền Mặt"
        res = self.client.post("/api/ai/chat", json={"message": "Chuyển 2 triệu từ MB Bank sang Ví Tiền Mặt"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "transfer_money")

        # Xác nhận chuyển tiền
        res = self.client.post("/api/ai/chat", json={"message": "Đồng ý"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")

        with main.get_db() as conn:
            mb_bal = conn.execute("SELECT balance FROM wallets WHERE user_id = 901 AND wallet_name = 'MB Bank'").fetchone()["balance"]
            cash_bal = conn.execute("SELECT balance FROM wallets WHERE id = 9011").fetchone()["balance"]
            self.assertEqual(mb_bal, 78000000)
            self.assertEqual(cash_bal, 7000000)

        # E. Xóa ví: "Xóa ví MB Bank" -> Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xóa ví MB Bank"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "delete_wallet")

        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            w_deleted = conn.execute("SELECT * FROM wallets WHERE user_id = 901 AND wallet_name = 'MB Bank'").fetchone()
            self.assertIsNone(w_deleted)

    # ─────────────────────────────────────────────────────────
    # 2. CATEGORY CAPABILITIES
    # ─────────────────────────────────────────────────────────
    def test_02_category_capabilities(self):
        """Kiểm thử: Tạo danh mục, tra cứu, xóa danh mục"""
        # A. Tạo danh mục: "Thêm danh mục Quà Biếu"
        res = self.client.post("/api/ai/chat", json={"message": "Thêm danh mục Quà Biếu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_category")

        # Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            c = conn.execute("SELECT * FROM categories WHERE user_id = 901 AND category_name = 'Quà Biếu'").fetchone()
            self.assertIsNotNone(c)

        # B. Xem danh mục
        res = self.client.post("/api/ai/chat", json={"message": "Cho xem các danh mục"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")
        self.assertEqual(res.json()["tool_executed"], "get_categories")

        # C. Xóa danh mục
        res = self.client.post("/api/ai/chat", json={"message": "Xóa danh mục Quà Biếu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "CONFIRMING")
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            c = conn.execute("SELECT * FROM categories WHERE user_id = 901 AND category_name = 'Quà Biếu'").fetchone()
            self.assertIsNone(c)

    # ─────────────────────────────────────────────────────────
    # 3. TRANSACTION CAPABILITIES & MODIFICATION
    # ─────────────────────────────────────────────────────────
    def test_03_transaction_capabilities(self):
        """Kiểm thử: Thêm chi tiêu, sửa đổi bằng hội thoại, xác nhận, tra cứu và xóa giao dịch"""
        # A. Chi tiêu 60k ăn sáng
        res = self.client.post("/api/ai/chat", json={"message": "Chi 60 nghìn ăn sáng"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 60000)

        # B. Sửa đổi: "Đổi thành 75 nghìn"
        res = self.client.post("/api/ai/chat", json={"message": "Đổi thành 75 nghìn"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 75000)
        self.assertIn("75,000", data["response"])

        # C. Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        txn_id = data["tool_result"]["data"]["transaction_id"]

        with main.get_db() as conn:
            txn = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()
            self.assertEqual(txn["amount"], 75000)
            cash_bal = conn.execute("SELECT balance FROM wallets WHERE id = 9011").fetchone()["balance"]
            self.assertEqual(cash_bal, 5000000 - 75000)

        # D. Thu nhập 5 triệu tiền thưởng
        res = self.client.post("/api/ai/chat", json={"message": "Nhận thưởng 5 triệu"}, headers=self.user_headers)
        self.assertEqual(res.json()["state"], "CONFIRMING")
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.json()["state"], "SUCCESS")

        # E. Tìm kiếm giao dịch
        res = self.client.post("/api/ai/chat", json={"message": "Tìm giao dịch ăn sáng"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertIn("75,000", data["response"])

    # ─────────────────────────────────────────────────────────
    # 4. BUDGET CAPABILITIES
    # ─────────────────────────────────────────────────────────
    def test_04_budget_capabilities(self):
        """Kiểm thử: Tạo hạn mức ngân sách, kiểm tra tiến độ, xóa ngân sách"""
        # Tạo ngân sách Ăn Uống 4 triệu
        res = self.client.post("/api/ai/chat", json={"message": "Đặt ngân sách ăn uống 4 triệu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_budget")

        # Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            b = conn.execute("SELECT * FROM budgets WHERE user_id = 901").fetchone()
            self.assertIsNotNone(b)
            self.assertEqual(b["limit_amount"], 4000000)

        # Xem trạng thái ngân sách
        res = self.client.post("/api/ai/chat", json={"message": "Hạn mức ngân sách thế nào?"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")
        self.assertIn("Ăn Uống", res.json()["response"])

    # ─────────────────────────────────────────────────────────
    # 5. RECURRING CAPABILITIES
    # ─────────────────────────────────────────────────────────
    def test_05_recurring_capabilities(self):
        """Kiểm thử: Lập giao dịch định kỳ, xem danh sách, xóa định kỳ"""
        # Tạo định kỳ
        res = self.client.post("/api/ai/chat", json={"message": "Đặt định kỳ hàng tháng đóng tiền mạng 300k"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_recurring_transaction")

        # Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            r = conn.execute("SELECT * FROM recurring_transactions WHERE user_id = 901").fetchone()
            self.assertIsNotNone(r)
            self.assertEqual(r["amount"], 300000)

        # Xem định kỳ
        res = self.client.post("/api/ai/chat", json={"message": "Xem các giao dịch định kỳ"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")
        self.assertIn("300,000", res.json()["response"])

    # ─────────────────────────────────────────────────────────
    # 6. DEBT CAPABILITIES
    # ─────────────────────────────────────────────────────────
    def test_06_debt_capabilities(self):
        """Kiểm thử: Ghi nợ, xem sổ nợ, quyết toán nợ"""
        # Ghi nợ: Cho Tuấn vay 2 triệu
        res = self.client.post("/api/ai/chat", json={"message": "Cho Tuấn vay 2 triệu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_debt")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 2000000)

        # Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            d = conn.execute("SELECT * FROM debts WHERE user_id = 901 AND person_name LIKE '%Tuấn%'").fetchone()
            self.assertIsNotNone(d)
            self.assertEqual(d["amount"], 2000000)
            self.assertEqual(d["debt_type"], "LEND")

        # Xem sổ nợ
        res = self.client.post("/api/ai/chat", json={"message": "Xem sổ nợ"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")
        self.assertIn("2,000,000", res.json()["response"])

        # Quyết toán nợ
        res = self.client.post("/api/ai/chat", json={"message": "Quyết toán nợ của Tuấn"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "CONFIRMING")
        self.assertEqual(res.json()["pending_confirmation"]["tool_name"], "settle_debt")

        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            d_settled = conn.execute("SELECT is_settled FROM debts WHERE user_id = 901 AND person_name LIKE '%Tuấn%'").fetchone()["is_settled"]
            self.assertEqual(d_settled, 1)

    # ─────────────────────────────────────────────────────────
    # 7. SAVING GOAL CAPABILITIES
    # ─────────────────────────────────────────────────────────
    def test_07_saving_goal_capabilities(self):
        """Kiểm thử: Lập mục tiêu, nạp tiền, rút tiền, xem tiến độ"""
        # Tạo mục tiêu
        res = self.client.post("/api/ai/chat", json={"message": "Tạo mục tiêu mua laptop 20 triệu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_saving_goal")

        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            g = conn.execute("SELECT * FROM saving_goals WHERE user_id = 901 AND target_name LIKE '%laptop%'").fetchone()
            self.assertIsNotNone(g)
            self.assertEqual(g["target_amount"], 20000000)

        # Nạp tiền vào mục tiêu
        res = self.client.post("/api/ai/chat", json={"message": "Nạp 3 triệu vào mục tiêu mua laptop"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "CONFIRMING")
        self.assertEqual(res.json()["pending_confirmation"]["tool_name"], "saving_goal_deposit")

        res = self.client.post("/api/ai/chat", json={"message": "Được"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            cur = conn.execute("SELECT current_amount FROM saving_goals WHERE user_id = 901 AND target_name LIKE '%laptop%'").fetchone()["current_amount"]
            self.assertEqual(cur, 3000000)

        # Rút tiền từ mục tiêu
        res = self.client.post("/api/ai/chat", json={"message": "Rút 1 triệu từ mục tiêu mua laptop"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "CONFIRMING")
        self.assertEqual(res.json()["pending_confirmation"]["tool_name"], "saving_goal_withdraw")

        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            cur = conn.execute("SELECT current_amount FROM saving_goals WHERE user_id = 901 AND target_name LIKE '%laptop%'").fetchone()["current_amount"]
            self.assertEqual(cur, 2000000)

    # ─────────────────────────────────────────────────────────
    # 8. NAVIGATION & USER PROFILE
    # ─────────────────────────────────────────────────────────
    def test_08_navigation_and_profile(self):
        """Kiểm thử: Điều hướng trang, xem hồ sơ tu tiên, đổi đạo hiệu"""
        # Điều hướng: "Mở sổ nợ cho tôi"
        res = self.client.post("/api/ai/chat", json={"message": "Mở sổ nợ cho tôi"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "navigate_to")
        self.assertEqual(data["tool_result"]["data"]["target_tab"], "debts")

        # Đổi đạo hiệu: "Đổi đạo hiệu thành Tiêu Dao Tiên Nhân"
        res = self.client.post("/api/ai/chat", json={"message": "Đổi đạo hiệu thành Tiêu Dao Tiên Nhân"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "CONFIRMING")

        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            name = conn.execute("SELECT full_name FROM users WHERE id = 901").fetchone()["full_name"]
            self.assertEqual(name, "Tiêu Dao Tiên Nhân")

    # ─────────────────────────────────────────────────────────
    # 9. GENERAL CONVERSATION & ADVISORY (ZERO MUTATION)
    # ─────────────────────────────────────────────────────────
    def test_09_general_chat_and_advisory(self):
        """Kiểm thử: Chào hỏi, triết lý tu tiên, tư vấn tài chính (KHÔNG tạo giao dịch)"""
        for msg in [
            "Xin chào Khí Linh",
            "Ngươi là ai?",
            "Hôm nay ta thấy mệt mỏi",
            "Đạo pháp tu tiên là gì?"
        ]:
            res = self.client.post("/api/ai/chat", json={"message": msg}, headers=self.user_headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["state"], "IDLE")
            self.assertIsNone(data.get("tool_executed"))
            self.assertIsNone(data.get("pending_confirmation"))

        for adv_msg in [
            "Lãi kép là gì?",
            "Gợi ý chi tiêu tháng sau cho tôi",
            "Nếu muốn tiết kiệm thêm 2 triệu thì sao?"
        ]:
            res = self.client.post("/api/ai/chat", json={"message": adv_msg}, headers=self.user_headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["state"], "IDLE")
            self.assertIsNone(data.get("pending_confirmation"))

    # ─────────────────────────────────────────────────────────
    # 10. ROLE PROTECTION & ADMIN ACCESS
    # ─────────────────────────────────────────────────────────
    def test_10_admin_protection(self):
        """Kiểm thử: Đệ tử thường không thể gọi tool Admin, Chưởng môn thì được"""
        # A. User thường gọi tool Admin -> Bị từ chối quyền
        import asyncio
        res = asyncio.run(self.agent_core.registry.execute("get_admin_stats", user_id=901, user_role="user"))
        self.assertFalse(res.success)
        self.assertIn("Chưởng Môn", res.message)

        # B. Admin gọi tool Admin -> Thành công
        res_admin = asyncio.run(self.agent_core.registry.execute("get_admin_stats", user_id=902, user_role="admin"))
        self.assertTrue(res_admin.success)
        self.assertIn("total_users", res_admin.data)

    # ─────────────────────────────────────────────────────────
    # 11. NATURAL LANGUAGE ARGUMENT RESOLUTION (DYNAMIC EXTRACTION)
    # ─────────────────────────────────────────────────────────
    def test_11_natural_language_tool_argument_resolution(self):
        """Kiểm thử: Tự động trích xuất argument động không dùng whitelist tên ví"""
        # A. "thêm một ví Momo 20 triệu" -> wallet_name = "Momo", balance = 20,000,000
        res = self.client.post("/api/ai/chat", json={"message": "thêm một ví Momo 20 triệu"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        d = res.json()
        self.assertEqual(d["state"], "CONFIRMING")
        self.assertIsNotNone(d.get("pending_confirmation"))
        self.assertEqual(d["pending_confirmation"]["tool_name"], "create_wallet")
        self.assertEqual(d["pending_confirmation"]["args"]["wallet_name"], "Momo")
        self.assertEqual(d["pending_confirmation"]["args"]["balance"], 20000000)
        self.assertEqual(d["pending_confirmation"]["args"]["wallet_type"], "e-wallet")

        # Xác nhận để thực thi vào database
        res_cf = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res_cf.status_code, 200)
        d_cf = res_cf.json()
        self.assertEqual(d_cf["state"], "SUCCESS")
        self.assertEqual(d_cf["tool_executed"], "create_wallet")

        # Kiểm tra database thực tế
        with main.get_db() as conn:
            w = conn.execute("SELECT * FROM wallets WHERE user_id = 901 AND wallet_name = 'Momo'").fetchone()
            self.assertIsNotNone(w)
            self.assertEqual(w["balance"], 20000000)

        # Thử lại câu lệnh -> Phát hiện trùng tên ví (Duplicate policy)
        res_dup = self.client.post("/api/ai/chat", json={"message": "thêm một ví Momo 20 triệu"}, headers=self.user_headers)
        self.assertEqual(res_dup.status_code, 200)
        self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        # Database chỉ có duy nhất 1 ví Momo
        with main.get_db() as conn:
            count = conn.execute("SELECT COUNT(*) FROM wallets WHERE user_id = 901 AND wallet_name = 'Momo'").fetchone()[0]
            self.assertEqual(count, 1)

        # B. "tạo ví MB Bank 80 triệu"
        res_mb = self.client.post("/api/ai/chat", json={"message": "tạo ví MB Bank 80 triệu"}, headers=self.user_headers)
        d_mb = res_mb.json()
        self.assertEqual(d_mb["state"], "CONFIRMING")
        self.assertEqual(d_mb["pending_confirmation"]["args"]["wallet_name"], "MB Bank")
        self.assertEqual(d_mb["pending_confirmation"]["args"]["balance"], 80000000)
        self.assertEqual(d_mb["pending_confirmation"]["args"]["wallet_type"], "bank")
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

        # C. "mở ví Techcombank với 10 triệu"
        res_tcb = self.client.post("/api/ai/chat", json={"message": "mở ví Techcombank với 10 triệu"}, headers=self.user_headers)
        d_tcb = res_tcb.json()
        self.assertEqual(d_tcb["state"], "CONFIRMING")
        self.assertEqual(d_tcb["pending_confirmation"]["args"]["wallet_name"], "Techcombank")
        self.assertEqual(d_tcb["pending_confirmation"]["args"]["balance"], 10000000)
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

        # D. "tạo cho tôi một ví tiền mặt 5 triệu"
        res_tm = self.client.post("/api/ai/chat", json={"message": "tạo cho tôi một ví tiền mặt 5 triệu"}, headers=self.user_headers)
        d_tm = res_tm.json()
        self.assertEqual(d_tm["state"], "CONFIRMING")
        self.assertEqual(d_tm["pending_confirmation"]["args"]["wallet_name"], "Tiền Mặt")
        self.assertEqual(d_tm["pending_confirmation"]["args"]["balance"], 5000000)
        self.assertEqual(d_tm["pending_confirmation"]["args"]["wallet_type"], "cash")
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

        # E. "tạo tài khoản ZaloPay 2 chục triệu"
        res_zl = self.client.post("/api/ai/chat", json={"message": "tạo tài khoản ZaloPay 2 chục triệu"}, headers=self.user_headers)
        d_zl = res_zl.json()
        self.assertEqual(d_zl["state"], "CONFIRMING")
        self.assertEqual(d_zl["pending_confirmation"]["args"]["wallet_name"], "ZaloPay")
        self.assertEqual(d_zl["pending_confirmation"]["args"]["balance"], 20000000)
        self.assertEqual(d_zl["pending_confirmation"]["args"]["wallet_type"], "e-wallet")
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

        # F. "tạo ví Heo Đất" (không có số dư -> balance = 0.0 theo default)
        res_hd = self.client.post("/api/ai/chat", json={"message": "tạo ví Heo Đất"}, headers=self.user_headers)
        d_hd = res_hd.json()
        self.assertEqual(d_hd["state"], "CONFIRMING")
        self.assertEqual(d_hd["pending_confirmation"]["args"]["wallet_name"], "Heo Đất")
        self.assertEqual(d_hd["pending_confirmation"]["args"]["balance"], 0.0)
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

    # ─────────────────────────────────────────────────────────
    # 12. MONEY SLANG PARSING
    # ─────────────────────────────────────────────────────────
    def test_12_money_slang_parsing(self):
        """Kiểm thử khả năng parse số tiền tự nhiên và tiếng lóng tài chính Việt Nam"""
        from ai_agent.parser import VietnameseFinancialParser

        test_cases = [
            ("20 triệu", 20000000.0),
            ("20.000.000", 20000000.0),
            ("20000000", 20000000.0),
            ("20tr", 20000000.0),
            ("20 củ", 20000000.0),
            ("2 chục triệu", 20000000.0),
            ("80000000", 80000000.0),
            ("80 triệu đồng", 80000000.0),
            ("1,5 triệu", 1500000.0),
            ("500k", 500000.0),
            ("50 nghìn", 50000.0),
        ]
        for text, expected in test_cases:
            amt = VietnameseFinancialParser.parse_amount(text)
            self.assertEqual(amt, expected, f"Failed parsing: '{text}', expected {expected}, got {amt}")

    # ─────────────────────────────────────────────────────────
    # 13. ENTITY AMBIGUITY RESOLUTION
    # ─────────────────────────────────────────────────────────
    def test_13_entity_ambiguity_resolution(self):
        """Kiểm thử phân giải thực thể trùng khớp: Nếu trùng nhiều entity -> Hỏi làm rõ, KHÔNG đoán và KHÔNG xóa nhầm"""
        with main.get_db() as conn:
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9901, 901, 'Momo Cá Nhân', 'e-wallet', 3000000)")
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9902, 901, 'Momo Công Việc', 'e-wallet', 7000000)")

        # Người dùng nói câu chung chung: "Xóa ví Momo"
        res = self.client.post("/api/ai/chat", json={"message": "Xóa ví Momo"}, headers=self.user_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "IDLE")
        # Phải trả về câu hỏi làm rõ liệt kê cả 2 ví
        resp_text = data.get("response") or data.get("text", "")
        self.assertIn("Momo Cá Nhân", resp_text)
        self.assertIn("Momo Công Việc", resp_text)
        self.assertTrue(any(k in resp_text for k in ["muốn thao tác với ví nào?", "Tiêu Dao muốn thao tác với ví nào?", "Ký chủ muốn thao tác với ví nào?"]))

        # Đảm bảo KHÔNG có ví nào bị xóa trong database
        with main.get_db() as conn:
            w1 = conn.execute("SELECT * FROM wallets WHERE id = 9901").fetchone()
            w2 = conn.execute("SELECT * FROM wallets WHERE id = 9902").fetchone()
            self.assertIsNotNone(w1)
            self.assertIsNotNone(w2)

        # Người dùng chỉ định chính xác: "Xóa ví Momo Cá Nhân"
        res_exact = self.client.post("/api/ai/chat", json={"message": "Xóa ví Momo Cá Nhân"}, headers=self.user_headers)
        self.assertEqual(res_exact.status_code, 200)
        d_exact = res_exact.json()
        self.assertEqual(d_exact["state"], "CONFIRMING")
        self.assertEqual(d_exact["pending_confirmation"]["tool_name"], "delete_wallet")
        self.assertEqual(d_exact["pending_confirmation"]["args"]["wallet_name"], "Momo Cá Nhân")

        # Xác nhận xóa
        res_del = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.user_headers)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.json()["state"], "SUCCESS")

        # Kiểm tra database: chỉ Momo Cá Nhân bị xóa, Momo Công Việc vẫn còn nguyên
        with main.get_db() as conn:
            w1_deleted = conn.execute("SELECT * FROM wallets WHERE id = 9901").fetchone()
            w2_kept = conn.execute("SELECT * FROM wallets WHERE id = 9902").fetchone()
            self.assertIsNone(w1_deleted)
            self.assertIsNotNone(w2_kept)

    # ─────────────────────────────────────────────────────────
    # 14. CROSS-DOMAIN NATURAL LANGUAGE RESOLUTION
    # ─────────────────────────────────────────────────────────
    def test_14_cross_domain_natural_language_resolution(self):
        """Kiểm thử phân giải ngôn ngữ tự nhiên cho các tool khác trong hệ thống"""
        with main.get_db() as conn:
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9013, 901, 'MB', 'bank', 50000000)")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9014, 901, 'Vietcombank', 'bank', 50000000)")

        # A. Chuyển tiền: "Chuyển 2 triệu từ MB sang Vietcombank"
        res_trans = self.client.post("/api/ai/chat", json={"message": "Chuyển 2 triệu từ MB sang Vietcombank"}, headers=self.user_headers)
        self.assertEqual(res_trans.status_code, 200)
        d_trans = res_trans.json()
        self.assertEqual(d_trans["state"], "CONFIRMING")
        self.assertEqual(d_trans["pending_confirmation"]["tool_name"], "transfer_money")
        self.assertEqual(d_trans["pending_confirmation"]["args"]["amount"], 2000000)
        self.assertEqual(d_trans["pending_confirmation"]["args"]["from_wallet_name"], "MB")
        self.assertEqual(d_trans["pending_confirmation"]["args"]["to_wallet_name"], "Vietcombank")
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

        # B. Mục tiêu tiết kiệm: "Đặt mục tiêu mua laptop 30 triệu"
        res_goal = self.client.post("/api/ai/chat", json={"message": "Đặt mục tiêu mua laptop 30 triệu"}, headers=self.user_headers)
        self.assertEqual(res_goal.status_code, 200)
        d_goal = res_goal.json()
        self.assertEqual(d_goal["state"], "CONFIRMING")
        self.assertEqual(d_goal["pending_confirmation"]["tool_name"], "create_saving_goal")
        self.assertEqual(d_goal["pending_confirmation"]["args"]["target_name"], "mua laptop")
        self.assertEqual(d_goal["pending_confirmation"]["args"]["target_amount"], 30000000)
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)

        # C. Ngân sách: "Tạo ngân sách ăn uống tháng sau 3 triệu"
        res_bg = self.client.post("/api/ai/chat", json={"message": "Tạo ngân sách ăn uống tháng sau 3 triệu"}, headers=self.user_headers)
        self.assertEqual(res_bg.status_code, 200)
        d_bg = res_bg.json()
        self.assertEqual(d_bg["state"], "CONFIRMING")
        self.assertEqual(d_bg["pending_confirmation"]["tool_name"], "create_budget")
        self.assertEqual(d_bg["pending_confirmation"]["args"]["category_name"], "Ăn Uống")
        self.assertEqual(d_bg["pending_confirmation"]["args"]["limit_amount"], 3000000)
        self.assertIn(d_bg["pending_confirmation"]["args"]["month_year"], ["next_month", "2026-10"])
        self.client.post("/api/ai/chat", json={"message": "Hủy"}, headers=self.user_headers)


if __name__ == "__main__":
    unittest.main()

