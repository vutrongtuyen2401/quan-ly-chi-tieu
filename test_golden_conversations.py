"""
Golden Conversation Test Suite — Khí Linh AI Agent
Kiểm thử 20 kịch bản đàm thoại chuẩn mực (Golden Conversation Tests) theo mục 19 của yêu cầu kiểm định:
1. "thêm 1 hạn mức mới cho tôi" -> CREATE_BUDGET, hỏi thông tin còn thiếu.
2. "thêm hạn mức ăn uống 2 triệu" -> CREATE_BUDGET -> CONFIRMING.
3. "1 triệu" trong pending budget context -> limit_amount.
4. "xóa khoản nợ" -> nếu nhiều nợ: liệt kê và hỏi chọn.
5. "xóa khoản nợ ... cho anh A" -> nhận diện nợ duy nhất -> CONFIRMING.
6. "chuyển tiền mặt sang momo" -> pending transfer awaiting amount.
7. "1 triệu" -> amount injected into pending transfer -> CONFIRMING.
8. "không, 2 triệu" -> modify pending amount -> re-confirm.
9. "xác nhận" -> execute only if valid confirmation pending.
10. "không" -> cancel pending.
11. "chuyển từ ví ngân hàng" -> hỏi ví nào nếu ambiguous.
12. "tiền mặt" -> resolve exact wallet if unique.
13. "tạo ví ngân hàng" -> CREATE_WALLET, not search existing wallet.
14. "cho tôi biết tháng này tiêu bao nhiêu" -> read analytics.
15. "tháng này ta tiêu gì nhiều nhất?" -> analytics/category analysis.
16. "còn hạn mức nào?" -> budget read/status.
17. "hạn mức ăn uống còn bao nhiêu?" -> resolve budget + status.
18. "đổi hạn mức ăn uống thành 3 triệu" -> UPDATE_BUDGET -> confirmation.
19. "xóa hạn mức ăn uống" -> resolve budget -> show -> confirmation -> delete -> verify.
20. "đạo hiệu của ta là X" -> POLICY_EXPLANATION, không cho mutate profile trực tiếp qua chat.
"""

import unittest
import asyncio
import os
import sqlite3
import datetime
from ai_agent.core import AgentCore, AgentState, AgentResponse
from ai_agent.tools import ToolRegistry, build_default_tool_registry
from ai_agent.provider import MockAIProvider
from ai_agent.parser import VietnameseFinancialParser
import main


