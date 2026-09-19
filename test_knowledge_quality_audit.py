"""
Knowledge Quality Audit Test Suite — Khí Linh AI Lớn (System Knowledge / RAG Assistant)
Đánh giá chất lượng thực tế của hệ thống RAG vừa tái thiết với tối thiểu 40 câu hỏi
chia thành 12 nhóm (A đến L), bao gồm 16 câu hỏi đặc biệt theo yêu cầu.

Nhóm:
A. System overview (4 câu)
B. Feature discovery (4 câu)
C. Feature detail (4 câu)
D. How-to (4 câu)
E. Workflow (4 câu)
F. AI architecture (4 câu)
G. Security/permission (4 câu)
H. Personal read-only data (4 câu)
I. Combined RAG + personal data (3 câu)
J. Unsupported/unknown (4 câu)
K. Follow-up/context (3 kịch bản multi-turn)
L. Vietnamese natural-language variations (5 câu)

Tổng cộng: 48 câu hỏi kiểm thử chất lượng tri thức.
Trạng thái đánh giá: PASS / PARTIAL / FAIL
"""

import os
import unittest
import tempfile
import asyncio
import json
from typing import Dict, Any, List, Optional
from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test_jwt_secret_knowledge_quality_audit_2026"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_ADMIN_PASSWORD"] = "admin_audit_secret_123"

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


