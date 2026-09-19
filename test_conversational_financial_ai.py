"""
Regression Test Suite: Conversational Financial AI Agent
Kiểm thử toàn diện 12 hạng mục trọng yếu theo yêu cầu kiến trúc:
1. General conversation (chào hỏi, tu tiên, đàm đạo phi tài chính) -> IDLE, không tool
2. Financial question không có amount ("Gợi ý chi tiêu...", "Nên chi tiêu thế nào?") -> IDLE, advice, không write tool
3. Financial analysis có amount nhưng là giả định ("Nếu muốn tiết kiệm thêm 2 triệu...") -> IDLE, không tạo transaction
4. Financial read ("Tháng này tôi đã chi bao nhiêu?", "Ví còn bao nhiêu?") -> SUCCESS, read tool, không mutation
5. Expense write ("Hôm nay tôi ăn sáng hết 50 nghìn") -> CONFIRMING, create_expense
6. Income write ("Nhận lương 15 triệu") -> CONFIRMING, create_income
7. Budget write ("Đặt ngân sách ăn uống tháng sau là 3 triệu") -> CONFIRMING, create_budget
8. Transfer ("Chuyển 500k từ ví Tiền Mặt sang ví Ngân Hàng") -> CONFIRMING, transfer_money
9. Confirmation ("Xác nhận") -> SUCCESS, execute pending action
10. Cancellation ("Hủy khoản vừa rồi") -> IDLE, clear pending, DB nguyên vẹn
11. Modification ("Đổi thành 70 nghìn") -> CONFIRMING, update pending args
12. Orphan confirmation ("Xác nhận" khi không có pending) -> IDLE, từ chối an toàn
"""

import os
import unittest
import tempfile
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_key_financial_ai_conversational_999"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_123"

import main
from main import app, init_db, create_token
from ai_agent import AgentCore, MockAIProvider, build_default_tool_registry, AgentState


