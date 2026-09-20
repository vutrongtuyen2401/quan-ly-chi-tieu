"""
Golden Question Evaluation Test Suite — Khí Linh AI Lớn (System Knowledge RAG Assistant)
Kiểm thử toàn diện 12 nhóm Golden Questions (A đến L) cùng Code-Level Tool Permission Enforcement:

Group A: SYSTEM OVERVIEW ("Hệ thống có những chức năng nào?")
Group B: FEATURE ("Túi Càn Khôn dùng để làm gì?")
Group C: FEATURE DETAIL ("Túi Càn Khôn có thể quản lý những gì?")
Group D: WORKFLOW ("Làm sao để tạo một ví?")
Group E: AI ARCHITECTURE ("Khí Linh AI lớn có thể làm gì?")
Group F: PERMISSION ("Khí Linh AI lớn có thể tự thêm ví cho tôi không?")
Group G: ACTION ROUTING ("Thêm ví Momo 20 triệu" trong Knowledge mode -> Từ chối, không thay đổi DB)
Group H: PERSONAL READ ("Tôi hiện có những ví nào?" trong Knowledge mode -> Read tool thành công)
Group I: COMBINED QUERY ("Hệ thống có ngân sách không và ngân sách ăn uống của tôi tháng này thế nào?")
Group J: UNKNOWN FEATURE ("Hệ thống có giao dịch cổ phiếu tự động không?" -> Khẳng định chưa hỗ trợ, không hallucinate)
Group K: CONTEXT FOLLOW-UP ("Hệ thống có mục tiêu tiết kiệm không?" -> "Giải thích kỹ hơn")
Group L: OUTSIDE KNOWLEDGE ("RAG là gì?" -> Phân biệt khái niệm chung và hệ thống)

CODE-LEVEL SECURITY:
- ToolRegistry.execute chặn tuyệt đối mutation tools khi mode == AgentMode.KNOWLEDGE (PERMISSION_DENIED)
- ToolRegistry.execute cho phép toàn bộ READ tools khi mode == AgentMode.KNOWLEDGE
- Action Mode (Khí Linh Nhỏ) giữ nguyên 100% năng lực action & confirmation
"""

import os
import unittest
import tempfile
import asyncio
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_key_knowledge_rag_golden_999"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_test_pass_123"

import main
from main import app, init_db, create_token
from ai_agent import (
    AgentCore,
    AgentMode,
    OperationType,
    AgentState,
    build_default_tool_registry,
    AIProvider,
)
from ai_agent.knowledge.rag import KnowledgeRAG