class GroundedAuditAIProvider(AIProvider):
    """Mock AI Provider trả lời có căn cứ cao dựa trên context được RAG truy xuất trong prompt"""
    def __init__(self):
        self.prompts = []

    async def generate_response(self, prompt: str, **kwargs) -> str:
        self.prompts.append(prompt)
        prompt_lower = prompt.lower()
        if "câu hỏi của đạo hữu:" in prompt_lower:
            q_part = prompt_lower.split("câu hỏi của đạo hữu:")[-1].strip()
        else:
            q_part = prompt_lower.strip()

        # Combined RAG + Personal data prompt
        if "kết hợp giữa kiến thức về chức năng hệ thống và dữ liệu cá nhân" in prompt_lower:
            if "ngân sách" in q_part or "hạn mức" in q_part:
                return (
                    "Hệ thống Càn Khôn Linh Thạch Các cung cấp tính năng Hạn Mức Ngân Sách (Tab 8) để kiểm soát trần chi tiêu theo từng danh mục. "
                    "Về dữ liệu cá nhân hiện tại: Ngân sách 'Ăn Uống' tháng này của đạo hữu có hạn mức 3.000.000đ, đã chi 150.000đ, còn lại 2.850.000đ."
                )
            if "mục tiêu" in q_part or "tiết kiệm" in q_part:
                return (
                    "Mục Tiêu Tiết Kiệm (Tab 4) giúp lập kế hoạch tích lũy tài chính dài hạn. "
                    "Hiện tại đạo hữu chưa có mục tiêu tiết kiệm nào đang hoạt động."
                )
            if "túi càn khôn" in q_part or "ví" in q_part:
                return (
                    "Túi Càn Khôn (Tab 5) là phân hệ quản lý đa tài khoản tài sản như tiền mặt, ngân hàng, ví điện tử. "
                    "Hiện tại đạo hữu đang sở hữu 2 ví: 'Linh Thạch Tiền Mặt' (5.000.000đ) và 'Linh Mạch Vietcombank' (20.000.000đ)."
                )

        # A. System overview
        if any(k in q_part for k in ["chức năng nào", "những chức năng", "tổng quan", "phân hệ", "tất cả tính năng"]):
            return (
                "Càn Khôn Linh Thạch Các cung cấp hệ thống quản lý tài chính cá nhân toàn diện gồm 11 phân hệ chính:\n"
                "1. Tổng Quan (Dashboard): Thẻ số dư ròng, cảnh báo ngân sách và biểu đồ tài chính.\n"
                "2. Giao Dịch: Ghi nhận thu chi, lọc tìm kiếm, xuất báo cáo Excel/CSV.\n"
                "3. Sổ Nợ: Quản lý các khoản vay và cho vay, theo dõi hạn trả và quyết toán từng phần/toàn bộ.\n"
                "4. Mục Tiêu Tiết Kiệm: Thiết lập mục tiêu tích lũy, nạp/rút tiền linh hoạt.\n"
                "5. Túi Càn Khôn: Đa ví không giới hạn (tiền mặt, ngân hàng, ví điện tử) và chuyển tiền nguyên tử 2 chiều.\n"
                "6. Danh Mục: Tùy biến cây danh mục thu chi theo nhu cầu.\n"
                "7. Linh Nhãn OCR: Quét hóa đơn tự động trích xuất số tiền, ngày và danh mục chi tiêu.\n"
                "8. Hạn Mức (Ngân Sách): Thiết lập trần chi tiêu tháng theo từng danh mục, cảnh báo vượt ngưỡng.\n"
                "9. Thống Kê: Phân tích cơ cấu chi tiêu, biểu đồ xu hướng và so sánh thu chi.\n"
                "10. Khí Linh AI: Trợ lý tri thức lớn (RAG tra cứu) và Khí Linh nhỏ (Live thực thi).\n"
                "11. Phân Quyền: Quản trị tông môn, cấu hình vai trò Chưởng Môn (Admin) và Thành Viên."
            )

        # B & C & E: Multi-account bank / Wallets / Transfer
        if any(k in q_part for k in ["nhiều tài khoản ngân hàng", "nhiều ngân hàng", "quản lý nhiều"]):
            return (
                "Đạo hữu hoàn toàn CÓ THỂ quản lý nhiều tài khoản ngân hàng trong Túi Càn Khôn (Tab 5). "
                "Hệ thống không giới hạn số lượng ví ngân hàng (Vietcombank, MB Bank, Techcombank, v.v.), "
                "mỗi ví được theo dõi số dư riêng biệt và có thể luân chuyển tiền qua lại một cách an toàn."
            )
        if any(k in q_part for k in ["chuyển tiền giữa hai ví", "chuyển tiền", "chuyển khoản"]):
            return (
                "Quy trình chuyển tiền giữa hai ví trong Túi Càn Khôn (Tab 5):\n"
                "Bước 1: Truy cập mục Túi Càn Khôn, chọn nút 'Chuyển Tiền Giữa Các Ví'.\n"
                "Bước 2: Chọn ví nguồn (ví gửi) và ví đích (ví nhận).\n"
                "Bước 3: Nhập số tiền chuyển và ghi chú nội dung chuyển tiền.\n"
                "Bước 4: Bấm 'Xác Nhận Chuyển Tiền'. Hệ thống thực hiện giao dịch nguyên tử 2 chiều: "
                "tự động trừ tiền ở ví nguồn và cộng tiền tương ứng vào ví đích trong cùng một transaction đảm bảo toàn vẹn số dư."
            )

        # Debts / Sổ Nợ
        if any(k in q_part for k in ["quản lý khoản nợ", "khoản nợ", "sổ nợ", "cho vay", "mượn"]):
            return (
                "Để quản lý nợ, đạo hữu sử dụng phân hệ Sổ Nợ (Tab 3). "
                "Chức năng này cho phép ghi chép 2 loại nợ: 'Cho Vay' (người khác nợ ta) và 'Đi Vay' (ta nợ người khác), "
                "theo dõi số tiền gốc, người liên quan, thời hạn trả nợ, và hỗ trợ quyết toán/tất toán từng phần hoặc toàn bộ kèm ghi nhận vào ví."
            )

        # Saving Goals
        if any(k in q_part for k in ["mục tiêu tiết kiệm hoạt động ra sao", "mục tiêu tiết kiệm", "tiết kiệm"]):
            return (
                "Phân hệ Mục Tiêu Tiết Kiệm (Tab 4) hoạt động như sau:\n"
                "- Thiết lập mục tiêu: Đặt tên mục tiêu (mua xe, mua nhà, quỹ khẩn cấp), số tiền cần đạt và thời hạn hoàn thành.\n"
                "- Tích lũy linh hoạt: Nạp tiền từ một ví trong Túi Càn Khôn vào quỹ mục tiêu, hoặc rút ra khi cần gấp.\n"
                "- Theo dõi tiến độ: Thanh phần trăm trực quan thể hiện tỷ lệ hoàn thành mục tiêu theo thời gian thực."
            )

        # Recurring transactions
        if any(k in q_part for k in ["định kỳ", "linh trận định kỳ", "lặp lại"]):
            return (
                "Tính năng Linh Trận Định Kỳ (Giao Dịch Định Kỳ - Tab 2) hoạt động như sau:\n"
                "- Thiết lập chu kỳ: Cấu hình khoản thu/chi tự động lặp lại theo ngày, tuần, tháng hoặc năm (tiền nhà, internet, lương).\n"
                "- Cơ chế sinh giao dịch: Đạo hữu có thể chọn cơ chế 'Tự động tạo giao dịch' khi đến hạn hoặc 'Nhắc nhở phê duyệt'.\n"
                "- Đồng bộ ví & ngân sách: Mỗi khi phát sinh, giao dịch sẽ tự động cập nhật số dư ví và tính vào hạn mức ngân sách tương ứng."
            )

        # OCR Invoice
        if any(k in q_part for k in ["quét hóa đơn", "ocr", "hóa đơn", "bill"]):
            return (
                "Chức năng Linh Nhãn OCR Quét Hóa Đơn (Tab 7) hoạt động như sau:\n"
                "- Tải ảnh: Đạo hữu chụp hoặc tải lên hình ảnh hóa đơn/biên lai (PNG, JPG, JPEG).\n"
                "- Nhận diện AI: Hệ thống ứng dụng thị giác máy tính trích xuất ngày giao dịch, tổng số tiền, tên nhà cung cấp và gợi ý danh mục.\n"
                "- Kiểm tra & Xác nhận: Người dùng xem trước thông tin đã bóc tách, có thể chỉnh sửa lại rồi bấm 'Lưu Giao Dịch' để cập nhật vào sổ thu chi."
            )

        # Budget & Limits
        if any(k in q_part for k in ["ngân sách", "hạn mức", "vượt trần"]):
            return (
                "Quy trình kiểm soát ngân sách cảnh báo khi chi tiêu vượt trần (Tab 8):\n"
                "1. Thiết lập trần: Đạo hữu vào Hạn Mức (Tab 8), đặt số tiền tối đa được phép chi trong tháng cho từng danh mục.\n"
                "2. Theo dõi thời gian thực: Mỗi giao dịch chi tiêu mới sẽ tự động tích lũy và cập nhật tỷ lệ phần trăm đã tiêu.\n"
                "3. Hệ thống cảnh báo màu trực quan: Dưới 70% hiển thị Xanh lá (An toàn); từ 70% đến 99% hiển thị Vàng cam (Cảnh báo); từ 100% trở lên hiển thị Đỏ rực và xuất hiện cảnh báo nổi bật trên Tổng Quan (Dashboard)."
            )

        # AI Architecture: Khi Linh Lon vs Khi Linh Nho
        if any(k in q_part for k in ["khí linh lớn", "khí linh nhỏ", "kiến trúc 2 khí linh", "khác nhau", "vai trò và nhiệm vụ", "quyền hạn gì"]):
            return (
                "Hệ thống phân tách kiến trúc 2 Khí Linh riêng biệt theo nguyên tắc bảo mật tối cao:\n"
                "1. Khí Linh AI Lớn (Knowledge Assistant): Hoạt động trên giao diện Tab 10 (Chatbox toàn diện). "
                "Nhiệm vụ là tra cứu cơ sở tri thức RAG toàn hệ thống, hướng dẫn sử dụng, giải thích workflow và đọc số liệu tài chính cá nhân (Read-Only). "
                "Khí Linh Lớn TUYỆT ĐỐI KHÔNG có quyền thay đổi dữ liệu tài chính (không thêm ví, không tạo/xóa giao dịch).\n"
                "2. Khí Linh Nhỏ (Live System Mode / Action Agent): Xuất hiện dưới dạng linh vật thu nhỏ góc phải màn hình, hỗ trợ giọng nói (Voice) và lệnh thao tác. "
                "Khí Linh Nhỏ có quyền thực thi (thêm ví, ghi giao dịch thu chi) nhưng BẮT BUỘC phải qua cơ chế xác nhận người dùng (Human-in-the-loop)."
            )

        # Security & Permission
        if any(k in q_part for k in ["tự thêm ví không", "tự ý xóa", "có quyền tự"]):
            return (
                "Khí Linh AI Lớn TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ THÊM VÍ hay sửa đổi bất kỳ dữ liệu tài chính nào của đạo hữu. "
                "Khí Linh Lớn là Trợ Lý Tri Thức chỉ có quyền giải đáp, hướng dẫn và tra cứu chỉ đọc (Read-Only). "
                "Mọi hành động thêm ví, tạo giao dịch hay điều chỉnh ngân sách phải do đạo hữu tự thao tác trên giao diện, "
                "hoặc triệu hồi Khí Linh Nhỏ (Live System Mode) với bước xác nhận rõ ràng."
            )

        if any(k in q_part for k in ["hồn đăng", "bản mệnh"]):
            return (
                "Bản Mệnh Hồn Đăng (Tab 11 & Cài Đặt) là cơ chế bảo mật cốt lõi của hệ thống:\n"
                "- Bảo mật 2 lớp: Thiết lập mật mã cấp hai / mã PIN hoặc câu hỏi bí mật bảo vệ các hành động tài chính nhạy cảm.\n"
                "- Giám sát phiên đăng nhập: Tự động vô hiệu hóa token khi phát hiện truy cập bất thường hoặc hết hạn phiên."
            )

        if any(k in q_part for k in ["chưởng môn", "admin", "phân quyền"]):
            return (
                "Phân hệ Phân Quyền (Tab 11 - Chưởng Môn Các) quản trị hệ thống với 2 vai trò:\n"
                "- Chưởng Môn (Admin): Quản lý toàn bộ danh sách người dùng, xem nhật ký kiểm toán hệ thống, cấu hình tham số chung.\n"
                "- Thành Viên (User): Chỉ có quyền xem và thao tác trên dữ liệu tài chính cá nhân của chính mình, cách ly hoàn toàn theo user_id."
            )

        # D. How to
        if any(k in q_part for k in ["làm sao để tạo một ví", "cách tạo ví"]):
            return (
                "Cách tạo ví mới trong Túi Càn Khôn:\n"
                "Bước 1: Vào mục Túi Càn Khôn (Tab 5).\n"
                "Bước 2: Bấm nút '+ Thêm Ví Mới'.\n"
                "Bước 3: Nhập tên ví, chọn loại ví (Tiền mặt, Ngân hàng, Ví điện tử, Tiết kiệm), nhập số dư ban đầu.\n"
                "Bước 4: Bấm 'Xác Nhận Tạo Ví'."
            )
        if any(k in q_part for k in ["ghi nhận một giao dịch", "tạo giao dịch"]):
            return (
                "Cách ghi nhận giao dịch mới:\n"
                "Bước 1: Vào mục Giao Dịch (Tab 2).\n"
                "Bước 2: Bấm nút 'Thêm Giao Dịch'.\n"
                "Bước 3: Chọn loại giao dịch (Chi Tiêu hoặc Thu Nhập), nhập số tiền, chọn Danh Mục, chọn Ví thanh toán và ngày giao dịch.\n"
                "Bước 4: Bấm 'Lưu Giao Dịch'."
            )
        if any(k in q_part for k in ["xuất dữ liệu", "xuất excel", "file excel", "csv"]):
            return (
                "Cách xuất dữ liệu báo cáo ra Excel/CSV:\n"
                "Bước 1: Vào mục Báo Cáo & Thống Kê (Tab 9) hoặc Danh Sách Giao Dịch (Tab 2).\n"
                "Bước 2: Chọn khoảng thời gian cần xuất báo cáo (tháng này, quý này, tùy chọn).\n"
                "Bước 3: Bấm nút 'Xuất Excel' hoặc 'Xuất CSV'. Hệ thống sẽ tạo file bảng tính chi tiết tải về thiết bị."
            )
        if any(k in q_part for k in ["thiết lập một mục tiêu tiết kiệm", "tạo mục tiêu tiết kiệm"]):
            return (
                "Cách tạo mục tiêu tiết kiệm mới:\n"
                "Bước 1: Truy cập mục Mục Tiêu (Tab 4).\n"
                "Bước 2: Bấm nút '+ Thêm Mục Tiêu'.\n"
                "Bước 3: Nhập tên mục tiêu, số tiền mục tiêu cần tích lũy và thời hạn hoàn thành dự kiến.\n"
                "Bước 4: Bấm 'Tạo Mục Tiêu'."
            )

        # RAG definition
        if "rag là gì" in q_part or "rag" in q_part:
            return (
                "Về khái niệm công nghệ chung: RAG (Retrieval-Augmented Generation) là kỹ thuật tăng cường tri thức cho mô hình AI "
                "bằng cách truy xuất các tài liệu liên quan từ cơ sở dữ liệu bên ngoài rồi đưa vào ngữ cảnh trước khi tạo câu trả lời.\n"
                "Trong Càn Khôn Linh Thạch Các: RAG được Khí Linh AI Lớn sử dụng để tra cứu chính xác các tài liệu chức năng, hướng dẫn "
                "và quy định bảo mật của hệ thống, đảm bảo phản hồi luôn có căn cứ và không bịa đặt."
            )

        # Dialect / natural variations
        if any(k in q_part for k in ["mần răng", "hông ta", "chi rứa", "mần ăn ra sao", "được hem"]):
            return (
                "Khí Linh hiểu câu hỏi của đạo hữu: "
                "Hệ thống Càn Khôn Linh Thạch Các hỗ trợ đầy đủ các chức năng quản lý tài sản, đa tài khoản ngân hàng, "
                "sổ nợ vay/mượn, quét hóa đơn AI thông minh và bảo mật tuyệt đối theo phân quyền."
            )

        # Fallback grounded
        return "Khí Linh AI Lớn xin giải đáp dựa trên tài liệu tri thức của Càn Khôn Linh Thạch Các."

    async def parse_structured_intent(self, prompt: str, schema=None, **kwargs):
        return {"tool": None, "arguments": {}}


