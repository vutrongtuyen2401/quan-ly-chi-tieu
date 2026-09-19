"""
Test Suite: Agent Core Overhaul — Context + Entity Resolution + Money Parsing + Transaction Actions
Kiểm thử toàn diện cho hệ thống Agent Core:
A. 'ăn sáng hết 50.000đ' -> amount = 50000
B. 'ăn sáng hết 50k' -> amount = 50000
C. 'ăn sáng hết 50 nghìn' -> amount = 50000
- Canonical money parser: 50.000đ, 50.000 VNĐ, 50 ngàn, 50k, 2 triệu, 20 triệu, 1,5 triệu, 1.5 triệu, 1tr5, 150.000, 150,000
- 'ai toa sáng hết 50.000đ' -> create_expense(50000, 'ai toa sáng', 'Ăn Uống')
D. Create expense -> confirmation -> execute -> real transaction ID returned
E. 'xóa khoản chi vừa rồi' -> delete_transaction -> resolves real last transaction ID
F. 'xóa khoản chi vừa rồi' MUST NOT resolve to create_expense
G. 'sửa khoản vừa rồi thành 70 nghìn' -> update_transaction -> amount = 70000
H. 'Xác nhận' với pending delete -> execute delete -> DB transaction removed, wallet balance refunded
I. 'Hủy' với pending delete -> transaction remains in DB
J. 'Xác nhận' khi không có pending action -> no mutation
K. Context reference: 'tạo giao dịch' -> 'xóa nó' -> correct transaction entity
L. Multiple transactions: create A -> create B -> 'xóa khoản vừa rồi' -> deletes B, not A
M. Multiple entities: create wallet -> create transaction -> 'giao dịch vừa rồi' resolves transaction; 'ví vừa tạo' resolves wallet
N. Live HTTP API test: multi-turn chat through /api/ai/chat with database verification
"""

import os
import unittest
import tempfile
import asyncio
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_key_agent_core_overhaul_999"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_999"

import main
from main import app, init_db, create_token
from ai_agent import (
    AgentCore,
    MockAIProvider,
    build_default_tool_registry,
    AgentState,
    VietnameseFinancialParser
)