class TestGoldenConversations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main.init_db()
        cls.registry = build_default_tool_registry()
        cls.provider = MockAIProvider()
        cls.agent = AgentCore(provider=cls.provider, registry=cls.registry)
        cls.test_user_id = 99999

    def setUp(self):
        # Reset state & DB records for test_user_id
        self.agent.clear_pending_action(self.test_user_id)
        if self.test_user_id in self.agent._last_action:
            del self.agent._last_action[self.test_user_id]
        if self.test_user_id in self.agent._last_user_tool:
            del self.agent._last_user_tool[self.test_user_id]

        with main.get_db() as conn:
            conn.execute("DELETE FROM transactions WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM budgets WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM debts WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM saving_goals WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM wallets WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM categories WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (self.test_user_id,))

            # Tạo user mẫu với Đạo hiệu 'Bắc Huyền Tiên Tôn'
            conn.execute(
                "INSERT INTO users (id, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
                (self.test_user_id, "bachuyen@sect.com", "hash", "Bắc Huyền Tiên Tôn", "user")
            )

            # Tạo ví mẫu: 1 Tiền Mặt, 2 Ngân Hàng (VCB, ACB), 1 MoMo
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Ví Tiền Mặt", 5000000, "cash"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Ngân hàng VCB", 20000000, "bank"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Ngân hàng ACB", 15000000, "bank"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Ví MoMo", 3000000, "e-wallet"))

            # Tạo danh mục mẫu
            conn.execute("INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Ăn Uống", "EXPENSE", "🍜"))
            conn.execute("INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Mua Sắm", "EXPENSE", "🛍️"))

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 1: "thêm 1 hạn mức mới cho tôi" -> CREATE_BUDGET, hỏi thiếu thông tin
    # ─────────────────────────────────────────────────────────────
    def test_golden_01_create_budget_missing_info(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "thêm 1 hạn mức mới cho tôi"))
        self.assertIn(resp.pending_confirmation["tool_name"], "create_budget")
        self.assertEqual(resp.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertTrue(any(w in resp.text.lower() for w in ["danh mục", "ăn uống", "mua sắm"]))

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 2: "thêm hạn mức ăn uống 2 triệu" -> CREATE_BUDGET -> CONFIRMING
    # ─────────────────────────────────────────────────────────────
    def test_golden_02_create_budget_complete_confirming(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "thêm hạn mức ăn uống 2 triệu"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "create_budget")
        self.assertEqual(resp.pending_confirmation["args"]["limit_amount"], 2000000)
        self.assertEqual(resp.pending_confirmation["args"]["category_name"], "Ăn Uống")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 3: "1 triệu" trong pending budget context -> limit_amount
    # ─────────────────────────────────────────────────────────────
    def test_golden_03_create_budget_followup_amount(self):
        # Turn 1: Thêm hạn mức ăn uống (thiếu số tiền)
        resp1 = asyncio.run(self.agent.process_request(self.test_user_id, "tạo hạn mức ăn uống"))
        self.assertEqual(resp1.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertEqual(resp1.pending_confirmation["args"]["category_name"], "Ăn Uống")

        # Turn 2: Người dùng nhập "1 triệu"
        resp2 = asyncio.run(self.agent.process_request(self.test_user_id, "1 triệu"))
        self.assertEqual(resp2.state, AgentState.CONFIRMING)
        self.assertEqual(resp2.pending_confirmation["args"]["limit_amount"], 1000000)
        self.assertEqual(resp2.pending_confirmation["args"]["category_name"], "Ăn Uống")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 4: "xóa khoản nợ" -> nếu nhiều nợ: liệt kê và hỏi chọn
    # ─────────────────────────────────────────────────────────────
    def test_golden_04_delete_debt_multiple_ask_selection(self):
        with main.get_db() as conn:
            conn.execute("INSERT INTO debts (user_id, debt_type, person_name, amount) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "BORROW", "Anh Minh", 5000000))
            conn.execute("INSERT INTO debts (user_id, debt_type, person_name, amount) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "LEND", "Chị Lan", 3000000))

        resp = asyncio.run(self.agent.process_request(self.test_user_id, "xóa khoản nợ"))
        self.assertEqual(resp.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertIn("Anh Minh", resp.text)
        self.assertIn("Chị Lan", resp.text)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 5: "xóa khoản nợ cho anh A" -> nhận diện nợ duy nhất -> CONFIRMING
    # ─────────────────────────────────────────────────────────────
    def test_golden_05_delete_debt_exact_target(self):
        with main.get_db() as conn:
            conn.execute("INSERT INTO debts (user_id, debt_type, person_name, amount) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "LEND", "Anh Tuấn", 5000000))

        resp = asyncio.run(self.agent.process_request(self.test_user_id, "xóa khoản nợ cho Anh Tuấn"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "delete_debt")
        self.assertEqual(resp.pending_confirmation["args"]["person_name"], "Anh Tuấn")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 6: "chuyển tiền mặt sang momo" -> pending transfer
    # ─────────────────────────────────────────────────────────────
    def test_golden_06_transfer_pending_awaiting_amount(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "chuyển tiền mặt sang momo"))
        self.assertEqual(resp.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertEqual(resp.pending_confirmation["missing_param"], "amount")
        self.assertTrue(any(w in resp.text.lower() for w in ["bao nhiêu", "số tiền"]))

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 7: "1 triệu" vào pending transfer -> CONFIRMING
    # ─────────────────────────────────────────────────────────────
    def test_golden_07_transfer_followup_amount_confirming(self):
        asyncio.run(self.agent.process_request(self.test_user_id, "chuyển tiền mặt sang momo"))
        resp2 = asyncio.run(self.agent.process_request(self.test_user_id, "1 triệu"))
        self.assertEqual(resp2.state, AgentState.CONFIRMING)
        self.assertEqual(resp2.pending_confirmation["args"]["amount"], 1000000)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 8: "không, 2 triệu" -> modify pending amount -> re-confirm
    # ─────────────────────────────────────────────────────────────
    def test_golden_08_transfer_modification_reconfirm(self):
        asyncio.run(self.agent.process_request(self.test_user_id, "chuyển tiền mặt sang momo"))
        asyncio.run(self.agent.process_request(self.test_user_id, "1 triệu"))
        resp3 = asyncio.run(self.agent.process_request(self.test_user_id, "không, 2 triệu"))
        self.assertEqual(resp3.state, AgentState.CONFIRMING)
        self.assertEqual(resp3.pending_confirmation["args"]["amount"], 2000000)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 9: "xác nhận" -> execute only if valid confirmation pending
    # ─────────────────────────────────────────────────────────────
    def test_golden_09_execute_only_if_valid_confirmation(self):
        # Khi không có pending:
        resp_orphan = asyncio.run(self.agent.process_request(self.test_user_id, "xác nhận"))
        self.assertEqual(resp_orphan.state, AgentState.IDLE)
        self.assertIn("không có giao dịch", resp_orphan.text)

        # Khi có pending hợp lệ:
        asyncio.run(self.agent.process_request(self.test_user_id, "chuyển 500k từ tiền mặt sang momo"))
        resp_exec = asyncio.run(self.agent.process_request(self.test_user_id, "xác nhận"))
        self.assertEqual(resp_exec.state, AgentState.SUCCESS)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 10: "không" -> cancel pending
    # ─────────────────────────────────────────────────────────────
    def test_golden_10_cancel_pending_action(self):
        asyncio.run(self.agent.process_request(self.test_user_id, "chuyển 500k từ tiền mặt sang momo"))
        resp_cancel = asyncio.run(self.agent.process_request(self.test_user_id, "không"))
        self.assertEqual(resp_cancel.state, AgentState.IDLE)
        self.assertIn("hủy bỏ", resp_cancel.text.lower())
        self.assertIsNone(self.agent.get_pending_action(self.test_user_id))

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 11: "chuyển từ ví ngân hàng" -> hỏi ví nào nếu ambiguous
    # ─────────────────────────────────────────────────────────────
    def test_golden_11_ambiguous_bank_wallet_transfer(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "chuyển 1 triệu từ ví ngân hàng sang momo"))
        self.assertEqual(resp.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertIn("Ngân hàng VCB", resp.text)
        self.assertIn("Ngân hàng ACB", resp.text)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 12: "tiền mặt" -> resolve exact wallet if unique
    # ─────────────────────────────────────────────────────────────
    def test_golden_12_unique_cash_wallet_resolved(self):
        res = self.agent._resolve_wallet_for_transfer(self.test_user_id, "tiền mặt")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["wallet"]["wallet_name"], "Ví Tiền Mặt")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 13: "tạo ví ngân hàng" -> CREATE_WALLET, not search existing
    # ─────────────────────────────────────────────────────────────
    def test_golden_13_create_wallet_intent_not_search(self):
        action = asyncio.run(self.agent._plan_action(self.test_user_id, "tạo ví ngân hàng MB Bank 10 triệu"))
        self.assertEqual(action["tool"], "create_wallet")
        self.assertIn("mb bank", action["arguments"]["wallet_name"].lower())
        self.assertEqual(action["arguments"]["balance"], 10000000)

        # Kiểm tra thêm "tạo ví ngân hàng" không bị nhầm sang tra cứu ví
        action2 = asyncio.run(self.agent._plan_action(self.test_user_id, "tạo ví ngân hàng"))
        self.assertEqual(action2["tool"], "create_wallet")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 14: "cho tôi biết tháng này tiêu bao nhiêu" -> read analytics
    # ─────────────────────────────────────────────────────────────
    def test_golden_14_read_spending_analytics(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "cho tôi biết tháng này tiêu bao nhiêu"))
        self.assertEqual(resp.tool_executed, "spending_summary")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 15: "tháng này ta tiêu gì nhiều nhất?" -> category analysis
    # ─────────────────────────────────────────────────────────────
    def test_golden_15_spending_by_category_most(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "tháng này ta tiêu gì nhiều nhất?"))
        self.assertEqual(resp.tool_executed, "spending_by_category")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 16: "còn hạn mức nào?" -> budget read/status
    # ─────────────────────────────────────────────────────────────
    def test_golden_16_read_budgets_status(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "còn hạn mức nào?"))
        self.assertEqual(resp.tool_executed, "budget_status")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 17: "hạn mức ăn uống còn bao nhiêu?" -> resolve budget + status
    # ─────────────────────────────────────────────────────────────
    def test_golden_17_read_specific_budget_status(self):
        with main.get_db() as conn:
            c_row = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_row["id"], 2000000, datetime.date.today().strftime("%Y-%m")))
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "hạn mức ăn uống còn bao nhiêu?"))
        self.assertEqual(resp.tool_executed, "budget_status")
        self.assertEqual(resp.tool_result["data"]["category_name"], "Ăn Uống")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 18: "đổi hạn mức ăn uống thành 3 triệu" -> UPDATE_BUDGET -> confirmation
    # ─────────────────────────────────────────────────────────────
    def test_golden_18_update_budget_confirming(self):
        with main.get_db() as conn:
            c_row = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_row["id"], 2000000, datetime.date.today().strftime("%Y-%m")))

        resp = asyncio.run(self.agent.process_request(self.test_user_id, "đổi hạn mức ăn uống thành 3 triệu"))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertEqual(resp.pending_confirmation["tool_name"], "update_budget")
        self.assertEqual(resp.pending_confirmation["args"]["limit_amount"], 3000000)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 19: "xóa hạn mức ăn uống" -> resolve budget -> confirmation -> delete -> verify
    # ─────────────────────────────────────────────────────────────
    def test_golden_19_delete_budget_resolved_and_verified(self):
        with main.get_db() as conn:
            c_row = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_row["id"], 2000000, datetime.date.today().strftime("%Y-%m")))

        resp1 = asyncio.run(self.agent.process_request(self.test_user_id, "xóa hạn mức ăn uống"))
        self.assertEqual(resp1.state, AgentState.CONFIRMING)
        self.assertEqual(resp1.pending_confirmation["tool_name"], "delete_budget")

        resp2 = asyncio.run(self.agent.process_request(self.test_user_id, "xác nhận"))
        self.assertEqual(resp2.state, AgentState.SUCCESS)

        # Verification: ngân sách không còn trong DB
        with main.get_db() as conn:
            b_count = conn.execute("SELECT COUNT(*) FROM budgets WHERE user_id = ?", (self.test_user_id,)).fetchone()[0]
            self.assertEqual(b_count, 0)

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN 20: "đạo hiệu của ta là X" -> POLICY_EXPLANATION, không mutate profile qua chat
    # ─────────────────────────────────────────────────────────────
    def test_golden_20_dao_hieu_profile_policy_protection(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "đạo hiệu của ta là Cửu U Ma Tôn"))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertTrue(any(w in resp.text.lower() for w in ["hồ sơ", "quy định", "cá nhân", "sửa đổi"]))

        # Verification: full_name trong DB không bị thay đổi
        with main.get_db() as conn:
            u_row = conn.execute("SELECT full_name FROM users WHERE id = ?", (self.test_user_id,)).fetchone()
            self.assertEqual(u_row["full_name"], "Bắc Huyền Tiên Tôn")

    # ─────────────────────────────────────────────────────────────
    # KỊCH BẢN BỔ SUNG: Multi-tool Planning ("Xem tháng này ta tiêu bao nhiêu và khoản nào đang vượt hạn mức")
    # ─────────────────────────────────────────────────────────────
    def test_golden_extra_multi_tool_planning(self):
        resp = asyncio.run(self.agent.process_request(self.test_user_id, "Xem tháng này ta tiêu bao nhiêu và khoản nào đang vượt hạn mức"))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "financial_overview+budget_status")
        self.assertIn("chi tổng cộng", resp.text)


if __name__ == "__main__":
    unittest.main()
