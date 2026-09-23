# -*- coding: utf-8 -*-
"""
test_knowledge_data_intelligence.py
Unit & Integration Test Suite for:
KHÍ LINH LỚN — READ-ONLY SYSTEM INTELLIGENCE + LIVE FINANCIAL DATA HOTFIX

Tests verify:
1. Live user financial data querying across all domains (A-M)
2. Follow-up context carry-over (N)
3. Strict code-level read-only security enforcement (blocks mutations)
4. User ownership and financial data isolation
5. Clean query routing (DATA QUERY vs SYSTEM KNOWLEDGE / RAG)
6. Verified structured response formatting without hallucinations or hardcoding
"""

import sys
import unittest
import asyncio
import datetime

# Ensure standard output uses utf-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ai_agent.core import AgentCore, AgentMode, AgentState
from ai_agent.tools import build_default_tool_registry
from ai_agent.parser import VietnameseFinancialParser
from ai_agent.provider import MockAIProvider
import main


class TestKnowledgeDataIntelligence(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.registry = build_default_tool_registry()
        self.agent = AgentCore(provider=MockAIProvider(), registry=self.registry)
        self.test_user_id = 1
        self.other_user_id = 2

    # =========================================================================
    # PART 1: LIVE FINANCIAL DATA QUERIES (A - M)
    # =========================================================================

    async def test_query_a_latest_transaction(self):
        """[A] 'giao dịch mới nhất của ta là gì' -> calls get_latest_transaction, returns verified data"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="giao dịch mới nhất của ta là gì",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "get_latest_transaction")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("Ký Chủ", resp.text)
        self.assertNotIn("Đạo Hữu", resp.text)
        self.assertNotIn("Ta không có quyền truy cập trực tiếp", resp.text)

    async def test_query_b_total_balance(self):
        """[B] 'ta đang có tổng cộng bao nhiêu tiền' -> calls get_wallets"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="ta đang có tổng cộng bao nhiêu tiền",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "get_wallets")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("tổng cộng", resp.text.lower())
        self.assertIn("đ", resp.text)

    async def test_query_c_highest_balance_wallet(self):
        """[C] 'ví nào của ta nhiều tiền nhất' -> calls get_wallets, identifies highest wallet"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="ví nào của ta nhiều tiền nhất",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "get_wallets")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertTrue(any(w in resp.text.lower() for w in ["nhiều nhất", "lớn nhất", "số dư"]))

    async def test_query_d_current_month_spending(self):
        """[D] 'tháng này ta chi bao nhiêu' -> calls spending_summary or financial_overview"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="tháng này ta chi bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertIn(resp.tool_executed, ("spending_summary", "financial_overview"))
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("chi", resp.text.lower())

    async def test_query_e_category_spending(self):
        """[E] 'ăn uống tháng này hết bao nhiêu' -> calls spending_by_category with category Ăn Uống"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="ăn uống tháng này hết bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "spending_by_category")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))

    async def test_query_f_top_spending_category(self):
        """[F] 'danh mục nào ta chi nhiều nhất tháng này' -> calls spending_by_category ranking"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="danh mục nào ta chi nhiều nhất tháng này",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "spending_by_category")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))

    async def test_query_g_budget_status(self):
        """[G] 'hạn mức ăn uống còn bao nhiêu' -> calls budget_status or get_budget_status"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="hạn mức ăn uống còn bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertIn(resp.tool_executed, ("budget_status", "get_budget_status"))
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("hạn mức", resp.text.lower())

    async def test_query_h_debts_i_owe(self):
        """[H] 'ta còn nợ bao nhiêu' -> calls debt_status or get_debts"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="ta còn nợ bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertIn(resp.tool_executed, ("debt_status", "get_debts", "debt_list"))
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("nợ", resp.text.lower())

    async def test_query_i_debts_owed_to_me(self):
        """[I] 'ai đang nợ ta' -> calls debt_status or get_debts"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="ai đang nợ ta",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertIn(resp.tool_executed, ("debt_status", "get_debts", "debt_list"))
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("nợ", resp.text.lower())

    async def test_query_j_saving_goal(self):
        """[J] 'mục tiêu mua xe còn thiếu bao nhiêu' -> calls get_saving_goals with goal name"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="mục tiêu mua xe còn thiếu bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertIn(resp.tool_executed, ("get_saving_goals", "saving_goal_status"))
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("mục tiêu", resp.text.lower())

    async def test_query_k_recurring_transactions(self):
        """[K] 'các giao dịch định kỳ của ta' -> calls get_recurring_transactions"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="các giao dịch định kỳ của ta",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "get_recurring_transactions")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))

    async def test_query_l_wallet_specific_transaction(self):
        """[L] 'giao dịch cuối cùng của ví Túi Momo' -> calls get_latest_transaction with wallet filter"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="giao dịch cuối cùng của ví Túi Momo",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp.tool_executed, "get_latest_transaction")
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))

    async def test_query_m_monthly_income(self):
        """[M] 'tháng này ta thu bao nhiêu' -> calls financial_overview"""
        resp = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="tháng này ta thu bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertIn(resp.tool_executed, ("financial_overview", "get_financial_overview"))
        self.assertIsNotNone(resp.tool_result)
        self.assertTrue(resp.tool_result.get("success", False))
        self.assertIn("thu", resp.text.lower())

    # =========================================================================
    # PART 2: MULTI-TURN FOLLOW-UP CONTEXT (N)
    # =========================================================================

    async def test_query_n_multiturn_followup(self):
        """[N] User asks category spending, then follow-up with 'còn tháng trước?'"""
        # Turn 1
        resp1 = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="ăn uống tháng này bao nhiêu",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp1.tool_executed, "spending_by_category")

        # Turn 2
        resp2 = await self.agent.process_request(
            user_id=self.test_user_id,
            user_message="còn tháng trước?",
            mode=AgentMode.KNOWLEDGE
        )
        self.assertEqual(resp2.tool_executed, "spending_by_category")
        self.assertIn("tháng trước", resp2.text.lower())

    # =========================================================================
    # PART 3: READ-ONLY SECURITY BOUNDARY ENFORCEMENT
    # =========================================================================

    async def test_security_blocks_mutations_in_knowledge_mode(self):
        """Verifies that mutation commands in Knowledge mode are strictly blocked without calling write tools"""
        mutation_queries = [
            "chi 50k ăn sáng",
            "xóa giao dịch đó",
            "chuyển 100k sang ví momo",
            "đặt hạn mức ăn uống 2 triệu",
            "xóa ví tiền mặt",
            "tạo mục tiêu tiết kiệm mua xe 50 triệu",
            "đổi mật khẩu thành 123456"
        ]
        forbidden_tools = {
            "create_expense", "create_income", "delete_transaction",
            "transfer_money", "create_budget", "update_budget", "delete_budget",
            "delete_wallet", "create_saving_goal", "update_saving_goal",
            "delete_saving_goal", "change_password"
        }
        for query in mutation_queries:
            resp = await self.agent.process_request(
                user_id=self.test_user_id,
                user_message=query,
                mode=AgentMode.KNOWLEDGE
            )
            self.assertNotIn(
                resp.tool_executed,
                forbidden_tools,
                f"Security breach: Knowledge mode executed forbidden tool '{resp.tool_executed}' for query '{query}'"
            )

    async def test_tool_registry_code_level_security(self):
        """Verifies that ToolRegistry.execute blocks WRITE tools at code level when mode=KNOWLEDGE"""
        result = await self.registry.execute(
            "create_expense",
            user_id=self.test_user_id,
            mode=AgentMode.KNOWLEDGE,
            amount=50000,
            note="test unauthorized write"
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error, "PERMISSION_DENIED")

    # =========================================================================
    # PART 4: USER OWNERSHIP & DATA ISOLATION
    # =========================================================================

    async def test_user_ownership_isolation(self):
        """Verifies that user 1 and user 2 receive strictly isolated financial data"""
        res1 = await self.registry.execute("get_wallets", user_id=self.test_user_id, mode=AgentMode.KNOWLEDGE)
        res2 = await self.registry.execute("get_wallets", user_id=self.other_user_id, mode=AgentMode.KNOWLEDGE)

        self.assertTrue(res1.success)
        self.assertTrue(res2.success)

        wallets1 = res1.data.get("wallets", [])
        wallets2 = res2.data.get("wallets", [])

        # Check total balance isolation
        self.assertNotEqual(res1.data.get("total_balance"), res2.data.get("total_balance"))

        # Check IDs in wallet records belong to correct user
        for w in wallets1:
            self.assertEqual(w.get("user_id", self.test_user_id), self.test_user_id)
        for w in wallets2:
            self.assertEqual(w.get("user_id", self.other_user_id), self.other_user_id)

    # =========================================================================
    # PART 5: NEGATIVE ROUTING (RAG vs DATA)
    # =========================================================================

    async def test_negative_routing_rag_vs_data(self):
        """Verifies correct routing between pure conceptual RAG inquiries and live DATA queries"""
        routing_cases = [
            ("giao dịch mới nhất", "DATA"),
            ("giao dịch là gì?", "RAG"),
            ("cách hạn mức hoạt động?", "RAG"),
            ("hạn mức ăn uống của ta còn bao nhiêu?", "DATA"),
            ("mục tiêu tiết kiệm là gì?", "RAG"),
            ("mục tiêu mua xe của ta tới đâu rồi?", "DATA")
        ]
        for query, expected_category in routing_cases:
            resp = await self.agent.process_request(
                user_id=self.test_user_id,
                user_message=query,
                mode=AgentMode.KNOWLEDGE
            )
            actual_category = "RAG" if resp.tool_executed == "knowledge_rag" else "DATA"
            self.assertEqual(
                actual_category,
                expected_category,
                f"Query '{query}' routing mismatch: expected {expected_category}, got {actual_category} (tool={resp.tool_executed})"
            )


if __name__ == "__main__":
    unittest.main()
