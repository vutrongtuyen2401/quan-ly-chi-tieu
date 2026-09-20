import unittest
import asyncio
import os
import sys
from unittest.mock import AsyncMock

# Add workspace to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ai_agent.core import AgentCore, AgentState
from ai_agent.core import AgentCore, AgentState
from ai_agent.tools import ToolRegistry, build_default_tool_registry, AgentMode
from ai_agent.parser import VietnameseFinancialParser


class DummyProvider:
    async def generate_response(self, prompt: str) -> str:
        return "Khí Linh phản hồi thử nghiệm."

    async def parse_structured_intent(self, prompt: str, schema: dict) -> dict:
        return {"tool": None, "arguments": {}}


class TestDebtRoutingFix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import main
        main.init_db()
        cls.registry = build_default_tool_registry()
        cls.provider = DummyProvider()

    def setUp(self):
        self.agent = AgentCore(provider=self.provider, registry=self.registry)
        self.user_id = 1

    def test_amount_parsing_formats(self):
        """Kiểm tra parse_amount với các định dạng số tiền khác nhau"""
        test_cases = [
            ("5 triệu", 5_000_000),
            ("5tr", 5_000_000),
            ("5.000.000đ", 5_000_000),
            ("5,000,000đ", 5_000_000),
            ("5 triệu đồng", 5_000_000),
            ("5000000", 5_000_000),
            ("50.000đ", 50_000),
            ("20 triệu", 20_000_000),
            ("80 triệu", 80_000_000),
            ("3 triệu", 3_000_000),
            ("10 triệu", 10_000_000),
        ]
        for text, expected in test_cases:
            parsed = VietnameseFinancialParser.parse_amount(text)
            self.assertEqual(parsed, expected, f"Lỗi parse '{text}': kỳ vọng {expected}, thực tế {parsed}")

    def test_regression_A_them_khoan_no_5_trieu(self):
        """Case A: 'Cho tôi thêm 1 khoản nợ 5 triệu' -> create_debt, amount=5_000_000, không create_wallet"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Cho tôi thêm 1 khoản nợ 5 triệu"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_debt")
        self.assertNotEqual(plan.get("tool"), "create_wallet")
        args = plan.get("arguments", {})
        self.assertEqual(args.get("amount"), 5_000_000)

        # Full flow check via process_request
        res = asyncio.run(self.agent.process_request(self.user_id, "Cho tôi thêm 1 khoản nợ 5 triệu", mode=AgentMode.ACTION))
        self.assertEqual(res.state, AgentState.CONFIRMING)
        self.assertIsNotNone(res.pending_confirmation)
        self.assertEqual(res.pending_confirmation["tool_name"], "create_debt")
        self.assertNotEqual(res.pending_confirmation["tool_name"], "create_wallet")
        self.assertEqual(res.pending_confirmation["args"]["amount"], 5_000_000)
        self.assertNotIn("Túi Càn Khôn", res.text)
        self.assertIn("Ghi Nợ", res.text)

    def test_regression_B_them_mot_khoan_no_5tr(self):
        """Case B: 'Thêm một khoản nợ 5tr' -> create_debt"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Thêm một khoản nợ 5tr"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_debt")
        self.assertEqual(plan.get("arguments", {}).get("amount"), 5_000_000)

    def test_regression_C_ghi_nhan_khoan_no_formatted(self):
        """Case C: 'Ghi nhận khoản nợ 5.000.000đ' -> create_debt, amount=5_000_000"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Ghi nhận khoản nợ 5.000.000đ"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_debt")
        self.assertEqual(plan.get("arguments", {}).get("amount"), 5_000_000)

    def test_regression_D_them_vi_momo(self):
        """Case D: 'Thêm ví MoMo 20 triệu' -> create_wallet, không create_debt"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Thêm ví MoMo 20 triệu"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_wallet")
        self.assertNotEqual(plan.get("tool"), "create_debt")
        self.assertEqual(plan.get("arguments", {}).get("wallet_name"), "MoMo")
        self.assertEqual(plan.get("arguments", {}).get("balance"), 20_000_000.0)

    def test_regression_E_tao_tui_can_khon_mb(self):
        """Case E: 'Tạo Túi Càn Khôn MB Bank 80 triệu' -> create_wallet"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Tạo Túi Càn Khôn MB Bank 80 triệu"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_wallet")
        self.assertEqual(plan.get("arguments", {}).get("wallet_name"), "MB Bank")
        self.assertEqual(plan.get("arguments", {}).get("balance"), 80_000_000.0)

    def test_regression_F_ghi_nhan_khoan_chi(self):
        """Case F: 'Cho tôi ghi nhận khoản chi 50.000đ' -> create_expense, amount=50_000"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Cho tôi ghi nhận khoản chi 50.000đ"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_expense")
        self.assertEqual(plan.get("arguments", {}).get("amount"), 50_000)

    def test_regression_G_khoan_no_co_person(self):
        """Case G: 'Cho tôi thêm một khoản nợ 5 triệu cho anh A' -> create_debt, đúng entity liên quan, không wallet"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Cho tôi thêm một khoản nợ 5 triệu cho anh A"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_debt")
        self.assertNotEqual(plan.get("tool"), "create_wallet")
        args = plan.get("arguments", {})
        self.assertEqual(args.get("amount"), 5_000_000)
        self.assertEqual(args.get("person_name"), "Anh A")

        # Full flow check via process_request
        res = asyncio.run(self.agent.process_request(self.user_id, "Cho tôi thêm một khoản nợ 5 triệu cho anh A", mode=AgentMode.ACTION))
        self.assertEqual(res.state, AgentState.CONFIRMING)
        self.assertEqual(res.pending_confirmation["tool_name"], "create_debt")
        self.assertEqual(res.pending_confirmation["args"]["person_name"], "Anh A")
        self.assertEqual(res.pending_confirmation["args"]["amount"], 5_000_000)

    def test_regression_H_them_khoan_vay(self):
        """Case H: 'Thêm khoản vay 20 triệu' -> create_debt"""
        plan = asyncio.run(self.agent._plan_action(self.user_id, "Thêm khoản vay 20 triệu"))
        self.assertIsNotNone(plan)
        self.assertEqual(plan.get("tool"), "create_debt")
        self.assertEqual(plan.get("arguments", {}).get("amount"), 20_000_000)

    def test_regression_I_xac_nhan_khi_co_pending_debt(self):
        """Case I: 'Xác nhận' khi pending=create_debt -> chỉ execute create_debt"""
        # Step 1: Set up pending create_debt
        res1 = asyncio.run(self.agent.process_request(self.user_id, "Cho Tuấn vay 2 triệu", mode=AgentMode.ACTION))
        self.assertEqual(res1.state, AgentState.CONFIRMING)
        self.assertEqual(res1.pending_confirmation["tool_name"], "create_debt")

        # Step 2: Confirm
        res2 = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận", mode=AgentMode.ACTION))
        self.assertEqual(res2.state, AgentState.SUCCESS)
        self.assertEqual(res2.tool_executed, "create_debt")
        self.assertIn("sổ nợ", res2.text.lower())

    def test_regression_J_xac_nhan_khi_khong_co_pending(self):
        """Case J: 'Xác nhận' khi không có pending action -> không execute bất kỳ mutation nào"""
        # Ensure pending is clear
        self.agent._pending_confirmations.clear()

        res = asyncio.run(self.agent.process_request(self.user_id, "Xác nhận", mode=AgentMode.ACTION))
        self.assertEqual(res.state, AgentState.IDLE)
        self.assertIsNone(res.tool_executed)
        self.assertIn("không có giao dịch hoặc thao tác tài chính nào đang chờ xác nhận", res.text.lower())

    def test_additional_debt_natural_variations(self):
        """Kiểm tra các biến thể ngôn ngữ tự nhiên nợ khác"""
        variations = [
            ("tôi đang nợ 5 triệu", "create_debt", 5_000_000),
            ("tạo khoản nợ 5 triệu", "create_debt", 5_000_000),
            ("ghi nhận khoản nợ 5 triệu", "create_debt", 5_000_000),
            ("thêm nợ 10 triệu cho tôi", "create_debt", 10_000_000),
            ("tạo khoản vay 20 triệu", "create_debt", 20_000_000),
            ("ghi khoản phải trả 3 triệu", "create_debt", 3_000_000),
        ]
        for query, expected_tool, expected_amount in variations:
            plan = asyncio.run(self.agent._plan_action(self.user_id, query))
            self.assertIsNotNone(plan, f"Plan None cho '{query}'")
            self.assertEqual(plan.get("tool"), expected_tool, f"Lỗi routing cho '{query}': {plan.get('tool')}")
            self.assertEqual(plan.get("arguments", {}).get("amount"), expected_amount, f"Lỗi amount cho '{query}'")


if __name__ == "__main__":
    unittest.main()
