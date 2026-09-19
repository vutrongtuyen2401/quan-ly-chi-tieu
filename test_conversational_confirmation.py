"""
Test Suite: Conversational Confirmation — Khí Linh AI Agent
Kiểm thử toàn diện tính năng xác nhận, hủy bỏ và sửa đổi qua đối thoại tự nhiên:
- Case A: User yêu cầu đột biến tài chính -> chuyển sang CONFIRMING, tạo pending action, DB chưa đổi.
- Case B: User xác nhận bằng ngôn ngữ tự nhiên -> thực thi, DB biến động, state SUCCESS.
- Case C: Lượt đối thoại tiếp theo sau khi confirm -> xử lý trơn tru (không bị kẹt hay ngắt session).
- Case D: User sửa đổi bằng ngôn ngữ tự nhiên ("Đổi thành 70 nghìn.") -> pending action được modify, chưa execute.
- Case E: User xác nhận sau khi modify -> execute với dữ liệu đã sửa đổi.
- Case F: User hủy bằng ngôn ngữ tự nhiên ("Thôi, không làm.") -> cancel, pending action bị xóa, DB giữ nguyên.
- Case G: User nói "Xác nhận." khi KHÔNG có pending action -> tuyệt đối không thực thi thao tác tài chính nào.
- Case H: Kiểm thử các biến thể ngôn ngữ tự nhiên phong phú (đồng ý, được, làm đi, ok, không cần, thôi...).
"""

import os
import unittest
import tempfile
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_key_conversational_confirmation_123"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_123"

import main
from main import app, init_db, create_token
from ai_agent import AgentCore, MockAIProvider, build_default_tool_registry, AgentState


