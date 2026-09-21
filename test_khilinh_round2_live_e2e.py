"""
End-to-End Live Verification Test for Khí Linh Round 2 Hotfixes
Tests full lifecycles against FastAPI app + DB:
1. Multi-turn Saving Goal (Name first -> Amount -> Confirm -> DB verify)
2. Multi-turn Saving Goal (Amount first -> Name -> Confirm -> DB verify)
3. Multi-turn Expense Action ("thêm 1 mục chi tiêu mới" -> Amount -> Note/Wallet -> Confirm -> DB verify)
4. Multi-turn Income Action ("thêm khoản thu 10 triệu" -> Note/Wallet -> Confirm -> DB verify)
5. Category Read isolation ("danh mục chi tiêu" -> read list, not action)
"""

import os
import unittest
import tempfile
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_khilinh_round2_e2e_888"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_123"

import main
from main import app, init_db, create_token
from ai_agent import AgentCore, MockAIProvider, build_default_tool_registry

class TestKhiLinhRound2E2ELive(unittest.TestCase):
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
            conn.execute("DELETE FROM chat_sessions WHERE user_id = 999")
            conn.execute("DELETE FROM transactions WHERE user_id = 999")
            conn.execute("DELETE FROM saving_goals WHERE user_id = 999")
            conn.execute("DELETE FROM budgets WHERE user_id = 999")
            conn.execute("DELETE FROM debts WHERE user_id = 999")
            conn.execute("DELETE FROM wallets WHERE user_id = 999")
            conn.execute("DELETE FROM categories WHERE user_id = 999")

            conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (999, 'khilinh_round2_user@gmail.com', 'dummy_hash', 'Đạo Hữu Round 2', 'user')")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9991, 999, 'Ví Tiền Mặt', 'CASH', 5000000)")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9992, 999, 'Vietcombank', 'BANK', 20000000)")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9993, 999, 'MoMo', 'E_WALLET', 3000000)")
            conn.execute("INSERT OR REPLACE INTO categories (id, user_id, category_name, category_type, icon) VALUES (9991, 999, 'Ăn Uống', 'EXPENSE', '🍜')")
            conn.execute("INSERT OR REPLACE INTO categories (id, user_id, category_name, category_type, icon) VALUES (9992, 999, 'Lương', 'INCOME', '💵')")
            conn.execute("INSERT OR REPLACE INTO categories (id, user_id, category_name, category_type, icon) VALUES (9993, 999, 'Thưởng', 'INCOME', '🎁')")

        self.token = create_token(user_id=999, email="khilinh_round2_user@gmail.com", role="user")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        self.mock_provider = MockAIProvider(default_response="Khí Linh đã tiếp nhận khẩu lệnh.")
        self.core = AgentCore(provider=self.mock_provider, registry=build_default_tool_registry())
        main.set_agent_core(self.core)

    def test_e2e_saving_goal_flow_1_name_first(self):
        """Flow 1: 'thêm 1 mục tiêu tiết kiệm mới' -> 'mua iphone' -> '1 triệu' -> 'xác nhận' -> DB verify"""
        # Step 1: "thêm 1 mục tiêu tiết kiệm mới"
        r1 = self.client.post("/api/ai/chat", json={"message": "thêm 1 mục tiêu tiết kiệm mới", "mode": "action"}, headers=self.headers)
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertIsNotNone(d1["pending_confirmation"])
        self.assertEqual(d1["pending_confirmation"]["status"], "AWAITING_PARAM")
        self.assertIn(d1["pending_confirmation"]["missing_param"], ["target_name", "goal_name", "goal_details"])

        # Step 2: "mua iphone"
        r2 = self.client.post("/api/ai/chat", json={"message": "mua iphone", "mode": "action"}, headers=self.headers)
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertIsNotNone(d2["pending_confirmation"])
        self.assertEqual(d2["pending_confirmation"]["status"], "AWAITING_PARAM")
        self.assertEqual(d2["pending_confirmation"]["missing_param"], "target_amount")
        self.assertEqual(d2["pending_confirmation"]["args"]["target_name"], "Mua Iphone")

        # Step 3: "1 triệu"
        r3 = self.client.post("/api/ai/chat", json={"message": "1 triệu", "mode": "action"}, headers=self.headers)
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["state"], "CONFIRMING")
        conf = d3["pending_confirmation"]
        self.assertEqual(conf["tool_name"], "create_saving_goal")
        self.assertEqual(conf["args"]["target_name"], "Mua Iphone")
        self.assertEqual(conf["args"]["target_amount"], 1000000)

        # Step 4: "xác nhận" -> Real DB execution
        r4 = self.client.post("/api/ai/chat", json={"message": "xác nhận", "mode": "action"}, headers=self.headers)
        self.assertEqual(r4.status_code, 200)
        d4 = r4.json()
        self.assertEqual(d4["state"], "SUCCESS")
        self.assertEqual(d4["tool_executed"], "create_saving_goal")

        # Verify record in SQLite database
        with main.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT target_name, target_amount FROM saving_goals WHERE user_id = 999 AND target_name = 'Mua Iphone'")
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Saving goal 'Mua Iphone' must exist in database")
            self.assertEqual(row["target_amount"], 1000000)
        print("✅ E2E Flow 1 (Saving Goal Name First) passed with DB verification.")

    def test_e2e_saving_goal_flow_2_amount_first(self):
        """Flow 2: 'tạo mục tiêu tiết kiệm 50 triệu' -> 'mua ô tô' -> 'xác nhận' -> DB verify"""
        # Step 1: "tạo mục tiêu tiết kiệm 50 triệu"
        r1 = self.client.post("/api/ai/chat", json={"message": "tạo mục tiêu tiết kiệm 50 triệu", "mode": "action"}, headers=self.headers)
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertIsNotNone(d1["pending_confirmation"])
        self.assertEqual(d1["pending_confirmation"]["missing_param"], "target_name")
        self.assertEqual(d1["pending_confirmation"]["args"]["target_amount"], 50000000)

        # Step 2: "mua ô tô"
        r2 = self.client.post("/api/ai/chat", json={"message": "mua ô tô", "mode": "action"}, headers=self.headers)
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2["state"], "CONFIRMING")
        conf = d2["pending_confirmation"]
        self.assertEqual(conf["tool_name"], "create_saving_goal")
        self.assertEqual(conf["args"]["target_name"], "Mua Ô Tô")
        self.assertEqual(conf["args"]["target_amount"], 50000000)

        # Step 3: "xác nhận" -> Real DB execution
        r3 = self.client.post("/api/ai/chat", json={"message": "xác nhận", "mode": "action"}, headers=self.headers)
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["state"], "SUCCESS")
        self.assertEqual(d3["tool_executed"], "create_saving_goal")

        # Verify record in SQLite database
        with main.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT target_name, target_amount FROM saving_goals WHERE user_id = 999 AND target_name = 'Mua Ô Tô'")
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Saving goal 'Mua Ô Tô' must exist in database")
            self.assertEqual(row["target_amount"], 50000000)
        print("✅ E2E Flow 2 (Saving Goal Amount First) passed with DB verification.")

    def test_e2e_expense_flow_3_missing_amount(self):
        """Flow 3: 'thêm 1 mục chi tiêu mới' -> '50k' -> 'ăn trưa ví tiền mặt' -> 'xác nhận' -> DB verify"""
        # Step 1: "thêm 1 mục chi tiêu mới"
        r1 = self.client.post("/api/ai/chat", json={"message": "thêm 1 mục chi tiêu mới", "mode": "action"}, headers=self.headers)
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertIsNotNone(d1["pending_confirmation"])
        self.assertEqual(d1["pending_confirmation"]["missing_param"], "amount")

        # Step 2: "50k"
        r2 = self.client.post("/api/ai/chat", json={"message": "50k", "mode": "action"}, headers=self.headers)
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertIsNotNone(d2["pending_confirmation"])
        self.assertEqual(d2["pending_confirmation"]["args"]["amount"], 50000)

        # Step 3: "ăn trưa ví tiền mặt"
        r3 = self.client.post("/api/ai/chat", json={"message": "ăn trưa ví tiền mặt", "mode": "action"}, headers=self.headers)
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["state"], "CONFIRMING")
        conf = d3["pending_confirmation"]
        self.assertEqual(conf["tool_name"], "create_expense")
        self.assertEqual(conf["args"]["amount"], 50000)
        self.assertIn("ăn trưa", conf["args"]["note"].lower())

        # Step 4: "xác nhận" -> Real DB execution
        r4 = self.client.post("/api/ai/chat", json={"message": "xác nhận", "mode": "action"}, headers=self.headers)
        self.assertEqual(r4.status_code, 200)
        d4 = r4.json()
        self.assertEqual(d4["state"], "SUCCESS")
        self.assertEqual(d4["tool_executed"], "create_expense")

        # Verify transaction in SQLite
        with main.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT amount, transaction_type, note FROM transactions WHERE user_id = 999 AND transaction_type = 'EXPENSE'")
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Expense transaction must exist in DB")
            self.assertEqual(row["amount"], 50000)
        print("✅ E2E Flow 3 (Expense multi-turn) passed with DB verification.")

    def test_e2e_income_flow_4(self):
        """Flow 4: 'thêm khoản thu 10 triệu' -> 'thưởng dự án vào vietcombank' -> 'xác nhận' -> DB verify"""
        # Step 1: "thêm khoản thu 10 triệu"
        r1 = self.client.post("/api/ai/chat", json={"message": "thêm khoản thu 10 triệu", "mode": "action"}, headers=self.headers)
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["state"], "CONFIRMING")
        self.assertEqual(d1["pending_confirmation"]["tool_name"], "create_income")
        self.assertEqual(d1["pending_confirmation"]["args"]["amount"], 10000000)

        # Step 2: "thưởng dự án vào vietcombank" -> updates pending confirmation
        r2 = self.client.post("/api/ai/chat", json={"message": "thưởng dự án vào vietcombank", "mode": "action"}, headers=self.headers)
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2["state"], "CONFIRMING")
        conf = d2["pending_confirmation"]
        self.assertEqual(conf["tool_name"], "create_income")
        self.assertEqual(conf["args"]["amount"], 10000000)
        self.assertEqual(conf["args"]["wallet_name"], "Vietcombank")

        # Step 3: "xác nhận" -> Real DB execution
        r3 = self.client.post("/api/ai/chat", json={"message": "xác nhận", "mode": "action"}, headers=self.headers)
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["state"], "SUCCESS")
        self.assertEqual(d3["tool_executed"], "create_income")

        # Verify transaction in SQLite
        with main.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT amount, transaction_type, note FROM transactions WHERE user_id = 999 AND transaction_type = 'INCOME'")
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Income transaction must exist in DB")
            self.assertEqual(row["amount"], 10000000)
        print("✅ E2E Flow 4 (Income multi-turn) passed with DB verification.")

    def test_e2e_category_read_isolation(self):
        """Flow 5: Pure category read must call get_categories and return list, not create_expense"""
        r = self.client.post("/api/ai/chat", json={"message": "danh mục chi tiêu", "mode": "action"}, headers=self.headers)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertNotEqual(d.get("state"), "CONFIRMING")
        self.assertEqual(d.get("tool_executed"), "get_categories")
        print("✅ E2E Flow 5 (Category Read Isolation) passed.")

if __name__ == "__main__":
    unittest.main()
