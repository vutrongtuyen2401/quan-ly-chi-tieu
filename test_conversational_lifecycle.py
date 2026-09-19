"""
Test Suite: Conversational Action Lifecycle & Voice Lifecycle
Kiểm thử toàn diện luồng hành động đàm thoại của Khí Linh:
- Complete transfer command enters CONFIRMING directly without asking for amount
- Follow-up parameter merging ("1 triệu", wallet names, selection indices)
- Multiple matching wallets resolution
- "Tiền mặt" wallet resolution and missing wallet safety (no auto-create)
- Execution upon confirmation and DB balance updates
- Modification ("đổi thành 2 triệu") and re-confirmation
- Cancellation ("hủy", "thôi") clears pending action
- Unrelated new intent overrides old pending action
- Timeout/Close (/api/ai/cancel-pending) clears pending action so subsequent "xác nhận" does nothing
- Multi-user pending action isolation (no leak between sessions)
- Large Khí Linh (Knowledge mode) cannot execute or access pending actions
"""

import os
import unittest
import tempfile
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_key_lifecycle_test_456"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_lifecycle_456"

import main
from main import app, init_db, create_token
from ai_agent import AgentCore, MockAIProvider, build_default_tool_registry, AgentState, AgentMode


class TestConversationalLifecycle(unittest.TestCase):
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
            conn.execute(
                "INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) "
                "VALUES (101, 'user101@example.com', 'hash', 'Đạo Hữu Tu Tiên', 'user')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) "
                "VALUES (102, 'user102@example.com', 'hash', 'Đạo Hữu Phụ', 'user')"
            )
            conn.execute("DELETE FROM chat_sessions WHERE user_id IN (101, 102)")
            conn.execute("DELETE FROM transactions WHERE user_id IN (101, 102)")
            conn.execute("DELETE FROM budgets WHERE user_id IN (101, 102)")
            conn.execute("DELETE FROM debts WHERE user_id IN (101, 102)")
            conn.execute("DELETE FROM saving_goals WHERE user_id IN (101, 102)")
            conn.execute("DELETE FROM wallets WHERE user_id IN (101, 102)")

            # Wallets for User 1:
            # 1. E-wallet MoMo (E_WALLET)
            conn.execute(
                "INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) "
                "VALUES (1001, 101, 'MoMo', 'E_WALLET', 5000000)"
            )
            # 2. Cash wallet (CASH)
            conn.execute(
                "INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) "
                "VALUES (1002, 101, 'Tiền mặt', 'CASH', 2000000)"
            )
            # 3. Bank wallet 1: Vietcombank
            conn.execute(
                "INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) "
                "VALUES (1003, 101, 'Vietcombank', 'BANK', 10000000)"
            )
            # 4. Bank wallet 2: Techcombank
            conn.execute(
                "INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) "
                "VALUES (1004, 101, 'Techcombank', 'BANK', 8000000)"
            )

            # Wallets for User 2 (For multi-user isolation test)
            conn.execute(
                "INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) "
                "VALUES (2001, 102, 'Ví Phụ', 'CASH', 1000000)"
            )

        self.token1 = create_token(user_id=101, email="user101@example.com", role="user")
        self.headers1 = {"Authorization": f"Bearer {self.token1}"}

        self.token2 = create_token(user_id=102, email="user102@example.com", role="user")
        self.headers2 = {"Authorization": f"Bearer {self.token2}"}

        self.mock_provider = MockAIProvider(default_response="Tiên Trí ghi nhận mệnh lệnh.")
        self.agent_core = AgentCore(provider=self.mock_provider, registry=build_default_tool_registry())
        main.set_agent_core(self.agent_core)

    def test_01_complete_transfer_enters_confirming_immediately(self):
        """Example A: 'chuyển 1 triệu từ ví điện tử sang tiền mặt' -> CONFIRMING immediately, no amount question"""
        res = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ ví điện tử sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        pending = data["pending_confirmation"]
        self.assertEqual(pending["tool_name"], "transfer_money")
        self.assertEqual(pending["args"]["amount"], 1000000)
        self.assertEqual(pending["args"]["from_wallet_name"], "MoMo")
        self.assertEqual(pending["args"]["to_wallet_name"], "Tiền mặt")
        # Ensure it does NOT ask "muốn chuyển bao nhiêu"
        self.assertNotIn("bao nhiêu", data["response"].lower())

    def test_02_missing_amount_followup_merging(self):
        """Example B: 'chuyển tiền từ MoMo sang tiền mặt' -> asks amount -> '1 triệu' -> CONFIRMING immediately"""
        # Turn 1: Partial request
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển tiền từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertIn("bao nhiêu", data1["response"].lower())

        # Verify pending action is stored
        pending1 = self.agent_core.get_pending_action(101)
        self.assertIsNotNone(pending1)
        self.assertEqual(pending1["status"], "AWAITING_PARAM")
        self.assertEqual(pending1["missing_param"], "amount")

        # Turn 2: Follow-up response with amount
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "1 triệu", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()

        # Must merge and immediately enter CONFIRMING without another conversational turn!
        self.assertEqual(data2["state"], "CONFIRMING")
        self.assertIsNotNone(data2["pending_confirmation"])
        self.assertEqual(data2["pending_confirmation"]["args"]["amount"], 1000000)
        self.assertEqual(data2["pending_confirmation"]["args"]["from_wallet_name"], "MoMo")
        self.assertEqual(data2["pending_confirmation"]["args"]["to_wallet_name"], "Tiền mặt")

    def test_03_multiple_bank_wallets_resolution(self):
        """Example C: 'chuyển 1 triệu từ ngân hàng sang tiền mặt' -> asks which bank -> 'Vietcombank' -> CONFIRMING"""
        # Turn 1: Ambiguous source bank
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ ngân hàng sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertIn("Vietcombank", data1["response"])
        self.assertIn("Techcombank", data1["response"])

        pending1 = self.agent_core.get_pending_action(101)
        self.assertIsNotNone(pending1)
        self.assertEqual(pending1["missing_param"], "from_wallet_name")

        # Turn 2: Follow-up with bank name
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "Vietcombank", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()

        self.assertEqual(data2["state"], "CONFIRMING")
        self.assertIsNotNone(data2["pending_confirmation"])
        self.assertEqual(data2["pending_confirmation"]["args"]["from_wallet_name"], "Vietcombank")
        self.assertEqual(data2["pending_confirmation"]["args"]["to_wallet_name"], "Tiền mặt")
        self.assertEqual(data2["pending_confirmation"]["args"]["amount"], 1000000)

    def test_04_multiple_bank_selection_by_index(self):
        """Selection by number: user says '1' to select first wallet option"""
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ ngân hàng sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "1", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["state"], "CONFIRMING")
        self.assertEqual(data2["pending_confirmation"]["args"]["from_wallet_name"], "Vietcombank")

    def test_05_missing_cash_wallet_reported_no_auto_create(self):
        """If 'tiền mặt' does not exist, reports not found and does NOT auto-create wallet"""
        # User 102 only has 'Ví Phụ', no 'Tiền mặt'
        res = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 500 nghìn từ Ví Phụ sang tiền mặt", "mode": "action"},
            headers=self.headers2
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("không tìm thấy", data["response"].lower())

        # Ensure no new wallet was created
        with main.get_db() as conn:
            wallets = conn.execute("SELECT wallet_name FROM wallets WHERE user_id = 102").fetchall()
            names = [w["wallet_name"] for w in wallets]
            self.assertNotIn("Tiền mặt", names)
            self.assertEqual(len(names), 1)

    def test_06_pending_transfer_modification(self):
        """Example D: Pending transfer -> 'đổi thành 2 triệu' -> amount updated -> remains CONFIRMING"""
        # Step 1: Create pending transfer
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ ví điện tử sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )

        # Step 2: Modify amount
        res = self.client.post(
            "/api/ai/chat",
            json={"message": "đổi thành 2 triệu", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 2000000)

        # Step 3: Confirm modified amount
        res_conf = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res_conf.status_code, 200)
        data_conf = res_conf.json()
        self.assertEqual(data_conf["state"], "SUCCESS")

        # Verify DB updated by 2,000,000 (MoMo: 5M -> 3M, Tiền mặt: 2M -> 4M)
        with main.get_db() as conn:
            momo_bal = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
            cash_bal = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
        self.assertEqual(momo_bal, 3000000)
        self.assertEqual(cash_bal, 4000000)

    def test_07_pending_transfer_execution(self):
        """Example E: Complete transfer -> 'xác nhận' -> executed, verified DB mutation, pending cleared"""
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )

        res = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "transfer_money")

        # Verify DB balances (MoMo: 5M -> 4M, Tiền mặt: 2M -> 3M)
        with main.get_db() as conn:
            momo = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
            cash = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
        self.assertEqual(momo, 4000000)
        self.assertEqual(cash, 3000000)

        # Verify pending action cleared
        self.assertIsNone(self.agent_core.get_pending_action(101))

        # Subsequent "xác nhận" does not re-execute!
        res_stale = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res_stale.status_code, 200)
        self.assertNotEqual(res_stale.json()["state"], "SUCCESS")
        self.assertTrue("không có" in res_stale.json()["response"].lower() and "chờ xác nhận" in res_stale.json()["response"].lower())

    def test_08_pending_cancellation(self):
        """Example F: Pending transfer -> 'hủy' -> cleared, no DB mutation"""
        with main.get_db() as conn:
            momo_before = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]

        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        res = self.client.post(
            "/api/ai/chat",
            json={"message": "hủy", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("hủy", data["response"].lower())
        self.assertIsNone(self.agent_core.get_pending_action(101))

        # DB must be unchanged
        with main.get_db() as conn:
            momo_after = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(momo_before, momo_after)

    def test_09_unrelated_new_intent_overrides_pending(self):
        """Pending transfer -> 'Hôm nay tôi ăn sáng 50 nghìn.' -> cancels transfer, plans expense for 50k"""
        # Step 1: Create pending transfer
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # Step 2: Unrelated new expense intent
        res = self.client.post(
            "/api/ai/chat",
            json={"message": "Hôm nay tôi ăn sáng 50 nghìn.", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # The new action should be create_expense, NOT transfer_money
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_expense")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 50000)

    def test_10_cancel_pending_api_endpoint(self):
        """Test POST /api/ai/cancel-pending endpoint directly"""
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # Call cancel endpoint (same as frontend timeout / X close)
        res_cancel = self.client.post("/api/ai/cancel-pending", headers=self.headers1)
        self.assertEqual(res_cancel.status_code, 200)
        self.assertIn(res_cancel.json()["status"], ("ok", "success"))

        # Verify pending cleared on backend
        self.assertIsNone(self.agent_core.get_pending_action(101))

        # Stale confirmation attempt MUST NOT execute
        res_conf = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertTrue("không có" in res_conf.json()["response"].lower() and "chờ xác nhận" in res_conf.json()["response"].lower())

    def test_11_parameter_reply_after_timeout_does_not_revive_action(self):
        """Missing param transfer -> timeout (/api/ai/cancel-pending) -> '1 triệu' -> does NOT revive old action"""
        # Turn 1: Partial transfer
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển tiền từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # 10s silence timeout occurs
        self.client.post("/api/ai/cancel-pending", headers=self.headers1)

        # User says "1 triệu" after timeout
        res = self.client.post(
            "/api/ai/chat",
            json={"message": "1 triệu", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        # Should not enter CONFIRMING for transfer
        self.assertNotEqual(res.json().get("state"), "CONFIRMING")

    def test_12_multi_user_pending_action_isolation(self):
        """User 101's pending action does NOT leak to User 102"""
        # User 101 creates pending transfer
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))
        self.assertIsNone(self.agent_core.get_pending_action(102))

        # User 102 says "xác nhận"
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers2
        )
        self.assertEqual(res2.status_code, 200)
        self.assertTrue("không có" in res2.json()["response"].lower() and "chờ xác nhận" in res2.json()["response"].lower())

        # User 101's pending action is still intact
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # User 101 can confirm their own action
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["state"], "SUCCESS")

    def test_13_large_khi_linh_knowledge_mode_no_mutation_or_pending(self):
        """Large Khí Linh (mode = 'knowledge') cannot execute mutations or access pending actions"""
        # User 101 sets pending action in Action mode
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )

        # Attempting "xác nhận" in Knowledge mode is strictly rejected
        res_know = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "knowledge"},
            headers=self.headers1
        )
        self.assertEqual(res_know.status_code, 200)
        data = res_know.json()
        self.assertIn("Khí Linh AI Lớn hoạt động ở chế độ Tra cứu Tri thức", data["response"])
        self.assertNotEqual(data["state"], "SUCCESS")

        # Direct mutation command in Knowledge mode is also rejected
        res_mut = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "knowledge"},
            headers=self.headers1
        )
        self.assertEqual(res_mut.status_code, 200)
        self.assertIn("không có quyền thực hiện thao tác này", res_mut.json()["response"])

    def test_14_missing_destination_wallet_followup(self):
        """User: 'chuyển 1 triệu từ MoMo' -> AI asks destination -> 'tiền mặt' -> CONFIRMING"""
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        self.assertIn("sang ví nào", res1.json()["response"].lower())

        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["state"], "CONFIRMING")
        self.assertEqual(data2["pending_confirmation"]["args"]["from_wallet_name"], "MoMo")
        self.assertEqual(data2["pending_confirmation"]["args"]["to_wallet_name"], "Tiền mặt")
        self.assertEqual(data2["pending_confirmation"]["args"]["amount"], 1000000)

    def test_15_confirmation_after_timeout_does_not_execute(self):
        """Example G: Pending transfer -> 10s timeout (/api/ai/cancel-pending) -> 'xác nhận' -> does NOT execute"""
        with main.get_db() as conn:
            momo_start = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]

        # Step 1: Create pending transfer
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # Step 2: 10s timeout triggers /api/ai/cancel-pending
        res_to = self.client.post("/api/ai/cancel-pending", headers=self.headers1)
        self.assertEqual(res_to.status_code, 200)
        self.assertIsNone(self.agent_core.get_pending_action(101))

        # Step 3: User says 'xác nhận' after timeout
        res_conf = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res_conf.status_code, 200)
        self.assertNotEqual(res_conf.json()["state"], "SUCCESS")
        self.assertTrue("không có" in res_conf.json()["response"].lower() and "chờ xác nhận" in res_conf.json()["response"].lower())

        # Balance remains unmodified
        with main.get_db() as conn:
            momo_after = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(momo_start, momo_after)

    def test_16_confirmation_after_x_close_does_not_execute(self):
        """Pending transfer -> X close (/api/ai/cancel-pending) -> 'xác nhận' -> does NOT execute"""
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # User clicks X in Live Mode
        res_x = self.client.post("/api/ai/cancel-pending", headers=self.headers1)
        self.assertEqual(res_x.status_code, 200)

        # 'xác nhận' afterwards cannot execute anything
        res_conf = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertNotEqual(res_conf.json()["state"], "SUCCESS")
        self.assertIsNone(self.agent_core.get_pending_action(101))

    def test_17_parameter_reply_after_x_does_not_revive_action(self):
        """Missing param transfer -> X close -> 'MoMo' -> does not revive old action"""
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        # Close with X
        self.client.post("/api/ai/cancel-pending", headers=self.headers1)

        # Parameter reply
        res = self.client.post(
            "/api/ai/chat",
            json={"message": "MoMo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(res.json().get("state"), "CONFIRMING")

    def test_18_transfer_insufficient_balance_does_not_report_success(self):
        """Transfer amount exceeds balance -> confirms -> tool fails -> state ERROR, no balance change"""
        with main.get_db() as conn:
            momo_before = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]

        # Request transfer 50M (MoMo only has 5M)
        self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 50 triệu từ MoMo sang tiền mặt", "mode": "action"},
            headers=self.headers1
        )

        res_conf = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res_conf.status_code, 200)
        data = res_conf.json()
        self.assertNotEqual(data["state"], "SUCCESS")
        self.assertEqual(data["state"], "ERROR")
        self.assertIn("không đủ", data["response"].lower())

        with main.get_db() as conn:
            momo_after = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(momo_before, momo_after)

    def test_19_transfer_with_amount_immediate_confirming(self):
        """User: 'chuyển 1 triệu từ ví tiền mặt sang ví momo' -> enters CONFIRMING immediately"""
        with main.get_db() as conn:
            cash_before = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_before = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]

        res = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ ví tiền mặt sang ví momo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNone(data["tool_executed"])
        self.assertIsNotNone(data["pending_confirmation"])
        p = data["pending_confirmation"]
        self.assertEqual(p["tool_name"], "transfer_money")
        self.assertEqual(p["args"]["amount"], 1000000.0)
        self.assertEqual(p["args"]["from_wallet_id"], 1002)
        self.assertEqual(p["args"]["to_wallet_id"], 1001)

        # Balances remain untouched before confirmation
        with main.get_db() as conn:
            cash_after = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_after = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(cash_before, cash_after)
        self.assertEqual(momo_before, momo_after)

    def test_20_transfer_without_amount_full_lifecycle_and_mutation_safety(self):
        """Turn 1: 'chuyển từ ví tiền mặt sang ví momo' -> asks amount (NO mutation).
        Turn 2 (invalid confirm): 'xác nhận' -> blocked because amount is missing.
        Turn 3 (follow-up): '1 triệu' -> merges amount -> enters CONFIRMING.
        Turn 4: 'xác nhận' -> executes transfer atomically.
        """
        with main.get_db() as conn:
            cash_start = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_start = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]

        # Turn 1: Transfer without amount
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển từ ví tiền mặt sang ví momo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["state"], "IDLE")
        self.assertIsNone(data1["tool_executed"])
        self.assertIsNone(data1["tool_result"])
        self.assertIn("bao nhiêu", data1["response"].lower())
        p1 = data1["pending_confirmation"]
        self.assertIsNotNone(p1)
        self.assertEqual(p1["tool_name"], "transfer_money")
        self.assertEqual(p1["status"], "AWAITING_PARAM")
        self.assertEqual(p1["missing_param"], "amount")
        self.assertEqual(p1["args"]["from_wallet_id"], 1002)
        self.assertEqual(p1["args"]["to_wallet_id"], 1001)

        # Database is completely untouched!
        with main.get_db() as conn:
            cash_mid1 = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_mid1 = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(cash_start, cash_mid1)
        self.assertEqual(momo_start, momo_mid1)

        # Turn 2: Premature confirmation while amount is missing must NOT execute
        res_premature = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res_premature.status_code, 200)
        data_premature = res_premature.json()
        self.assertNotEqual(data_premature["state"], "SUCCESS")
        self.assertIn("chưa đủ thông tin", data_premature["response"].lower())

        with main.get_db() as conn:
            cash_mid2 = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_mid2 = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(cash_start, cash_mid2)
        self.assertEqual(momo_start, momo_mid2)

        # Turn 3: Follow-up amount '1 triệu'
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "1 triệu", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["state"], "CONFIRMING")
        p2 = data2["pending_confirmation"]
        self.assertIsNotNone(p2)
        self.assertEqual(p2["args"]["amount"], 1000000.0)
        self.assertEqual(p2["args"]["from_wallet_id"], 1002)
        self.assertEqual(p2["args"]["to_wallet_id"], 1001)
        self.assertIn("xác nhận", data2["response"].lower())

        # Still no financial mutation before confirmation!
        with main.get_db() as conn:
            cash_mid3 = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_mid3 = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(cash_start, cash_mid3)
        self.assertEqual(momo_start, momo_mid3)

        # Turn 4: Confirmation 'xác nhận' executes the transfer
        res3 = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res3.status_code, 200)
        data3 = res3.json()
        self.assertEqual(data3["state"], "SUCCESS")
        self.assertEqual(data3["tool_executed"], "transfer_money")
        self.assertIsNone(self.agent_core.get_pending_action(101))

        # Verified mutation: 1M transferred from cash (2M -> 1M) to MoMo (5M -> 6M)
        with main.get_db() as conn:
            cash_end = conn.execute("SELECT balance FROM wallets WHERE id = 1002").fetchone()["balance"]
            momo_end = conn.execute("SELECT balance FROM wallets WHERE id = 1001").fetchone()["balance"]
        self.assertEqual(cash_end, cash_start - 1000000.0)
        self.assertEqual(momo_end, momo_start + 1000000.0)

    def test_21_transfer_without_amount_cancellation(self):
        """User: 'chuyển từ ví tiền mặt sang ví momo' -> 'hủy' -> clears pending action"""
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển từ ví tiền mặt sang ví momo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        self.assertIsNotNone(self.agent_core.get_pending_action(101))

        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "hủy", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        self.assertIn("hủy", res2.json()["response"].lower())
        self.assertIsNone(self.agent_core.get_pending_action(101))

    def test_22_transfer_missing_wallet_not_found(self):
        """User transfers to/from non-existent wallet -> clear wallet-not-found response, no auto wallet create"""
        with main.get_db() as conn:
            wallets_before = conn.execute("SELECT COUNT(*) FROM wallets WHERE user_id = 101").fetchone()[0]

        res = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 1 triệu từ ví tiền mặt sang ví không tồn tại xyz", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("không tìm thấy ví", data["response"].lower())
        self.assertIsNone(self.agent_core.get_pending_action(101))

        # Ensure no wallet was created automatically
        with main.get_db() as conn:
            wallets_after = conn.execute("SELECT COUNT(*) FROM wallets WHERE user_id = 101").fetchone()[0]
        self.assertEqual(wallets_before, wallets_after)

    def test_23_transfer_ambiguous_wallet(self):
        """When multiple wallets match, system asks for clarification without auto-guessing"""
        with main.get_db() as conn:
            conn.execute(
                "INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) "
                "VALUES (1005, 101, 'MoMo Phụ', 'E_WALLET', 1000000)"
            )

        res = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển 500k từ ví tiền mặt sang ví momo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("có 2 ví", data["response"].lower())
        self.assertEqual(data["state"], "IDLE")

        # Disambiguate by replying with selection index '1'
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "1", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["state"], "CONFIRMING")

    def test_24_transfer_reversed_source_and_destination(self):
        """User: 'chuyển từ ví momo sang ví tiền mặt' -> source is MoMo, dest is Tiền mặt"""
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển từ ví momo sang ví tiền mặt", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        p1 = res1.json()["pending_confirmation"]
        self.assertIsNotNone(p1)
        self.assertEqual(p1["args"]["from_wallet_id"], 1001)  # MoMo
        self.assertEqual(p1["args"]["to_wallet_id"], 1002)    # Tiền mặt

        # Provide amount
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "500 nghìn", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        p2 = res2.json()["pending_confirmation"]
        self.assertEqual(p2["args"]["amount"], 500000.0)
        self.assertEqual(p2["args"]["from_wallet_id"], 1001)
        self.assertEqual(p2["args"]["to_wallet_id"], 1002)

        # Confirm
        res3 = self.client.post(
            "/api/ai/chat",
            json={"message": "xác nhận", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["state"], "SUCCESS")

    def test_25_repeated_transfer_command_no_nonetype_exception(self):
        """Calling transfer command consecutively when pending action exists must NOT raise NoneType exception"""
        # Call 1
        res1 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển từ ví tiền mặt sang ví momo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res1.status_code, 200)
        self.assertNotIn("Tiên Trí gặp trở ngại", res1.json().get("response", ""))

        # Call 2: repeated identical command
        res2 = self.client.post(
            "/api/ai/chat",
            json={"message": "chuyển từ ví tiền mặt sang ví momo", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res2.status_code, 200)
        self.assertNotIn("Tiên Trí gặp trở ngại", res2.json().get("response", ""))
        self.assertIn("bao nhiêu", res2.json()["response"].lower())

        # Call 3: follow-up amount succeeds
        res3 = self.client.post(
            "/api/ai/chat",
            json={"message": "1 triệu", "mode": "action"},
            headers=self.headers1
        )
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["state"], "CONFIRMING")


if __name__ == "__main__":
    unittest.main()