class TestConversationalConfirmation(unittest.TestCase):
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
        # Thiết lập user và ví mẫu riêng biệt cho từng test
        with main.get_db() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id = 888")
            conn.execute("DELETE FROM transactions WHERE user_id = 888")
            conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (888, 'conv_user@gmail.com', 'dummy_hash', 'Đạo Hữu Đối Thoại', 'user')")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (8881, 888, 'Ví Tiền Mặt', 'CASH', 5000000)")
            conn.execute("INSERT OR REPLACE INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (8882, 888, 'Ví Ngân Hàng', 'BANK', 10000000)")

        self.token = create_token(user_id=888, email="conv_user@gmail.com", role="user")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        self.mock_provider = MockAIProvider(default_response="Tiên Trí đã lắng nghe lời đạo hữu.")
        self.agent_core = AgentCore(provider=self.mock_provider, registry=build_default_tool_registry())
        main.set_agent_core(self.agent_core)

    def test_case_a_confirmation_required(self):
        """Case A: User: 'Hôm nay tôi ăn sáng hết 50 nghìn.' -> confirmation required, DB unchanged"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]

        res = self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn."}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["tool_name"], "create_expense")
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 50000)
        self.assertIn("Xác nhận", data["response"])

        # Đảm bảo DB chưa bị thay đổi số dư và chưa ghi nhận transaction
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]
            txns = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 888").fetchone()[0]
        self.assertEqual(w_before, w_after)
        self.assertEqual(txns, 0)

    def test_case_b_confirmation_executed(self):
        """Case B: User: 'Xác nhận.' -> transaction executed, balance deducted, DB persistent"""
        # Bước 1: Tạo pending action
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn."}, headers=self.headers)

        # Bước 2: User xác nhận bằng lời nói
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận."}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "create_expense")
        self.assertIsNone(data["pending_confirmation"])

        # Kiểm tra số dư ví bị trừ 50,000 và có transaction EXPENSE
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]
            txn = conn.execute("SELECT * FROM transactions WHERE user_id = 888 ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(w_after, 5000000 - 50000)
        self.assertIsNotNone(txn)
        self.assertEqual(txn["amount"], 50000)
        self.assertEqual(txn["transaction_type"], "EXPENSE")

    def test_case_c_conversation_continues_seamlessly(self):
        """Case C: Sau khi confirm -> 'Tháng này tôi đã chi bao nhiêu cho ăn uống?' -> xử lý như lượt tiếp theo"""
        # 1. Tạo và xác nhận giao dịch chi ăn sáng 50k
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn."}, headers=self.headers)
        self.client.post("/api/ai/chat", json={"message": "Xác nhận."}, headers=self.headers)

        # 2. Ngay lập tức hỏi câu tiếp theo
        res = self.client.post("/api/ai/chat", json={"message": "Tháng này tôi đã chi bao nhiêu cho ăn uống?"}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "spending_by_category")
        self.assertIsNone(data["pending_confirmation"])
        self.assertIn("Ăn Uống", str(data["tool_result"]))

    def test_case_d_modify_pending_action(self):
        """Case D: Đang pending, User: 'Đổi thành 70 nghìn.' -> pending action được modify, chưa execute"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]

        # 1. Tạo yêu cầu 50k
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn."}, headers=self.headers)

        # 2. User yêu cầu đổi số tiền: 'Đổi thành 70 nghìn.'
        res = self.client.post("/api/ai/chat", json={"message": "Đổi thành 70 nghìn."}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Phải giữ nguyên trạng thái CONFIRMING và cập nhật amount lên 70,000
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])
        self.assertEqual(data["pending_confirmation"]["args"]["amount"], 70000)
        self.assertIn("70,000", data["response"])

        # DB vẫn chưa bị trừ tiền
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]
            txns = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 888").fetchone()[0]
        self.assertEqual(w_before, w_after)
        self.assertEqual(txns, 0)

    def test_case_e_confirm_modified_action(self):
        """Case E: User: 'Xác nhận.' sau khi modify -> execute với 70.000đ"""
        self.client.post("/api/ai/chat", json={"message": "Hôm nay tôi ăn sáng hết 50 nghìn."}, headers=self.headers)
        self.client.post("/api/ai/chat", json={"message": "Đổi thành 70 nghìn."}, headers=self.headers)

        # Xác nhận sau khi sửa
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận."}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(data["tool_executed"], "create_expense")

        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]
            txn = conn.execute("SELECT * FROM transactions WHERE user_id = 888 ORDER BY id DESC LIMIT 1").fetchone()
        self.assertEqual(w_after, 5000000 - 70000)
        self.assertEqual(txn["amount"], 70000)

    def test_case_f_cancellation_preserves_db(self):
        """Case F: Pending action: 'Thôi, không làm.' -> cancel, DB unchanged, conversation continues"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]

        # 1. Tạo yêu cầu
        self.client.post("/api/ai/chat", json={"message": "Chi 500k mua linh dược"}, headers=self.headers)

        # 2. Hủy bằng ngôn ngữ tự nhiên: 'Thôi, không làm.'
        res = self.client.post("/api/ai/chat", json={"message": "Thôi, không làm."}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "IDLE")
        self.assertIsNone(data["pending_confirmation"])
        self.assertIn("hủy bỏ", data["response"].lower())

        # DB không đổi
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]
            txns = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 888").fetchone()[0]
        self.assertEqual(w_before, w_after)
        self.assertEqual(txns, 0)

    def test_case_g_orphan_confirmation_rejected(self):
        """Case G: 'Xác nhận.' khi KHÔNG có pending action -> không được execute bất kỳ financial action nào"""
        with main.get_db() as conn:
            w_before = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]

        # Gửi 'Xác nhận.' khi chưa có pending action
        res = self.client.post("/api/ai/chat", json={"message": "Xác nhận."}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["state"], "IDLE")
        self.assertIsNone(data.get("tool_executed"))
        self.assertIsNone(data.get("pending_confirmation"))
        self.assertIn("không có giao dịch", data["response"].lower())

        # Gửi 'Đồng ý' khi chưa có pending action
        res2 = self.client.post("/api/ai/chat", json={"message": "Đồng ý"}, headers=self.headers)
        self.assertEqual(res2.json()["state"], "IDLE")
        self.assertIsNone(res2.json().get("tool_executed"))

        # Gửi 'Làm đi' khi chưa có pending action
        res3 = self.client.post("/api/ai/chat", json={"message": "Làm đi"}, headers=self.headers)
        self.assertEqual(res3.json()["state"], "IDLE")
        self.assertIsNone(res3.json().get("tool_executed"))

        # Đảm bảo 100% DB không có transaction nào phát sinh
        with main.get_db() as conn:
            w_after = conn.execute("SELECT balance FROM wallets WHERE id = 8881").fetchone()["balance"]
            txns = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 888").fetchone()[0]
        self.assertEqual(w_before, w_after)
        self.assertEqual(txns, 0)

    def test_case_h_natural_variations_coverage(self):
        """Case H: Kiểm thử các biến thể ngôn ngữ phong phú (đồng ý, được, làm đi, ok, thôi khỏi, 70k thôi)"""
        # 1. Xác nhận bằng "Đồng ý"
        self.client.post("/api/ai/chat", json={"message": "Chi 20k tiền gửi xe"}, headers=self.headers)
        res1 = self.client.post("/api/ai/chat", json={"message": "Đồng ý"}, headers=self.headers)
        self.assertEqual(res1.json()["state"], "SUCCESS")
        self.assertEqual(res1.json()["tool_executed"], "create_expense")

        # 2. Xác nhận bằng "Được"
        self.client.post("/api/ai/chat", json={"message": "Chi 30k cà phê"}, headers=self.headers)
        res2 = self.client.post("/api/ai/chat", json={"message": "Được"}, headers=self.headers)
        self.assertEqual(res2.json()["state"], "SUCCESS")

        # 3. Xác nhận bằng "Làm đi"
        self.client.post("/api/ai/chat", json={"message": "Chi 40k ăn trưa"}, headers=self.headers)
        res3 = self.client.post("/api/ai/chat", json={"message": "Làm đi"}, headers=self.headers)
        self.assertEqual(res3.json()["state"], "SUCCESS")

        # 4. Xác nhận bằng "OK"
        self.client.post("/api/ai/chat", json={"message": "Chi 25k bánh mì"}, headers=self.headers)
        res4 = self.client.post("/api/ai/chat", json={"message": "OK"}, headers=self.headers)
        self.assertEqual(res4.json()["state"], "SUCCESS")

        # 5. Hủy bằng "Thôi khỏi"
        self.client.post("/api/ai/chat", json={"message": "Chi 100k mua sách"}, headers=self.headers)
        res5 = self.client.post("/api/ai/chat", json={"message": "Thôi khỏi"}, headers=self.headers)
        self.assertEqual(res5.json()["state"], "IDLE")

        # 6. Sửa bằng "80k thôi"
        self.client.post("/api/ai/chat", json={"message": "Chi 50k đổ xăng"}, headers=self.headers)
        res6 = self.client.post("/api/ai/chat", json={"message": "80k thôi"}, headers=self.headers)
        self.assertEqual(res6.json()["state"], "CONFIRMING")
        self.assertEqual(res6.json()["pending_confirmation"]["args"]["amount"], 80000)

        res6_confirm = self.client.post("/api/ai/chat", json={"message": "Triển đi"}, headers=self.headers)
        self.assertEqual(res6_confirm.json()["state"], "SUCCESS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