class TestAgentCoreOverhaul(unittest.TestCase):
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
        self.user_id = 1001
        with main.get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
                (self.user_id, "daohuu_overhaul@gmail.com", "dummyhash", "Đạo Hữu Overhaul", "user")
            )
            conn.execute("DELETE FROM chat_sessions WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM transactions WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM saving_goals WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM budgets WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM debts WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM wallets WHERE user_id = ?", (self.user_id,))

            conn.execute(
                "INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                (self.user_id, "Túi Tiền Mặt", 5000000.0, "CASH")
            )
            w_row = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = ?", (self.user_id, "Túi Tiền Mặt")).fetchone()
            self.wallet_id = w_row["id"]

        self.token = create_token(user_id=self.user_id, email="daohuu_overhaul@gmail.com", role="user")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        self.registry = build_default_tool_registry()
        self.provider = MockAIProvider()
        self.agent = AgentCore(provider=self.provider, registry=self.registry)
        main.set_agent_core(self.agent)

    # =========================================================================
    # 1. MONEY PARSER TESTS (A, B, C & Canonical Representation)
    # =========================================================================
    def test_A_parse_amount_50_000d(self):
        """A. 'ăn sáng hết 50.000đ' -> amount = 50000 (không được thành 50)"""
        amt = VietnameseFinancialParser.parse_amount("ăn sáng hết 50.000đ")
        self.assertEqual(amt, 50000)

    def test_B_parse_amount_50k(self):
        """B. 'ăn sáng hết 50k' -> amount = 50000"""
        amt = VietnameseFinancialParser.parse_amount("ăn sáng hết 50k")
        self.assertEqual(amt, 50000)

    def test_C_parse_amount_50_nghin(self):
        """C. 'ăn sáng hết 50 nghìn' -> amount = 50000"""
        amt = VietnameseFinancialParser.parse_amount("ăn sáng hết 50 nghìn")
        self.assertEqual(amt, 50000)

    def test_canonical_vietnamese_money_formats(self):
        """Kiểm tra toàn bộ các định dạng tiền tệ bắt buộc trong yêu cầu"""
        test_cases = {
            "50.000đ": 50000,
            "50.000 VNĐ": 50000,
            "50 nghìn": 50000,
            "50 ngàn": 50000,
            "50k": 50000,
            "2 triệu": 2000000,
            "20 triệu": 20000000,
            "1,5 triệu": 1500000,
            "1.5 triệu": 1500000,
            "1tr5": 1500000,
            "150.000": 150000,
            "150,000": 150000,
            "ai toa sáng hết 50.000đ": 50000,
            "50000": 50000,
            "2 củ": 2000000,
            "3 lít": 300000,
            "50.000 đồng": 50000,
            "50,000đ": 50000,
        }
        for phrase, expected in test_cases.items():
            parsed = VietnameseFinancialParser.parse_amount(phrase)
            self.assertEqual(parsed, expected, f"Failed for input '{phrase}': got {parsed}, expected {expected}")

    # =========================================================================
    # 2. CREATE EXPENSE RESOLUTION WITH ACCURATE ATTRIBUTES
    # =========================================================================
    def test_ai_toa_sang_create_expense_resolution(self):
        """Với 'ai toa sáng hết 50.000đ' -> create_expense(amount=50000, note='ai toa sáng', category='Ăn Uống')"""
        resp = asyncio.run(self.agent.process_request(self.user_id, "ai toa sáng hết 50.000đ"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertIsNotNone(resp.pending_confirmation)
        pending = resp.pending_confirmation
        self.assertEqual(pending["tool_name"], "create_expense")
        self.assertEqual(pending["args"]["amount"], 50000)
        self.assertIn("ai toa sáng", pending["args"]["note"])
        self.assertEqual(pending["args"]["category_name"], "Ăn Uống")

    # =========================================================================
    # 3. END-TO-END FLOW (D, E, F, G, H, I, J, K, L, M)
    # =========================================================================
    def test_D_create_expense_confirmation_and_execution(self):
        """D. create expense -> confirmation -> execute -> real transaction ID returned & saved in context"""
        resp1 = asyncio.run(self.agent.process_request(self.user_id, "Ăn sáng hết 50 nghìn"))
        self.assertEqual(resp1.state, AgentState.CONFIRMING)

        resp2 = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        self.assertEqual(resp2.state, AgentState.SUCCESS)
        self.assertEqual(resp2.tool_executed, "create_expense")
        self.assertIsNotNone(resp2.tool_result)
        txn_id = resp2.tool_result["data"]["transaction_id"]
        self.assertIsInstance(txn_id, int)
        self.assertGreater(txn_id, 0)

        # Kiểm tra action context được lưu ID thật từ DB
        last_action = self.agent.get_last_action(self.user_id)
        self.assertIsNotNone(last_action)
        self.assertEqual(last_action.tool_name, "create_expense")
        self.assertEqual(last_action.entity_type, "transaction")
        self.assertEqual(last_action.entity_id, txn_id)
        self.assertEqual(last_action.entity_data["amount"], 50000)

        # Kiểm tra DB thực tế
        with main.get_db() as conn:
            row = conn.execute("SELECT id, amount, note, wallet_id FROM transactions WHERE id = ?", (txn_id,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["amount"], 50000)

    def test_E_and_F_delete_last_transaction_intent_priority(self):
        """E & F: 'xóa khoản chi vừa rồi đi' MUST resolve to delete_transaction with real transaction ID.
        MUST NOT resolve to create_expense and MUST NOT ask for amount!
        """
        # 1. Tạo giao dịch ban đầu
        asyncio.run(self.agent.process_request(self.user_id, "ai toa sáng hết 50.000đ"))
        confirm_resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        created_txn_id = confirm_resp.tool_result["data"]["transaction_id"]

        # 2. Ra lệnh 'xóa khoản chi vừa rồi đi'
        del_resp = asyncio.run(self.agent.process_request(self.user_id, "xóa khoản chi vừa rồi đi"))

        # F. MUST NOT be create_expense and MUST NOT be CLARIFICATION_NEEDED asking for amount
        self.assertNotEqual(del_resp.tool_executed, "create_expense")
        self.assertNotEqual(del_resp.text, "Khí Linh đã ghi nhận ý định chi tiêu. Đạo hữu vui lòng cho biết số tiền Linh Thạch đã chi là bao nhiêu để lưu vào sổ sách?")
        self.assertEqual(del_resp.state, AgentState.CONFIRMING)
        self.assertIsNotNone(del_resp.pending_confirmation)

        # E. MUST resolve delete_transaction with real target ID
        pending = del_resp.pending_confirmation
        self.assertEqual(pending["tool_name"], "delete_transaction")
        self.assertEqual(pending["args"]["transaction_id"], created_txn_id)

    def test_G_update_last_transaction(self):
        """G. 'sửa khoản vừa rồi thành 70 nghìn' -> update_transaction -> amount = 70000"""
        # Tạo giao dịch 50k
        asyncio.run(self.agent.process_request(self.user_id, "Ăn trưa hết 50.000đ"))
        c_resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        txn_id = c_resp.tool_result["data"]["transaction_id"]

        # Sửa khoản vừa rồi thành 70 nghìn
        update_resp = asyncio.run(self.agent.process_request(self.user_id, "sửa khoản vừa rồi thành 70 nghìn"))
        self.assertEqual(update_resp.state, AgentState.CONFIRMING)
        pending = update_resp.pending_confirmation
        self.assertEqual(pending["tool_name"], "update_transaction")
        self.assertEqual(pending["args"]["transaction_id"], txn_id)
        self.assertEqual(pending["args"]["amount"], 70000)

        # Xác nhận sửa
        exec_resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        self.assertEqual(exec_resp.state, AgentState.SUCCESS)
        self.assertEqual(exec_resp.tool_executed, "update_transaction")

        # Kiểm tra DB thực tế
        with main.get_db() as conn:
            row = conn.execute("SELECT amount FROM transactions WHERE id = ?", (txn_id,)).fetchone()
            self.assertEqual(row["amount"], 70000)

    def test_H_confirm_pending_delete_removes_from_db(self):
        """H. 'Xác nhận' với pending delete -> execute delete -> DB transaction removed, balance restored"""
        # Số dư ban đầu = 5.000.000đ
        asyncio.run(self.agent.process_request(self.user_id, "Ăn sáng 50.000đ"))
        c_resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        txn_id = c_resp.tool_result["data"]["transaction_id"]

        with main.get_db() as conn:
            w_bal = conn.execute("SELECT balance FROM wallets WHERE id = ?", (self.wallet_id,)).fetchone()["balance"]
            self.assertEqual(w_bal, 4950000.0)

        # Yêu cầu xóa
        asyncio.run(self.agent.process_request(self.user_id, "xóa khoản chi vừa rồi đi"))
        # Xác nhận xóa
        del_exec = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        self.assertEqual(del_exec.state, AgentState.SUCCESS)
        self.assertEqual(del_exec.tool_executed, "delete_transaction")

        # Kiểm tra DB: transaction bị xóa hoàn toàn, số dư ví được hoàn lại
        with main.get_db() as conn:
            txn_row = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()
            self.assertIsNone(txn_row)
            w_bal_after = conn.execute("SELECT balance FROM wallets WHERE id = ?", (self.wallet_id,)).fetchone()["balance"]
            self.assertEqual(w_bal_after, 5000000.0)

    def test_I_cancel_pending_delete_preserves_transaction(self):
        """I. 'Hủy' / 'Thôi không xóa nữa' với pending delete -> transaction remains in DB"""
        asyncio.run(self.agent.process_request(self.user_id, "Ăn trưa 60 nghìn"))
        c_resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        txn_id = c_resp.tool_result["data"]["transaction_id"]

        # Yêu cầu xóa
        asyncio.run(self.agent.process_request(self.user_id, "xóa khoản chi vừa rồi"))
        # Hủy lệnh xóa
        cancel_resp = asyncio.run(self.agent.process_request(self.user_id, "Thôi không xóa nữa"))
        self.assertEqual(cancel_resp.state, AgentState.IDLE)
        self.assertIn("hủy bỏ", cancel_resp.text.lower())

        # Kiểm tra DB: transaction vẫn còn nguyên
        with main.get_db() as conn:
            txn_row = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()
            self.assertIsNotNone(txn_row)
            self.assertEqual(txn_row["amount"], 60000)

    def test_J_confirm_when_no_pending_action_does_not_mutate(self):
        """J. 'Xác nhận' khi không có pending action -> no mutation, no error, returns safe idle response"""
        with main.get_db() as conn:
            cnt_before = conn.execute("SELECT COUNT(*) as c FROM transactions WHERE user_id = ?", (self.user_id,)).fetchone()["c"]

        resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertIn("không có giao dịch", resp.text.lower())

        with main.get_db() as conn:
            cnt_after = conn.execute("SELECT COUNT(*) as c FROM transactions WHERE user_id = ?", (self.user_id,)).fetchone()["c"]
        self.assertEqual(cnt_before, cnt_after)

    def test_K_context_reference_tao_giao_dich_xoa_no(self):
        """K. Context reference: 'tạo giao dịch' -> 'xóa nó đi' -> correct entity"""
        asyncio.run(self.agent.process_request(self.user_id, "Ăn tối hết 120k"))
        c_resp = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        txn_id = c_resp.tool_result["data"]["transaction_id"]

        # User dùng đại từ tham chiếu 'xóa nó đi'
        resp = asyncio.run(self.agent.process_request(self.user_id, "xóa nó đi"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "delete_transaction")
        self.assertEqual(resp.pending_confirmation["args"]["transaction_id"], txn_id)

    def test_L_multiple_transactions_deletes_B_not_A(self):
        """L. Multiple transactions: create A -> create B -> 'xóa khoản vừa rồi' -> deletes B, not A"""
        # Tạo A: 40k
        asyncio.run(self.agent.process_request(self.user_id, "Ăn sáng 40 nghìn"))
        resp_a = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        txn_a_id = resp_a.tool_result["data"]["transaction_id"]

        # Tạo B: 90k
        asyncio.run(self.agent.process_request(self.user_id, "Đổ xăng 90 nghìn"))
        resp_b = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        txn_b_id = resp_b.tool_result["data"]["transaction_id"]

        self.assertNotEqual(txn_a_id, txn_b_id)

        # Xóa khoản vừa rồi
        del_req = asyncio.run(self.agent.process_request(self.user_id, "xóa khoản vừa rồi"))
        self.assertEqual(del_req.pending_confirmation["args"]["transaction_id"], txn_b_id)

        # Xác nhận xóa
        asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))

        # DB: B bị xóa, A vẫn tồn tại
        with main.get_db() as conn:
            row_b = conn.execute("SELECT id FROM transactions WHERE id = ?", (txn_b_id,)).fetchone()
            self.assertIsNone(row_b)
            row_a = conn.execute("SELECT id, amount FROM transactions WHERE id = ?", (txn_a_id,)).fetchone()
            self.assertIsNotNone(row_a)
            self.assertEqual(row_a["amount"], 40000)

    def test_M_multiple_entities_wallet_and_transaction(self):
        """M. Multiple entities: create wallet -> create transaction -> 'giao dịch vừa rồi' resolves transaction, 'ví vừa tạo' resolves wallet"""
        # 1. Tạo ví mới
        asyncio.run(self.agent.process_request(self.user_id, "Tạo ví Tiết Kiệm VCB 2 triệu"))
        w_confirm = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        new_wallet_id = w_confirm.tool_result["data"]["wallet_id"]

        # 2. Tạo giao dịch
        asyncio.run(self.agent.process_request(self.user_id, "Mua sách hết 80.000đ"))
        t_confirm = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        new_txn_id = t_confirm.tool_result["data"]["transaction_id"]

        # 3. 'giao dịch vừa rồi' -> resolves transaction
        t_req = asyncio.run(self.agent.process_request(self.user_id, "xóa giao dịch vừa rồi"))
        self.assertEqual(t_req.pending_confirmation["tool_name"], "delete_transaction")
        self.assertEqual(t_req.pending_confirmation["args"]["transaction_id"], new_txn_id)
        # Hủy pending để không ảnh hưởng bước tiếp
        asyncio.run(self.agent.process_request(self.user_id, "Hủy"))

        # 4. 'ví vừa tạo' -> resolves wallet
        w_req = asyncio.run(self.agent.process_request(self.user_id, "xóa ví vừa tạo"))
        self.assertEqual(w_req.pending_confirmation["tool_name"], "delete_wallet")
        self.assertEqual(w_req.pending_confirmation["args"]["wallet_id"], new_wallet_id)

    # =========================================================================
    # 4. LIVE HTTP API TEST (FULL CHAT MULTI-TURN VERIFICATION)
    # =========================================================================
    def test_N_live_http_chat_multi_turn_e2e(self):
        """N. Live HTTP API Test (/api/ai/chat) E2E:
        1. 'ai toa sáng hết 50.000đ' -> pending_confirmation create_expense(50000)
        2. 'Xác nhận' -> execute create_expense, DB record created
        3. 'xóa khoản chi vừa rồi đi' -> pending_confirmation delete_transaction(id)
        4. 'Xác nhận' -> execute delete_transaction, DB record deleted
        """
        # Turn 1: Yêu cầu chi tiêu
        r1 = self.client.post("/api/ai/chat", json={"message": "ai toa sáng hết 50.000đ"}, headers=self.headers)
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["state"], "CONFIRMING")
        self.assertIsNotNone(d1["pending_confirmation"])
        self.assertEqual(d1["pending_confirmation"]["tool_name"], "create_expense")
        self.assertEqual(d1["pending_confirmation"]["args"]["amount"], 50000)

        # Turn 2: Xác nhận tạo
        r2 = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.headers)
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2["state"], "SUCCESS")
        self.assertEqual(d2["tool_executed"], "create_expense")
        created_id = d2["tool_result"]["data"]["transaction_id"]
        self.assertGreater(created_id, 0)

        # DB check: giao dịch đã được lưu
        with main.get_db() as conn:
            row = conn.execute("SELECT id, amount, note FROM transactions WHERE id = ?", (created_id,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["amount"], 50000)

        # Turn 3: Yêu cầu xóa giao dịch vừa rồi
        r3 = self.client.post("/api/ai/chat", json={"message": "xóa khoản chi vừa rồi đi"}, headers=self.headers)
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["state"], "CONFIRMING")
        self.assertIsNotNone(d3["pending_confirmation"])
        self.assertEqual(d3["pending_confirmation"]["tool_name"], "delete_transaction")
        self.assertEqual(d3["pending_confirmation"]["args"]["transaction_id"], created_id)

        # Turn 4: Xác nhận xóa
        r4 = self.client.post("/api/ai/chat", json={"message": "Xác nhận"}, headers=self.headers)
        self.assertEqual(r4.status_code, 200)
        d4 = r4.json()
        self.assertEqual(d4["state"], "SUCCESS")
        self.assertEqual(d4["tool_executed"], "delete_transaction")

        # DB check: giao dịch đã bị xóa
        with main.get_db() as conn:
            row_deleted = conn.execute("SELECT * FROM transactions WHERE id = ?", (created_id,)).fetchone()
            self.assertIsNone(row_deleted)

    # =========================================================================
    # 5. ADDITIONAL PHRASES & ENTITY DOMAINS VERIFICATION
    # =========================================================================
    def test_O_bo_khoan_vua_ghi(self):
        """'bỏ khoản vừa ghi' -> MUST resolve to delete_transaction"""
        asyncio.run(self.agent.process_request(self.user_id, "Ăn sáng 35 nghìn"))
        c = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        t_id = c.tool_result["data"]["transaction_id"]

        resp = asyncio.run(self.agent.process_request(self.user_id, "bỏ khoản vừa ghi"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "delete_transaction")
        self.assertEqual(resp.pending_confirmation["args"]["transaction_id"], t_id)

    def test_P_go_giao_dich_vua_roi(self):
        """'gỡ giao dịch vừa rồi' -> MUST resolve to delete_transaction"""
        asyncio.run(self.agent.process_request(self.user_id, "Uống cafe 25k"))
        c = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        t_id = c.tool_result["data"]["transaction_id"]

        resp = asyncio.run(self.agent.process_request(self.user_id, "gỡ giao dịch vừa rồi"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "delete_transaction")
        self.assertEqual(resp.pending_confirmation["args"]["transaction_id"], t_id)

    def test_Q_xoa_giao_dich_50k_hom_nay(self):
        """'Xóa giao dịch 50 nghìn hôm nay' -> MUST resolve to delete_transaction"""
        asyncio.run(self.agent.process_request(self.user_id, "Ăn trưa 50.000đ"))
        c = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        t_id = c.tool_result["data"]["transaction_id"]

        resp = asyncio.run(self.agent.process_request(self.user_id, "Xóa giao dịch 50 nghìn hôm nay"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "delete_transaction")
        self.assertEqual(resp.pending_confirmation["args"]["transaction_id"], t_id)

    def test_R_xem_khoan_vua_roi_must_not_create_expense(self):
        """'xem khoản vừa rồi' MUST route to get_recent_transactions, NEVER create_expense"""
        resp = asyncio.run(self.agent.process_request(self.user_id, "xem khoản vừa rồi"))
        self.assertNotEqual(resp.tool_executed, "create_expense")
        self.assertEqual(resp.tool_executed, "get_recent_transactions")

    def test_S_no_context_delete_does_not_guess(self):
        """Khi không có giao dịch nào trong DB hoặc context, 'xóa khoản chi vừa rồi' hỏi làm rõ chứ không đoán mò ID"""
        resp = asyncio.run(self.agent.process_request(self.user_id, "xóa khoản chi vừa rồi"))
        self.assertIn("không tìm thấy", resp.text.lower())
        self.assertIsNone(resp.pending_confirmation)

    def test_T_contextual_deletion_other_entities(self):
        """Kiểm tra xóa ngữ cảnh cho Ngân sách, Mục tiêu tiết kiệm và Nợ"""
        # 1. Ngân sách
        asyncio.run(self.agent.process_request(self.user_id, "Đặt ngân sách ăn uống 2 triệu tháng này"))
        asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        b_del = asyncio.run(self.agent.process_request(self.user_id, "xóa ngân sách vừa đặt"))
        self.assertEqual(b_del.pending_confirmation["tool_name"], "delete_budget")
        asyncio.run(self.agent.process_request(self.user_id, "Hủy"))

        # 2. Mục tiêu tiết kiệm
        asyncio.run(self.agent.process_request(self.user_id, "Tạo mục tiêu mua xe 50 triệu"))
        asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        g_del = asyncio.run(self.agent.process_request(self.user_id, "xóa mục tiêu vừa tạo"))
        self.assertEqual(g_del.pending_confirmation["tool_name"], "delete_saving_goal")
        asyncio.run(self.agent.process_request(self.user_id, "Hủy"))

        # 3. Sổ nợ
        asyncio.run(self.agent.process_request(self.user_id, "Cho anh Nam vay 500k"))
        asyncio.run(self.agent.process_request(self.user_id, "Xác nhận"))
        d_del = asyncio.run(self.agent.process_request(self.user_id, "xóa khoản nợ vừa rồi"))
        self.assertEqual(d_del.pending_confirmation["tool_name"], "delete_debt")
        asyncio.run(self.agent.process_request(self.user_id, "Hủy"))


if __name__ == "__main__":
    unittest.main()
