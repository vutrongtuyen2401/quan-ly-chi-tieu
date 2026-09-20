"""
Golden Conversation Test Suite Round 2 — Khí Linh AI Agent
Kiểm thử toàn diện 24 kịch bản trí tuệ nâng cao (Round 2 Intelligence Evolution):
1. Multi-intent: 'Xem tháng này ta tiêu bao nhiêu và cho ta biết khoản nào vượt ngân sách' (financial_overview + budget_status)
2. Multi-intent: 'Kiểm tra ví MoMo rồi cho ta biết tháng này ta tiêu qua ví đó bao nhiêu' (get_wallets + transaction_search)
3. Multi-intent: 'Xem các khoản nợ của ta và cho biết khoản nào sắp đến hạn' (debt_list -> overdue & upcoming 7 days)
4. Analytics: 'Tháng này so với tháng trước ra sao?' (month_comparison / delta calculation)
5. Analytics: 'Ví nào đang có nhiều tiền nhất?' (max_wallet -> ranking)
6. Analytics: 'Ta tiêu nhiều nhất vào đâu?' (top_spending_category -> category ranking)
7. Analytics: 'Tháng này ta tiết kiệm được bao nhiêu?' (net_savings -> income - expense & savings rate)
8. Analytics: 'Có khoản nào bất thường không?' (abnormal_spending -> outlier detection)
9. Conditional Read-Only (thỏa mãn): 'Nếu ví MoMo còn dưới 500 nghìn thì báo ta'
10. Conditional Read-Only (không thỏa mãn): 'Nếu ví MoMo còn dưới 500 nghìn thì báo ta' (số dư an toàn)
11. Conditional Mixed Write (thỏa mãn): 'Xem hạn mức ăn uống còn bao nhiêu, rồi nếu còn dưới 500 nghìn thì tăng lên 2 triệu' -> CONFIRMING update_budget
12. Conditional Mixed Write (không thỏa mãn): hạn mức còn đủ -> ZERO mutation, stays IDLE
13. Conversation Correction: 'chuyển 1 triệu từ MoMo sang tiền mặt' -> 'nhầm, từ tiền mặt sang MoMo' (reverse/swap)
14. Conversation Correction: 'chuyển 500k từ MoMo sang tiền mặt' -> 'không phải tiền mặt, Vietcombank' (wallet replacement)
15. Conversation Correction: 'chuyển 1 triệu từ MoMo sang tiền mặt' -> 'không phải 1 triệu, 2 triệu' (amount replacement)
16. Conversation Correction: 'đổi hạn mức ăn uống thành 2 triệu tháng này' -> 'không phải tháng này, tháng trước' (period correction)
17. Context Reference: 'ví MoMo' -> 'kiểm tra nó' (pronoun reference via _active_entities)
18. Context Reference: 'không phải khoản đó, khoản kia' (preceding item resolution via offset=1)
19. Deep Natural Language & Slang: 'nạp 1 củ rưỡi vào ví MoMo', 'chi nửa củ ăn sáng ví tiền mặt'
20. Xianxia Terminology: 'Khí Linh, xem ngân khố', 'tán tài 50k ăn sáng', 'nạp tài 2 triệu'
21. Failure Recovery: lỗi khi thực thi công cụ -> báo lỗi chi tiết, không claim thành công giả mạo
22. Adversarial Non-existent Wallet: 'chuyển 100k từ MoMo sang ví Paypal' -> từ chối, không tự tạo ví
23. Context Isolation: Đang pending transfer -> 'xem ngân sách tháng này' -> hủy pending cũ, trả lời ngân sách
24. Zero Orphan Execution: 'ok', 'xác nhận', 'đúng rồi' khi không có pending -> từ chối, zero mutation
"""

import unittest
import asyncio
import datetime
import sqlite3

from ai_agent.core import AgentCore, AgentState, AgentResponse
from ai_agent.tools import ToolRegistry, build_default_tool_registry
from ai_agent.provider import MockAIProvider
from ai_agent.parser import VietnameseFinancialParser
import main