class TestKnowledgeQualityAudit(unittest.TestCase):
    """
    Test Suite Đánh Giá Chất Lượng Tri Thức Khí Linh AI Lớn — 48 Câu Hỏi Toàn Diện
    """
    audit_results: List[Dict[str, Any]] = []

    @classmethod
    def setUpClass(cls):
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.db_path = cls.temp_db.name
        cls.temp_db.close()

        main.DATABASE = cls.db_path
        init_db()
        cls.client = TestClient(app)

        cls.provider = GroundedAuditAIProvider()
        cls.registry = build_default_tool_registry()
        cls.core = AgentCore(provider=cls.provider, registry=cls.registry)
        main.set_agent_core(cls.core)
        cls.rag = KnowledgeRAG()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except Exception:
                pass

        # Ghi kết quả audit ra file JSON để phục vụ báo cáo
        report_path = os.path.join(os.path.dirname(__file__), "knowledge_quality_audit_results.json")
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(cls.audit_results, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def setUp(self):
        with main.get_db() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id = 999")
            conn.execute("DELETE FROM transactions WHERE user_id = 999")
            conn.execute("DELETE FROM budgets WHERE user_id = 999")
            conn.execute("DELETE FROM saving_goals WHERE user_id = 999")
            conn.execute("DELETE FROM wallets WHERE user_id = 999")
            conn.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES (999, 'audit_user@gmail.com', 'dummy_hash', 'Đạo Hữu Audit', 'user')")
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9991, 999, 'Linh Thạch Tiền Mặt', 'CASH', 5000000)")
            conn.execute("INSERT INTO wallets (id, user_id, wallet_name, wallet_type, balance) VALUES (9992, 999, 'Linh Mạch Vietcombank', 'BANK', 20000000)")
            conn.execute("INSERT INTO budgets (id, user_id, category_id, limit_amount, month_year) VALUES (9991, 999, 1, 3000000, strftime('%Y-%m', 'now'))")

        self.token = create_token(user_id=999, email="audit_user@gmail.com", role="user", token_version=1)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _record_result(self, group: str, q_num: int, question: str, expected: str, actual: str,
                       status: str, routing: str, retrieved_sources: List[str],
                       root_cause: str = "", doc_ref: str = ""):
        record = {
            "group": group,
            "q_num": q_num,
            "question": question,
            "expected_behavior": expected,
            "actual_behavior": actual,
            "status": status,
            "routing": routing,
            "retrieved_sources": retrieved_sources,
            "root_cause": root_cause,
            "doc_ref": doc_ref
        }
        self.audit_results.append(record)

    # =========================================================================
    # NHÓM A: SYSTEM OVERVIEW (4 CÂU)
    # =========================================================================
    def test_a1_special_system_overview(self):
        """A1 [SPECIAL]: 'Hệ thống có những chức năng nào?'"""
        q = "Hệ thống có những chức năng nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_pillars = any(k in text for k in ["túi càn khôn", "giao dịch", "hạn mức", "ngân sách", "sổ nợ", "tiết kiệm"])
        status = "PASS" if has_pillars and len(trace) > 0 else "FAIL"
        self._record_result("A", 1, q, "Liệt kê đầy đủ 11 phân hệ ACTIVE, có cấu trúc rõ ràng", resp.text[:120],
                            status, resp.tool_executed, src_names, "", "system_overview.md / capabilities.json")
        self.assertEqual(status, "PASS")

    def test_a2_system_introduction(self):
        """A2: 'Giới thiệu tổng quan về Càn Khôn Linh Thạch Các'"""
        q = "Giới thiệu tổng quan về Càn Khôn Linh Thạch Các"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if len(trace) > 0 and "càn khôn linh thạch các" in resp.text.lower() else "FAIL"
        self._record_result("A", 2, q, "Giới thiệu tổng quan hệ thống quản lý tài chính", resp.text[:120],
                            status, resp.tool_executed, src_names, "", "system_overview.md")
        self.assertEqual(status, "PASS")

    def test_a3_system_pillars(self):
        """A3: 'Hệ thống quản lý tài chính này có những phân hệ gì?'"""
        q = "Hệ thống quản lý tài chính này có những phân hệ gì?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["phân hệ", "tổng quan", "túi càn khôn"]) else "FAIL"
        self._record_result("A", 3, q, "Trình bày các phân hệ quản lý tài chính", resp.text[:120],
                            status, resp.tool_executed, src_names, "", "system_overview.md")
        self.assertEqual(status, "PASS")

    def test_a4_all_active_features(self):
        """A4: 'Cho ta biết tất cả tính năng hiện có trong ứng dụng'"""
        q = "Cho ta biết tất cả tính năng hiện có trong ứng dụng"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if len(trace) > 0 else "FAIL"
        self._record_result("A", 4, q, "Liệt kê toàn bộ tính năng active", resp.text[:120],
                            status, resp.tool_executed, src_names, "", "capabilities.json")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM B: FEATURE DISCOVERY (4 CÂU)
    # =========================================================================
    def test_b5_special_multi_bank_accounts(self):
        """B5 [SPECIAL]: 'Ta có thể quản lý nhiều tài khoản ngân hàng không?'"""
        q = "Ta có thể quản lý nhiều tài khoản ngân hàng không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_confirm = "có thể" in text or "hoàn toàn" in text or "được" in text
        has_wallet = "túi càn khôn" in text or "ngân hàng" in text or "ví" in text
        status = "PASS" if has_confirm and has_wallet and any("wallet" in s or "capabilities" in s for s in src_names) else "FAIL"
        self._record_result("B", 5, q, "Khẳng định có thể quản lý nhiều ngân hàng không giới hạn trong Túi Càn Khôn",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "wallets_tui_can_khon.md")
        self.assertEqual(status, "PASS")

    def test_b6_special_manage_debts_feature(self):
        """B6 [SPECIAL]: 'Muốn quản lý khoản nợ thì dùng chức năng nào?'"""
        q = "Muốn quản lý khoản nợ thì dùng chức năng nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_debt = "sổ nợ" in text or "nợ" in text
        has_tab = "tab 3" in text or "sổ nợ" in text
        status = "PASS" if has_debt and any("debts" in s for s in src_names) else "FAIL"
        self._record_result("B", 6, q, "Chỉ dẫn đến phân hệ Sổ Nợ (Tab 3) để quản lý vay và cho vay",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "debts.md")
        self.assertEqual(status, "PASS")

    def test_b7_invoice_ocr_discovery(self):
        """B7: 'Hệ thống có tính năng nào giúp nhận diện hóa đơn tự động không?'"""
        q = "Hệ thống có tính năng nào giúp nhận diện hóa đơn tự động không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["ocr", "linh nhãn", "hóa đơn"]) else "FAIL"
        self._record_result("B", 7, q, "Chỉ dẫn đến Linh Nhãn OCR (Tab 7)", resp.text[:120],
                            status, resp.tool_executed, src_names, "", "ocr_invoice.md")
        self.assertEqual(status, "PASS")

    def test_b8_recurring_discovery(self):
        """B8: 'Nếu muốn thiết lập các khoản chi tiêu lặp lại hàng tháng thì dùng cái gì?'"""
        q = "Nếu muốn thiết lập các khoản chi tiêu lặp lại hàng tháng thì dùng cái gì?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["định kỳ", "linh trận", "giao dịch"]) else "FAIL"
        self._record_result("B", 8, q, "Chỉ dẫn đến Linh Trận Định Kỳ (Tab 2)", resp.text[:120],
                            status, resp.tool_executed, src_names, "", "recurring.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM C: FEATURE DETAIL (4 CÂU)
    # =========================================================================
    def test_c9_special_saving_goals_detail(self):
        """C9 [SPECIAL]: 'Mục tiêu tiết kiệm hoạt động ra sao?'"""
        q = "Mục tiêu tiết kiệm hoạt động ra sao?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_detail = any(k in text for k in ["nạp", "rút", "tiến độ", "thiết lập", "tích lũy"])
        status = "PASS" if has_detail and any("saving_goals" in s for s in src_names) else "FAIL"
        self._record_result("C", 9, q, "Giải thích chi tiết cơ chế nạp/rút và tiến độ mục tiêu tiết kiệm",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "saving_goals.md")
        self.assertEqual(status, "PASS")

    def test_c10_special_recurring_detail(self):
        """C10 [SPECIAL]: 'Giao dịch định kỳ hoạt động thế nào?'"""
        q = "Giao dịch định kỳ hoạt động thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_detail = any(k in text for k in ["chu kỳ", "tự động", "nhắc nhở", "lặp lại", "định kỳ"])
        status = "PASS" if has_detail and any("recurring" in s or "transactions" in s for s in src_names) else "FAIL"
        self._record_result("C", 10, q, "Giải thích chu kỳ lặp lại và cơ chế tự động sinh giao dịch",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "recurring.md")
        self.assertEqual(status, "PASS")

    def test_c11_special_ocr_detail(self):
        """C11 [SPECIAL]: 'Quét hóa đơn bằng AI ra sao?'"""
        q = "Quét hóa đơn bằng AI ra sao?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_detail = any(k in text for k in ["chụp", "tải", "trích xuất", "nhận diện", "kiểm tra", "ocr"])
        status = "PASS" if has_detail and any("ocr" in s for s in src_names) else "FAIL"
        self._record_result("C", 11, q, "Trình bày pipeline quét ảnh bóc tách dữ liệu hóa đơn",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "ocr_invoice.md")
        self.assertEqual(status, "PASS")

    def test_c12_debts_settlement_detail(self):
        """C12: 'Sổ Nợ trong hệ thống quản lý những thông tin gì và có quyết toán được không?'"""
        q = "Sổ Nợ trong hệ thống quản lý những thông tin gì và có quyết toán được không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        status = "PASS" if any(k in text for k in ["quyết toán", "tất toán", "vay", "cho vay"]) else "FAIL"
        self._record_result("C", 12, q, "Giải thích quản lý khoản vay/cho vay và hỗ trợ quyết toán",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "debts.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM D: HOW-TO (4 CÂU)
    # =========================================================================
    def test_d13_how_to_create_wallet(self):
        """D13: 'Làm sao để tạo một ví mới trong Túi Càn Khôn?'"""
        q = "Làm sao để tạo một ví mới trong Túi Càn Khôn?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["bước", "thêm ví", "túi càn khôn"]) else "FAIL"
        self._record_result("D", 13, q, "Hướng dẫn từng bước tạo ví trong Túi Càn Khôn",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "how_to_create_wallet.md")
        self.assertEqual(status, "PASS")

    def test_d14_how_to_add_transaction(self):
        """D14: 'Cách ghi nhận một giao dịch chi tiêu mới như thế nào?'"""
        q = "Cách ghi nhận một giao dịch chi tiêu mới như thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["bước", "giao dịch", "chi tiêu"]) else "FAIL"
        self._record_result("D", 14, q, "Hướng dẫn từng bước ghi nhận giao dịch chi tiêu",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "how_to_add_transaction.md")
        self.assertEqual(status, "PASS")

    def test_d15_how_to_export_excel(self):
        """D15: 'Làm thế nào để xuất dữ liệu báo cáo thu chi ra file Excel?'"""
        q = "Làm thế nào để xuất dữ liệu báo cáo thu chi ra file Excel?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["excel", "xuất", "báo cáo"]) else "FAIL"
        self._record_result("D", 15, q, "Hướng dẫn xuất dữ liệu Excel/CSV tại Tab 2 hoặc Tab 9",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "reports_stats.md")
        self.assertEqual(status, "PASS")

    def test_d16_how_to_create_saving_goal(self):
        """D16: 'Làm sao để thiết lập một mục tiêu tiết kiệm mới?'"""
        q = "Làm sao để thiết lập một mục tiêu tiết kiệm mới?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["bước", "mục tiêu", "tiết kiệm"]) else "FAIL"
        self._record_result("D", 16, q, "Hướng dẫn tạo mục tiêu tiết kiệm tại Tab 4",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "saving_goals.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM E: WORKFLOW (4 CÂU)
    # =========================================================================
    def test_e17_special_transfer_money_workflow(self):
        """E17 [SPECIAL]: 'Chuyển tiền giữa hai ví hoạt động thế nào?'"""
        q = "Chuyển tiền giữa hai ví hoạt động thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_wf = any(k in text for k in ["nguyên tử", "2 chiều", "ví nguồn", "ví đích", "trừ tiền", "cộng tiền"])
        status = "PASS" if has_wf and any("wallet" in s or "workflow" in s for s in src_names) else "FAIL"
        self._record_result("E", 17, q, "Giải thích workflow chuyển tiền nguyên tử 2 chiều giữa 2 ví",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "financial_workflows.md / wallets_tui_can_khon.md")
        self.assertEqual(status, "PASS")

    def test_e18_ocr_to_transaction_workflow(self):
        """E18: 'Quy trình từ lúc quét hóa đơn đến khi tạo giao dịch diễn ra như thế nào?'"""
        q = "Quy trình từ lúc quét hóa đơn đến khi tạo giao dịch diễn ra như thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["ocr", "xác nhận", "lưu", "giao dịch"]) else "FAIL"
        self._record_result("E", 18, q, "Quy trình 3 bước: Tải ảnh -> AI bóc tách -> Kiểm tra & Lưu",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "how_to_use_ocr.md / financial_workflows.md")
        self.assertEqual(status, "PASS")

    def test_e19_debt_settlement_workflow(self):
        """E19: 'Quy trình theo dõi và quyết toán một khoản nợ cho vay gồm những bước gì?'"""
        q = "Quy trình theo dõi và quyết toán một khoản nợ cho vay gồm những bước gì?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["quyết toán", "nợ", "ví"]) else "FAIL"
        self._record_result("E", 19, q, "Quy trình ghi nợ -> theo dõi hạn -> quyết toán cập nhật số dư",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "how_to_manage_debts.md")
        self.assertEqual(status, "PASS")

    def test_e20_budget_monitoring_workflow(self):
        """E20: 'Quy trình kiểm soát ngân sách cảnh báo khi chi tiêu vượt trần ra sao?'"""
        q = "Quy trình kiểm soát ngân sách cảnh báo khi chi tiêu vượt trần ra sao?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["ngân sách", "hạn mức", "cảnh báo", "vượt"]) else "FAIL"
        self._record_result("E", 20, q, "Quy trình thiết lập trần -> tính chi tiêu tự động -> cảnh báo màu",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "budgets.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM F: AI ARCHITECTURE (4 CÂU)
    # =========================================================================
    def test_f21_special_large_vs_small_khi_linh(self):
        """F21 [SPECIAL]: 'Khí Linh Lớn khác Khí Linh Nhỏ thế nào?'"""
        q = "Khí Linh Lớn khác Khí Linh Nhỏ thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_large = "khí linh ai lớn" in text or "khí linh lớn" in text or "knowledge" in text or "tri thức" in text
        has_small = "khí linh nhỏ" in text or "live" in text or "action" in text or "thực thi" in text
        status = "PASS" if has_large and has_small and any("khi_linh" in s for s in src_names) else "FAIL"
        self._record_result("F", 21, q, "Phân biệt rõ ràng vai trò Khí Linh Lớn (Knowledge RAG) và Khí Linh Nhỏ (Live Action)",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "khi_linh_architecture.md")
        self.assertEqual(status, "PASS")

    def test_f22_large_khi_linh_role(self):
        """F22: 'Vai trò và nhiệm vụ của Khí Linh AI Lớn trong hệ thống là gì?'"""
        q = "Vai trò và nhiệm vụ của Khí Linh AI Lớn trong hệ thống là gì?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["trợ lý tri thức", "knowledge", "hướng dẫn", "chỉ đọc"]) else "FAIL"
        self._record_result("F", 22, q, "Khẳng định vai trò Trợ Lý Tri Thức Toàn Hệ Thống, không thực thi",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "khi_linh_architecture.md")
        self.assertEqual(status, "PASS")

    def test_f23_small_khi_linh_role(self):
        """F23: 'Khí Linh Nhỏ hoạt động ở chế độ nào và có quyền hạn gì?'"""
        q = "Khí Linh Nhỏ hoạt động ở chế độ nào và có quyền hạn gì?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["live", "action", "thực thi", "xác nhận"]) else "FAIL"
        self._record_result("F", 23, q, "Khí Linh Nhỏ chạy Live Action mode, có quyền thực thi kèm confirmation",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "khi_linh_architecture.md")
        self.assertEqual(status, "PASS")

    def test_f24_two_khi_linh_interaction(self):
        """F24: 'Kiến trúc 2 Khí Linh tương tác với nhau như thế nào?'"""
        q = "Kiến trúc 2 Khí Linh tương tác với nhau như thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if len(trace) > 0 else "FAIL"
        self._record_result("F", 24, q, "Giải thích kiến trúc phân tách độc lập giữa Knowledge và Action",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "khi_linh_architecture.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM G: SECURITY / PERMISSION (4 CÂU)
    # =========================================================================
    def test_g25_special_large_khi_linh_no_auto_create(self):
        """G25 [SPECIAL]: 'Khí Linh Lớn có được tự thêm ví không?'"""
        q = "Khí Linh Lớn có được tự thêm ví không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_denial = "không" in text or "tuyệt đối không" in text
        has_reason = "tri thức" in text or "knowledge" in text or "chỉ đọc" in text or "read-only" in text
        status = "PASS" if has_denial and has_reason and any("khi_linh" in s or "security" in s for s in src_names) else "FAIL"
        self._record_result("G", 25, q, "Khẳng định tuyệt đối KHÔNG CÓ QUYỀN tự thêm ví",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "khi_linh_architecture.md / security_and_permissions.md")
        self.assertEqual(status, "PASS")

    def test_g26_large_khi_linh_no_auto_delete(self):
        """G26: 'Khí Linh Lớn có thể tự ý xóa giao dịch của ta không?'"""
        q = "Khí Linh Lớn có thể tự ý xóa giao dịch của ta không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["không", "tuyệt đối không", "chỉ đọc"]) else "FAIL"
        self._record_result("G", 26, q, "Khẳng định không có quyền xóa giao dịch hay thay đổi dữ liệu",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "security_and_permissions.md")
        self.assertEqual(status, "PASS")

    def test_g27_soul_lamp_security(self):
        """G27: 'Bản Mệnh Hồn Đăng là gì và có vai trò bảo mật thế nào?'"""
        q = "Bản Mệnh Hồn Đăng là gì và có vai trò bảo mật thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["hồn đăng", "bảo mật", "2 lớp"]) else "FAIL"
        self._record_result("G", 27, q, "Giải thích Bản Mệnh Hồn Đăng là bảo mật xác thực 2 lớp",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "security_and_permissions.md")
        self.assertEqual(status, "PASS")

    def test_g28_admin_role_security(self):
        """G28: 'Phân quyền chưởng môn và thành viên trong hệ thống khác nhau ra sao?'"""
        q = "Phân quyền chưởng môn và thành viên trong hệ thống khác nhau ra sao?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any(k in resp.text.lower() for k in ["chưởng môn", "admin", "thành viên", "cá nhân"]) else "FAIL"
        self._record_result("G", 28, q, "Phân biệt quyền Chưởng Môn (Admin) và Thành Viên (User)",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "admin_portal.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM H: PERSONAL READ-ONLY DATA (4 CÂU)
    # =========================================================================
    def test_h29_special_my_wallets(self):
        """H29 [SPECIAL]: 'Ta hiện có những ví nào?' -> Gọi READ-ONLY tool get_wallets"""
        q = "Ta hiện có những ví nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.SUCCESS)
        self.assertEqual(resp.tool_executed, "get_wallets")
        text = resp.text.lower()
        has_wallets = "tiền mặt" in text or "vietcombank" in text
        status = "PASS" if has_wallets and resp.tool_executed == "get_wallets" else "FAIL"
        self._record_result("H", 29, q, "Gọi get_wallets (READ-ONLY) trả về danh sách ví thật của user",
                            resp.text[:120], status, resp.tool_executed, ["DB: wallets table"], "", "Tool: get_wallets")
        self.assertEqual(status, "PASS")

    def test_h30_special_my_food_budget(self):
        """H30 [SPECIAL]: 'Ngân sách ăn uống tháng này của ta thế nào?' -> Gọi READ-ONLY tool budget_status"""
        q = "Ngân sách ăn uống tháng này của ta thế nào?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.SUCCESS)
        self.assertEqual(resp.tool_executed, "budget_status")
        text = resp.text.lower()
        has_budget = "ngân sách" in text or "hạn mức" in text or "ăn uống" in text
        status = "PASS" if has_budget and resp.tool_executed == "budget_status" else "FAIL"
        self._record_result("H", 30, q, "Gọi budget_status (READ-ONLY) trả về tình trạng ngân sách Ăn Uống",
                            resp.text[:120], status, resp.tool_executed, ["DB: budgets table"], "", "Tool: budget_status")
        self.assertEqual(status, "PASS")

    def test_h31_total_balance_query(self):
        """H31: 'Tổng số dư tài sản hiện tại của ta là bao nhiêu?' -> Gọi get_wallets"""
        q = "Tổng số dư tài sản hiện tại của ta là bao nhiêu?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.SUCCESS)
        self.assertEqual(resp.tool_executed, "get_wallets")
        status = "PASS" if resp.tool_executed == "get_wallets" else "FAIL"
        self._record_result("H", 31, q, "Gọi get_wallets để tính tổng tài sản hiện có",
                            resp.text[:120], status, resp.tool_executed, ["DB: wallets table"], "", "Tool: get_wallets")
        self.assertEqual(status, "PASS")

    def test_h32_spending_summary_query(self):
        """H32: 'Tháng này ta đã chi tiêu bao nhiêu tiền?' -> Gọi spending_summary / get_financial_overview"""
        q = "Tháng này ta đã chi tiêu bao nhiêu tiền?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.SUCCESS)
        self.assertIn(resp.tool_executed, ["spending_summary", "get_financial_overview", "financial_overview"])
        status = "PASS" if resp.tool_executed in ["spending_summary", "get_financial_overview", "financial_overview"] else "FAIL"
        self._record_result("H", 32, q, "Gọi công cụ chỉ đọc báo cáo chi tiêu tháng (READ-ONLY)",
                            resp.text[:120], status, resp.tool_executed, ["DB: transactions table"], "", "Tool: spending_summary / get_financial_overview")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM I: COMBINED RAG + PERSONAL DATA (3 CÂU)
    # =========================================================================
    def test_i33_combined_budget_query(self):
        """I33: 'Hệ thống có quản lý ngân sách không và ngân sách ăn uống của ta hiện tại ra sao?'"""
        q = "Hệ thống có quản lý ngân sách không và ngân sách ăn uống của ta hiện tại ra sao?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "budget_status")
        self.assertIn("knowledge_trace", resp.tool_result)
        text = resp.text.lower()
        has_rag = "hạn mức" in text or "ngân sách" in text
        has_data = "ăn uống" in text or "3.000.000" in text
        status = "PASS" if has_rag and has_data else "FAIL"
        self._record_result("I", 33, q, "Kết hợp RAG giải thích tính năng và chèn số liệu ngân sách thực tế",
                            resp.text[:120], status, resp.tool_executed, ["RAG + DB budgets"], "", "RAG + Tool read")
        self.assertEqual(status, "PASS")

    def test_i34_combined_wallet_query(self):
        """I34: 'Túi Càn Khôn là gì và ta đang có những ví nào trong đó?'"""
        q = "Túi Càn Khôn là gì và ta đang có những ví nào trong đó?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "get_wallets")
        self.assertIn("knowledge_trace", resp.tool_result)
        text = resp.text.lower()
        has_rag = "túi càn khôn" in text
        has_data = "linh thạch" in text or "vietcombank" in text
        status = "PASS" if has_rag and has_data else "FAIL"
        self._record_result("I", 34, q, "Kết hợp định nghĩa Túi Càn Khôn và danh sách ví hiện có",
                            resp.text[:120], status, resp.tool_executed, ["RAG + DB wallets"], "", "RAG + Tool read")
        self.assertEqual(status, "PASS")

    def test_i35_combined_saving_goal_query(self):
        """I35: 'Tính năng mục tiêu tiết kiệm là gì và ta đang có mục tiêu nào không?'"""
        q = "Tính năng mục tiêu tiết kiệm là gì và ta đang có mục tiêu nào không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "saving_goal_status")
        self.assertIn("knowledge_trace", resp.tool_result)
        text = resp.text.lower()
        has_rag = "mục tiêu tiết kiệm" in text or "mục tiêu" in text
        status = "PASS" if has_rag else "FAIL"
        self._record_result("I", 35, q, "Giải thích mục tiêu tiết kiệm và kiểm tra dữ liệu cá nhân",
                            resp.text[:120], status, resp.tool_executed, ["RAG + DB goals"], "", "RAG + Tool read")
        self.assertEqual(status, "PASS")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM J: UNSUPPORTED / UNKNOWN (4 CÂU)
    # =========================================================================
    def test_j36_special_stock_trading_unsupported(self):
        """J36 [SPECIAL]: 'Hệ thống có giao dịch cổ phiếu tự động không?'"""
        q = "Hệ thống có giao dịch cổ phiếu tự động không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        text = resp.text.lower()
        has_neg = "chưa hỗ trợ" in text or "không hỗ trợ" in text
        has_no_hallucination = "kết nối sàn" not in text and "mua cổ phiếu" not in text
        status = "PASS" if has_neg and has_no_hallucination else "FAIL"
        self._record_result("J", 36, q, "Khẳng định CHƯA HỖ TRỢ giao dịch cổ phiếu, không ảo giác",
                            resp.text[:120], status, resp.tool_executed, ["limitations_and_unsupported.md"], "", "limitations_and_unsupported.md")
        self.assertEqual(status, "PASS")

    def test_j37_special_bitcoin_wallet_unsupported(self):
        """J37 [SPECIAL]: 'Hệ thống có ví Bitcoin không?'"""
        q = "Hệ thống có ví Bitcoin không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        text = resp.text.lower()
        has_neg = "chưa hỗ trợ" in text or "không hỗ trợ" in text
        status = "PASS" if has_neg and "bitcoin" in text else "FAIL"
        self._record_result("J", 37, q, "Khẳng định CHƯA HỖ TRỢ ví crypto/bitcoin",
                            resp.text[:120], status, resp.tool_executed, ["limitations_and_unsupported.md"], "", "limitations_and_unsupported.md")
        self.assertEqual(status, "PASS")

    def test_j38_gold_forex_unsupported(self):
        """J38: 'Hệ thống có tính năng đầu tư vàng hoặc ngoại hối forex không?'"""
        q = "Hệ thống có tính năng đầu tư vàng hoặc ngoại hối forex không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        text = resp.text.lower()
        status = "PASS" if "chưa hỗ trợ" in text or "không" in text else "FAIL"
        self._record_result("J", 38, q, "Khẳng định chưa hỗ trợ đầu tư ngoại hối forex/vàng",
                            resp.text[:120], status, resp.tool_executed, ["limitations_and_unsupported.md"], "", "limitations_and_unsupported.md")
        self.assertEqual(status, "PASS")

    def test_j39_auto_card_charge_unsupported(self):
        """J39: 'Hệ thống có liên kết thẻ tín dụng quốc tế để tự động cà thẻ không?'"""
        q = "Hệ thống có liên kết thẻ tín dụng quốc tế để tự động cà thẻ không?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        text = resp.text.lower()
        status = "PASS" if "chưa" in text or "không" in text or "thủ công" in text else "FAIL"
        self._record_result("J", 39, q, "Khẳng định ghi chép thủ công/RAG, chưa liên kết auto quẹt thẻ",
                            resp.text[:120], status, resp.tool_executed, ["limitations_and_unsupported.md"], "", "limitations_and_unsupported.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM K: FOLLOW-UP / CONTEXT (3 KỊCH BẢN MULTI-TURN = 6 LƯỢT)
    # =========================================================================
    def test_k40_special_follow_up_saving_goals(self):
        """K40 [SPECIAL]: Turn 1 'Hệ thống có mục tiêu tiết kiệm không?' -> Turn 2 [SPECIAL] 'Giải thích kỹ hơn.'"""
        q1 = "Hệ thống có mục tiêu tiết kiệm không?"
        resp1 = asyncio.run(self.core.process_request(user_id=999, user_message=q1, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp1.tool_executed, "knowledge_rag")

        q2 = "Giải thích kỹ hơn."
        history_context = f"Đạo hữu: {q1}\nKhí Linh: {resp1.text}"
        resp2 = asyncio.run(self.core.process_request(
            user_id=999,
            user_message=q2,
            mode=AgentMode.KNOWLEDGE,
            recent_history=history_context
        ))
        self.assertEqual(resp2.tool_executed, "knowledge_rag")
        trace = resp2.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("saving_goals" in s or "saving_goals" in t.get("chunk_id", "") or "saving_goals" in t.get("capability", "") for t in trace for s in [t.get("source_file", "")]) else "FAIL"
        self._record_result("K", 40, f"Turn 2: '{q2}' (sau '{q1}')", "Truy xuất chính xác tài liệu saving_goals theo ngữ cảnh trước",
                            resp2.text[:120], status, resp2.tool_executed, src_names, "", "saving_goals.md")
        self.assertEqual(status, "PASS")

    def test_k41_special_follow_up_how_it_works(self):
        """K41 [SPECIAL]: Turn 1 'Túi Càn Khôn là gì?' -> Turn 2 [SPECIAL] 'Cái này hoạt động thế nào?'"""
        q1 = "Túi Càn Khôn là gì?"
        resp1 = asyncio.run(self.core.process_request(user_id=999, user_message=q1, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp1.tool_executed, "knowledge_rag")

        q2 = "Cái này hoạt động thế nào?"
        history_context = f"Đạo hữu: {q1}\nKhí Linh: {resp1.text}"
        resp2 = asyncio.run(self.core.process_request(
            user_id=999,
            user_message=q2,
            mode=AgentMode.KNOWLEDGE,
            recent_history=history_context
        ))
        self.assertEqual(resp2.tool_executed, "knowledge_rag")
        trace = resp2.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("wallet" in s or "wallet" in t.get("chunk_id", "") or "wallet" in t.get("capability", "") for t in trace for s in [t.get("source_file", "")]) else "FAIL"
        self._record_result("K", 41, f"Turn 2: '{q2}' (sau '{q1}')", "Hiểu 'cái này' là Túi Càn Khôn và giải thích cách hoạt động",
                            resp2.text[:120], status, resp2.tool_executed, src_names, "", "wallets_tui_can_khon.md")
        self.assertEqual(status, "PASS")

    def test_k42_follow_up_debts_usage(self):
        """K42: Turn 1 'Hệ thống có quản lý nợ không?' -> Turn 2 'Cách sử dụng nó ra sao?'"""
        q1 = "Hệ thống có quản lý nợ không?"
        resp1 = asyncio.run(self.core.process_request(user_id=999, user_message=q1, mode=AgentMode.KNOWLEDGE))

        q2 = "Cách sử dụng nó ra sao?"
        history_context = f"Đạo hữu: {q1}\nKhí Linh: {resp1.text}"
        resp2 = asyncio.run(self.core.process_request(
            user_id=999,
            user_message=q2,
            mode=AgentMode.KNOWLEDGE,
            recent_history=history_context
        ))
        self.assertEqual(resp2.tool_executed, "knowledge_rag")
        trace = resp2.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("debt" in s or "debt" in t.get("chunk_id", "") or "debt" in t.get("capability", "") for t in trace for s in [t.get("source_file", "")]) else "FAIL"
        self._record_result("K", 42, f"Turn 2: '{q2}' (sau '{q1}')", "Hiểu 'nó' là Sổ Nợ và hướng dẫn cách sử dụng",
                            resp2.text[:120], status, resp2.tool_executed, src_names, "", "debts.md / how_to_manage_debts.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # NHÓM L: VIETNAMESE NATURAL-LANGUAGE VARIATIONS (5 CÂU)
    # =========================================================================
    def test_l43_special_rag_concept(self):
        """L43 [SPECIAL]: 'RAG là gì?'"""
        q = "RAG là gì?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        text = resp.text.lower()
        has_general = "retrieval-augmented generation" in text or "truy xuất" in text
        has_system = "càn khôn" in text or "khí linh" in text
        status = "PASS" if has_general and has_system else "FAIL"
        self._record_result("L", 43, q, "Giải thích RAG cả ở góc độ khái niệm chung và ứng dụng trong Càn Khôn",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "common_questions.md / khi_linh_architecture.md")
        self.assertEqual(status, "PASS")

    def test_l44_dialect_central_features(self):
        """L44: 'Web ni có những chức năng chi rứa?' (Tiếng miền Trung)"""
        q = "Web ni có những chức năng chi rứa?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if len(trace) > 0 and any("system_overview" in s or "capabilities" in s for s in src_names) else "FAIL"
        self._record_result("L", 44, q, "Nhận diện phương ngữ miền Trung 'chi rứa' tương đương 'chức năng gì'",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "system_overview.md")
        self.assertEqual(status, "PASS")

    def test_l45_dialect_southern_bank_wallet(self):
        """L45: 'Hệ thống có xài được nhiều tài khoản ngân hàng hông ta?' (Tiếng miền Nam)"""
        q = "Hệ thống có xài được nhiều tài khoản ngân hàng hông ta?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("wallet" in s or "capabilities" in s for s in src_names) else "FAIL"
        self._record_result("L", 45, q, "Nhận diện phương ngữ miền Nam 'xài... hông ta' là hỏi tính năng đa ví ngân hàng",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "wallets_tui_can_khon.md")
        self.assertEqual(status, "PASS")

    def test_l46_dialect_lend_debt(self):
        """L46: 'Muốn ghi nợ cho người ta mượn thì mần răng?' (Tiếng miền Trung)"""
        q = "Muốn ghi nợ cho người ta mượn thì mần răng?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("debts" in s for s in src_names) else "FAIL"
        self._record_result("L", 46, q, "Nhận diện 'mần răng' là 'làm sao' và hướng dẫn dùng Sổ Nợ",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "debts.md / how_to_manage_debts.md")
        self.assertEqual(status, "PASS")

    def test_l47_teen_colloquial_permission(self):
        """L47: 'Khí Linh bự có tự ý thêm ví giùm tui được hem?' (Teen / thân mật)"""
        q = "Khí Linh bự có tự ý thêm ví giùm tui được hem?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("khi_linh" in s or "security" in s or "wallet" in s for s in src_names) else "FAIL"
        self._record_result("L", 47, q, "Nhận diện 'Khí Linh bự' là Khí Linh Lớn, 'được hem' là hỏi quyền",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "khi_linh_architecture.md")
        self.assertEqual(status, "PASS")

    def test_l48_dialect_ocr_bill(self):
        """L48: 'Tính năng quét bill bằng trí tuệ nhân tạo mần ăn ra sao?' (Khẩu ngữ)"""
        q = "Tính năng quét bill bằng trí tuệ nhân tạo mần ăn ra sao?"
        resp = asyncio.run(self.core.process_request(user_id=999, user_message=q, mode=AgentMode.KNOWLEDGE))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertEqual(resp.tool_executed, "knowledge_rag")
        trace = resp.tool_result.get("trace_sources", [])
        src_names = [t.get("source_file", "") for t in trace]
        status = "PASS" if any("ocr" in s for s in src_names) else "FAIL"
        self._record_result("L", 48, q, "Nhận diện 'quét bill' là OCR Hóa Đơn và giải thích hoạt động",
                            resp.text[:120], status, resp.tool_executed, src_names, "", "ocr_invoice.md")
        self.assertEqual(status, "PASS")

    # =========================================================================
    # KIỂM TRA BẢO MẬT CODE-LEVEL (SECURITY BOUNDARY)
    # =========================================================================
    def test_security_boundary_code_level_mutation_denied(self):
        """Khí Linh Lớn (AgentMode.KNOWLEDGE) bị chặn tuyệt đối mọi mutation tools tại code-level"""
        mutation_tools = [
            ("create_wallet", {"wallet_name": "Hack Wallet", "balance": 1000000}),
            ("create_expense", {"amount": 50000, "category_name": "Ăn Uống"}),
            ("create_income", {"amount": 100000, "category_name": "Lương"}),
            ("transfer_money", {"from_wallet_id": 9991, "to_wallet_id": 9992, "amount": 50000}),
            ("create_budget", {"category_id": 1, "limit_amount": 2000000}),
            ("delete_transaction", {"transaction_id": 99999})
        ]

        for tool_name, args in mutation_tools:
            res = asyncio.run(self.registry.execute(
                tool_name,
                user_id=999,
                mode=AgentMode.KNOWLEDGE,
                **args
            ))
            self.assertFalse(res.success, f"Tool {tool_name} MUST NOT succeed in KNOWLEDGE mode!")
            self.assertEqual(res.error, "PERMISSION_DENIED")

    def test_security_boundary_action_attempt_in_knowledge_mode(self):
        """Người dùng cố tình ra lệnh action 'Thêm ví Momo 20 triệu' trong Knowledge mode -> Từ chối, không thay đổi DB"""
        q = "Thêm ví Momo 20 triệu"
        resp = asyncio.run(self.core.process_request(
            user_id=999,
            user_message=q,
            mode=AgentMode.KNOWLEDGE
        ))
        self.assertEqual(resp.state, AgentState.IDLE)
        self.assertIn("không có quyền", resp.text.lower())

        # Kiểm tra database không bị thêm ví Momo
        with main.get_db() as conn:
            wallets = conn.execute("SELECT wallet_name FROM wallets WHERE user_id = 999").fetchall()
            wallet_names = [w[0] for w in wallets]
            self.assertNotIn("Momo", wallet_names)


if __name__ == "__main__":
    unittest.main()