class TestConversationalFinancialAI(unittest.TestCase):
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
        # Thiết lập user và dữ liệu nền tảng
        with main.get_db() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id = 777")
            conn.execute("DELETE FROM transactions WHERE user_id = 777")
            conn.execute("DELETE FROM budgets WHERE user_id = 777")
            conn.execute("DELETE FROM saving_goals WHERE user_id = 777")
            conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (777, 'conversational_ai@gmail.com', 'dummy_hash', 'Đạo Hữu Tiên Trí', 'user')")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (7771, 777, 'Ví Tiền Mặt', 'CASH', 5000000)")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (7772, 777, 'Ví Ngân Hàng', 'BANK', 10000000)")
            conn.execute("INSERT OR REPLACE INTO categories (id, user_id, category_name, category_type, icon) VALUES (7771, 777, 'Ăn Uống', 'EXPENSE', '🍜')")
            conn.execute("INSERT OR REPLACE INTO categories (id, user_id, category_name, category_type, icon) VALUES (7772, 777, 'Tiền Lương', 'INCOME', '💵')")
            conn.execute("INSERT OR REPLACE INTO saving_goals (id, user_id, target_name, target_amount, current_amount) VALUES (7771, 777, 'Mua Phi Kiếm', 20000000, 3000000)")

        self.token = create_token(user_id=777, email="conversational_ai@gmail.com", role="user")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        self.mock_provider = MockAIProvider(default_response="Khí Linh Tiên Trí xin đàm đạo cùng đạo hữu: Hãy tu dưỡng tâm tính và quản lý ngân sách vững vàng.")
        self.core = AgentCore(provider=self.mock_provider, registry=build_default_tool_registry())
        main.set_agent_core(self.core)

    # ─────────────────────────────────────────────────────────────
    # 1. GENERAL CONVERSATION (Không gọi tool, IDLE)
    # ─────────────────────────────────────────────────────────────
    def test_01_general_conversation(self):
        """1. General conversation: Chào hỏi, đàm đạo tu tiên -> Trả lời tự nhiên, không gọi tool tài chính"""
        for query in [
            "Xin chào Khí Linh",
            "Đạo pháp tu tiên là gì?",
            "Ngươi là ai?",
            "Hôm nay thời tiết thế nào?"
        ]:
            res = self.client.post("/api/ai/chat", json={"message": query}, headers=self.headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["state"], "IDLE", f"Failed IDLE state for: {query}")
            self.assertIsNone(data.get("tool_executed"), f"Tool should not be executed for: {query}")
            self.assertIsNone(data.get("pending_confirmation"))
            self.assertNotIn("số tiền phải lớn hơn 0", data["response"].lower())

    # ─────────────────────────────────────────────────────────────
    # 2. FINANCIAL QUESTION KHÔNG CÓ AMOUNT (Advice / Analysis)
    # ─────────────────────────────────────────────────────────────
    def test_02_financial_question_without_amount(self):
        """2. Financial question không có amount: Tư vấn/gợi ý chi tiêu -> IDLE, không create_expense, không lỗi amount"""
        for query in [
            "Gợi ý chi tiêu tháng sau cho tôi",
            "Tháng sau tôi nên chi tiêu thế nào?",
            "Làm sao để chi tiêu hợp lý hơn?",
            "Tôi có nên tiết kiệm tiền không?"
        ]:
            res = self.client.post("/api/ai/chat", json={"message": query}, headers=self.headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["state"], "IDLE", f"Failed IDLE state for: {query}")
            self.assertIsNone(data.get("pending_confirmation"), f"Pending confirmation must be None for: {query}")
            self.assertIsNone(data.get("tool_executed"), f"Should not execute write tool for: {query}")
            self.assertNotIn("số tiền phải lớn hơn 0", data["response"].lower())
            self.assertNotIn("chưa rõ thông tin", data["response"].lower())

    # ─────────────────────────────────────────────────────────────
    # 3. FINANCIAL ANALYSIS CÓ AMOUNT NHƯNG LÀ GIẢ ĐỊNH
    # ─────────────────────────────────────────────────────────────
    def test_03_financial_analysis_with_amount_not_transaction(self):
        """3. Financial analysis có amount giả định: 'Nếu tôi muốn tiết kiệm thêm 2 triệu thì nên làm gì?' -> IDLE, không mutation"""
        with main.get_db() as conn:
            txns_before = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 777").fetchone()[0]
            goals_before = conn.execute("SELECT current_amount FROM saving_goals WHERE id = 7771").fetchone()["current_amount"]

        queries = [
            "Nếu tôi muốn tiết kiệm thêm 2 triệu thì nên làm gì?",
            "Giả sử tôi dành 5 triệu đầu tư thì sao?",
            "Nếu tháng sau tôi giảm 1 triệu tiền ăn uống thì có ổn không?"
        ]
        for query in queries:
            res = self.client.post("/api/ai/chat", json={"message": query}, headers=self.headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["state"], "IDLE", f"Hypothetical question must be IDLE for: {query}")
            self.assertIsNone(data.get("pending_confirmation"), f"No pending confirmation should be created for: {query}")

        # Kiểm tra DB tuyệt đối không bị biến động
        with main.get_db() as conn:
            txns_after = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 777").fetchone()[0]
            goals_after = conn.execute("SELECT current_amount FROM saving_goals WHERE id = 7771").fetchone()["current_amount"]
        self.assertEqual(txns_before, txns_after, "Không được tạo transaction giả định")
        self.assertEqual(goals_before, goals_after, "Không được nạp tiền vào saving goal")

    # ─────────────────────────────────────────────────────────────
    # 4. FINANCIAL READ (Tra cứu thông tin tài chính)
    # ─────────────────────────────────────────────────────────────
    def test_04_financial_read(self):
        """4. Financial read: 'Tháng này tôi đã chi bao nhiêu?', 'Ví còn bao nhiêu?' -> SUCCESS, gọi read tool"""
        # A. Tra cứu chi tiêu
        res1 = self.client.post("/api/ai/chat", json={"message": "Tháng này tôi đã chi bao nhiêu?"}, headers=self.headers)
        self.assertEqual(res1.status_code, 200)
        d1 = res1.json()
        self.assertEqual(d1["state"], "SUCCESS")
        self.assertEqual(d1["tool_executed"], "spending_summary")

        # B. Tra cứu số dư ví
        res2 = self.client.post("/api/ai/chat", json={"message": "Ví tiền mặt còn bao nhiêu tiền?"}, headers=self.headers)
        self.assertEqual(res2.status_code, 200)
        d2 = res2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "get_wallets")

        # C. Tra cứu hạn mức
        res3 = self.client.post("/api/ai/chat", json={"message": "Hạn mức chi tiêu thế nào?"}, headers=self.headers)
        self.assertEqual(res3.status_code, 200)
        d3 = res3.json()
        self.assertEqual(d3["state"], "SUCCESS")
        self.assertEqual(d3["tool_executed"], "get_budget_status")

    # ─────────────────────────────────────────────────────────────
    # 5. EXPENSE WRITE (Chi tiêu có số tiền)
    # ─────────────────────────────────────────────────────────────
    def test_05_expense_write_flow(self):
        """5. Expense write: 'Hôm nay tôi ăn sáng hết 50 nghìn' -> CONFIRMING, create_expense, 50k"""
        res = self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_expense")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 50000)
        self.assertIn("Ăn Uống", str(data["pending_confirmation"]["args"]))

    # ─────────────────────────────────────────────────────────────
    # 6. INCOME WRITE (Thu nhập có số tiền)
    # ─────────────────────────────────────────────────────────────
    def test_06_income_write_flow(self):
        """6. Income write: 'Nhận lương 15 triệu' -> CONFIRMING, create_income, 15tr"""
        res = self.client.post("/api/ai/chat", json={"message": "Nhận lương 15 triệu"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_income")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 15000000)

    # ─────────────────────────────────────────────────────────────
    # 7. BUDGET WRITE (Thiết lập ngân sách mới)
    # ─────────────────────────────────────────────────────────────
    def test_07_budget_write_flow(self):
        """7. Budget write: 'Đặt ngân sách ăn uống tháng sau là 3 triệu' -> CONFIRMING, create_budget, 3tr"""
        res = self.client.post("/api/ai/chat", json={"message": "Đặt ngân sách ăn uống tháng sau là 3 triệu"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_budget")
        self.assertEqual(data["pending_confirmation"]["args"]["limit_amount"], 3000000)
        self.assertEqual(data["pending_confirmation"]["args"]["category_name"], "Ăn Uống")

        # Xác nhận để kiểm tra lưu vào DB
        confirm_res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.headers)
        self.assertEqual(confirm_res.status_code, 200)
        self.assertEqual(confirm_res.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            budget = conn.execute("SELECT * FROM budgets WHERE user_id = 777 ORDER BY id DESC LIMIT 1").fetchone()
            self.assertIsNotNone(budget)
            self.assertEqual(budget["limit_amount"], 3000000)

    # ─────────────────────────────────────────────────────────────
    # 8. TRANSFER MONEY (Chuyển tiền giữa hai ví)
    # ─────────────────────────────────────────────────────────────
    def test_08_transfer_flow(self):
        """8. Transfer: 'Chuyển 500k từ ví Tiền Mặt sang ví Ngân Hàng' -> CONFIRMING, transfer_money, 500k"""
        res = self.client.post("/api/ai/chat", json={"message": "Chuyển 500k từ ví Tiền Mặt sang ví Ngân Hàng"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["tool_name"], "transfer_money")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 500000)

    # ─────────────────────────────────────────────────────────────
    # 9. CONFIRMATION (Xác nhận khi có pending action)
    # ─────────────────────────────────────────────────────────────
    def test_09_confirmation_flow(self):
        """9. Confirmation: Gửi 'Xác nhận' khi đang có pending action -> execute và cập nhật DB"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 7771").fetchone()["balance"]

        # Tạo pending chi tiêu
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn"}, headers=self.headers)

        # Xác nhận
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "create_expense")
        self.assertIsNone(data.get("pending_confirmation"))

        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 7771").fetchone()["balance"]
        self.assertEqual(w_after, w_before - 50000)

    # ─────────────────────────────────────────────────────────────
    # 10. CANCELLATION (Hủy bỏ khi có pending action)
    # ─────────────────────────────────────────────────────────────
    def test_10_cancellation_flow(self):
        """10. Cancellation: Gửi 'Hủy khoản vừa rồi' khi đang có pending action -> hủy pending, DB nguyên vẹn"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 7771").fetchone()["balance"]

        # Tạo pending chi tiêu
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn"}, headers=self.headers)

        # Hủy bằng câu nói tự nhiên
        res = self.client.post("/api/ai/chat", json={"message": "Hủy khoản vừa rồi"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "IDLE")
        self.assertIsNone(data.get("pending_confirmation"))

        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 7771").fetchone()["balance"]
            txns = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 777").fetchone()[0]
        self.assertEqual(w_after, w_before)
        self.assertEqual(txns, 0)

    # ─────────────────────────────────────────────────────────────
    # 11. MODIFICATION (Sửa đổi tham số khi đang pending)
    # ─────────────────────────────────────────────────────────────
    def test_11_modification_flow(self):
        """11. Modification: 'Đổi thành 70 nghìn' khi đang pending -> cập nhật số tiền, giữ CONFIRMING"""
        # Tạo pending 50k
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn"}, headers=self.headers)

        # Yêu cầu sửa đổi
        res = self.client.post("/api/ai/chat", json={"message": "Đổi thành 70 nghìn"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 70000)

        # Xác nhận số tiền đã đổi
        res_confirm = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.headers)
        self.assertEqual(res_confirm.status_code, 200)
        self.assertEqual(res_confirm.json()["state"], "SUCCESS")

        with main.get_db() as conn:
            txn = conn.execute("SELECT * FROM transactions WHERE user_id = 777 ORDER BY id DESC LIMIT 1").fetchone()
            self.assertIsNotNone(txn)
            self.assertEqual(txn["amount"], 70000)

    # ─────────────────────────────────────────────────────────────
    # 12. ORPHAN CONFIRMATION (Xác nhận khi không có pending)
    # ─────────────────────────────────────────────────────────────
    def test_12_orphan_confirmation_rejected(self):
        """12. Orphan confirmation: Gửi 'Xác nhận' khi không có pending action -> IDLE, từ chối an toàn"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 7771").fetchone()["balance"]
            txns_before = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 777").fetchone()[0]

        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "IDLE")
        self.assertIsNone(data.get("tool_executed"))
        self.assertIn("không có giao dịch", data["response"].lower())

        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 7771").fetchone()["balance"]
            txns_after = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 777").fetchone()[0]
        self.assertEqual(w_before, w_after)
        self.assertEqual(txns_before, txns_after)


if __name__ == "__main__":
    unittest.main()