class TestGoldenConversationsRound2(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        main.init_db()
        cls.registry = build_default_tool_registry()
        cls.provider = MockAIProvider()
        cls.agent = AgentCore(provider=cls.provider, registry=cls.registry)
        cls.test_user_id = 88888

    def setUp(self):
        self.agent.clear_pending_action(self.test_user_id)
        if self.test_user_id in self.agent._last_action:
            del self.agent._last_action[self.test_user_id]
        if self.test_user_id in self.agent._last_user_tool:
            del self.agent._last_user_tool[self.test_user_id]
        if self.test_user_id in self.agent._active_entities:
            del self.agent._active_entities[self.test_user_id]
        if self.test_user_id in self.agent._action_history:
            del self.agent._action_history[self.test_user_id]

        # Reset DB tables for test user
        with main.get_db() as conn:
            conn.execute("DELETE FROM transactions WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM budgets WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM debts WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM saving_goals WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM wallets WHERE user_id = ?", (self.test_user_id,))
            conn.execute("DELETE FROM categories WHERE user_id = ?", (self.test_user_id,))

            # Setup basic test data
            conn.execute("INSERT OR REPLACE INTO users (id, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
                         (self.test_user_id, "kychu88@gmail.com", "fake_hash", "Bạch Y Kiếm Tiên", "user"))
            # Wallets
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "MoMo", 5000000, "e-wallet"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Tiền Mặt", 2000000, "cash"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, "Vietcombank", 15000000, "bank"))

            # Categories
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)",
                         (self.test_user_id, "Ăn Uống", "EXPENSE"))
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)",
                         (self.test_user_id, "Mua Sắm", "EXPENSE"))
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)",
                         (self.test_user_id, "Lương", "INCOME"))

    # =========================================================================
    # 1. MULTI-INTENT & CAPABILITY COMPOSITION
    # =========================================================================

    async def test_case_01_spent_and_budget_status(self):
        """1. Multi-intent: 'Xem tháng này ta tiêu bao nhiêu và cho ta biết khoản nào vượt ngân sách'"""
        with main.get_db() as conn:
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            # Tạo budget 1,000,000 cho Ăn Uống tháng này
            this_m = datetime.date.today().strftime("%Y-%m")
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_an, 1000000, this_m))
            # Tạo chi tiêu 1,500,000 vượt ngân sách
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 1500000, "EXPENSE", datetime.date.today().isoformat(), "Ăn tiệc linh đình"))

        res = await self.agent.process_request(self.test_user_id, "Xem tháng này ta tiêu bao nhiêu và cho ta biết khoản nào vượt ngân sách")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIn("financial_overview", res.tool_executed)
        self.assertIn("budget_status", res.tool_executed)
        self.assertIn("1,500,000", res.text)
        self.assertIn("Ăn Uống", res.text)
        self.assertIn("vượt", res.text.lower())

    async def test_case_02_wallet_and_spending(self):
        """2. Multi-intent: 'Kiểm tra ví MoMo rồi cho ta biết tháng này ta tiêu qua ví đó bao nhiêu'"""
        with main.get_db() as conn:
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 350000, "EXPENSE", datetime.date.today().isoformat(), "Đi ăn phở"))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 150000, "EXPENSE", datetime.date.today().isoformat(), "Uống trà sữa"))

        res = await self.agent.process_request(self.test_user_id, "Kiểm tra ví MoMo rồi cho ta biết tháng này ta tiêu qua ví đó bao nhiêu")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIn("get_wallets", res.tool_executed)
        self.assertIn("transaction_search", res.tool_executed)
        self.assertIn("5,000,000", res.text)  # Số dư ví MoMo
        self.assertIn("500,000", res.text)    # Tổng chi qua MoMo (350k + 150k)

    async def test_case_03_debts_and_upcoming_due_dates(self):
        """3. Multi-intent: 'Xem các khoản nợ của ta và cho biết khoản nào sắp đến hạn'"""
        today = datetime.date.today()
        d_upcoming = (today + datetime.timedelta(days=3)).isoformat()
        d_overdue = (today - datetime.timedelta(days=2)).isoformat()
        d_far = (today + datetime.timedelta(days=30)).isoformat()

        with main.get_db() as conn:
            conn.execute("INSERT INTO debts (user_id, person_name, amount, debt_type, due_date, is_settled) VALUES (?, ?, ?, ?, ?, 0)",
                         (self.test_user_id, "Diệp Phàm", 1000000, "BORROW", d_upcoming))
            conn.execute("INSERT INTO debts (user_id, person_name, amount, debt_type, due_date, is_settled) VALUES (?, ?, ?, ?, ?, 0)",
                         (self.test_user_id, "Tiêu Viêm", 2000000, "LEND", d_overdue))
            conn.execute("INSERT INTO debts (user_id, person_name, amount, debt_type, due_date, is_settled) VALUES (?, ?, ?, ?, ?, 0)",
                         (self.test_user_id, "Hàn Lập", 5000000, "LEND", d_far))

        res = await self.agent.process_request(self.test_user_id, "Xem các khoản nợ của ta và cho biết khoản nào sắp đến hạn")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertEqual(res.tool_executed, "debt_list")
        self.assertIn("Diệp Phàm", res.text)  # Sắp đến hạn
        self.assertIn("Tiêu Viêm", res.text)  # Quá hạn

    async def test_case_04_month_comparison_analytics(self):
        """4. Analytics: 'Tháng này so với tháng trước ra sao?'"""
        res = await self.agent.process_request(self.test_user_id, "Tháng này so với tháng trước ra sao?")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertTrue(any(t in res.tool_executed for t in ("compare_months", "financial_overview_compare")))
        self.assertTrue(len(res.text) > 20)

    async def test_case_05_max_wallet_analytics(self):
        """5. Analytics: 'Ví nào đang có nhiều tiền nhất?'"""
        res = await self.agent.process_request(self.test_user_id, "Ví nào đang có nhiều tiền nhất?")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertEqual(res.tool_executed, "get_wallets")
        self.assertIn("Vietcombank", res.text)
        self.assertIn("15,000,000", res.text)

    async def test_case_06_top_spending_category(self):
        """6. Analytics: 'Ta tiêu nhiều nhất vào đâu?'"""
        with main.get_db() as conn:
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            c_mua = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Mua Sắm'", (self.test_user_id,)).fetchone()["id"]
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 500000, "EXPENSE", datetime.date.today().isoformat(), "Ăn uống"))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_mua, 2500000, "EXPENSE", datetime.date.today().isoformat(), "Mua pháp bảo"))

        res = await self.agent.process_request(self.test_user_id, "Ta tiêu nhiều nhất vào đâu?")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertEqual(res.tool_executed, "spending_by_category")
        self.assertIn("Mua Sắm", res.text)
        self.assertIn("2,500,000", res.text)

    async def test_case_07_net_savings_analytics(self):
        """7. Analytics: 'Tháng này ta tiết kiệm được bao nhiêu?'"""
        with main.get_db() as conn:
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            c_luong = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Lương'", (self.test_user_id,)).fetchone()["id"]
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_luong, 20000000, "INCOME", datetime.date.today().isoformat(), "Lương tháng này"))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 5000000, "EXPENSE", datetime.date.today().isoformat(), "Ăn uống"))

        res = await self.agent.process_request(self.test_user_id, "Tháng này ta tiết kiệm được bao nhiêu?")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertEqual(res.tool_executed, "financial_overview")
        self.assertIn("15,000,000", res.text)  # Net savings = 20M - 5M = 15M

    async def test_case_08_abnormal_spending_detection(self):
        """8. Analytics: 'Có khoản nào bất thường không?'"""
        with main.get_db() as conn:
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            # 3 khoản bình thường
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 50000, "EXPENSE", datetime.date.today().isoformat(), "Bánh mì"))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 60000, "EXPENSE", datetime.date.today().isoformat(), "Cơm trưa"))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 40000, "EXPENSE", datetime.date.today().isoformat(), "Cà phê"))
            # 1 khoản đột biến 5,000,000
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 5000000, "EXPENSE", datetime.date.today().isoformat(), "Mua đan dược cao cấp"))

        res = await self.agent.process_request(self.test_user_id, "Có khoản nào bất thường không?")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertEqual(res.tool_executed, "transaction_search")
        self.assertIn("5,000,000", res.text)
        self.assertIn("Mua đan dược cao cấp", res.text)

    # =========================================================================
    # 2. CONDITIONAL REASONING (READ-ONLY vs MIXED READ+WRITE)
    # =========================================================================

    async def test_case_09_conditional_read_only_alert_triggered(self):
        """9. Conditional Read-Only: 'Nếu ví MoMo còn dưới 500 nghìn thì báo ta' (Số dư = 200k < 500k -> Báo động)"""
        with main.get_db() as conn:
            conn.execute("UPDATE wallets SET balance = 200000 WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,))

        res = await self.agent.process_request(self.test_user_id, "Nếu ví MoMo còn dưới 500 nghìn thì báo ta")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIn("200,000", res.text)
        self.assertIn("dưới ngưỡng", res.text)
        self.assertIsNone(res.pending_confirmation)

    async def test_case_10_conditional_read_only_safe(self):
        """10. Conditional Read-Only: 'Nếu ví MoMo còn dưới 500 nghìn thì báo ta' (Số dư = 5 triệu >= 500k -> An toàn)"""
        res = await self.agent.process_request(self.test_user_id, "Nếu ví MoMo còn dưới 500 nghìn thì báo ta")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIn("5,000,000", res.text)
        self.assertIn("an toàn", res.text)
        self.assertIsNone(res.pending_confirmation)

    async def test_case_11_conditional_mixed_write_condition_met(self):
        """11. Conditional Mixed Write: 'Xem hạn mức ăn uống còn bao nhiêu, rồi nếu còn dưới 500 nghìn thì tăng lên 2 triệu'
        (Budget = 1,000,000; đã chi 800,000 -> còn 200,000 < 500,000 -> Chuẩn bị nâng lên 2,000,000 -> CONFIRMING)"""
        with main.get_db() as conn:
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            this_m = datetime.date.today().strftime("%Y-%m")
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_an, 1000000, this_m))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 800000, "EXPENSE", datetime.date.today().isoformat(), "Ăn uống"))

        res = await self.agent.process_request(self.test_user_id, "Xem hạn mức ăn uống còn bao nhiêu, rồi nếu còn dưới 500 nghìn thì tăng lên 2 triệu")
        self.assertEqual(res.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res.pending_confirmation)
        self.assertEqual(res.pending_confirmation["tool_name"], "update_budget")
        self.assertEqual(res.pending_confirmation["args"]["limit_amount"], 2000000)
        self.assertIn("2,000,000", res.text)

    async def test_case_12_conditional_mixed_write_condition_not_met(self):
        """12. Conditional Mixed Write: Hạn mức còn 800,000 >= 500,000 -> Điều kiện không thỏa -> ZERO mutation, IDLE"""
        with main.get_db() as conn:
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            this_m = datetime.date.today().strftime("%Y-%m")
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_an, 1000000, this_m))
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (self.test_user_id, w_id, c_an, 200000, "EXPENSE", datetime.date.today().isoformat(), "Ăn nhẹ"))

        res = await self.agent.process_request(self.test_user_id, "Xem hạn mức ăn uống còn bao nhiêu, rồi nếu còn dưới 500 nghìn thì tăng lên 2 triệu")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIsNone(res.pending_confirmation)
        self.assertIn("không thực hiện thay đổi", res.text)

    # =========================================================================
    # 3. CONVERSATION CORRECTION & PARAMETER SWAPPING
    # =========================================================================

    async def test_case_13_correction_wallet_swap(self):
        """13. Correction: 'chuyển 1 triệu từ MoMo sang tiền mặt' -> 'nhầm, từ tiền mặt sang MoMo' (Đảo ví nguồn/đích)"""
        res1 = await self.agent.process_request(self.test_user_id, "chuyển 1 triệu từ MoMo sang tiền mặt")
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertEqual(res1.pending_confirmation["args"]["from_wallet_name"], "MoMo")
        self.assertEqual(res1.pending_confirmation["args"]["to_wallet_name"], "Tiền Mặt")

        # User đính chính đảo lại
        res2 = await self.agent.process_request(self.test_user_id, "nhầm, từ tiền mặt sang MoMo")
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertEqual(res2.pending_confirmation["args"]["from_wallet_name"], "Tiền Mặt")
        self.assertEqual(res2.pending_confirmation["args"]["to_wallet_name"], "MoMo")
        self.assertEqual(res2.pending_confirmation["args"]["amount"], 1000000)

    async def test_case_14_correction_wallet_replacement(self):
        """14. Correction: 'chuyển 500k từ MoMo sang tiền mặt' -> 'không phải tiền mặt, Vietcombank'"""
        res1 = await self.agent.process_request(self.test_user_id, "chuyển 500k từ MoMo sang tiền mặt")
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertEqual(res1.pending_confirmation["args"]["to_wallet_name"], "Tiền Mặt")

        res2 = await self.agent.process_request(self.test_user_id, "không phải tiền mặt, Vietcombank")
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertEqual(res2.pending_confirmation["args"]["to_wallet_name"], "Vietcombank")
        self.assertEqual(res2.pending_confirmation["args"]["from_wallet_name"], "MoMo")

    async def test_case_15_correction_amount_replacement(self):
        """15. Correction: 'chuyển 1 triệu từ MoMo sang tiền mặt' -> 'không phải 1 triệu, 2 triệu'"""
        res1 = await self.agent.process_request(self.test_user_id, "chuyển 1 triệu từ MoMo sang tiền mặt")
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertEqual(res1.pending_confirmation["args"]["amount"], 1000000)

        res2 = await self.agent.process_request(self.test_user_id, "không phải 1 triệu, 2 triệu")
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertEqual(res2.pending_confirmation["args"]["amount"], 2000000)

    async def test_case_16_correction_period_replacement(self):
        """16. Correction: 'đổi hạn mức ăn uống thành 2 triệu tháng này' -> 'không phải tháng này, tháng trước'"""
        with main.get_db() as conn:
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            this_m = datetime.date.today().strftime("%Y-%m")
            conn.execute("INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                         (self.test_user_id, c_an, 1000000, this_m))

        res1 = await self.agent.process_request(self.test_user_id, "đổi hạn mức ăn uống thành 2 triệu tháng này")
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertIn(res1.pending_confirmation["args"]["month_year"], ("this_month", datetime.date.today().strftime("%Y-%m")))

        res2 = await self.agent.process_request(self.test_user_id, "không phải tháng này, tháng trước")
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertIn(res2.pending_confirmation["args"]["month_year"], ("last_month", (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")))

    # =========================================================================
    # 4. CONTEXT REFERENCE & MEMORY
    # =========================================================================

    async def test_case_17_pronoun_reference_wallet(self):
        """17. Context Reference: 'ví MoMo' -> 'kiểm tra nó' (Pronoun resolution via memory)"""
        # Turn 1: Tra cứu hoặc nhắc đến ví MoMo
        res1 = await self.agent.process_request(self.test_user_id, "ví MoMo có bao nhiêu tiền")
        self.assertIn(res1.state, (AgentState.IDLE, AgentState.SUCCESS))
        self.assertIn("5,000,000", res1.text)
        self.assertEqual(self.agent._active_entities[self.test_user_id]["wallet"]["name"], "MoMo")

        # Turn 2: Người dùng dùng đại từ 'kiểm tra nó'
        res2 = await self.agent.process_request(self.test_user_id, "kiểm tra nó")
        self.assertIn(res2.state, (AgentState.IDLE, AgentState.SUCCESS))
        self.assertEqual(res2.tool_executed, "get_wallets")
        self.assertIn("MoMo", res2.text)
        self.assertIn("5,000,000", res2.text)

    async def test_case_18_context_reference_preceding_offset(self):
        """18. Context Reference: 'không phải khoản đó, khoản kia' (offset=1 resolution)"""
        with main.get_db() as conn:
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name = 'MoMo'", (self.test_user_id,)).fetchone()["id"]
            c_an = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Ăn Uống'", (self.test_user_id,)).fetchone()["id"]
            # Khoản cũ hơn (offset 1)
            c1 = conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, 75000, 'EXPENSE', '2026-09-01', 'Ăn sáng phở')",
                              (self.test_user_id, w_id, c_an))
            old_txn_id = c1.lastrowid
            # Khoản mới hơn (offset 0)
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note) VALUES (?, ?, ?, 45000, 'EXPENSE', '2026-09-02', 'Uống cafe')",
                         (self.test_user_id, w_id, c_an))

        # Yêu cầu xóa khoản kia (khoản trước đó)
        res = await self.agent.process_request(self.test_user_id, "xóa khoản kia, không phải khoản đó")
        self.assertEqual(res.state, AgentState.CONFIRMING)
        self.assertEqual(res.pending_confirmation["tool_name"], "delete_transaction")
        # Phải khớp ID của khoản cũ hơn (Ăn sáng phở 75k)
        self.assertEqual(res.pending_confirmation["args"]["transaction_id"], old_txn_id)
        self.assertIn("75,000", res.text)

    # =========================================================================
    # 5. DEEP NATURAL LANGUAGE, SLANG & XIANXIA
    # =========================================================================

    async def test_case_19_vietnamese_numeric_slang(self):
        """19. Slang numbers: '1 củ rưỡi', 'nửa củ', '2 tr rưỡi'"""
        # Test parser deterministic normalization
        self.assertEqual(VietnameseFinancialParser.parse_amount("1 củ rưỡi"), 1500000)
        self.assertEqual(VietnameseFinancialParser.parse_amount("nửa củ"), 500000)
        self.assertEqual(VietnameseFinancialParser.parse_amount("2 tr rưỡi"), 2500000)
        self.assertEqual(VietnameseFinancialParser.parse_amount("1 tỷ 2"), 1200000000)

        # In conversation: "chi nửa củ ăn sáng ví tiền mặt"
        res = await self.agent.process_request(self.test_user_id, "chi nửa củ ăn sáng ví tiền mặt")
        self.assertEqual(res.state, AgentState.CONFIRMING)
        self.assertEqual(res.pending_confirmation["args"]["amount"], 500000)
        self.assertEqual(res.pending_confirmation["args"]["wallet_name"], "Tiền Mặt")

    async def test_case_20_xianxia_semantic_layer(self):
        """20. Xianxia Terminology: 'Khí Linh, xem ngân khố', 'tán tài 50k ăn sáng ví tiền mặt'"""
        # Ngân khố -> Financial Overview
        res1 = await self.agent.process_request(self.test_user_id, "Khí Linh, xem ngân khố")
        self.assertIn(res1.state, (AgentState.IDLE, AgentState.SUCCESS))
        self.assertEqual(res1.tool_executed, "financial_overview")

        # Tán tài -> Chi tiêu
        res2 = await self.agent.process_request(self.test_user_id, "tán tài 50k ăn sáng ví tiền mặt")
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertEqual(res2.pending_confirmation["tool_name"], "create_expense")
        self.assertEqual(res2.pending_confirmation["args"]["amount"], 50000)

    # =========================================================================
    # 6. FAILURE RECOVERY & ADVERSARIAL CASES
    # =========================================================================

    async def test_case_21_failure_recovery_no_false_claim(self):
        """21. Failure recovery: Tool fails (e.g. invalid DB ID) -> Reports exact failure, never claims success"""
        # Đặt pending delete transaction với ID không tồn tại
        pending = {
            "tool_name": "delete_transaction",
            "args": {"transaction_id": 99999999},
            "status": "CONFIRMING",
            "summary": "Xóa giao dịch #99999999"
        }
        self.agent.set_pending_action(self.test_user_id, pending)

        res = await self.agent.process_request(self.test_user_id, "Xác nhận")
        self.assertEqual(res.state, AgentState.ERROR)
        self.assertIn("Thất bại", res.text)
        self.assertNotIn("thành công", res.text.lower())

    async def test_case_22_adversarial_non_existent_wallet(self):
        """22. Adversarial: Chuyển tiền sang ví không tồn tại ('ví Paypal') -> Bị chặn, không tự tạo ví"""
        res = await self.agent.process_request(self.test_user_id, "chuyển 100k từ MoMo sang ví Paypal")
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIsNone(res.pending_confirmation)
        self.assertIn("Không tìm thấy ví", res.text)

        # Kiểm tra DB không bị tự động tạo thêm ví Paypal
        with main.get_db() as conn:
            row = conn.execute("SELECT id FROM wallets WHERE user_id = ? AND wallet_name LIKE '%Paypal%'", (self.test_user_id,)).fetchone()
            self.assertIsNone(row)

    async def test_case_23_context_isolation(self):
        """23. Context Isolation: Pending transfer -> User hỏi 'xem ngân sách tháng này' -> Hủy pending cũ, chạy đọc ngân sách"""
        # Step 1: Tạo pending transfer
        res1 = await self.agent.process_request(self.test_user_id, "chuyển 1 triệu từ MoMo sang tiền mặt")
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertIsNotNone(self.agent.get_pending_action(self.test_user_id))

        # Step 2: Người dùng đổi ý hỏi ngân sách tháng này
        res2 = await self.agent.process_request(self.test_user_id, "xem ngân sách tháng này")
        self.assertEqual(res2.state, AgentState.SUCCESS)
        self.assertEqual(res2.tool_executed, "budget_status")
        # Pending transfer phải bị xóa sạch, không bị rò rỉ tham số
        self.assertIsNone(self.agent.get_pending_action(self.test_user_id))

    async def test_case_24_zero_orphan_execution(self):
        """24. Zero Orphan Execution: 'ok', 'xác nhận', 'đúng rồi' khi không có pending action -> Từ chối, zero mutation"""
        for trigger in ["ok", "xác nhận", "đúng rồi", "chuẩn rồi"]:
            res = await self.agent.process_request(self.test_user_id, trigger)
            self.assertEqual(res.state, AgentState.IDLE)
            self.assertIn("không có giao dịch hoặc thao tác tài chính nào đang chờ", res.text)
            self.assertIsNone(res.tool_executed)


if __name__ == "__main__":
    unittest.main()