class GroundedMockAIProvider(AIProvider):
    """Mock Provider phản hồi có căn cứ dựa trên prompt truyền vào từ RAG"""
    def __init__(self):
        self.prompts = []

    async def generate_response(self, prompt: str, **kwargs) -> str:
        self.prompts.append(prompt)
        prompt_lower = prompt.lower()
        if "câu hỏi của ký chủ:" in prompt_lower:
            q_part = prompt_lower.split("câu hỏi của ký chủ:")[-1].strip()
        elif "câu hỏi của đạo hữu:" in prompt_lower:
            q_part = prompt_lower.split("câu hỏi của đạo hữu:")[-1].strip()
        else:
            q_part = prompt_lower.strip()

        # Group I: Combined Query synthesis (không có header "CÂU HỎI CỦA ĐẠO HỮU" trong combined prompt)
        if "kết hợp giữa kiến thức về chức năng hệ thống và dữ liệu cá nhân" in prompt_lower:
            return (
                "Hệ thống Càn Khôn có tính năng Hạn Mức Ngân Sách giúp ký chủ kiểm soát trần chi tiêu theo danh mục. "
                "Hiện tại ngân sách của ký chủ: Ăn Uống tháng này hạn mức 3.000.000đ, đã tiêu 150.000đ (còn dư 2.850.000đ)."
            )

        # Group A: System Overview
        if "chức năng nào" in q_part or "những chức năng" in q_part:
            return (
                "Càn Khôn Linh Thạch Các sở hữu hệ thống quản lý tài chính toàn diện với các phân hệ chính:\n"
                "1. Quản lý Tài sản & Tiền tệ: Túi Càn Khôn (đa ví tiền mặt, ngân hàng, ví điện tử), Sổ Nợ (vay/cho vay).\n"
                "2. Ghi chép & Vận hành: Giao Dịch thu chi, Giao Dịch Định Kỳ tự động, Khám Hóa Đơn OCR.\n"
                "3. Kế hoạch & Mục tiêu: Hạn Mức Ngân Sách theo danh mục, Mục Tiêu Tiết Kiệm tích lũy.\n"
                "4. Phân tích & Báo cáo: Báo cáo xu hướng, cơ cấu danh mục, so sánh thu chi, xuất Excel/CSV.\n"
                "5. Bảo mật & Thần trí: Bản Mệnh Hồn Đăng (xác thực 2 lớp), Khí Linh Lớn (Tra cứu tri thức) và Khí Linh Nhỏ (Thực thi)."
            )

        # Group D: Workflow tạo ví
        if "tạo một ví" in q_part or "tạo ví" in q_part:
            return (
                "Quy trình tạo Túi Càn Khôn mới:\n"
                "Bước 1: Truy cập mục Túi Càn Khôn trên giao diện chính.\n"
                "Bước 2: Bấm nút '+ Thêm Ví Mới'.\n"
                "Bước 3: Nhập Tên ví, chọn Loại ví (Tiền mặt, Ngân hàng, Ví điện tử), nhập Số dư ban đầu.\n"
                "Bước 4: Bấm 'Xác Nhận Tạo Ví' để hoàn tất."
            )

        # Group F: Permission inquiry
        if "tự thêm ví cho tôi không" in q_part or "tự thêm ví" in q_part:
            return (
                "Khí Linh AI Lớn KHÔNG CÓ QUYỀN tự thêm ví hay thay đổi dữ liệu tài chính của Ký chủ. "
                "Khí Linh AI Lớn là Trợ Lý Tri Thức chỉ có quyền giải đáp và hướng dẫn. "
                "Để thêm ví, Ký chủ vui lòng triệu hồi Khí Linh Nhỏ (Live System Mode) để thực hiện."
            )

        # Group E: AI Architecture
        if "khí linh ai lớn có thể làm gì" in q_part or "khí linh ai lớn" in q_part:
            return (
                "Khí Linh AI Lớn là Trợ Lý Tri Thức Toàn Hệ Thống (Knowledge Assistant). "
                "Có nhiệm vụ giải đáp, hướng dẫn sử dụng, giải thích workflow và tra cứu số liệu chỉ đọc (Read-Only). "
                "Khí Linh AI Lớn TUYỆT ĐỐI KHÔNG có quyền tự thêm ví hay biến động dữ liệu tài chính. "
                "Để thực hiện thao tác, Ký chủ vui lòng triệu hồi Khí Linh Nhỏ (Live System Mode)."
            )

        # Group B & C: Túi Càn Khôn
        if "túi càn khôn" in q_part or "dùng để làm gì" in q_part or "quản lý những gì" in q_part:
            return (
                "Túi Càn Khôn là pháp bảo quản lý đa tài khoản nguồn tiền (tiền mặt, ngân hàng, ví điện tử, tiết kiệm). "
                "Cho phép ký chủ theo dõi số dư tức thời, luân chuyển tiền giữa các ví và kiểm soát dòng tiền chi tiết."
            )

        # Group K: Context Follow-up
        if "kỹ hơn" in q_part or "mục tiêu tiết kiệm" in q_part:
            return (
                "Tính năng Mục Tiêu Tiết Kiệm cho phép ký chủ thiết lập các cột mốc tài chính dài hạn (mua xe, mua nhà, quỹ dự phòng). "
                "Ký chủ có thể nạp tiền từ ví vào mục tiêu, rút tiền ra khi cần, và theo dõi tiến độ hoàn thành theo thời gian thực."
            )

        # Group L: Outside knowledge (RAG là gì)
        if "rag là gì" in q_part or "khái niệm" in q_part:
            return (
                "Về mặt khái niệm chung: RAG (Retrieval-Augmented Generation) là kỹ thuật kết hợp giữa truy xuất thông tin "
                "từ cơ sở tri thức bên ngoài và mô hình ngôn ngữ lớn (LLM) để câu trả lời luôn chính xác và có căn cứ.\n"
                "Trong hệ thống Càn Khôn Linh Thạch Các: RAG được Khí Linh AI Lớn sử dụng để tra cứu toàn bộ tài liệu chức năng, "
                "workflow và chính sách bảo mật thực tế của hệ thống nhằm trả lời ký chủ một cách chuẩn xác."
            )

        return "Khí Linh Tiên Trí giải đáp thông tin hệ thống dựa trên tài liệu tri thức đã được kiểm chứng."

    async def parse_structured_intent(self, prompt: str, schema=None, **kwargs):
        return {"tool": None, "arguments": {}}


