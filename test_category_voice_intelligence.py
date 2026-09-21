import asyncio
import unittest
import os
import sqlite3
from ai_agent import AgentCore, AgentMode, AgentState, MockAIProvider, build_default_tool_registry
import main

class TestCategoryVoiceIntelligence(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        main.init_db()
        provider = MockAIProvider()
        registry = build_default_tool_registry()
        self.agent = AgentCore(provider=provider, registry=registry)
        self.user_id = 99992
        self.user_name = "Ký Chủ"
        self.user_role = "user"
        self.agent.clear_pending_action(self.user_id)

        with main.get_db() as conn:
            conn.execute("DELETE FROM transactions WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM budgets WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM debts WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM saving_goals WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM wallets WHERE user_id = ?", (self.user_id,))
            conn.execute("DELETE FROM categories WHERE user_id = ?", (self.user_id,))
            conn.execute("INSERT OR REPLACE INTO users (id, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
                         (self.user_id, "test_category@gmail.com", "fake_hash", "Ký Chủ", "user"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.user_id, "Tiền Mặt", 50000000, "cash"))

    # ══════════════════════════════════════════════════════════════════════
    # GROUP A: CATEGORY INTELLIGENCE & MULTI-TURN FLOWS
    # ══════════════════════════════════════════════════════════════════════

    async def test_01_create_category_missing_all_turn_flow(self):
        """Case 2.1: 'thêm cho tôi 1 mục thu chi' -> missing all -> asks Thu/Chi -> 'Chi' -> asks name -> 'Du lịch' -> confirmation -> execute -> DB verified"""
        # Turn 1: "thêm cho tôi 1 mục thu chi"
        res1 = await self.agent.process_request(self.user_id, "thêm cho tôi 1 mục thu chi", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.IDLE)
        self.assertIsNotNone(res1.pending_confirmation)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_category")
        self.assertEqual(res1.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertEqual(res1.pending_confirmation["missing_param"], "category_type")
        self.assertIn("Thu hay Chi", res1.text)

        # Turn 2: "Chi"
        res2 = await self.agent.process_request(self.user_id, "Chi", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.IDLE)
        self.assertIsNotNone(res2.pending_confirmation)
        self.assertEqual(res2.pending_confirmation["args"].get("category_type"), "EXPENSE")
        self.assertEqual(res2.pending_confirmation["missing_param"], "category_name")
        self.assertIn("tên", res2.text.lower())

        # Turn 3: "Du lịch"
        res3 = await self.agent.process_request(self.user_id, "Du lịch", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res3.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res3.pending_confirmation)
        self.assertEqual(res3.pending_confirmation["args"].get("category_type"), "EXPENSE")
        self.assertEqual(res3.pending_confirmation["args"].get("category_name"), "Du Lịch")
        self.assertEqual(res3.pending_confirmation["args"].get("icon"), "✈️")

        # Turn 4: "Xác nhận"
        res4 = await self.agent.process_request(self.user_id, "Xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res4.state, AgentState.SUCCESS)
        self.assertEqual(res4.tool_executed, "create_category")

        # Verify in DB
        with main.get_db() as conn:
            row = conn.execute("SELECT id, category_name, category_type, icon FROM categories WHERE user_id = ? AND category_name = 'Du Lịch'", (self.user_id,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["category_type"], "EXPENSE")
            self.assertEqual(row["icon"], "✈️")

    async def test_02_create_category_name_first_then_type(self):
        """Case 2.2: 'thêm danh mục Học tập' -> asks Thu hay Chi -> 'Chi' -> confirmation -> execute -> DB verified"""
        res1 = await self.agent.process_request(self.user_id, "thêm danh mục Học tập", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.IDLE)
        self.assertIsNotNone(res1.pending_confirmation)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_category")
        self.assertEqual(res1.pending_confirmation["args"].get("category_name"), "Học Tập")
        self.assertEqual(res1.pending_confirmation["missing_param"], "category_type")
        self.assertIn("Thu hay Chi", res1.text)

        # Turn 2: "Chi"
        res2 = await self.agent.process_request(self.user_id, "Chi", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res2.pending_confirmation)
        self.assertEqual(res2.pending_confirmation["args"].get("category_name"), "Học Tập")
        self.assertEqual(res2.pending_confirmation["args"].get("category_type"), "EXPENSE")
        self.assertEqual(res2.pending_confirmation["args"].get("icon"), "📚")

        # Turn 3: "Xác nhận"
        res3 = await self.agent.process_request(self.user_id, "Xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res3.state, AgentState.SUCCESS)

        # Verify in DB
        with main.get_db() as conn:
            row = conn.execute("SELECT id, category_name, category_type, icon FROM categories WHERE user_id = ? AND category_name = 'Học Tập'", (self.user_id,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["category_type"], "EXPENSE")
            self.assertEqual(row["icon"], "📚")

    async def test_03_create_category_type_first_then_name(self):
        """Case 2.3: 'thêm cho ta một danh mục Chi' -> asks name -> 'Tiền điện' -> confirmation"""
        res1 = await self.agent.process_request(self.user_id, "thêm cho ta một danh mục Chi", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.IDLE)
        self.assertIsNotNone(res1.pending_confirmation)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_category")
        self.assertEqual(res1.pending_confirmation["args"].get("category_type"), "EXPENSE")
        self.assertEqual(res1.pending_confirmation["missing_param"], "category_name")
        self.assertIn("tên", res1.text.lower())

        # Turn 2: "Tiền điện"
        res2 = await self.agent.process_request(self.user_id, "Tiền điện", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res2.pending_confirmation)
        self.assertEqual(res2.pending_confirmation["args"].get("category_name"), "Tiền Điện")
        self.assertEqual(res2.pending_confirmation["args"].get("category_type"), "EXPENSE")
        self.assertEqual(res2.pending_confirmation["args"].get("icon"), "💡")

    async def test_04_create_category_fully_specified(self):
        """Case 2.4: 'thêm danh mục Chi tên Mua sắm' -> direct confirmation with auto-icon"""
        res = await self.agent.process_request(self.user_id, "thêm danh mục Chi tên Mua sắm", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res.pending_confirmation)
        self.assertEqual(res.pending_confirmation["tool_name"], "create_category")
        self.assertEqual(res.pending_confirmation["args"].get("category_name"), "Mua Sắm")
        self.assertEqual(res.pending_confirmation["args"].get("category_type"), "EXPENSE")
        self.assertEqual(res.pending_confirmation["args"].get("icon"), "🛍️")

    # ══════════════════════════════════════════════════════════════════════
    # GROUP B: CATEGORY VS TRANSACTION CLASSIFICATION ISOLATION
    # ══════════════════════════════════════════════════════════════════════

    async def test_05_category_vs_transaction_isolation(self):
        """Ensures statements with expense/income verbs but financial amounts route to transactions, while classification group statements route to categories."""
        # 1. Category statement with "thu chi"
        self.agent.clear_pending_action(self.user_id)
        res_cat = await self.agent.process_request(self.user_id, "thêm cho tôi 1 mục thu chi", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_cat.pending_confirmation["tool_name"], "create_category")
        self.assertNotEqual(res_cat.pending_confirmation["tool_name"], "create_expense")
        self.assertNotEqual(res_cat.pending_confirmation["tool_name"], "create_income")

        # 2. Expense: "sáng nay tôi ăn sáng hết 50k"
        self.agent.clear_pending_action(self.user_id)
        res_exp1 = await self.agent.process_request(self.user_id, "sáng nay tôi ăn sáng hết 50k", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_exp1.state, AgentState.CONFIRMING)
        self.assertEqual(res_exp1.pending_confirmation["tool_name"], "create_expense")
        self.assertEqual(res_exp1.pending_confirmation["args"].get("amount"), 50000.0)

        # 3. Expense: "nay tôi mua một cái máy tính 16 triệu"
        self.agent.clear_pending_action(self.user_id)
        res_exp2 = await self.agent.process_request(self.user_id, "nay tôi mua một cái máy tính 16 triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_exp2.state, AgentState.CONFIRMING)
        self.assertEqual(res_exp2.pending_confirmation["tool_name"], "create_expense")
        self.assertEqual(res_exp2.pending_confirmation["args"].get("amount"), 16000000.0)

        # 4. Expense: "thêm khoản chi 50 nghìn tiền ăn sáng"
        self.agent.clear_pending_action(self.user_id)
        res_exp3 = await self.agent.process_request(self.user_id, "thêm khoản chi 50 nghìn tiền ăn sáng", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_exp3.state, AgentState.CONFIRMING)
        self.assertEqual(res_exp3.pending_confirmation["tool_name"], "create_expense")
        self.assertEqual(res_exp3.pending_confirmation["args"].get("amount"), 50000.0)

        # 5. Expense: "hôm nay tôi tiêu 200 nghìn"
        self.agent.clear_pending_action(self.user_id)
        res_exp4 = await self.agent.process_request(self.user_id, "hôm nay tôi tiêu 200 nghìn", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_exp4.state, AgentState.CONFIRMING)
        self.assertEqual(res_exp4.pending_confirmation["tool_name"], "create_expense")
        self.assertEqual(res_exp4.pending_confirmation["args"].get("amount"), 200000.0)

        # 6. Income: "nay tôi nhận lương 20 triệu"
        self.agent.clear_pending_action(self.user_id)
        res_inc1 = await self.agent.process_request(self.user_id, "nay tôi nhận lương 20 triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_inc1.state, AgentState.CONFIRMING)
        self.assertEqual(res_inc1.pending_confirmation["tool_name"], "create_income")
        self.assertEqual(res_inc1.pending_confirmation["args"].get("amount"), 20000000.0)

        # 7. Income: "thêm khoản thu 10 triệu"
        self.agent.clear_pending_action(self.user_id)
        res_inc2 = await self.agent.process_request(self.user_id, "thêm khoản thu 10 triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_inc2.state, AgentState.CONFIRMING)
        self.assertEqual(res_inc2.pending_confirmation["tool_name"], "create_income")
        self.assertEqual(res_inc2.pending_confirmation["args"].get("amount"), 10000000.0)

        # 8. Income: "hôm nay tôi được trả lương 20 triệu"
        self.agent.clear_pending_action(self.user_id)
        res_inc3 = await self.agent.process_request(self.user_id, "hôm nay tôi được trả lương 20 triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res_inc3.state, AgentState.CONFIRMING)
        self.assertEqual(res_inc3.pending_confirmation["tool_name"], "create_income")
        self.assertEqual(res_inc3.pending_confirmation["args"].get("amount"), 20000000.0)

    # ══════════════════════════════════════════════════════════════════════
    # GROUP C: DELETE CATEGORY (CONFIRMATION, AMBIGUITY, DEPENDENCY INTEGRITY)
    # ══════════════════════════════════════════════════════════════════════

    async def test_06_delete_category_flow_success(self):
        """User creates category 'Giải trí' -> deletes category -> confirmation -> DB deleted"""
        # Create category first in DB
        with main.get_db() as conn:
            conn.execute("INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, 'Giải Trí', 'EXPENSE', '🎮')", (self.user_id,))

        res1 = await self.agent.process_request(self.user_id, "xóa danh mục Giải Trí", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res1.pending_confirmation)
        self.assertEqual(res1.pending_confirmation["tool_name"], "delete_category")
        self.assertEqual(res1.pending_confirmation["args"].get("category_name"), "Giải Trí")

        # Confirm deletion
        res2 = await self.agent.process_request(self.user_id, "Xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.SUCCESS)
        self.assertEqual(res2.tool_executed, "delete_category")

        # Verify DB deletion
        with main.get_db() as conn:
            del_row = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_name = 'Giải Trí'", (self.user_id,)).fetchone()
            self.assertIsNone(del_row)

    async def test_07_delete_category_ambiguity_resolution(self):
        """User has two categories named 'Đầu Tư' (one EXPENSE, one INCOME). 'xóa danh mục Đầu Tư' -> asks user -> 'Chi' -> confirmation"""
        with main.get_db() as conn:
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, 'Đầu Tư', 'EXPENSE')", (self.user_id,))
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, 'Đầu Tư', 'INCOME')", (self.user_id,))

        res1 = await self.agent.process_request(self.user_id, "xóa danh mục Đầu Tư", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.IDLE)
        self.assertIn("Có 2 danh mục phù hợp", res1.text)

        # Select Chi
        res2 = await self.agent.process_request(self.user_id, "Chi", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.CONFIRMING)
        self.assertEqual(res2.pending_confirmation["tool_name"], "delete_category")
        self.assertEqual(res2.pending_confirmation["args"].get("category_type"), "EXPENSE")

    async def test_08_delete_category_dependency_rejection(self):
        """Category with linked transactions cannot be deleted. Agent reports exact reason and does not claim success."""
        with main.get_db() as conn:
            cur = conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, 'Tập Gym', 'EXPENSE')", (self.user_id,))
            cat_id = cur.lastrowid
            w_id = conn.execute("SELECT id FROM wallets WHERE user_id = ?", (self.user_id,)).fetchone()["id"]
            conn.execute("INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date) VALUES (?, ?, ?, 300000, 'EXPENSE', '2026-09-21')",
                         (self.user_id, w_id, cat_id))

        res1 = await self.agent.process_request(self.user_id, "xóa danh mục Tập Gym", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.CONFIRMING)

        # User confirms
        res2 = await self.agent.process_request(self.user_id, "Xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.ERROR)
        self.assertIn("Không thể xóa", res2.text)
        self.assertIn("dữ liệu liên kết", res2.text)

        # Verify still in DB
        with main.get_db() as conn:
            exists = conn.execute("SELECT id FROM categories WHERE id = ?", (cat_id,)).fetchone()
            self.assertIsNotNone(exists)

if __name__ == "__main__":
    unittest.main()
