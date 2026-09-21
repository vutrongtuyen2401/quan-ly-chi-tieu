import asyncio
import unittest
import os
import sqlite3
from ai_agent import AgentCore, AgentMode, AgentState, MockAIProvider, build_default_tool_registry
import main

class TestKhiLinhHotfixRound2(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        main.init_db()
        provider = MockAIProvider()
        registry = build_default_tool_registry()
        self.agent = AgentCore(provider=provider, registry=registry)
        self.user_id = 99991
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
                         (self.user_id, "test_khilinh@gmail.com", "fake_hash", "Ký Chủ", "user"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.user_id, "Tiền Mặt", 50000000, "cash"))
            conn.execute("INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
                         (self.user_id, "MoMo", 10000000, "e-wallet"))
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)",
                         (self.user_id, "Ăn Uống", "EXPENSE"))
            conn.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)",
                         (self.user_id, "Thu Nhập Khác", "INCOME"))

    async def test_01_saving_goal_multi_turn_name_then_amount(self):
        """Turn 1: 'thêm 1 mục tiêu tiết kiệm mới' -> Turn 2: 'mua iphone' -> Turn 3: '1 triệu' -> Turn 4: 'xác nhận'"""
        # Turn 1
        res1 = await self.agent.process_request(self.user_id, "thêm 1 mục tiêu tiết kiệm mới", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.IDLE)
        self.assertIsNotNone(res1.pending_confirmation)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_saving_goal")
        self.assertEqual(res1.pending_confirmation["status"], "AWAITING_PARAM")

        # Turn 2: Provide goal name
        res2 = await self.agent.process_request(self.user_id, "mua iphone", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.IDLE)
        self.assertIsNotNone(res2.pending_confirmation)
        self.assertEqual(res2.pending_confirmation["args"].get("target_name"), "Mua Iphone")
        self.assertEqual(res2.pending_confirmation["status"], "AWAITING_PARAM")
        self.assertEqual(res2.pending_confirmation["missing_param"], "target_amount")

        # Turn 3: Provide amount '1 triệu'
        res3 = await self.agent.process_request(self.user_id, "1 triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res3.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res3.pending_confirmation)
        self.assertEqual(res3.pending_confirmation["args"].get("target_name"), "Mua Iphone")
        self.assertEqual(res3.pending_confirmation["args"].get("target_amount"), 1000000.0)

        # Turn 4: Confirm
        res4 = await self.agent.process_request(self.user_id, "xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res4.state, AgentState.SUCCESS)
        self.assertEqual(res4.tool_executed, "create_saving_goal")

        # Verify in DB
        with main.get_db() as conn:
            row = conn.execute("SELECT target_name, target_amount FROM saving_goals WHERE user_id = ? AND target_name = ?", (self.user_id, "Mua Iphone")).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["target_amount"], 1000000.0)

    async def test_02_saving_goal_multi_turn_amount_then_name(self):
        """Turn 1: 'tạo mục tiêu tiết kiệm' -> Turn 2: 'hai mươi triệu' -> Turn 3: 'mua xe wave' -> Turn 4: 'đồng ý'"""
        self.agent.clear_pending_action(self.user_id)
        # Turn 1
        res1 = await self.agent.process_request(self.user_id, "tạo mục tiêu tiết kiệm", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_saving_goal")

        # Turn 2: Provide amount 'hai mươi triệu'
        res2 = await self.agent.process_request(self.user_id, "hai mươi triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.pending_confirmation["args"].get("target_amount"), 20000000.0)
        self.assertEqual(res2.pending_confirmation["missing_param"], "target_name")

        # Turn 3: Provide name 'mua xe wave'
        res3 = await self.agent.process_request(self.user_id, "mua xe wave", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res3.state, AgentState.CONFIRMING)
        self.assertEqual(res3.pending_confirmation["args"].get("target_name"), "Mua Xe Wave")
        self.assertEqual(res3.pending_confirmation["args"].get("target_amount"), 20000000.0)

        # Turn 4: Confirm
        res4 = await self.agent.process_request(self.user_id, "đồng ý", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res4.state, AgentState.SUCCESS)

    async def test_03_create_expense_multi_turn(self):
        """Turn 1: 'thêm 1 mục chi tiêu mới' -> Turn 2: '50k' -> Turn 3: 'ăn sáng' -> Turn 4: 'xác nhận'"""
        self.agent.clear_pending_action(self.user_id)
        # Turn 1
        res1 = await self.agent.process_request(self.user_id, "thêm 1 mục chi tiêu mới", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.IDLE)
        self.assertIsNotNone(res1.pending_confirmation)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_expense")
        self.assertEqual(res1.pending_confirmation["missing_param"], "amount")

        # Turn 2: '50k'
        res2 = await self.agent.process_request(self.user_id, "50k", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.pending_confirmation["args"].get("amount"), 50000.0)

        # Turn 3: 'ăn sáng'
        res3 = await self.agent.process_request(self.user_id, "ăn sáng", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res3.state, AgentState.CONFIRMING)
        self.assertEqual(res3.pending_confirmation["args"].get("amount"), 50000.0)
        note_or_cat = (res3.pending_confirmation["args"].get("note") or "") + (res3.pending_confirmation["args"].get("category_name") or "")
        self.assertTrue("Ăn" in note_or_cat or "ăn" in note_or_cat.lower())

        # Turn 4: 'xác nhận'
        res4 = await self.agent.process_request(self.user_id, "xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res4.state, AgentState.SUCCESS)
        self.assertEqual(res4.tool_executed, "create_expense")

    async def test_04_create_income_flow(self):
        """'thêm khoản thu 10 triệu' -> confirms create_income -> 'xác nhận'"""
        self.agent.clear_pending_action(self.user_id)
        res1 = await self.agent.process_request(self.user_id, "thêm khoản thu 10 triệu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_income")
        self.assertEqual(res1.pending_confirmation["args"].get("amount"), 10000000.0)

        res2 = await self.agent.process_request(self.user_id, "xác nhận", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res2.state, AgentState.SUCCESS)
        self.assertEqual(res2.tool_executed, "create_income")

    async def test_05_category_read_query_does_not_trigger_action(self):
        """'danh mục chi tiêu' or 'xem danh mục' -> calls get_categories, NOT create_expense"""
        self.agent.clear_pending_action(self.user_id)
        res = await self.agent.process_request(self.user_id, "danh mục chi tiêu", user_role=self.user_role, user_name=self.user_name, mode=AgentMode.ACTION)
        self.assertEqual(res.state, AgentState.SUCCESS)
        self.assertEqual(res.tool_executed, "get_categories")
        self.assertIsNone(self.agent.get_pending_action(self.user_id))

if __name__ == "__main__":
    unittest.main()