class TestKnowledgeRAGGolden(unittest.TestCase):
    """Kiểm thử toàn diện bộ tiêu chuẩn vàng (Golden Evaluation) của Khí Linh AI Lớn"""

    @classmethod
    def setUpClass(cls):
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()

        main.DATABASE = cls.db_path
        init_db()
        cls.client = TestClient(app)

        cls.provider = GroundedMockAIProvider()
        cls.registry = build_default_tool_registry()
        cls.core = AgentCore(provider=cls.provider, registry=cls.registry)
        main.set_agent_core(cls.core)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except Exception:
                pass

    def setUp(self):
        with main.get_db() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id = 888")
            conn.execute("DELETE FROM transactions WHERE user_id = 888")
            conn.execute("DELETE FROM budgets WHERE user_id = 888")
            conn.execute("DELETE FROM saving_goals WHERE user_id = 888")
            conn.execute("DELETE FROM wallets WHERE user_id = 888")
            conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (888, 'rag_golden@gmail.com', 'dummy_hash', 'Ký Chủ RAG', 'user')")
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (8881, 888, 'Linh Thạch Tiền Mặt', 'CASH', 5000000)")
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (8882, 888, 'Linh Mạch Vietcombank', 'BANK', 20000000)")
            conn.execute("INSERT INTO budgets (id, user_id, category_id, limit_amount, month_year) VALUES (8881, 888, 1, 3000000, strftime('%Y-%m', 'now'))")

        self.token = create_token(user_id=888, email="rag_golden@gmail.com", role="user", token_version=1)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # ─────────────────────────────────────────────────────────────
    # A. SYSTEM OVERVIEW
    # ─────────────────────────────────────────────────────────────
    def test_golden_a_system_overview(self):
        """A: 'Hệ thống có những chức năng nào?' phải trả về đầy đủ các năng lực ACTIVE, không trả lời generic"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Hệ thống có những chức năng nào?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        # Không được là câu generic cũ
        self.assertNotEqual(resp.text.strip(), "Càn Khôn Linh Thạch Các hỗ trợ toàn diện các tính năng quản lý tài chính cá nhân.")
        # Phải chứa các phân hệ thực tế
        text = resp.text.lower()
        self.assertTrue(any(k in text for k in ["túi càn khôn", "ví", "giao dịch", "ngân sách", "hạn mức", "sổ nợ", "tiết kiệm"]))
        # Kiểm tra metadata truy xuất RAG
        trace = resp.tool_result.get("trace_sources", [])
        self.assertTrue(len(trace) > 0)
        self.assertTrue(any("capabilities" in t["source_file"] or "system_overview" in t["source_file"] for t in trace))

    # ─────────────────────────────────────────────────────────────
    # B. FEATURE EXPLANATION
    # ─────────────────────────────────────────────────────────────
    def test_golden_b_feature_explanation(self):
        """B: 'Túi Càn Khôn dùng để làm gì?' giải thích đúng vai trò của Túi Càn Khôn"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Túi Càn Khôn dùng để làm gì?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        self.assertTrue(any(w in resp.text.lower() for w in ["quản lý", "ví", "số dư", "tiền mặt", "ngân hàng"]))

    # ─────────────────────────────────────────────────────────────
    # C. FEATURE DETAIL
    # ─────────────────────────────────────────────────────────────
    def test_golden_c_feature_detail(self):
        """C: 'Túi Càn Khôn có thể quản lý những gì?' giải thích sâu về các loại tài sản"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Túi Càn Khôn có thể quản lý những gì?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        self.assertTrue(any("wallets" in t["source_file"] or "cap_wallets" in t["capability"] for t in trace))

    # ─────────────────────────────────────────────────────────────
    # D. WORKFLOW / USER GUIDE
    # ─────────────────────────────────────────────────────────────
    def test_golden_d_workflow_guide(self):
        """D: 'Làm sao để tạo một ví?' hướng dẫn từng bước thao tác tạo ví"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Làm sao để tạo một ví?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        self.assertTrue("bước" in resp.text.lower() or "quy trình" in resp.text.lower() or "hướng dẫn" in resp.text.lower())
        trace = resp.tool_result.get("trace_sources", [])
        self.assertTrue(any("wallet" in t["source_file"] for t in trace))

    # ─────────────────────────────────────────────────────────────
    # E. AI ARCHITECTURE EXPLANATION
    # ─────────────────────────────────────────────────────────────
    def test_golden_e_ai_architecture(self):
        """E: 'Khí Linh AI lớn có thể làm gì?' giải thích vai trò Knowledge Assistant"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Khí Linh AI lớn có thể làm gì?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        self.assertTrue("tri thức" in resp.text.lower() or "knowledge" in resp.text.lower() or "giải đáp" in resp.text.lower())

    # ─────────────────────────────────────────────────────────────
    # F. PERMISSION INQUIRY
    # ─────────────────────────────────────────────────────────────
    def test_golden_f_permission_inquiry(self):
        """F: 'Khí Linh AI lớn có thể tự thêm ví cho tôi không?' khẳng định rõ KHÔNG có quyền"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Khí Linh AI lớn có thể tự thêm ví cho tôi không?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        text = resp.text.lower()
        self.assertTrue("không" in text or "khong" in text)
        self.assertTrue("quyền" in text or "triệu hồi" in text or "khí linh nhỏ" in text)

    # ─────────────────────────────────────────────────────────────
    # G. ACTION ROUTING & DENIAL IN KNOWLEDGE MODE
    # ─────────────────────────────────────────────────────────────
    def test_golden_g_action_denied_in_knowledge_mode(self):
        """G: 'Thêm ví Momo 20 triệu' trong Knowledge mode: BỊ TỪ CHỐI, KHÔNG ĐỔI DB"""
        with main.get_db() as conn:
            init_wallets_count = conn.execute("SELECT COUNT(*) FROM wallets WHERE user_id = 888").fetchone()[0]

        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Thêm ví Momo 20 triệu.",
            mode=AgentMode.KNOWLEDGE
        ))

        # Phải bị chặn ở IDLE và giải thích rõ giới hạn
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertIsNone(resp.pending_confirmation)
        self.assertIsNone(resp.tool_executed)
        self.assertTrue("chỉ có quyền giải đáp" in resp.text or "không có quyền" in resp.text)
        self.assertTrue("triệu hồi khí linh" in resp.text.lower())

        # Kiểm tra tính bất biến toàn vẹn của Database: không có ví mới nào được tạo!
        with main.get_db() as conn:
            after_wallets_count = conn.execute("SELECT COUNT(*) FROM wallets WHERE user_id = 888").fetchone()[0]
        self.assertEqual(init_wallets_count, after_wallets_count)

    def test_golden_g2_expense_denied_in_knowledge_mode(self):
        """G2: 'Ăn sáng hết 50.000đ' trong Knowledge mode: BỊ TỪ CHỐI, KHÔNG TẠO GIAO DỊCH"""
        with main.get_db() as conn:
            init_txn_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 888").fetchone()[0]

        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Ăn sáng hết 50.000đ",
            mode=AgentMode.KNOWLEDGE
        ))

        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertIsNone(resp.pending_confirmation)
        self.assertTrue("không có quyền" in resp.text or "chỉ có quyền giải đáp" in resp.text)

        with main.get_db() as conn:
            after_txn_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = 888").fetchone()[0]
        self.assertEqual(init_txn_count, after_txn_count)

    # ─────────────────────────────────────────────────────────────
    # H. PERSONAL READ-ONLY IN KNOWLEDGE MODE
    # ─────────────────────────────────────────────────────────────
    def test_golden_h_personal_read_in_knowledge_mode(self):
        """H: 'Tôi hiện có những ví nào?' trong Knowledge mode: Read tool get_wallets thành công"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Tôi hiện có những ví nào?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.SUCCESS)
        self.assertEqual(resp.tool_executed, "get_wallets")
        self.assertIn("2 Túi Càn Khôn", resp.text)
        wallets = resp.tool_result.get("data", {}).get("wallets", [])
        w_names = [w["wallet_name"] for w in wallets]
        self.assertIn("Linh Thạch Tiền Mặt", w_names)
        self.assertIn("Linh Mạch Vietcombank", w_names)

    # ─────────────────────────────────────────────────────────────
    # I. COMBINED QUERY (KNOWLEDGE + PERSONAL READ-ONLY)
    # ─────────────────────────────────────────────────────────────
    def test_golden_i_combined_query(self):
        """I: 'Hệ thống có ngân sách không và ngân sách ăn uống của tôi tháng này thế nào?' kết hợp RAG + Read tool"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Hệ thống có ngân sách không và ngân sách ăn uống của tôi tháng này thế nào?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "budget_status")
        self.assertIsNotNone(resp.tool_result)
        self.assertIn("personal_data", resp.tool_result)
        self.assertIn("knowledge_trace", resp.tool_result)
        # Kiểm tra nội dung tổng hợp có cả tính năng và số liệu cá nhân
        self.assertTrue("ngân sách" in resp.text.lower() or "hạn mức" in resp.text.lower())
        self.assertTrue("3.000.000" in resp.text or "3000000" in str(resp.tool_result))

    # ─────────────────────────────────────────────────────────────
    # J. UNKNOWN FEATURE HANDLING (ZERO HALLUCINATION)
    # ─────────────────────────────────────────────────────────────
    def test_golden_j_unknown_feature(self):
        """J: 'Hệ thống có giao dịch cổ phiếu tự động không?' khẳng định rõ chưa hỗ trợ, không bịa đặt"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Hệ thống có giao dịch cổ phiếu tự động không?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        text = resp.text.lower()
        self.assertTrue("chưa hỗ trợ" in text or "không hỗ trợ" in text)
        self.assertTrue("cổ phiếu" in text or "chứng khoán" in text)

    def test_golden_j2_unknown_crypto(self):
        """J2: 'Hệ thống có ví crypto Bitcoin không?' khẳng định rõ chưa hỗ trợ"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Hệ thống có ví crypto Bitcoin không?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        self.assertTrue("chưa hỗ trợ" in resp.text.lower())

    # ─────────────────────────────────────────────────────────────
    # K. CONTEXT FOLLOW-UP
    # ─────────────────────────────────────────────────────────────
    def test_golden_k_context_followup(self):
        """K: Follow-up 'Giải thích kỹ hơn' phân giải đúng chủ đề từ lịch sử đối thoại"""
        history = "Đạo hữu: Hệ thống có mục tiêu tiết kiệm không?\nTiên Trí: Càn Khôn Linh Thạch Các có hỗ trợ tính năng Mục Tiêu Tiết Kiệm..."
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Giải thích kỹ hơn.",
            recent_history=history,
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        self.assertTrue(any("saving_goals" in t["source_file"] or "cap_saving_goals" in t["capability"] for t in trace))

    # ─────────────────────────────────────────────────────────────
    # L. OUTSIDE KNOWLEDGE (RAG LÀ GÌ)
    # ─────────────────────────────────────────────────────────────
    def test_golden_l_outside_knowledge(self):
        """L: 'RAG là gì?' giải thích khái niệm chung và liên hệ hệ thống rõ ràng"""
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="RAG là gì?",
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        self.assertTrue("khái niệm" in resp.text.lower() or "retrieval" in resp.text.lower() or "truy xuất" in resp.text.lower())

    # ─────────────────────────────────────────────────────────────
    # CODE-LEVEL SECURITY & PERMISSION BOUNDARY TESTS
    # ─────────────────────────────────────────────────────────────
    def test_code_level_permission_denial_for_mutations(self):
        """Code-Level: registry.execute bắt buộc từ chối mọi mutation tool khi mode == AgentMode.KNOWLEDGE"""
        # 1. create_wallet
        res = asyncio.run(self.registry.execute("create_wallet", user_id=888, mode=AgentMode.KNOWLEDGE, wallet_name="Hack Wallet", balance=1000000))
        self.assertFalse(res.success)
        self.assertEqual(res.error, "PERMISSION_DENIED")
        self.assertIn("không có thẩm quyền", res.message)

        # 2. create_expense
        res = asyncio.run(self.registry.execute("create_expense", user_id=888, mode=AgentMode.KNOWLEDGE, amount=50000, note="Hack expense"))
        self.assertFalse(res.success)
        self.assertEqual(res.error, "PERMISSION_DENIED")

        # 3. delete_transaction
        res = asyncio.run(self.registry.execute("delete_transaction", user_id=888, mode=AgentMode.KNOWLEDGE, transaction_id=1))
        self.assertFalse(res.success)
        self.assertEqual(res.error, "PERMISSION_DENIED")

        # 4. transfer_money
        res = asyncio.run(self.registry.execute("transfer_money", user_id=888, mode=AgentMode.KNOWLEDGE, amount=500000, to_wallet_name="Ví Tiền Mặt"))
        self.assertFalse(res.success)
        self.assertEqual(res.error, "PERMISSION_DENIED")

        # 5. create_budget
        res = asyncio.run(self.registry.execute("create_budget", user_id=888, mode=AgentMode.KNOWLEDGE, limit_amount=1000000, category_name="Ăn Uống"))
        self.assertFalse(res.success)
        self.assertEqual(res.error, "PERMISSION_DENIED")

    def test_code_level_permission_allow_for_reads(self):
        """Code-Level: registry.execute cho phép toàn bộ READ tools hoạt động bình thường khi mode == AgentMode.KNOWLEDGE"""
        read_tools = ["financial_overview", "get_wallets", "budget_status", "debt_status", "saving_goal_status"]
        for tool_name in read_tools:
            res = asyncio.run(self.registry.execute(tool_name, user_id=888, mode=AgentMode.KNOWLEDGE))
            self.assertTrue(res.success, f"Read tool {tool_name} failed in Knowledge mode: {res.error}")

    # ─────────────────────────────────────────────────────────────
    # ACTION MODE (KHÍ LINH NHỎ) NON-REGRESSION
    # ─────────────────────────────────────────────────────────────
    def test_action_mode_non_regression_retains_confirmation_and_mutation(self):
        """Khí Linh Nhỏ (Action Mode) không bị ảnh hưởng: vẫn nhận lệnh, lập confirmation và execute thành công"""
        # 1. Gửi lệnh tạo ví trong Action mode -> CONFIRMING
        resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Thêm ví MoMo 10 triệu",
            mode=AgentMode.ACTION
        ))
        self.assertEqual(resp.state, AgentState.CONFIRMING)
        self.assertIsNotNone(resp.pending_confirmation)
        self.assertEqual(resp.pending_confirmation["tool_name"], "create_wallet")

        # 2. Xác nhận trong Action mode -> SUCCESS, DB thay đổi
        confirm_resp = asyncio.run(self.core.process_request(
            user_id=888,
            user_message="Xác nhận",
            mode=AgentMode.ACTION
        ))
        self.assertEqual(confirm_resp.state, AgentState.SUCCESS)
        self.assertEqual(confirm_resp.tool_executed, "create_wallet")

        with main.get_db() as conn:
            w = conn.execute("SELECT wallet_name, balance FROM wallets WHERE user_id = 888 AND wallet_name LIKE '%MoMo%'").fetchone()
        self.assertIsNotNone(w)
        self.assertEqual(int(w["balance"]), 10000000)

    # ─────────────────────────────────────────────────────────────
    # HTTP LIVE API TEST (VIA TESTCLIENT)
    # ─────────────────────────────────────────────────────────────
    def test_http_api_chat_knowledge_mode(self):
        """HTTP Test: Gọi endpoint /api/ai/chat với mode='knowledge' từ Tab 8 Frontend"""
        payload = {
            "message": "Hệ thống có những chức năng nào?",
            "mode": "knowledge"
        }
        res = self.client.post("/api/ai/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "IDLE")
        self.assertEqual(data["tool_executed"], "knowledge_rag")
        self.assertTrue(len(data["response"]) > 50)

    def test_http_api_chat_action_mode(self):
        """HTTP Test: Gọi endpoint /api/ai/chat với mode='action' từ Khí Linh Nhỏ"""
        payload = {
            "message": "Ăn trưa phở bò 60k",
            "mode": "action"
        }
        res = self.client.post("/api/ai/chat", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["state"], "CONFIRMING")
        self.assertIsNotNone(data["pending_confirmation"])


if __name__ == "__main__":
    unittest.main()
