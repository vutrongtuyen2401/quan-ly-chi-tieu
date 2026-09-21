"""
Agent Core — Càn Khôn Linh Thạch Các
Bộ xử lý trung tâm của Khí Linh AI Agent:
- Quản lý trạng thái Agent (IDLE, THINKING, PLANNING, CONFIRMING, EXECUTING, SUCCESS, ERROR)
- Khám phá năng lực thông qua ToolRegistry và phân định rõ ràng READ / WRITE / DELETE / SYSTEM
- Cơ chế xác nhận đối thoại bắt buộc cho mọi thao tác biến động dữ liệu (Write & Delete operations)
- Hỗ trợ sửa đổi (modification) và hủy bỏ (cancellation) tự nhiên qua hội thoại
- Chặn xác nhận / hủy mồ côi (Zero orphan execution)
- Không bao giờ tuyên bố thành công giả tạo (Verified Result Invariant)
- Tách biệt hoàn toàn giữa đối thoại thông thường (General Chat), tư vấn phân tích (Advisory) và hành động tài chính (Financial Action).
"""

from enum import Enum
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass, field
import datetime
import json
import re
import uuid

from .provider import AIProvider
from .tools import ToolRegistry, Tool, ToolResult, RiskLevel, ToolActionType, OperationType, AgentMode, _match_wallet_name, resolve_category_icon
from .parser import VietnameseFinancialParser
from .knowledge.rag import KnowledgeRAG
from .knowledge.builder import remove_accents


class AgentState(str, Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    PLANNING = "PLANNING"
    CONFIRMING = "CONFIRMING"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


@dataclass
class AgentResponse:
    """Cấu trúc phản hồi đầy đủ của Khí Linh Agent"""
    text: str
    state: AgentState
    tool_executed: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    pending_confirmation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "state": self.state.value,
            "tool_executed": self.tool_executed,
            "tool_result": self.tool_result,
            "pending_confirmation": self.pending_confirmation,
            "error": self.error
        }


@dataclass
class ActionRecord:
    """Bản ghi hành động thực thi thành công của Agent"""
    tool_name: str
    operation: OperationType
    entity_type: str  # "transaction", "wallet", "budget", "saving_goal", "debt", "category", "recurring", "transfer"
    entity_id: Optional[int]
    entity_summary: str
    entity_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "operation": self.operation.value if hasattr(self.operation, "value") else str(self.operation),
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_summary": self.entity_summary,
            "entity_data": self.entity_data,
            "timestamp": self.timestamp.isoformat()
        }


class AgentCore:
    """Trung tâm điều phối Agent toàn hệ thống của Khí Linh Tiên Trí"""

    def __init__(self, provider: AIProvider, registry: ToolRegistry):
        self.provider = provider
        self.registry = registry
        self.rag = KnowledgeRAG()
        # Lưu trữ trạng thái chờ xác nhận cho từng user: {user_id: {"tool_name": ..., "args": ..., "summary": ...}}
        self._pending_confirmations: Dict[int, Dict[str, Any]] = {}
        # Quản lý vòng đời hành động đối thoại: AWAITING_PARAM và CONFIRMING
        self._pending_actions: Dict[int, Dict[str, Any]] = {}
        # Lưu trữ công cụ thực thi gần nhất cho từng user để hỗ trợ multi-turn context / follow-up
        self._last_user_tool: Dict[int, Dict[str, Any]] = {}
        # Quản lý Action Context và Entity Resolution chuyên sâu xuyên suốt phiên đối thoại
        self._last_action: Dict[int, ActionRecord] = {}
        self._action_history: Dict[int, List[ActionRecord]] = {}
        self._last_entity_by_type: Dict[int, Dict[str, ActionRecord]] = {}
        # Lưu trữ thực thể đang active theo loại (wallet, category, debt, transaction, budget) để hỗ trợ tham chiếu đại từ ('nó', 'cái đó', 'khoản đó')
        self._active_entities: Dict[int, Dict[str, Any]] = {}
        self.current_state: AgentState = AgentState.IDLE

    def get_pending_confirmation(self, user_id: int) -> Optional[Dict[str, Any]]:
        action = self._pending_actions.get(user_id)
        if action and action.get("status") == "CONFIRMING":
            return action
        return self._pending_confirmations.get(user_id)

    def get_pending_action(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self._pending_actions.get(user_id) or self._pending_confirmations.get(user_id)

    def set_pending_action(self, user_id: int, action: Dict[str, Any]):
        self._pending_actions[user_id] = action
        if action.get("status") == "CONFIRMING":
            self._pending_confirmations[user_id] = action
        elif user_id in self._pending_confirmations:
            del self._pending_confirmations[user_id]

    def clear_pending_action(self, user_id: int):
        if user_id in self._pending_actions:
            del self._pending_actions[user_id]
        if user_id in self._pending_confirmations:
            del self._pending_confirmations[user_id]

    def clear_pending_confirmation(self, user_id: int):
        self.clear_pending_action(user_id)

    def get_last_action(self, user_id: int) -> Optional[ActionRecord]:
        """Lấy bản ghi hành động gần nhất của người dùng từ memory context"""
        return self._last_action.get(user_id)

    def get_action_history(self, user_id: int) -> List[ActionRecord]:
        """Lấy toàn bộ lịch sử hành động trong phiên của người dùng"""
        return self._action_history.get(user_id, [])

    def record_successful_action(self, user_id: int, tool: Tool, args: Dict[str, Any], result: ToolResult):
        """Ghi nhận action context sau khi tool thực thi thành công dựa trên kết quả thực tế từ DB"""
        if not result.success:
            return

        res_data = result.data or {}
        tool_name = tool.name
        op_type = tool.operation_type

        entity_type = "unknown"
        entity_id = None
        summary = result.message or ""

        if tool.domain == "transaction":
            entity_type = "transaction"
            if tool_name in ("create_expense", "create_income", "update_transaction"):
                entity_id = res_data.get("transaction_id")
            elif tool_name == "delete_transaction":
                entity_id = res_data.get("deleted_transaction_id")
        elif tool.domain == "wallet":
            if tool_name == "transfer_money":
                entity_type = "transfer"
                entity_id = res_data.get("transfer_id")
            else:
                entity_type = "wallet"
                entity_id = res_data.get("wallet_id") or res_data.get("deleted_wallet_id")
        elif tool.domain == "budget":
            entity_type = "budget"
            entity_id = res_data.get("budget_id") or res_data.get("deleted_budget_id")
        elif tool.domain == "saving_goal":
            entity_type = "saving_goal"
            entity_id = res_data.get("goal_id") or res_data.get("deleted_goal_id")
        elif tool.domain == "debt":
            entity_type = "debt"
            entity_id = res_data.get("debt_id") or res_data.get("settled_debt_id") or res_data.get("deleted_debt_id")
        elif tool.domain == "category":
            entity_type = "category"
            entity_id = res_data.get("category_id") or res_data.get("deleted_category_id")
        elif tool.domain == "recurring":
            entity_type = "recurring"
            entity_id = res_data.get("recurring_id") or res_data.get("deleted_recurring_id")

        merged_data = dict(args)
        merged_data.update(res_data)

        rec = ActionRecord(
            tool_name=tool_name,
            operation=op_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_summary=summary,
            entity_data=merged_data
        )

        self._last_action[user_id] = rec
        self._action_history.setdefault(user_id, []).append(rec)

        if tool_name in ("delete_transaction", "delete_wallet", "delete_budget", "delete_saving_goal", "delete_debt"):
            if user_id in self._last_entity_by_type and entity_type in self._last_entity_by_type[user_id]:
                self._last_entity_by_type[user_id][entity_type].entity_data["deleted"] = True
            for past_rec in self._action_history.get(user_id, []):
                if past_rec.entity_type == entity_type and past_rec.entity_id == entity_id:
                    past_rec.entity_data["deleted"] = True
        else:
            self._last_entity_by_type.setdefault(user_id, {})[entity_type] = rec

    async def resolve_contextual_entity(
        self,
        user_id: int,
        entity_type: str,
        query_hint: Optional[str] = None,
        amount: Optional[int] = None,
        date_filter: Optional[str] = None,
        offset: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Phân giải thực thể từ conversational action context hoặc truy vấn DB an toàn.
        Hỗ trợ tham số offset để lấy thực thể kế trước (ví dụ: 'không phải khoản đó, khoản kia' -> offset=1).
        """
        import main

        # 1. Kiểm tra trong memory action history (ưu tiên từ mới nhất đến cũ nhất)
        user_history = self._action_history.get(user_id, [])
        matching_recs = []
        for rec in reversed(user_history):
            if rec.entity_type == entity_type and rec.entity_id and not rec.entity_data.get("deleted") and rec.tool_name not in ("delete_transaction", "delete_wallet", "delete_budget", "delete_saving_goal", "delete_debt"):
                # Nếu có yêu cầu khớp số tiền cụ thể
                if amount is not None and amount > 0:
                    rec_amt = rec.entity_data.get("amount") or rec.entity_data.get("limit_amount") or rec.entity_data.get("target_amount")
                    if rec_amt and int(float(rec_amt)) != int(amount):
                        continue
                matching_recs.append(rec)

        if len(matching_recs) > offset:
            rec = matching_recs[offset]
            # Xác minh thực thể vẫn còn tồn tại trong DB (không bị xóa bởi tác vụ khác)
            with main.get_db() as conn:
                if entity_type == "transaction":
                    row = conn.execute("SELECT id, amount, note, wallet_id, category_id, transaction_date FROM transactions WHERE id = ? AND user_id = ?", (rec.entity_id, user_id)).fetchone()
                    if row:
                        return {
                            "id": row["id"],
                            "amount": row["amount"],
                            "note": row["note"],
                            "wallet_name": rec.entity_data.get("wallet_name"),
                            "category_name": rec.entity_data.get("category_name"),
                            "raw_data": rec.entity_data
                        }
                elif entity_type == "wallet":
                    row = conn.execute("SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE id = ? AND user_id = ?", (rec.entity_id, user_id)).fetchone()
                    if row:
                        return dict(row)
                elif entity_type == "saving_goal":
                    row = conn.execute("SELECT id, target_name, target_amount, current_amount FROM saving_goals WHERE id = ? AND user_id = ?", (rec.entity_id, user_id)).fetchone()
                    if row:
                        return dict(row)
                elif entity_type == "budget":
                    row = conn.execute("SELECT id, limit_amount, month_year, category_id FROM budgets WHERE id = ? AND user_id = ?", (rec.entity_id, user_id)).fetchone()
                    if row:
                        return dict(row)
                elif entity_type == "debt":
                    row = conn.execute("SELECT id, person_name, amount, debt_type, is_settled FROM debts WHERE id = ? AND user_id = ? AND is_settled = 0", (rec.entity_id, user_id)).fetchone()
                    if row:
                        return dict(row)

        # 2. Nếu không tìm thấy trong memory context (ví dụ session mới hoặc server reload), truy vấn DB
        with main.get_db() as conn:
            if entity_type == "transaction":
                query = """
                    SELECT t.id, t.amount, t.note, t.transaction_date, t.wallet_id, t.category_id,
                           w.wallet_name, c.category_name
                    FROM transactions t
                    LEFT JOIN wallets w ON t.wallet_id = w.id
                    LEFT JOIN categories c ON t.category_id = c.id
                    WHERE t.user_id = ?
                """
                params = [user_id]
                if amount is not None and amount > 0:
                    query += " AND t.amount = ?"
                    params.append(amount)
                if date_filter:
                    query += " AND t.transaction_date = ?"
                    params.append(date_filter)

                query += f" ORDER BY t.id DESC LIMIT 1 OFFSET {offset}"
                row = conn.execute(query, tuple(params)).fetchone()
                if row:
                    return dict(row)

            elif entity_type == "wallet":
                row = conn.execute(
                    f"SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE user_id = ? ORDER BY id DESC LIMIT 1 OFFSET {offset}",
                    (user_id,)
                ).fetchone()
                if row:
                    return dict(row)

            elif entity_type == "budget":
                row = conn.execute(f"""
                    SELECT b.id, b.limit_amount, b.month_year, c.category_name
                    FROM budgets b
                    LEFT JOIN categories c ON b.category_id = c.id
                    WHERE b.user_id = ? ORDER BY b.id DESC LIMIT 1 OFFSET {offset}
                """, (user_id,)).fetchone()
                if row:
                    return dict(row)

            elif entity_type == "saving_goal":
                row = conn.execute(
                    f"SELECT id, target_name, target_amount, current_amount FROM saving_goals WHERE user_id = ? ORDER BY id DESC LIMIT 1 OFFSET {offset}",
                    (user_id,)
                ).fetchone()
                if row:
                    return dict(row)

            elif entity_type == "debt":
                row = conn.execute(
                    f"SELECT id, person_name, amount, debt_type, is_settled FROM debts WHERE user_id = ? AND is_settled = 0 ORDER BY id DESC LIMIT 1 OFFSET {offset}",
                    (user_id,)
                ).fetchone()
                if row:
                    return dict(row)

    def _is_mutation_command(self, message: str) -> bool:
        """Kiểm tra xem thông điệp có phải là một mệnh lệnh thay đổi dữ liệu tài chính (Mutation Command) không.
        Phân biệt rõ ràng giữa câu hỏi tra cứu/hướng dẫn (Inquiry) và mệnh lệnh thực thi trực tiếp (Command).
        """
        raw = message.lower().strip()
        raw_unacc = remove_accents(raw)

        # 1. Các từ khóa thể hiện câu hỏi tra cứu, quy trình, giải thích, quyền hạn (Inquiry Markers)
        # Nếu có các từ này, chắc chắn KHÔNG phải là direct mutation command
        inquiry_markers = [
            "làm sao", "lam sao", "cách nào", "cach nao", "làm thế nào", "lam the nao",
            "như thế nào", "nhu the nao", "hướng dẫn", "huong dan", "chỉ cách", "chi cach",
            "có thể tự", "co the tu", "có quyền", "co quyen", "được phép", "duoc phep",
            "có được tự", "co duoc tu", "có được", "co duoc", "được tự", "duoc tu",
            "có được phép", "co duoc phep", "có tự", "co tu", "tự thêm", "tu them",
            "giải thích", "giai thich", "là gì", "la gi", "có chức năng", "co chuc nang",
            "có tính năng", "co tinh nang", "hỗ trợ không", "ho tro khong", "dùng để làm gì",
            "tại sao", "tai sao", "quy trình", "quy trinh", "bước nào", "buoc nao",
            "hoạt động thế nào", "hoat dong the nao", "hoạt động ra sao", "hoat dong ra sao",
            "vận hành thế nào", "van hanh the nao", "vận hành ra sao", "van hanh ra sao",
            "hoạt động sao", "xài thế nào", "xai the nao", "dùng thế nào", "dung the nao",
            "có được không", "co duoc khong", "được không", "duoc khong",
            "chức năng nào", "chuc nang nao", "dùng chức năng", "dung chuc nang",
            "phân hệ nào", "phan he nao", "tab nào", "tab nao", "ở đâu", "o dau",
            "mần răng", "man rang", "mần sao", "man sao", "mần thế nào", "man the nao", "mần kiểu chi", "man kieu chi",
            "mần ăn ra sao", "man an ra sao", "được hem", "duoc hem", "được ko", "duoc ko", "được hông", "duoc hong",
            "có tự ý", "co tu y", "tự ý", "tu y"
        ]
        if any(marker in raw or marker in raw_unacc for marker in inquiry_markers):
            return False

        # 2. Kiểm tra các mệnh lệnh tạo ví
        if VietnameseFinancialParser.is_wallet_create_intent(message):
            return True

        # 3. Kiểm tra các mệnh lệnh xóa / hủy thực thể
        has_destructive_verb = any(re.search(rf"\b{re.escape(w)}\b", raw) for w in ["xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo", "xóa bỏ", "xoa bo"])
        if has_destructive_verb:
            return True

        # 4. Kiểm tra các mệnh lệnh cập nhật / sửa đổi thực thể
        has_update_verb = any(re.search(rf"\b{re.escape(w)}\b", raw) for w in ["sửa", "sua", "đổi", "doi", "cập nhật", "cap nhat", "chỉnh", "chinh", "thay đổi", "thay doi"])
        if has_update_verb:
            return True

        # 5. Kiểm tra các mệnh lệnh chi tiêu hoặc thu nhập có số tiền
        amt = VietnameseFinancialParser.parse_amount(message)
        expense_verbs = ["ăn", "an", "uống", "uong", "hết", "het", "mua", "chi", "tiêu", "tieu", "đổ xăng", "do xang", "trả tiền", "tra tien", "đóng tiền", "dong tien", "thanh toán", "thanh toan"]
        is_expense_trigger = any(re.search(rf"\b{re.escape(kw)}\b", raw) for kw in expense_verbs)
        is_income_trigger = any(re.search(rf"\b{re.escape(kw)}\b", raw) for kw in ["thu", "nhận", "lương", "thưởng", "được cho", "được tặng", "bán"])
        is_read_query = any(q in raw for q in ["bao nhiêu", "bao nhieu", "thế nào", "the nao", "ra sao", "mấy", "may", "lịch sử", "lich su", "xem", "tra cứu", "tra cuu", "tìm", "tim"])

        if amt is not None and (is_expense_trigger or is_income_trigger) and not is_read_query:
            return True

        # 6. Kiểm tra các mệnh lệnh chuyển tiền
        if any(kw in raw for kw in ["chuyển", "chuyen"]) and not any(kw in raw for kw in ["chuyển sang tab", "chuyển tab", "chuyển trang"]):
            from_w, to_w = VietnameseFinancialParser.extract_transfer_wallets(message)
            if amt or from_w or to_w:
                return True

        # 7. Kiểm tra các mệnh lệnh về nợ
        if (
            VietnameseFinancialParser.is_debt_create_intent(message)
            or VietnameseFinancialParser.is_debt_delete_intent(message)
            or VietnameseFinancialParser.is_debt_settle_intent(message)
            or any(kw in raw for kw in ["quyết toán nợ", "quyet toan no", "đã trả nợ", "da tra no", "đã thu nợ", "da thu no", "trả hết nợ", "tất toán nợ", "xóa nợ", "xoa no", "xóa khoản nợ"])
        ):
            return True

        # 8. Kiểm tra các mệnh lệnh mục tiêu tiết kiệm
        if VietnameseFinancialParser.is_saving_goal_create_intent(message):
            return True
        if any(kw in raw for kw in ["nạp", "nap", "đưa", "dua", "gửi", "gui", "thêm", "them", "rút", "rut", "lấy", "lay"]) and any(kw in raw for kw in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy", "tich luy"]):
            if amt:
                return True

        # 9. Kiểm tra các mệnh lệnh ngân sách
        if (
            VietnameseFinancialParser.is_budget_write(message)
            or VietnameseFinancialParser.is_budget_create_intent(message)
            or VietnameseFinancialParser.is_budget_delete_intent(message)
            or VietnameseFinancialParser.is_budget_update_intent(message)
        ):
            return True

        # 10. Mệnh lệnh danh mục
        if any(kw in raw for kw in ["thêm danh mục", "tạo danh mục", "mở danh mục"]):
            return True

        # 11. Mệnh lệnh định kỳ
        if any(kw in raw for kw in ["đặt định kỳ", "tạo giao dịch định kỳ", "thêm giao dịch định kỳ", "cài giao dịch định kỳ", "hàng tháng đóng", "hàng tuần đóng", "mỗi tháng tự động", "mỗi tuần tự động"]):
            return True

        return False

    def _is_combined_query(self, message: str) -> Tuple[bool, Optional[str]]:
        """Kiểm tra xem câu hỏi có kết hợp giữa tra cứu Tri thức Hệ thống và Dữ liệu Cá nhân Read-Only không.
        Ví dụ:
        - "Hệ thống có ngân sách không và ngân sách ăn uống tháng này của ta thế nào?"
        - "Trong hệ thống có mục tiêu tiết kiệm không và mục tiêu của ta hiện tại thế nào?"
        - "Hệ thống có ví không và tôi hiện có bao nhiêu tiền?"
        """
        raw = message.lower().strip()
        raw_unacc = remove_accents(raw)

        # Cần có cả 2 vế:
        # Vế 1: Hỏi về tính năng hệ thống
        has_sys = any(kw in raw or kw in raw_unacc for kw in [
            "hệ thống có", "he thong co", "trong hệ thống có", "trong he thong co",
            "có chức năng", "co chuc nang", "có tính năng", "co tinh nang",
            "hỗ trợ không", "ho tro khong", "có hỗ trợ", "co ho tro",
            "là gì", "la gi", "dùng để làm gì", "dung de lam gi"
        ])

        # Vế 2: Hỏi về dữ liệu cá nhân của người dùng
        has_personal = any(kw in raw or kw in raw_unacc for kw in [
            "của tôi", "cua toi", "của ta", "cua ta", "của mình", "cua minh",
            "tôi hiện có", "toi hien co", "ta hiện có", "ta hien co",
            "tôi có", "toi co", "ta có", "ta co",
            "tôi đang có", "toi dang co", "ta đang có", "ta dang co",
            "tháng này của tôi", "tháng này của ta",
            "của tôi thế nào", "của ta thế nào", "hiện tại thế nào", "hien tai the nao"
        ])

        if not (has_sys and has_personal):
            return False, None

        # Xác định domain dữ liệu cá nhân cần đọc
        if any(kw in raw for kw in ["ngân sách", "ngan sach", "hạn mức", "han muc"]):
            return True, "budget"
        if any(kw in raw for kw in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy"]):
            return True, "saving_goal"
        if any(kw in raw for kw in ["sổ nợ", "so no", "khoản nợ", "khoan no"]) or ("nợ" in raw and not any(w in raw for w in ["nó", "noi"])):
            return True, "debt"
        if any(kw in raw for kw in ["ví", "vi", "túi càn khôn", "bao nhiêu tiền", "số dư"]):
            return True, "wallet"

        return True, "overview"

    async def _handle_combined_query(
        self,
        user_id: int,
        message: str,
        domain: str,
        recent_history: str = "",
        user_role: str = "user"
    ) -> AgentResponse:
        """Xử lý câu hỏi kết hợp: RAG Tra cứu Kiến thức Hệ thống + Read-Only Personal Data"""
        # 1. RAG knowledge query
        rag_answer, rag_meta = await self.rag.answer_question(message, provider=self.provider, recent_history=recent_history)

        # 2. Read-only personal data query (đảm bảo truyền mode=AgentMode.KNOWLEDGE)
        cat = VietnameseFinancialParser.guess_category(message)
        tool_name = "financial_overview"
        tool_args: Dict[str, Any] = {}

        if domain == "budget":
            tool_name = "budget_status"
            if cat:
                tool_args["category_name"] = cat
        elif domain == "saving_goal":
            tool_name = "saving_goal_status"
            goal = VietnameseFinancialParser.extract_goal_name(message)
            if goal:
                tool_args["goal_name"] = goal
        elif domain == "wallet":
            tool_name = "get_wallets"
            w_name = VietnameseFinancialParser.extract_wallet_name(message)
            if w_name:
                tool_args["wallet_name"] = w_name
        elif domain == "debt":
            tool_name = "debt_status"
            p_name = VietnameseFinancialParser.extract_person_name(message)
            if p_name:
                tool_args["person_name"] = p_name
        else:
            tool_name = "financial_overview"
            tool_args["period"] = "this_month"

        tool_res = await self.registry.execute(tool_name, user_id=user_id, user_role=user_role, mode=AgentMode.KNOWLEDGE, **tool_args)

        # 3. Kết hợp 2 nguồn câu trả lời thành văn phong thống nhất
        prompt = f"""Bạn là "Khí Linh AI Lớn" — Trợ Lý Tri Thức kiêm Cố Vấn Toàn Hệ Thống của Càn Khôn Linh Thạch Các.
Người dùng vừa gửi câu hỏi kết hợp giữa KIẾN THỨC VỀ CHỨC NĂNG HỆ THỐNG và DỮ LIỆU CÁ NHÂN READ-ONLY.

Dưới đây là Thông tin tra cứu tri thức hệ thống:
{rag_answer}

Dưới đây là Dữ liệu tài chính thực tế của người dùng từ hệ thống:
{tool_res.message if tool_res.success else "Hiện tại chưa ghi nhận dữ liệu liên quan."}

Hãy kết hợp hai nguồn thông tin trên thành một câu trả lời hoàn chỉnh, mạch lạc, súc tích và chính xác:
- Trả lời rõ câu hỏi về tính năng hệ thống trước.
- Trình bày thông tin dữ liệu thực tế của người dùng ngay sau đó.
- Không thay đổi số liệu thực tế."""
        combined_ans = await self.provider.generate_response(prompt)

        return AgentResponse(
            text=combined_ans.strip(),
            state=AgentState.IDLE,
            tool_executed=tool_name,
            tool_result={
                "personal_data": tool_res.to_dict(),
                "knowledge_trace": rag_meta
            }
        )

    def _is_system_knowledge_query(self, message: str, recent_history: str = "") -> bool:
        """Kiểm tra xem câu hỏi có thuộc phạm vi tri thức hệ thống (System Knowledge) không.
        Bao gồm:
        - Tổng quan chức năng, năng lực hệ thống
        - Giải thích tính năng (Túi Càn Khôn, Giao Dịch, Ngân Sách, Sổ Nợ, Mục Tiêu, OCR...)
        - Hướng dẫn thao tác / quy trình (workflow / user guide)
        - Kiến trúc AI, phân biệt Khí Linh Lớn và Khí Linh Nhỏ
        - Bảo mật, quyền hạn (permission)
        - Tính năng chưa hỗ trợ / ngoại lai (chứng khoán, cổ phiếu, crypto...)
        - Khái niệm công nghệ chung (RAG là gì, Agent là gì...)
        - Follow-up context liên quan đến chức năng hệ thống
        """
        raw = message.lower().strip()
        raw_unacc = remove_accents(raw)

        # 0. Không nhận diện câu hỏi cá nhân chỉ đọc (Personal Read-Only) thuần túy làm câu hỏi tri thức hệ thống
        # Ví dụ: "ta hiện có những ví nào", "tổng tài sản hiện tại của ta là bao nhiêu", "ngân sách ăn uống tháng này của ta thế nào"
        personal_read_markers = [
            "của ta", "cua ta", "của tôi", "cua toi", "của mình", "cua minh",
            "tôi hiện có", "toi hien co", "ta hiện có", "ta hien co",
            "tôi có những", "ta có những", "tôi có mấy", "ta có mấy"
        ]
        is_personal_read = any(p in raw or p in raw_unacc for p in personal_read_markers)
        if is_personal_read:
            # Ngoại trừ trường hợp câu hỏi về quyền hạn của AI đối với tài sản của người dùng
            # Ví dụ: "Khí Linh Lớn có quyền tự chuyển tiền của ta không?"
            is_permission_query = any(k in raw or k in raw_unacc for k in [
                "có quyền", "được phép", "có được", "tự ý", "tự chuyển", "tự thêm", "tự trừ", "được tự"
            ])
            if not is_permission_query:
                return False

        # 1. Các câu hỏi về tri thức khái niệm chung (RAG, Agent, AI)
        if any(re.search(rf"\b{re.escape(w)}\b", raw) for w in ["rag là gì", "rag la gi", "agent là gì", "agent la gi", "rag hoạt động thế nào", "rag"]):
            return True

        # 2. Câu hỏi về năng lực/chức năng toàn hệ thống & khám phá tính năng
        if any(w in raw or w in raw_unacc for w in [
            "hệ thống có những chức năng nào", "he thong co nhung chuc nang nao",
            "chức năng nào", "chuc nang nao", "những chức năng gì", "nhung chuc nang gi",
            "toàn bộ chức năng", "toan bo chuc nang", "các tính năng", "cac tinh nang",
            "hệ thống làm được gì", "he thong lam duoc gi", "càn khôn có gì", "can khon co gi",
            "hệ thống có gì", "he thong co gi", "danh sách tính năng", "danh sach tinh nang",
            "tính năng gì", "tinh nang gi", "dùng chức năng nào", "dung chuc nang nao",
            "dùng tính năng nào", "dung tinh nang nao", "xài tính năng chi", "xai tinh nang chi",
            "dùng công cụ gì", "dung cong cu gi", "dùng cái gì", "dung cai gi", "xài cái gì", "xai cai gi",
            "mần chi", "man chi", "ra răng", "ra rang", "xài kiểu chi", "xai kieu chi"
        ]):
            return True

        # 3. Câu hỏi về tính năng ngoại lai / chưa hỗ trợ
        if any(w in raw or w in raw_unacc for w in [
            "cổ phiếu", "chứng khoán", "chay cổ phiếu", "đầu tư cổ phiếu",
            "crypto", "tiền mã hóa", "tiền mã hoá", "tiền ảo", "bitcoin", "blockchain",
            "giao dịch tự động", "giao dich tu dong", "đầu tư vàng", "ngoại hối", "forex"
        ]):
            return True

        # 4. Câu hỏi về phân quyền, bảo mật hoặc Khí Linh
        if any(w in raw or w in raw_unacc for w in [
            "khí linh ai lớn có thể làm gì", "khi linh ai lon co the lam gi",
            "khí linh ai lớn", "khi linh ai lon", "khí linh nhỏ", "khi linh nho",
            "khí linh có thể tự", "khi linh co the tu", "ai có quyền", "ai co quyen",
            "tự thêm ví", "tu them vi", "tự chuyển tiền", "tu chuyen tien", "có được tự", "co duoc tu",
            "phân biệt khí linh", "phan biet khi linh", "vai trò của khí linh", "vai tro cua khi linh",
            "khác khí linh", "khac khi linh", "khác nhau thế nào",
            "bảo mật", "bao mat", "quyền hạn", "quyen han", "hồn đăng", "hon dang",
            "chưởng môn các", "chuong mon cac", "phân quyền", "phan quyen"
        ]):
            return True

        # 5. Câu hỏi cơ chế hoạt động của tính năng ("hoạt động thế nào", "hoạt động ra sao", "vận hành ra sao"...)
        if any(w in raw or w in raw_unacc for w in [
            "hoạt động thế nào", "hoat dong the nao", "hoạt động ra sao", "hoat dong ra sao",
            "hoạt động sao", "hoat dong sao", "vận hành thế nào", "van hanh the nao",
            "vận hành ra sao", "van hanh ra sao"
        ]):
            return True

        # 6. Câu hỏi khả năng "Có thể ... không?", "Có được ... không?", "Hệ thống có ... không?"
        has_modal_question = any(w in raw or w in raw_unacc for w in [
            "có thể", "co the", "có được", "co duoc", "hệ thống có", "he thong co",
            "trong hệ thống có", "có hỗ trợ", "co ho tro", "quản lý nhiều", "quan ly nhieu"
        ])
        has_question_tail = any(w in raw or w in raw_unacc for w in [
            "không", "khong", "hông", "hong", "được không", "duoc khong", "được hông", "duoc hong"
        ])
        if has_modal_question and has_question_tail:
            return True

        # 7. Câu hỏi hướng dẫn, cách làm, workflow
        if any(w in raw or w in raw_unacc for w in [
            "làm sao để tạo một ví", "lam sao de tao mot vi", "làm sao để tạo ví", "lam sao de tao vi",
            "cách tạo ví", "cach tao vi", "hướng dẫn tạo ví", "huong dan tao vi",
            "làm sao", "lam sao", "cách nào", "cach nao", "hướng dẫn", "huong dan",
            "quy trình", "quy trinh", "như thế nào", "nhu the nao",
            "dùng để làm gì", "dung de lam gi", "dùng làm gì", "dung lam gi",
            "quản lý những gì", "quan ly nhung gi", "giải thích", "giai thich",
            "quét hóa đơn", "quet hoa don", "khám hóa đơn"
        ]):
            # Kiểm tra xem có phải hỏi về tính năng hệ thống không
            feature_keywords = [
                "túi càn khôn", "tui can khon", "ví", "vi", "giao dịch", "giao dich",
                "ngân sách", "ngan sach", "hạn mức", "han muc", "mục tiêu", "muc tieu",
                "tiết kiệm", "tiet kiem", "sổ nợ", "so no", "nợ", "no", "ocr", "hóa đơn", "hoa don",
                "báo cáo", "bao cao", "thống kê", "thong ke", "hệ thống", "he thong", "khí linh", "khi linh",
                "chuyển tiền", "chuyen tien", "ngân hàng", "ngan hang", "tài khoản", "tai khoan"
            ]
            if any(f in raw or f in raw_unacc for f in feature_keywords):
                return True

        # 8. Follow-up context queries
        followup_phrases = [
            "giải thích kỹ hơn", "giai thich ky hon", "nói rõ hơn", "noi ro hon",
            "còn cái này", "con cai nay", "nó có thể làm gì", "no co the lam gi",
            "còn ngân sách", "con ngan sach", "còn mục tiêu", "con muc tieu",
            "còn sổ nợ", "con so no", "còn túi càn khôn", "con tui can khon",
            "túi càn khôn thì sao", "tui can khon thi sao", "ngân sách thì sao", "ngan sach thi sao",
            "cái này hoạt động thế nào", "cai nay hoat dong the nao", "nó hoạt động thế nào", "cái này dùng thế nào",
            "cái này hoạt động ra sao"
        ]
        if any(p in raw or p in raw_unacc for p in followup_phrases):
            return True

        # 9. Tên tính năng đứng một mình hoặc kèm câu hỏi trực tiếp
        if raw in [
            "túi càn khôn", "tui can khon", "hạn mức ngân sách", "mục tiêu tiết kiệm", "sổ nợ",
            "ocr hóa đơn", "giao dịch định kỳ", "linh trận định kỳ", "khai thị tiết kiệm"
        ]:
            return True

        return False

    def _is_pure_personal_read_query(self, message: str) -> bool:
        """Kiểm tra xem câu hỏi có phải là câu hỏi tra cứu dữ liệu cá nhân thuần túy (Read-Only) không.
        Ví dụ: 'ta hiện có những ví nào', 'ngân sách ăn uống tháng này của ta thế nào',
               'tổng số dư tài sản hiện tại của ta là bao nhiêu', 'tháng này ta đã chi tiêu bao nhiêu tiền'.
        """
        raw = message.lower().strip()
        raw_unacc = remove_accents(raw)

        # 1. Nếu là câu hỏi về quyền hạn của AI đối với tài sản của người dùng -> Phải đưa vào RAG tri thức / permission
        permission_keywords = [
            "có quyền", "co quyen", "được phép", "duoc phep", "có được", "co duoc",
            "tự ý", "tu y", "tự chuyển", "tu chuyen", "tự thêm", "tu them", "tự trừ", "tu tru",
            "được tự", "duoc tu", "tự xóa", "tu xoa", "được hem", "duoc hem"
        ]
        if any(k in raw or k in raw_unacc for k in permission_keywords):
            return False

        # 2. Nếu là câu hỏi về hướng dẫn thao tác, workflow, giải thích khái niệm
        inquiry_verbs = [
            "làm sao", "lam sao", "làm thế nào", "lam the nao", "cách nào", "cach nao",
            "như thế nào", "nhu the nao", "hoạt động ra sao", "hoat dong ra sao", "hoạt động thế nào",
            "mần răng", "man rang", "mần sao", "man sao", "dùng để làm gì", "dung de lam gi"
        ]
        if any(v in raw or v in raw_unacc for v in inquiry_verbs):
            return False

        # 3. Các dấu hiệu nhận diện câu hỏi đọc dữ liệu cá nhân
        personal_markers = [
            "của ta", "cua ta", "của tôi", "cua toi", "của mình", "cua minh",
            "tôi hiện có", "toi hien co", "ta hiện có", "ta hien co",
            "tôi có những", "ta có những", "tôi có mấy", "ta có mấy",
            "tổng tài sản hiện tại", "tong tai san hien tai",
            "tổng số dư", "tong so du",
            "tháng này ta đã", "thang nay ta da", "tháng này tôi đã", "thang nay toi da",
            "tháng này chi tiêu", "thang nay chi tieu", "đã chi tiêu bao nhiêu", "da chi tieu bao nhieu"
        ]
        return any(p in raw or p in raw_unacc for p in personal_markers)

    def _detect_multi_tool_intent(self, message: str) -> Optional[str]:
        """Phát hiện dạng câu hỏi đa ý định (Multi-intent / Composite Query / Analytical Reasoning)"""
        raw = message.lower().strip()
        raw_unacc = remove_accents(raw)

        # 0. Câu điều kiện ('nếu... thì...')
        is_cond, cond_type = VietnameseFinancialParser.is_conditional_statement(message)
        if is_cond:
            if cond_type == "mixed_write":
                return "conditional_mixed_write"
            return "conditional_read_only"

        # 1. Tổng quan chi tiêu kết hợp trạng thái ngân sách ('Xem tháng này tiêu bao nhiêu và khoản nào vượt hạn mức')
        has_spent = any(k in raw or k in raw_unacc for k in ["tieu bao nhieu", "chi bao nhieu", "da chi", "da tieu", "tong chi", "tong tieu", "tiêu bao nhiêu", "chi bao nhiêu", "ta tiêu", "ta chi"])
        has_budget = any(k in raw or k in raw_unacc for k in ["vuot han muc", "vuot ngan sach", "han muc nao", "ngan sach nao", "vượt hạn mức", "vượt ngân sách", "khoản nào vượt", "khoan nao vuot", "khoản nào đang vượt"])
        if has_spent and has_budget:
            return "spent_and_budget"

        # 2. Kiểm tra ví và chi tiêu qua ví đó ('Kiểm tra ví MoMo rồi cho ta biết tháng này ta tiêu qua ví đó bao nhiêu')
        has_wallet_ref = any(k in raw or k in raw_unacc for k in ["ví momo", "vi momo", "ví tiền mặt", "vi tien mat", "ví vcb", "ví vietcombank", "ví đó", "vi do", "túi đó", "tui do", "qua ví", "qua vi"]) or ("ví" in raw and any(k in raw for k in ["momo", "tiền mặt", "tien mat", "vietcombank", "vcb"]))
        has_wallet_spending = any(k in raw or k in raw_unacc for k in ["tiêu qua", "tieu qua", "chi qua", "tiêu từ", "tieu tu", "chi từ", "chi tu", "tiêu qua ví đó", "tieu qua vi do", "chi qua ví đó"]) or (has_wallet_ref and has_spent)
        if has_wallet_ref and has_wallet_spending:
            return "wallet_and_spending"

        # 3. Xem danh sách nợ kết hợp khoản sắp đến hạn ('Xem các khoản nợ của ta và cho biết khoản nào sắp đến hạn')
        has_debt = any(k in raw or k in raw_unacc for k in ["khoản nợ", "khoan no", "sổ nợ", "so no", "các khoản nợ", "cac khoan no", "nợ của ta", "no cua ta"])
        has_due = any(k in raw or k in raw_unacc for k in ["sắp đến hạn", "sap den han", "đến hạn", "den han", "sắp tới hạn", "sap toi han", "đến ngày", "den ngay"])
        if has_debt and has_due:
            return "debts_and_due_dates"

        # 4. So sánh tháng này với tháng trước ('Tháng này so với tháng trước ra sao?', 'Khoản nào tăng mạnh nhất so với tháng trước?')
        if any(k in raw or k in raw_unacc for k in ["so với tháng trước", "so voi thang truoc", "so sánh tháng này", "so sanh thang nay", "khoản nào tăng mạnh nhất", "khoan nao tang manh nhat"]):
            return "month_comparison"

        # 5. Phân tích ví có số dư lớn nhất ('Ví nào đang có nhiều tiền nhất?', 'Ví nào nhiều tiền nhất?')
        if any(k in raw or k in raw_unacc for k in ["nhiều tiền nhất", "nhieu tien nhat", "lớn nhất", "lon nhat", "nhiều nhất", "nhieu nhat", "giàu nhất"]) and any(k in raw or k in raw_unacc for k in ["ví nào", "vi nao", "túi nào", "tui nao"]):
            return "max_wallet"

        # 6. Phân tích danh mục chi nhiều nhất / khoản chi lớn nhất ('Ta tiêu nhiều nhất vào đâu?', 'Khoản chi lớn nhất?')
        if any(k in raw or k in raw_unacc for k in ["tiêu nhiều nhất vào đâu", "tieu nhieu nhat vao dau", "chi nhiều nhất vào đâu", "chi nhieu nhat vao dau", "tiêu nhiều nhất cho", "khoản chi lớn nhất", "khoan chi lon nhat"]):
            return "top_spending_category"

        # 7. Phân tích thặng dư tích lũy / tiết kiệm ('Tháng này ta tiết kiệm được bao nhiêu?')
        if any(k in raw or k in raw_unacc for k in ["tiết kiệm được bao nhiêu", "tiet kiem duoc bao nhieu", "để dành được bao nhiêu", "de danh duoc bao nhieu", "dư được bao nhiêu", "du duoc bao nhieu"]):
            return "net_savings"

        # 8. Phát hiện chi tiêu bất thường ('Có khoản nào bất thường không?', 'Khoản chi nào bất thường?')
        if any(k in raw or k in raw_unacc for k in ["bất thường", "bat thuong", "khoản chi nào bất thường", "khoản nào bất thường"]):
            return "abnormal_spending"

        return None

    def _is_multi_tool_read_query(self, message: str) -> bool:
        """Kiểm tra xem câu hỏi có kết hợp nhiều nhu cầu tra cứu dữ liệu cá nhân cần phối hợp công cụ (Multi-tool Planning) không."""
        return self._detect_multi_tool_intent(message) is not None

    async def _handle_multi_tool_read_query(
        self,
        user_id: int,
        message: str,
        user_name: str = "Ký Chủ",
        user_role: str = "user"
    ) -> AgentResponse:
        """Thực thi kế hoạch đa công cụ đọc dữ liệu tài chính (Multi-Tool Execution & Synthesis)"""
        sub_intent = self._detect_multi_tool_intent(message)
        raw = message.lower().strip()
        period = VietnameseFinancialParser.parse_period(message) or "this_month"

        # ─────────────────────────────────────────────────────────────
        # 1. SPENT AND BUDGET STATUS
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "spent_and_budget":
            overview_res = await self.registry.execute("financial_overview", user_id=user_id, user_role=user_role, period=period)
            budget_res = await self.registry.execute("budget_status", user_id=user_id, user_role=user_role, month_year=period)

            # Failure recovery check:
            if not overview_res.success and not budget_res.success:
                self.current_state = AgentState.ERROR
                return AgentResponse(
                    text=f"❌ Không thể tra cứu dữ liệu tài chính: {overview_res.error or budget_res.error}.",
                    state=self.current_state
                )

            ov_data = overview_res.data or {}
            total_spent = ov_data.get("expense", 0)
            bg_data = budget_res.data or {}
            budgets = bg_data.get("budgets", [])
            exceeded = [b for b in budgets if b.get("is_exceeded")]

            period_title = "tháng này" if period == "this_month" else f"kỳ {period}"
            spent_msg = f"📊 Trong {period_title}, {user_name} đã chi tổng cộng {total_spent:,.0f} VNĐ."
            if exceeded:
                exc_details = ", ".join(f"'{b['category_name']}' (Đã chi {b['spent']:,.0f}/{b['limit_amount']:,.0f} VNĐ, vượt {b['percent']}%)" for b in exceeded)
                budget_msg = f"⚠️ Các danh mục đang vượt hạn mức: {exc_details}."
            elif budgets:
                budget_msg = f"✅ Tất cả {len(budgets)} danh mục đã thiết lập hạn mức đều đang được kiểm soát tốt, chưa có khoản nào vượt ngưỡng!"
            else:
                budget_msg = f"ℹ️ {user_name} chưa thiết lập hạn mức chi tiêu nào trong {period_title}."

            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=f"{spent_msg}\n{budget_msg}",
                state=self.current_state,
                tool_executed="financial_overview+budget_status",
                tool_result={"financial_overview": ov_data, "budget_status": bg_data}
            )

        # ─────────────────────────────────────────────────────────────
        # 2. WALLET AND SPENDING (e.g. 'Kiểm tra ví MoMo rồi cho ta biết tháng này ta tiêu qua ví đó bao nhiêu')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "wallet_and_spending":
            w_name = VietnameseFinancialParser.extract_wallet_name(message)
            if not w_name:
                active_w = self._active_entities.get(user_id, {}).get("wallet")
                if active_w and active_w.get("name"):
                    w_name = active_w["name"]
                elif "momo" in raw:
                    w_name = "MoMo"
                elif "tiền mặt" in raw or "tien mat" in raw:
                    w_name = "Tiền Mặt"
                elif "vietcombank" in raw or "vcb" in raw:
                    w_name = "Vietcombank"

            # Step 1: Tra cứu ví
            w_res = await self.registry.execute("get_wallets", user_id=user_id, user_role=user_role, wallet_name=w_name)
            if not w_res.success:
                self.current_state = AgentState.ERROR
                return AgentResponse(
                    text=f"❌ Không thể tra cứu ví '{w_name}': {w_res.error}.",
                    state=self.current_state
                )

            wallets = w_res.data.get("wallets", [])
            if not wallets:
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=f"Khí Linh không tìm thấy ví '{w_name}' trong Càn Khôn Các của {user_name}.",
                    state=self.current_state
                )

            target_w = wallets[0]
            w_balance = target_w.get("balance", 0)
            actual_w_name = target_w.get("wallet_name", w_name)
            self._active_entities.setdefault(user_id, {})["wallet"] = {"name": actual_w_name, "id": target_w.get("id")}

            # Step 2: Tra cứu chi tiêu qua ví này
            tx_res = await self.registry.execute("transaction_search", user_id=user_id, user_role=user_role, wallet_name=actual_w_name, time_frame=period, transaction_type="expense")
            if not tx_res.success:
                # Partial success reporting!
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=f"💳 Ví '{actual_w_name}' hiện có số dư là {w_balance:,.0f} VNĐ. Tuy nhiên bước tra cứu chi tiêu gặp trục trặc: {tx_res.error}.",
                    state=self.current_state,
                    tool_executed="get_wallets",
                    tool_result={"wallet": target_w}
                )

            tx_data = tx_res.data or {}
            transactions = tx_data.get("transactions", [])
            total_spent = sum(t.get("amount", 0) for t in transactions)
            tx_count = len(transactions)

            period_desc = "tháng này" if period == "this_month" else f"kỳ {period}"
            reply_text = (
                f"💳 Ví '{actual_w_name}' hiện có số dư là {w_balance:,.0f} VNĐ.\n"
                f"📊 Trong {period_desc}, {user_name} đã thực hiện {tx_count} khoản chi qua ví này với tổng số tiền là {total_spent:,.0f} VNĐ."
            )
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=reply_text,
                state=self.current_state,
                tool_executed="get_wallets+transaction_search",
                tool_result={"wallet": target_w, "spending": {"total_spent": total_spent, "count": tx_count, "transactions": transactions}}
            )

        # ─────────────────────────────────────────────────────────────
        # 3. DEBTS AND UPCOMING DUE DATES (e.g. 'Xem các khoản nợ của ta và cho biết khoản nào sắp đến hạn')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "debts_and_due_dates":
            debt_res = await self.registry.execute("debt_list", user_id=user_id, user_role=user_role)
            if not debt_res.success:
                self.current_state = AgentState.ERROR
                return AgentResponse(
                    text=f"❌ Không thể tra cứu sổ nợ: {debt_res.error}.",
                    state=self.current_state
                )

            debts = debt_res.data.get("debts", [])
            unsettled = [d for d in debts if not d.get("is_settled")]

            today = datetime.date.today()
            upcoming = []
            overdue = []
            for d in unsettled:
                due_str = d.get("due_date")
                if due_str:
                    try:
                        due_d = datetime.date.fromisoformat(due_str.split("T")[0])
                        diff = (due_d - today).days
                        if diff < 0:
                            overdue.append((d, abs(diff)))
                        elif 0 <= diff <= 7:
                            upcoming.append((d, diff))
                    except Exception:
                        pass

            payable = sum(d.get("amount", 0) for d in unsettled if d.get("debt_type") in ("payable", "BORROW"))
            receivable = sum(d.get("amount", 0) for d in unsettled if d.get("debt_type") in ("receivable", "LEND"))

            lines = [f"📜 Sổ nợ hiện có {len(unsettled)} khoản chưa tất toán (Cần thu: {receivable:,.0f} VNĐ | Cần trả: {payable:,.0f} VNĐ)."]
            if overdue:
                o_str = ", ".join(f"'{d['person_name']}' ({d['amount']:,.0f} VNĐ, quá hạn {days} ngày)" for d, days in overdue)
                lines.append(f"🚨 Các khoản nợ đã quá hạn: {o_str}.")
            if upcoming:
                u_str = ", ".join(f"'{d['person_name']}' ({d['amount']:,.0f} VNĐ, còn {days} ngày)" for d, days in upcoming)
                lines.append(f"⚠️ Các khoản nợ sắp đến hạn trong 7 ngày tới: {u_str}.")
            elif not overdue:
                lines.append(f"✅ Hiện tại không có khoản nợ nào sắp đến hạn trong vòng 7 ngày tới.")

            self.current_state = AgentState.IDLE
            return AgentResponse(
                text="\n".join(lines),
                state=self.current_state,
                tool_executed="debt_list",
                tool_result={"debts": debts, "upcoming": [d for d, _ in upcoming], "overdue": [d for d, _ in overdue]}
            )

        # ─────────────────────────────────────────────────────────────
        # 4. MONTH COMPARISON (e.g. 'Tháng này so với tháng trước ra sao?')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "month_comparison":
            comp_res = await self.registry.execute("compare_months", user_id=user_id, user_role=user_role)
            if comp_res.success and comp_res.message:
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=comp_res.message,
                    state=self.current_state,
                    tool_executed="compare_months",
                    tool_result=comp_res.data
                )
            # Fallback tính toán từ 2 tháng
            ov_now = await self.registry.execute("financial_overview", user_id=user_id, user_role=user_role, period="this_month")
            ov_prev = await self.registry.execute("financial_overview", user_id=user_id, user_role=user_role, period="last_month")
            now_d = ov_now.data or {}
            prev_d = ov_prev.data or {}
            exp_now = now_d.get("expense", 0)
            exp_prev = prev_d.get("expense", 0)
            diff = exp_now - exp_prev
            diff_pct = (diff / exp_prev * 100) if exp_prev > 0 else 0
            change_txt = f"tăng {diff:,.0f} VNĐ ({diff_pct:.1f}%)" if diff > 0 else f"giảm {abs(diff):,.0f} VNĐ ({abs(diff_pct):.1f}%)" if diff < 0 else "không đổi"
            reply_text = f"📊 Chi tiêu tháng này ({exp_now:,.0f} VNĐ) so với tháng trước ({exp_prev:,.0f} VNĐ) đã {change_txt}."
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=reply_text,
                state=self.current_state,
                tool_executed="financial_overview_compare",
                tool_result={"this_month": now_d, "last_month": prev_d}
            )

        # ─────────────────────────────────────────────────────────────
        # 5. MAX WALLET (e.g. 'Ví nào đang có nhiều tiền nhất?')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "max_wallet":
            w_res = await self.registry.execute("get_wallets", user_id=user_id, user_role=user_role)
            wallets = w_res.data.get("wallets", []) if w_res.success else []
            if not wallets:
                self.current_state = AgentState.IDLE
                return AgentResponse(text=f"{user_name} chưa có ví nào trong Càn Khôn Các.", state=self.current_state)

            wallets_sorted = sorted(wallets, key=lambda w: w.get("balance", 0), reverse=True)
            top_w = wallets_sorted[0]
            self._active_entities.setdefault(user_id, {})["wallet"] = {"name": top_w.get("wallet_name"), "id": top_w.get("id")}
            reply_text = f"💰 Ví đang có số dư lớn nhất là '{top_w['wallet_name']}' với {top_w.get('balance', 0):,.0f} VNĐ."
            if len(wallets_sorted) > 1:
                second_w = wallets_sorted[1]
                reply_text += f" (Kế tiếp là '{second_w['wallet_name']}': {second_w.get('balance', 0):,.0f} VNĐ)."
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=reply_text,
                state=self.current_state,
                tool_executed="get_wallets",
                tool_result={"top_wallet": top_w, "wallets": wallets_sorted}
            )

        # ─────────────────────────────────────────────────────────────
        # 6. TOP SPENDING CATEGORY (e.g. 'Ta tiêu nhiều nhất vào đâu?')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "top_spending_category":
            cat_res = await self.registry.execute("spending_by_category", user_id=user_id, user_role=user_role, period=period)
            categories = cat_res.data.get("categories", []) if cat_res.success else []
            if not categories:
                self.current_state = AgentState.IDLE
                return AgentResponse(text=f"Trong kỳ này {user_name} chưa có khoản chi tiêu nào.", state=self.current_state)

            cats_sorted = sorted(categories, key=lambda c: c.get("total_spent", 0) or c.get("total_amount", 0) or c.get("amount", 0), reverse=True)
            top_c = cats_sorted[0]
            top_amt = top_c.get("total_spent", 0) or top_c.get("total_amount", 0) or top_c.get("amount", 0)
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=f"🏆 Danh mục {user_name} tiêu nhiều nhất trong kỳ này là '{top_c.get('category_name')}' với tổng số tiền {top_amt:,.0f} VNĐ.",
                state=self.current_state,
                tool_executed="spending_by_category",
                tool_result={"top_category": top_c, "categories": cats_sorted}
            )

        # ─────────────────────────────────────────────────────────────
        # 7. NET SAVINGS (e.g. 'Tháng này ta tiết kiệm được bao nhiêu?')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "net_savings":
            ov_res = await self.registry.execute("financial_overview", user_id=user_id, user_role=user_role, period=period)
            ov_d = ov_res.data or {}
            inc = ov_d.get("income", 0)
            exp = ov_d.get("expense", 0)
            net = inc - exp
            rate = (net / inc * 100) if inc > 0 else 0
            if net > 0:
                reply_text = f"🎉 Trong kỳ này, {user_name} đã tiết kiệm được {net:,.0f} VNĐ (Tổng thu: {inc:,.0f} VNĐ | Tổng chi: {exp:,.0f} VNĐ), đạt tỷ lệ tiết kiệm {rate:.1f}%."
            else:
                reply_text = f"⚠️ Trong kỳ này, {user_name} chưa có khoản tiết kiệm thặng dư (Tổng thu: {inc:,.0f} VNĐ | Tổng chi: {exp:,.0f} VNĐ, thâm hụt {-net:,.0f} VNĐ)."
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=reply_text,
                state=self.current_state,
                tool_executed="financial_overview",
                tool_result={"income": inc, "expense": exp, "net_savings": net, "savings_rate": rate}
            )

        # ─────────────────────────────────────────────────────────────
        # 8. ABNORMAL SPENDING (e.g. 'Có khoản nào bất thường không?')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "abnormal_spending":
            tx_res = await self.registry.execute("transaction_search", user_id=user_id, user_role=user_role, time_frame=period, txn_type="EXPENSE")
            tx_list = (tx_res.data.get("transactions") or tx_res.data.get("results") or []) if tx_res.success else []
            if not tx_list:
                self.current_state = AgentState.IDLE
                return AgentResponse(text=f"Trong kỳ này {user_name} chưa ghi nhận giao dịch chi tiêu nào.", state=self.current_state, tool_executed="transaction_search", tool_result=tx_res.data)

            amts = [t.get("amount", 0) for t in tx_list if t.get("amount", 0) > 0]
            mean_val = sum(amts) / len(amts) if amts else 0
            high_txs = [t for t in tx_list if t.get("amount", 0) >= max(2.5 * mean_val, 1_000_000)]
            if high_txs:
                high_sorted = sorted(high_txs, key=lambda t: t.get("amount", 0), reverse=True)
                top_h = high_sorted[0]
                reply_text = f"🔍 Khí Linh phát hiện khoản chi đáng chú ý: '{top_h.get('note')}' ({top_h.get('amount', 0):,.0f} VNĐ, ngày {top_h.get('transaction_date')}), cao hơn đáng kể so với mức chi trung bình ({mean_val:,.0f} VNĐ) của các khoản chi khác trong kỳ."
            else:
                reply_text = f"✅ Tất cả {len(tx_list)} khoản chi trong kỳ đều duy trì ở mức ổn định, không có khoản chi nào đột biến bất thường."
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=reply_text,
                state=self.current_state,
                tool_executed="transaction_search",
                tool_result={"abnormal_transactions": high_txs, "mean_amount": mean_val}
            )

        # ─────────────────────────────────────────────────────────────
        # 9. CONDITIONAL READ-ONLY (e.g. 'Nếu ví MoMo còn dưới 500 nghìn thì báo ta')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "conditional_read_only":
            if "momo" in raw or "ví" in raw:
                w_name = VietnameseFinancialParser.extract_wallet_name(message) or "MoMo"
                thresh = VietnameseFinancialParser.parse_amount(message) or 500000
                w_res = await self.registry.execute("get_wallets", user_id=user_id, user_role=user_role, wallet_name=w_name)
                wallets = w_res.data.get("wallets", []) if w_res.success else []
                if wallets:
                    bal = wallets[0].get("balance", 0)
                    if bal < thresh:
                        reply_text = f"⚠️ Ví '{wallets[0]['wallet_name']}' hiện còn {bal:,.0f} VNĐ (dưới ngưỡng {thresh:,.0f} VNĐ), đúng như {user_name} dặn dò cần lưu ý!"
                    else:
                        reply_text = f"✅ Ví '{wallets[0]['wallet_name']}' hiện có {bal:,.0f} VNĐ (trên ngưỡng {thresh:,.0f} VNĐ), số dư vẫn đang ở mức an toàn."
                else:
                    reply_text = f"Khí Linh không tìm thấy ví '{w_name}' để kiểm tra điều kiện."
                self.current_state = AgentState.IDLE
                return AgentResponse(text=reply_text, state=self.current_state, tool_executed="get_wallets", tool_result=w_res.data)

            if "ngân sách" in raw or "hạn mức" in raw or "vượt" in raw:
                budget_res = await self.registry.execute("budget_status", user_id=user_id, user_role=user_role, month_year="this_month")
                budgets = budget_res.data.get("budgets", []) if budget_res.success else []
                exceeded = [b for b in budgets if b.get("is_exceeded")]
                if exceeded:
                    exc_str = ", ".join(f"'{b['category_name']}' (vượt {b['percent']}%)" for b in exceeded)
                    reply_text = f"⚠️ Trong tháng này đang có các danh mục vượt ngân sách: {exc_str}!"
                else:
                    reply_text = f"✅ Toàn bộ các hạn mức ngân sách tháng này đều đang được kiểm soát an toàn, chưa có danh mục nào vượt ngưỡng."
                self.current_state = AgentState.IDLE
                return AgentResponse(text=reply_text, state=self.current_state, tool_executed="budget_status", tool_result=budget_res.data)

            if "nợ" in raw:
                debt_res = await self.registry.execute("debt_list", user_id=user_id, user_role=user_role)
                debts = debt_res.data.get("debts", []) if debt_res.success else []
                unsettled = [d for d in debts if not d.get("is_settled")]
                today = datetime.date.today()
                upcoming = []
                for d in unsettled:
                    due_str = d.get("due_date")
                    if due_str:
                        try:
                            due_d = datetime.date.fromisoformat(due_str.split("T")[0])
                            diff = (due_d - today).days
                            if 0 <= diff <= 7:
                                upcoming.append(d)
                        except Exception: pass
                if upcoming:
                    u_str = ", ".join(f"'{d['person_name']}' ({d['amount']:,.0f} VNĐ)" for d in upcoming)
                    reply_text = f"⚠️ Có {len(upcoming)} khoản nợ đến hạn trong 7 ngày tới: {u_str}."
                else:
                    reply_text = f"✅ Không có khoản nợ nào đến hạn trong 7 ngày tới."
                self.current_state = AgentState.IDLE
                return AgentResponse(text=reply_text, state=self.current_state, tool_executed="debt_list", tool_result={"upcoming": upcoming})

        # ─────────────────────────────────────────────────────────────
        # 10. CONDITIONAL MIXED READ + WRITE (e.g. 'Xem hạn mức ăn uống còn bao nhiêu, rồi nếu còn dưới 500 nghìn thì tăng lên 2 triệu')
        # ─────────────────────────────────────────────────────────────
        if sub_intent == "conditional_mixed_write":
            cat_name = VietnameseFinancialParser.guess_category(message) or "Ăn Uống"
            m_under = re.search(r"(?:dưới|duoi|còn|con)\s+(\d+[\d.,]*\s*(?:k|nghìn|ngàn|tr|triệu|củ)?)\b", raw)
            thresh = VietnameseFinancialParser.parse_amount(m_under.group(1)) if m_under else 500000
            m_up = re.search(r"(?:lên|thành|tang len|dat thanh)\s+(\d+[\d.,]*\s*(?:k|nghìn|ngàn|tr|triệu|củ)?)\b", raw)
            new_limit = VietnameseFinancialParser.parse_amount(m_up.group(1)) if m_up else 2000000

            # Step 1: Read budget status
            budget_res = await self.registry.execute("budget_status", user_id=user_id, user_role=user_role, month_year="this_month")
            budgets = budget_res.data.get("budgets", []) if budget_res.success else []
            matched_b = None
            for b in budgets:
                if b.get("category_name", "").lower() == cat_name.lower():
                    matched_b = b
                    break

            limit_amt = matched_b.get("limit_amount", 0) if matched_b else 0
            spent_amt = matched_b.get("spent", 0) if matched_b else 0
            remaining = max(0, limit_amt - spent_amt) if matched_b else 0

            # Evaluate condition: remaining < thresh
            if matched_b and remaining < thresh:
                # Điều kiện THỎA MÃN -> Đề xuất mutation và chuyển sang CONFIRMING!
                pending_act = {
                    "tool_name": "update_budget",
                    "args": {
                        "category_name": matched_b["category_name"],
                        "limit_amount": new_limit,
                        "month_year": "this_month"
                    },
                    "status": "CONFIRMING",
                    "created_at": datetime.datetime.now().isoformat()
                }
                tool_obj = self.registry.get("update_budget")
                pending_act["summary"] = tool_obj.generate_summary(pending_act["args"]) if tool_obj else f"Cập nhật hạn mức {cat_name} thành {new_limit:,.0f} VNĐ"
                self.set_pending_action(user_id, pending_act)
                self.current_state = AgentState.CONFIRMING
                return AgentResponse(
                    text=(
                        f"🔮 **Khí Linh Tiên Trí** đã kiểm tra:\n"
                        f"Hạn mức danh mục '{matched_b['category_name']}' tháng này hiện chỉ còn lại {remaining:,.0f} VNĐ (dưới ngưỡng {thresh:,.0f} VNĐ).\n"
                        f"Đúng theo điều kiện của {user_name}, Khí Linh đã chuẩn bị nâng hạn mức lên {new_limit:,.0f} VNĐ:\n"
                        f"{pending_act['summary']}\n\n"
                        f"{user_name} có **Xác nhận** thực hiện thao tác này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
                    ),
                    state=self.current_state,
                    pending_confirmation=pending_act
                )
            else:
                # Điều kiện KHÔNG thỏa mãn -> KHÔNG mutation!
                rem_desc = f"{remaining:,.0f} VNĐ" if matched_b else "chưa thiết lập"
                reply_text = (
                    f"📊 Khí Linh đã kiểm tra: Hạn mức danh mục '{cat_name}' tháng này hiện còn lại {rem_desc} (không dưới ngưỡng {thresh:,.0f} VNĐ).\n"
                    f"Vì điều kiện chưa thỏa mãn, Khí Linh giữ nguyên hiện trạng và không thực hiện thay đổi nào."
                )
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=reply_text,
                    state=self.current_state,
                    tool_executed="budget_status",
                    tool_result=budget_res.data
                )

        # Fallback default
        self.current_state = AgentState.IDLE
        return AgentResponse(
            text=f"Khí Linh chưa phân tích được yêu cầu này của {user_name}.",
            state=self.current_state
        )


    async def process_request(
        self,
        user_id: int,
        user_message: str,
        recent_history: str = "",
        user_role: str = "user",
        mode: Any = "action",
        user_name: Optional[str] = None
    ) -> AgentResponse:
        """Xử lý yêu cầu bằng ngôn ngữ tự nhiên từ người dùng theo quy trình chuẩn của Agent Core"""
        clean_msg = user_message.strip()
        self.current_state = AgentState.THINKING

        # Chuẩn hóa Đạo hiệu / User Name (Principle 14 & 15: AI phải dùng Đạo hiệu khi xưng hô, fallback 'Ký Chủ', cấm 'Đạo hữu')
        if not user_name or not str(user_name).strip() or str(user_name).strip().lower() in ("đạo hữu", "user"):
            import main
            try:
                with main.get_db() as conn:
                    u_row = conn.execute("SELECT full_name FROM users WHERE id = ?", (user_id,)).fetchone()
                    if u_row and u_row["full_name"] and u_row["full_name"].strip() and u_row["full_name"].strip().lower() not in ("đạo hữu", "user"):
                        user_name = u_row["full_name"].strip()
                    else:
                        user_name = "Ký Chủ"
            except Exception:
                user_name = "Ký Chủ"
        else:
            user_name = str(user_name).strip()

        # Đảm bảo không bao giờ xưng hô "Đạo Hữu"
        if user_name:
            user_name_lower = user_name.lower()
            if user_name_lower.startswith("đạo hữu "):
                user_name = user_name[8:].strip()
            elif user_name_lower == "đạo hữu":
                user_name = "Ký Chủ"

        # Chuẩn hóa AgentMode
        if isinstance(mode, AgentMode):
            agent_mode = mode
        else:
            m_str = str(mode).lower() if mode else "action"
            agent_mode = AgentMode.KNOWLEDGE if m_str in ("knowledge", "rag", "read_only") else AgentMode.ACTION

        # ─────────────────────────────────────────────────────────────
        # 0. PHÂN LUỒNG TRI THỨC VÀ KIỂM SOÁT QUYỀN HẠN KHÍ LINH AI LỚN (KNOWLEDGE MODE)
        # ─────────────────────────────────────────────────────────────
        if agent_mode == AgentMode.KNOWLEDGE:
            # 0.A. Chặn xác nhận thao tác ghi dữ liệu từ chế độ Knowledge
            if VietnameseFinancialParser.is_confirmation(clean_msg):
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text="Khí Linh AI Lớn hoạt động ở chế độ Tra cứu Tri thức (Knowledge Assistant), không có quyền thực thi thao tác ghi dữ liệu. Hãy triệu hồi Khí Linh (nhỏ / Live System Mode) để thực hiện thao tác này!",
                    state=self.current_state
                )

            # 0.B. Chặn dứt khoát mọi mệnh lệnh biến động dữ liệu tài chính (Mutation Commands)
            if self._is_mutation_command(clean_msg):
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=(
                        "Ta có thể giải đáp và hướng dẫn Ký chủ các thông tin hoặc quy trình trên hệ thống, "
                        "nhưng Khí Linh AI Lớn không có quyền thực hiện thao tác này và chỉ có quyền giải đáp, tra cứu dữ liệu (Read-Only). "
                        "Hãy triệu hồi Khí Linh (nhỏ / Live System Mode) để thực hiện thao tác thay đổi số dư hoặc sổ sách này!"
                    ),
                    state=self.current_state
                )

            # 0.C. Xử lý câu hỏi kết hợp: RAG Tri thức Hệ thống + Dữ liệu Cá nhân Read-Only
            is_comb, comb_domain = self._is_combined_query(clean_msg)
            if is_comb and comb_domain:
                return await self._handle_combined_query(
                    user_id, clean_msg, comb_domain, recent_history=recent_history, user_role=user_role
                )

            # 0.D. Nếu là câu hỏi đọc dữ liệu cá nhân thuần túy (Personal Read-Only) -> Để fallthrough xuống planning chạy READ tool
            is_personal_read = self._is_pure_personal_read_query(clean_msg)
            if not is_personal_read:
                # Toàn bộ câu hỏi còn lại trong Knowledge Mode đều là tra cứu Tri Thức Hệ Thống qua RAG
                ans_text, trace = await self.rag.answer_question(clean_msg, provider=self.provider, recent_history=recent_history)
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=ans_text,
                    state=self.current_state,
                    tool_executed="knowledge_rag",
                    tool_result={"trace_sources": trace}
                )

        # Nếu là câu hỏi tri thức hệ thống thuần túy trong Action Mode (không phải mutation command), cũng dùng RAG
        if agent_mode == AgentMode.ACTION and self._is_system_knowledge_query(clean_msg, recent_history=recent_history) and not self._is_mutation_command(clean_msg):
            ans_text, trace = await self.rag.answer_question(clean_msg, provider=self.provider, recent_history=recent_history)
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=ans_text,
                state=self.current_state,
                tool_executed="knowledge_rag",
                tool_result={"trace_sources": trace}
            )

        # ─────────────────────────────────────────────────────────────
        # 1. KIỂM TRA LUỒNG HÀNH ĐỘNG ĐANG CHỜ (PENDING ACTION / CONFIRMATION / FOLLOW-UP)
        # ─────────────────────────────────────────────────────────────
        pending = self.get_pending_action(user_id) if agent_mode == AgentMode.ACTION else None
        if pending:
            # 1.A. Người dùng hủy bỏ thao tác đang chờ
            if VietnameseFinancialParser.is_cancellation(clean_msg):
                self.clear_pending_action(user_id)
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=f"Đã hủy bỏ thao tác theo lệnh của {user_name}. Số dư và sổ sách được giữ nguyên toàn vẹn.",
                    state=self.current_state
                )

            # 1.B. Kiểm tra nếu người dùng đưa ra một mệnh lệnh mới hoàn toàn không liên quan (Unrelated New Intent)
            # hoặc câu hỏi tra cứu đọc dữ liệu độc lập (Context Isolation)
            is_unrelated = (
                VietnameseFinancialParser.is_unrelated_new_intent(clean_msg, pending.get("tool_name"))
                or self._is_multi_tool_read_query(clean_msg)
                or self._is_pure_personal_read_query(clean_msg)
            )
            if is_unrelated and not VietnameseFinancialParser.is_modification(clean_msg):
                self.clear_pending_action(user_id)
                pending = None
                # Fall through xuống Bước 2 (Planning) để xử lý mệnh lệnh mới!

        if pending:
            # Nếu đang ở trạng thái CONFIRMING:
            if pending.get("status") == "CONFIRMING":
                # 1.C. Người dùng sửa đổi tham số của thao tác đang chờ (Dynamic Modification)
                if VietnameseFinancialParser.is_modification(clean_msg):
                    new_amt = VietnameseFinancialParser.parse_amount(clean_msg)
                    if new_amt and new_amt > 0:
                        for amt_field in ("amount", "limit_amount", "target_amount", "balance"):
                            if amt_field in pending["args"]:
                                pending["args"][amt_field] = new_amt
                                break

                    new_cat = VietnameseFinancialParser.guess_category(clean_msg)
                    if new_cat and any(kw in clean_msg.lower() for kw in ["danh mục", "danh muc", "thành", "thanh", "sang", "loại"]):
                        if "category_name" in pending["args"]:
                            pending["args"]["category_name"] = new_cat

                    # 1.C.1. Đảo chiều chuyển tiền: "ngược lại", "đảo lại"
                    if any(kw in clean_msg.lower() for kw in ["ngược lại", "nguoc lai", "đảo lại", "dao lai"]):
                        if "from_wallet_name" in pending["args"] and "to_wallet_name" in pending["args"]:
                            old_f = pending["args"].get("from_wallet_name")
                            old_t = pending["args"].get("to_wallet_name")
                            pending["args"]["from_wallet_name"] = old_t
                            pending["args"]["to_wallet_name"] = old_f
                            pending["args"]["from_wallet_id"] = None
                            pending["args"]["to_wallet_id"] = None

                    from_w, to_w = VietnameseFinancialParser.extract_transfer_wallets(clean_msg)
                    if to_w and "to_wallet_name" in pending["args"]:
                        pending["args"]["to_wallet_name"] = to_w
                        pending["args"]["to_wallet_id"] = None
                    if from_w and "from_wallet_name" in pending["args"]:
                        pending["args"]["from_wallet_name"] = from_w
                        pending["args"]["from_wallet_id"] = None

                    # 1.C.2. Đổi ví khi nói "không phải MoMo, Vietcombank"
                    w_single = VietnameseFinancialParser.extract_wallet_name(clean_msg)
                    if w_single and not to_w and not from_w:
                        if pending.get("tool_name") == "transfer_money":
                            if any(k in clean_msg.lower() for k in ["sang", "qua", "đích", "dich"]):
                                pending["args"]["to_wallet_name"] = w_single
                                pending["args"]["to_wallet_id"] = None
                            elif any(k in clean_msg.lower() for k in ["từ", "tu", "nguồn", "nguon"]):
                                pending["args"]["from_wallet_name"] = w_single
                                pending["args"]["from_wallet_id"] = None
                            else:
                                if "không phải" in clean_msg.lower() or "khong phai" in clean_msg.lower():
                                    old_from = pending["args"].get("from_wallet_name", "").lower()
                                    if old_from and old_from in clean_msg.lower():
                                        pending["args"]["from_wallet_name"] = w_single
                                        pending["args"]["from_wallet_id"] = None
                                    else:
                                        pending["args"]["to_wallet_name"] = w_single
                                        pending["args"]["to_wallet_id"] = None
                                else:
                                    pending["args"]["to_wallet_name"] = w_single
                                    pending["args"]["to_wallet_id"] = None
                        elif "wallet_name" in pending["args"]:
                            pending["args"]["wallet_name"] = w_single
                            pending["args"]["wallet_id"] = None

                    # 1.C.3. Đổi chu kỳ / thời gian: "không phải tháng này, tháng trước"
                    new_p = VietnameseFinancialParser.parse_period(clean_msg)
                    if new_p:
                        if "month_year" in pending["args"]:
                            pending["args"]["month_year"] = new_p
                        elif "period" in pending["args"]:
                            pending["args"]["period"] = new_p

                    p_cand = VietnameseFinancialParser.extract_person_name(clean_msg)
                    if p_cand and "person_name" in pending["args"]:
                        pending["args"]["person_name"] = p_cand

                    # Phân giải lại ví nếu cần cho transfer_money
                    if pending.get("tool_name") == "transfer_money":
                        self._check_pending_completeness(user_id, pending, user_name=user_name)

                    # Tái sinh tóm tắt xác nhận động từ Tool Registry
                    tool_obj = self.registry.get(pending["tool_name"])
                    if tool_obj:
                        pending["summary"] = tool_obj.generate_summary(pending["args"])
                    else:
                        pending["summary"] = f"👉 Thao tác {pending['tool_name']} với tham số: {pending['args']}"

                    self.set_pending_action(user_id, pending)
                    self.current_state = AgentState.CONFIRMING
                    return AgentResponse(
                        text=(
                            f"🔮 Đã cập nhật lại thông tin:\n"
                            f"{pending['summary']}\n\n"
                            f"{user_name} có **Xác nhận** thực hiện thao tác này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
                        ),
                        state=self.current_state,
                        pending_confirmation=pending
                    )

                # 1.D. Người dùng xác nhận thực hiện
                if VietnameseFinancialParser.is_confirmation(clean_msg):
                    self.current_state = AgentState.EXECUTING
                    tool_name = pending["tool_name"]
                    tool_args = pending["args"]

                    tool_obj = self.registry.get(tool_name)
                    tool_res = await self.registry.execute(tool_name, user_id=user_id, user_role=user_role, mode=agent_mode, **tool_args)
                    self.clear_pending_action(user_id)
                    self._last_user_tool[user_id] = {"tool_name": tool_name, "args": tool_args}

                    if tool_res.success:
                        self.current_state = AgentState.SUCCESS
                        if tool_obj:
                            self.record_successful_action(user_id, tool_obj, tool_args, tool_res)
                        return AgentResponse(
                            text=f"✅ {tool_res.message}",
                            state=AgentState.SUCCESS,
                            tool_executed=tool_name,
                            tool_result=tool_res.to_dict()
                        )
                    else:
                        self.current_state = AgentState.ERROR
                        return AgentResponse(
                            text=f"❌ Thất bại: {tool_res.error or tool_res.message}",
                            state=AgentState.ERROR,
                            tool_executed=tool_name,
                            tool_result=tool_res.to_dict(),
                            error=tool_res.error
                        )

                # 1.E. Người dùng cung cấp câu trả lời ngắn hoặc tham số bổ sung khi đang chờ xác nhận
                merged, _ = self._merge_followup_parameter(user_id, pending, clean_msg, user_name=user_name)
                if merged:
                    tool_obj = self.registry.get(pending["tool_name"])
                    if tool_obj:
                        pending["summary"] = tool_obj.generate_summary(pending["args"])
                    self.set_pending_action(user_id, pending)
                    self.current_state = AgentState.CONFIRMING
                    return AgentResponse(
                        text=(
                            f"🔮 Đã cập nhật lại thông tin:\n"
                            f"{pending['summary']}\n\n"
                            f"{user_name} có **Xác nhận** thực hiện thao tác này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
                        ),
                        state=self.current_state,
                        pending_confirmation=pending
                    )

                # 1.F. Người dùng nhắn nội dung khác khi đang chờ xác nhận -> Nhắc lại và tiếp tục chờ
                return AgentResponse(
                    text=(
                        f"🔮 Khí Linh đang chờ {user_name} xác nhận thao tác sau:\n"
                        f"{pending['summary']}\n\n"
                        f"{user_name} có thể trả lời **'Xác nhận'** để thực hiện, **'Hủy'** để hủy bỏ, hoặc yêu cầu sửa đổi (ví dụ: 'Đổi thành 2 triệu')."
                    ),
                    state=AgentState.CONFIRMING,
                    pending_confirmation=pending
                )

            # Nếu đang ở trạng thái AWAITING_PARAM (đang chờ bổ sung tham số còn thiếu):
            elif pending.get("status") == "AWAITING_PARAM":
                # Người dùng nói "xác nhận" khi chưa điền đủ tham số
                if VietnameseFinancialParser.is_confirmation(clean_msg):
                    miss = pending.get("missing_param", "tham số")
                    return AgentResponse(
                        text=f"Thao tác chưa đủ thông tin ({miss}). {user_name} vui lòng cung cấp thông tin còn thiếu trước khi xác nhận.",
                        state=AgentState.IDLE,
                        pending_confirmation=pending
                    )

                # Trộn tham số follow-up vào pending action
                merged, err_msg = self._merge_followup_parameter(user_id, pending, clean_msg, user_name=user_name)
                if not merged:
                    new_action = await self._plan_action(user_id, clean_msg, user_role=user_role, user_name=user_name)
                    if new_action and new_action.get("tool"):
                        self.clear_pending_action(user_id)
                        pending = None
                    else:
                        return AgentResponse(
                            text=err_msg or f"Khí Linh chưa nhận diện được thông tin. {user_name} vui lòng nêu rõ hơn.",
                            state=AgentState.IDLE,
                            pending_confirmation=pending
                        )

                # Kiểm tra tính hoàn thiện sau khi trộn
                if pending:
                    is_comp, next_miss = self._check_pending_completeness(user_id, pending, user_name=user_name)
                    if is_comp:
                        # Kiểm tra trùng lặp / tồn tại thực thể trước khi confirm
                        amb_chk = await self._check_entity_ambiguity(user_id, pending["tool_name"], pending["args"], user_name=user_name)
                        if amb_chk:
                            return AgentResponse(
                                text=amb_chk,
                                state=AgentState.IDLE,
                                pending_confirmation=pending
                            )
                        pending["status"] = "CONFIRMING"
                        pending["missing_param"] = None
                        tool_obj = self.registry.get(pending["tool_name"])
                        if tool_obj:
                            pending["summary"] = tool_obj.generate_summary(pending["args"])
                        else:
                            pending["summary"] = f"👉 Thao tác {pending['tool_name']}: {pending['args']}"
                        self.set_pending_action(user_id, pending)
                        self.current_state = AgentState.CONFIRMING
                        return AgentResponse(
                            text=(
                                f"🔮 **Khí Linh Tiên Trí** đã tiếp nhận ý định:\n"
                                f"{pending['summary']}\n\n"
                                f"{user_name} có **Xác nhận** thực hiện thao tác này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
                            ),
                            state=self.current_state,
                            pending_confirmation=pending
                        )
                    else:
                        pending["missing_param"] = next_miss
                        self.set_pending_action(user_id, pending)
                        tool_n = pending.get("tool_name", "")
                        prompt_text = f"{user_name} vui lòng cung cấp thêm thông tin còn thiếu."
                        if next_miss == "amount":
                            if tool_n == "create_expense":
                                prompt_text = f"{user_name} muốn ghi khoản chi bao nhiêu Linh Thạch?"
                            elif tool_n == "create_income":
                                prompt_text = f"{user_name} muốn ghi nhận khoản thu bao nhiêu Linh Thạch?"
                            elif tool_n == "create_debt":
                                prompt_text = f"{user_name} cho biết số tiền vay/nợ là bao nhiêu Linh Thạch?"
                            else:
                                prompt_text = f"{user_name} muốn chuyển bao nhiêu Linh Thạch?"
                        elif next_miss == "note":
                            if tool_n == "create_expense":
                                prompt_text = f"Khoản chi này dùng cho việc gì (ví dụ: ăn sáng, đổ xăng, mua sắm...)?"
                            elif tool_n == "create_income":
                                prompt_text = f"Khoản thu này đến từ nguồn nào (ví dụ: tiền lương, thưởng, bán đồ...)?"
                        elif next_miss == "from_wallet_name":
                            prompt_text = f"{user_name} muốn chuyển tiền từ ví nào?"
                        elif next_miss == "to_wallet_name":
                            prompt_text = f"{user_name} muốn chuyển tiền sang ví nào?"
                        elif next_miss == "category_type":
                            c_n = pending['args'].get('category_name')
                            if c_n:
                                prompt_text = f"Danh mục '{c_n}' thuộc Thu hay Chi?"
                            else:
                                prompt_text = f"{user_name} muốn thêm danh mục Thu hay Chi?"
                        elif next_miss == "category_name":
                            if tool_n == "create_category":
                                prompt_text = f"{user_name} muốn đặt tên danh mục là gì?"
                            elif tool_n == "delete_category":
                                prompt_text = f"{user_name} muốn xóa danh mục nào?"
                            elif tool_n == "create_budget":
                                prompt_text = f"{user_name} muốn đặt hạn mức chi tiêu cho danh mục nào (ví dụ: Ăn Uống, Mua Sắm, Di Chuyển...)?"
                            else:
                                prompt_text = f"{user_name} muốn thao tác với danh mục nào?"
                        elif next_miss == "category_selection":
                            prompt_text = f"{user_name} muốn chọn danh mục nào để xóa?"
                        elif next_miss == "limit_amount":
                            prompt_text = f"{user_name} muốn đặt hạn mức cho danh mục '{pending['args'].get('category_name', '')}' là bao nhiêu Linh Thạch?"
                        elif next_miss == "debt_selection":
                            prompt_text = f"{user_name} muốn thao tác với khoản nợ nào?"
                        elif next_miss == "budget_selection":
                            prompt_text = f"{user_name} muốn xóa hạn mức của danh mục nào?"
                        elif next_miss == "target_name":
                            prompt_text = f"{user_name} muốn đặt tên cho mục tiêu tiết kiệm này là gì (ví dụ: mua xe, du lịch, mua nhà)?"
                        elif next_miss == "target_amount":
                            prompt_text = f"{user_name} muốn đặt số tiền tiết kiệm cho mục tiêu '{pending['args'].get('target_name', '')}' là bao nhiêu Linh Thạch?"
                        elif next_miss == "goal_details":
                            prompt_text = f"{user_name} muốn lập mục tiêu tiết kiệm cho việc gì (ví dụ: mua xe, mua nhà) và với số tiền bao nhiêu Linh Thạch?"
                        return AgentResponse(
                            text=prompt_text,
                            state=AgentState.IDLE,
                            pending_confirmation=pending
                        )

        # ─────────────────────────────────────────────────────────────
        # 1.1. CHẶN XÁC NHẬN / HỦY MỒ CÔI (ZERO ORPHAN EXECUTION)
        # ─────────────────────────────────────────────────────────────
        if VietnameseFinancialParser.is_confirmation(clean_msg):
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=f"Hiện tại không có giao dịch hoặc thao tác tài chính nào đang chờ xác nhận. {user_name} có cần thực hiện thao tác nào mới không?",
                state=self.current_state
            )

        if VietnameseFinancialParser.is_cancellation(clean_msg):
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=f"Hiện tại không có thao tác tài chính nào đang chờ thực hiện. {user_name} có cần hỗ trợ gì khác không?",
                state=self.current_state
            )

        # ─────────────────────────────────────────────────────────────
        # 1.2. LẬP KẾ HOẠCH ĐA CÔNG CỤ TRA CỨU (MULTI-TOOL READ PLANNING)
        # ─────────────────────────────────────────────────────────────
        if self._is_multi_tool_read_query(clean_msg):
            return await self._handle_multi_tool_read_query(user_id, clean_msg, user_name=user_name, user_role=user_role)

        # ─────────────────────────────────────────────────────────────
        # 2. XÁC ĐỊNH Ý ĐỊNH VÀ KHÁM PHÁ CÔNG CỤ (PLANNING)
        # ─────────────────────────────────────────────────────────────
        self.current_state = AgentState.PLANNING
        planned_action = await self._plan_action(user_id, clean_msg, user_role=user_role, user_name=user_name)

        # 2.0. Giải thích quy tắc hệ thống / chính sách bảo mật (POLICY_EXPLANATION)
        if planned_action and planned_action.get("intent") == "POLICY_EXPLANATION":
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=planned_action.get("policy_message", ""),
                state=self.current_state
            )

        # 2.1. Cần làm rõ tham số (CLARIFICATION_NEEDED / AWAITING_PARAM)
        if planned_action and (planned_action.get("intent") == "CLARIFICATION_NEEDED" or planned_action.get("missing_param")):
            tool_name = planned_action.get("tool")
            tool_args = planned_action.get("arguments", {})
            clarification_msg = planned_action.get("clarification_message", f"{user_name} vui lòng cung cấp thêm thông tin chi tiết.")
            pending_act = None
            if tool_name and agent_mode == AgentMode.ACTION:
                pending_act = {
                    "tool_name": tool_name,
                    "args": tool_args,
                    "status": "AWAITING_PARAM",
                    "missing_param": planned_action.get("missing_param"),
                    "ambiguous_candidates": planned_action.get("ambiguous_candidates"),
                    "created_at": datetime.datetime.now().isoformat()
                }
                self.set_pending_action(user_id, pending_act)
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=clarification_msg,
                state=self.current_state,
                pending_confirmation=pending_act
            )

        # 2.2. Tư vấn / phân tích tài chính giả định (FINANCIAL_ADVICE)
        if planned_action and planned_action.get("intent") == "FINANCIAL_ADVICE":
            fin_ctx = planned_action.get("financial_context", "")
            prompt = f"""Bạn là "Khí Linh Tiên Trí" — cố vấn tài chính thông tuệ mang phong cách tu tiên cổ phong kết hợp nguyên tắc quản lý tài chính hiện đại (quy tắc 50/30/20, quỹ dự phòng, tối ưu chi tiêu).
Hãy tư vấn, phân tích và đưa ra gợi ý/lời khuyên thiết thực, súc tích, sâu sắc cho {user_name}. Tuyệt đối KHÔNG tuyên bố rằng đã ghi nhận giao dịch hay trừ tiền.
{fin_ctx}
{recent_history}
Yêu cầu tư vấn của {user_name}: {clean_msg}"""
            answer = await self.provider.generate_response(prompt)
            self.current_state = AgentState.IDLE
            return AgentResponse(text=answer, state=self.current_state)

        # 2.3. Đối thoại thông thường phi tài chính (GENERAL_CONVERSATION)
        if not planned_action or not planned_action.get("tool"):
            prompt = f"""Bạn là "Khí Linh Tiên Trí" — trợ lý AI tài chính phong cách tu tiên cho ứng dụng Càn Khôn Linh Thạch Các.
Hãy đàm đạo cùng {user_name} một cách ngắn gọn, súc tích, tự nhiên và hữu ích.
{recent_history}
Câu hỏi của {user_name}: {clean_msg}"""
            answer = await self.provider.generate_response(prompt)
            self.current_state = AgentState.IDLE
            return AgentResponse(text=answer, state=self.current_state)

        tool_name = planned_action["tool"]
        tool_args = planned_action.get("arguments", {})
        tool = self.registry.get(tool_name)

        if not tool:
            self.current_state = AgentState.ERROR
            return AgentResponse(
                text="Pháp bảo cần dùng không khả dụng trong Càn Khôn Các.",
                state=self.current_state,
                error=f"Unknown tool: {tool_name}"
            )

        # Kiểm tra phân quyền vai trò (Role Permission Check)
        if tool.required_role == "admin" and user_role != "admin":
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text="Chỉ Chưởng Môn (Admin) mới có quyền năng sử dụng pháp bảo này trong Càn Khôn Các.",
                state=self.current_state
            )

        # 2.4. Chuẩn hóa tham số và điền giá trị mặc định (Argument Canonicalization & Defaults)
        tool_args = self._canonicalize_and_fill_tool_args(tool, tool_args, raw_message=clean_msg)

        # 2.5. Kiểm tra thực thể và xử lý nhập nhằng (Entity Resolution & Ambiguity Check)
        ambiguity_msg = await self._check_entity_ambiguity(user_id, tool_name, tool_args, user_name=user_name)
        if ambiguity_msg:
            if tool_args.get("_not_found_wallet") or tool_args.get("_not_found_category"):
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=ambiguity_msg,
                    state=self.current_state,
                    pending_confirmation=None
                )
            pending_act = None
            if agent_mode == AgentMode.ACTION:
                miss_p = None
                if tool_args.get("_ambiguous_from"): miss_p = "from_wallet_name"
                elif tool_args.get("_ambiguous_to"): miss_p = "to_wallet_name"
                elif tool_args.get("_ambiguous_debts"): miss_p = "debt_selection"
                elif tool_args.get("_ambiguous_budgets"): miss_p = "budget_selection"
                elif tool_args.get("_ambiguous_categories"): miss_p = "category_name"

                cand_list = (
                    tool_args.get("_ambiguous_from")
                    or tool_args.get("_ambiguous_to")
                    or tool_args.get("_ambiguous_debts")
                    or tool_args.get("_ambiguous_budgets")
                    or tool_args.get("_ambiguous_categories")
                )

                pending_act = {
                    "tool_name": tool_name,
                    "args": tool_args,
                    "status": "AWAITING_PARAM",
                    "missing_param": miss_p,
                    "ambiguous_candidates": cand_list,
                    "created_at": datetime.datetime.now().isoformat()
                }
                self.set_pending_action(user_id, pending_act)
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=ambiguity_msg,
                state=self.current_state,
                pending_confirmation=pending_act
            )

        # Kiểm tra phân quyền KNOWLEDGE MODE: Tuyệt đối KHÔNG được thực thi hoặc xác nhận thao tác biến động dữ liệu!
        if agent_mode == AgentMode.KNOWLEDGE and tool.operation_type != OperationType.READ:
            self.current_state = AgentState.IDLE
            return AgentResponse(
                text=(
                    "Ta có thể giải đáp và hướng dẫn Ký chủ các thông tin hoặc quy trình trên hệ thống, "
                    "nhưng Khí Linh AI Lớn chỉ có quyền giải đáp và tra cứu dữ liệu (Read-Only). "
                    "Hãy triệu hồi Khí Linh (nhỏ / Live System Mode) để thực hiện thao tác thay đổi số dư hoặc sổ sách này!"
                ),
                state=self.current_state
            )

        # ─────────────────────────────────────────────────────────────
        # 3. THAO TÁC CÓ RỦI RO / BIẾN ĐỘNG DỮ LIỆU -> BẮT BUỘC XÁC NHẬN
        # ─────────────────────────────────────────────────────────────
        if tool.requires_confirmation:
            # Kiểm tra thiếu tham số cho create_category
            if tool.name == "create_category":
                c_name = tool_args.get("category_name")
                c_type = tool_args.get("category_type")

                # Case 1: Thiếu cả Thu/Chi và Tên danh mục (e.g. "thêm cho tôi 1 mục thu chi")
                if not c_type and not c_name:
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "category_type",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"{user_name} muốn thêm danh mục Thu hay Chi?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                # Case 2: Đã có Tên nhưng thiếu Thu/Chi (e.g. "thêm danh mục Ăn uống")
                if not c_type:
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "category_type",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"Danh mục '{c_name}' thuộc Thu hay Chi?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                # Case 3: Đã có Thu/Chi nhưng thiếu Tên (e.g. "thêm cho ta một danh mục Chi")
                if not c_name:
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "category_name",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"{user_name} muốn đặt tên danh mục là gì?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                # Case 4: Đủ thông tin -> tự động gán icon nếu chưa có hoặc mặc định
                if not tool_args.get("icon") or tool_args["icon"] == "📦":
                    tool_args["icon"] = resolve_category_icon(c_name, c_type)

            # Kiểm tra thiếu tham số cho delete_category
            if tool.name == "delete_category":
                if planned_action and planned_action.get("missing_param") == "category_selection":
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "category_selection",
                        "ambiguous_candidates": planned_action.get("ambiguous_candidates"),
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=planned_action.get("clarification_message", f"{user_name} muốn xóa danh mục nào?"),
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )
                if not tool_args.get("category_name") and not tool_args.get("category_id"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "category_name",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"{user_name} muốn xóa danh mục nào?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

            # Kiểm tra thiếu tham số cho create_budget
            if tool.name == "create_budget":
                if not tool_args.get("category_name"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "category_name",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"{user_name} muốn đặt hạn mức chi tiêu cho danh mục nào (ví dụ: Ăn Uống, Mua Sắm, Di Chuyển...)?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                if not tool_args.get("limit_amount") or tool_args["limit_amount"] <= 0:
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "limit_amount",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    cat_disp = tool_args.get("category_name", "")
                    return AgentResponse(
                        text=f"{user_name} muốn đặt hạn mức chi tiêu cho danh mục '{cat_disp}' là bao nhiêu Linh Thạch?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

            # Kiểm tra nếu thiếu tham số tạo mục tiêu tiết kiệm (target_name, target_amount)
            if tool.name == "create_saving_goal":
                if not tool_args.get("target_name") and (not tool_args.get("target_amount") or float(tool_args.get("target_amount", 0)) <= 0):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "goal_details",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"{user_name} muốn lập mục tiêu tiết kiệm cho việc gì (ví dụ: mua xe, mua nhà, du lịch) và với số tiền bao nhiêu Linh Thạch?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                if not tool_args.get("target_name"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "target_name",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    amt_disp = f"{float(tool_args.get('target_amount', 0)):,.0f} VNĐ"
                    return AgentResponse(
                        text=f"{user_name} muốn đặt tên cho mục tiêu tiết kiệm {amt_disp} này là gì (ví dụ: mua xe, du lịch, mua nhà)?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                if not tool_args.get("target_amount") or float(tool_args.get("target_amount", 0)) <= 0:
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "target_amount",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    goal_disp = tool_args.get("target_name", "")
                    return AgentResponse(
                        text=f"{user_name} muốn đặt hạn mức tiết kiệm cho mục tiêu '{goal_disp}' là bao nhiêu Linh Thạch?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

            # Kiểm tra nếu thiếu tham số ghi khoản chi (amount, note/category)
            if tool.name == "create_expense":
                if tool_args.get("amount") is not None and float(tool_args.get("amount", 0)) <= 0:
                    return AgentResponse(
                        text="Số tiền phải lớn hơn 0!",
                        state=AgentState.IDLE
                    )
                if not tool_args.get("amount"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "amount",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    target_desc = f" cho '{tool_args.get('note') or tool_args.get('category_name')}'" if (tool_args.get('note') or tool_args.get('category_name')) else ""
                    return AgentResponse(
                        text=f"{user_name} muốn ghi khoản chi{target_desc} bao nhiêu Linh Thạch?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )
                if not tool_args.get("note") and not tool_args.get("category_name"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "note",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    amt_str = f"{float(tool_args.get('amount', 0)):,.0f} VNĐ"
                    return AgentResponse(
                        text=f"Khoản chi {amt_str} này dùng cho việc gì (ví dụ: ăn sáng, đổ xăng, mua sắm...)?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

            # Kiểm tra nếu thiếu tham số ghi khoản thu (amount, note/category)
            if tool.name == "create_income":
                if tool_args.get("amount") is not None and float(tool_args.get("amount", 0)) <= 0:
                    return AgentResponse(
                        text="Số tiền phải lớn hơn 0!",
                        state=AgentState.IDLE
                    )
                if not tool_args.get("amount"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "amount",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"{user_name} muốn ghi nhận khoản thu bao nhiêu Linh Thạch?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )
                if not tool_args.get("note") and not tool_args.get("category_name"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "note",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    self.current_state = AgentState.IDLE
                    amt_str = f"{float(tool_args.get('amount', 0)):,.0f} VNĐ"
                    return AgentResponse(
                        text=f"Khoản thu {amt_str} này đến từ nguồn nào (ví dụ: tiền lương, thưởng, bán đồ...)?",
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

            # Kiểm tra nếu thiếu tham số chuyển tiền (amount, from_wallet, to_wallet)
            if tool.name == "transfer_money":
                if not tool_args.get("amount") or tool_args["amount"] <= 0:
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "amount",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    from_desc = f"từ ví {tool_args['from_wallet_name']}" if tool_args.get('from_wallet_name') else ""
                    to_desc = f"sang ví {tool_args['to_wallet_name']}" if tool_args.get('to_wallet_name') else ""
                    self.current_state = AgentState.IDLE
                    q_text = f"{user_name} muốn chuyển bao nhiêu Linh Thạch {from_desc} {to_desc}?".replace("  ", " ").strip()
                    return AgentResponse(
                        text=q_text,
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                # Nếu thiếu cả hai ví (nguồn và đích) -> Yêu cầu mơ hồ, yêu cầu làm rõ
                if not tool_args.get("from_wallet_name") and not tool_args.get("from_wallet_id") and not tool_args.get("to_wallet_name") and not tool_args.get("to_wallet_id"):
                    self.current_state = AgentState.IDLE
                    return AgentResponse(
                        text=f"Khí Linh chưa rõ thông tin: Chưa rõ ví nguồn và ví đích (ví dụ: chuyển 500k từ ví A sang ví B). {user_name} vui lòng cung cấp thêm chi tiết.",
                        state=self.current_state
                    )

                # Phân giải và xác thực ví nguồn / ví đích
                import main
                if tool_args.get("from_wallet_name") or tool_args.get("from_wallet_id"):
                    res_from = self._resolve_wallet_for_transfer(user_id, tool_args.get("from_wallet_name") or str(tool_args.get("from_wallet_id")), is_destination=False, user_name=user_name)
                    if res_from.get("status") == "NOT_FOUND":
                        self.current_state = AgentState.IDLE
                        return AgentResponse(text=res_from["message"], state=self.current_state)
                    elif res_from.get("status") == "RESOLVED":
                        tool_args["from_wallet_id"] = res_from["wallet"]["id"]
                        tool_args["from_wallet_name"] = res_from["wallet"]["wallet_name"]

                if tool_args.get("to_wallet_name") or tool_args.get("to_wallet_id"):
                    res_to = self._resolve_wallet_for_transfer(user_id, tool_args.get("to_wallet_name") or str(tool_args.get("to_wallet_id")), is_destination=True, user_name=user_name)
                    if res_to.get("status") == "NOT_FOUND":
                        self.current_state = AgentState.IDLE
                        return AgentResponse(text=res_to["message"], state=self.current_state)
                    elif res_to.get("status") == "RESOLVED":
                        tool_args["to_wallet_id"] = res_to["wallet"]["id"]
                        tool_args["to_wallet_name"] = res_to["wallet"]["wallet_name"]

                # Nếu chỉ có 1 ví được chỉ định thành công, tự động suy luận ví còn lại nếu người dùng chỉ có 2 ví
                if tool_args.get("from_wallet_id") and not tool_args.get("to_wallet_id") and not tool_args.get("to_wallet_name"):
                    with main.get_db() as conn:
                        user_wallets = [dict(r) for r in conn.execute("SELECT id, wallet_name, wallet_type FROM wallets WHERE user_id = ?", (user_id,)).fetchall()]
                    other_wallets = [w for w in user_wallets if w["id"] != tool_args["from_wallet_id"]]
                    if len(other_wallets) == 1:
                        tool_args["to_wallet_id"] = other_wallets[0]["id"]
                        tool_args["to_wallet_name"] = other_wallets[0]["wallet_name"]
                elif tool_args.get("to_wallet_id") and not tool_args.get("from_wallet_id") and not tool_args.get("from_wallet_name"):
                    with main.get_db() as conn:
                        user_wallets = [dict(r) for r in conn.execute("SELECT id, wallet_name, wallet_type FROM wallets WHERE user_id = ?", (user_id,)).fetchall()]
                    other_wallets = [w for w in user_wallets if w["id"] != tool_args["to_wallet_id"]]
                    if len(other_wallets) == 1:
                        tool_args["from_wallet_id"] = other_wallets[0]["id"]
                        tool_args["from_wallet_name"] = other_wallets[0]["wallet_name"]

                if not tool_args.get("from_wallet_name") and not tool_args.get("from_wallet_id"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "from_wallet_name",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    to_desc = f"sang ví {tool_args['to_wallet_name']}" if tool_args.get('to_wallet_name') else ""
                    self.current_state = AgentState.IDLE
                    amt_str = f"{tool_args.get('amount', 0):,.0f}đ"
                    q_text = f"{user_name} muốn chuyển {amt_str} {to_desc} từ ví nào?".replace("  ", " ").strip()
                    return AgentResponse(
                        text=q_text,
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

                if not tool_args.get("to_wallet_name") and not tool_args.get("to_wallet_id"):
                    pending_act = {
                        "tool_name": tool_name,
                        "args": tool_args,
                        "status": "AWAITING_PARAM",
                        "missing_param": "to_wallet_name",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    if agent_mode == AgentMode.ACTION:
                        self.set_pending_action(user_id, pending_act)
                    from_desc = f"từ ví {tool_args['from_wallet_name']}" if tool_args.get('from_wallet_name') else ""
                    self.current_state = AgentState.IDLE
                    amt_str = f"{tool_args.get('amount', 0):,.0f}đ"
                    q_text = f"{user_name} muốn chuyển {amt_str} {from_desc} sang ví nào?".replace("  ", " ").strip()
                    return AgentResponse(
                        text=q_text,
                        state=self.current_state,
                        pending_confirmation=pending_act
                    )

            validation_error = self._validate_tool_args(tool, tool_args)
            if validation_error:
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=f"Khí Linh chưa rõ thông tin: {validation_error}. {user_name} vui lòng cung cấp thêm chi tiết.",
                    state=self.current_state
                )

            if "operation_id" not in tool_args or not tool_args["operation_id"]:
                tool_args["operation_id"] = f"khilinh_op_{user_id}_{uuid.uuid4().hex[:12]}"

            self.current_state = AgentState.CONFIRMING
            summary = tool.generate_summary(tool_args)
            pending_conf = {
                "tool_name": tool_name,
                "args": tool_args,
                "summary": summary,
                "status": "CONFIRMING",
                "created_at": datetime.datetime.now().isoformat()
            }
            if agent_mode == AgentMode.ACTION:
                self.set_pending_action(user_id, pending_conf)

            confirm_prompt = (
                f"🔮 **Khí Linh Tiên Trí** đã tiếp nhận ý định:\n"
                f"{summary}\n\n"
                f"{user_name} có **Xác nhận** thực hiện thao tác này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
            )
            return AgentResponse(
                text=confirm_prompt,
                state=self.current_state,
                pending_confirmation=pending_conf
            )

        # ─────────────────────────────────────────────────────────────
        # 4. THAO TÁC ĐỌC / HỆ THỐNG AN TOÀN -> THỰC THI NGAY LẬP TỨC
        # ─────────────────────────────────────────────────────────────
        self.current_state = AgentState.EXECUTING
        tool_res = await self.registry.execute(tool_name, user_id=user_id, user_role=user_role, mode=agent_mode, **tool_args)

        if tool_res.success:
            self.current_state = AgentState.SUCCESS
            self._last_user_tool[user_id] = {"tool_name": tool_name, "args": tool_args}
            self.record_successful_action(user_id, tool, tool_args, tool_res)
            return AgentResponse(
                text=tool_res.message,
                state=self.current_state,
                tool_executed=tool_name,
                tool_result=tool_res.to_dict()
            )
        else:
            self.current_state = AgentState.ERROR
            return AgentResponse(
                text=f"Không thể thực thi pháp bảo: {tool_res.error or tool_res.message}",
                state=self.current_state,
                tool_executed=tool_name,
                tool_result=tool_res.to_dict(),
                error=tool_res.error
            )

    async def _plan_action(self, user_id: int, message: str, user_role: str = "user", user_name: str = "Ký Chủ") -> Optional[Dict[str, Any]]:
        """Lập kế hoạch hành động: phối hợp giữa phân loại ý định an toàn, trích xuất thực thể và Tool Registry"""
        raw = message.lower().strip()

        # 1. General conversation filter
        if VietnameseFinancialParser.is_general_conversation(message):
            return {"intent": "GENERAL_CONVERSATION", "tool": None}

        # 2. Financial advice / theoretical question filter
        if VietnameseFinancialParser.is_financial_advice_or_hypothetical(message):
            fin_ctx = ""
            try:
                overview_res = await self.registry.execute("financial_overview", user_id=user_id, user_role=user_role, period="this_month")
                if overview_res.success and overview_res.data:
                    d = overview_res.data
                    fin_ctx = f"\n[Dữ liệu tài chính tháng này của {user_name}: Tổng thu {d.get('income', 0):,.0f}đ, Tổng chi {d.get('expense', 0):,.0f}đ, Tiết kiệm thuần {d.get('net_savings', 0):,.0f}đ, Số dư khả dụng {d.get('total_balance', 0):,.0f}đ]"
            except Exception:
                fin_ctx = ""

            return {
                "intent": "FINANCIAL_ADVICE",
                "tool": None,
                "financial_context": fin_ctx
            }

        # 3. Trích xuất thực thể cơ bản
        amt = VietnameseFinancialParser.parse_amount(message)
        dt = VietnameseFinancialParser.parse_date(message)
        explicit_dt = VietnameseFinancialParser.parse_explicit_date(message)
        period = VietnameseFinancialParser.parse_period(message)
        cat = VietnameseFinancialParser.guess_category(message)
        w_name = VietnameseFinancialParser.extract_wallet_name(message)
        p_name = VietnameseFinancialParser.extract_person_name(message)
        freq = VietnameseFinancialParser.extract_frequency(message)
        nav_tab = VietnameseFinancialParser.extract_target_tab(message)

        # 4. Multi-turn follow-up context resolution
        last_tool_info = self._last_user_tool.get(user_id)
        if last_tool_info and VietnameseFinancialParser.is_followup_query(message):
            last_tool = last_tool_info["tool_name"]
            last_args = dict(last_tool_info.get("args", {}))

            if last_tool in ("spending_summary", "spending_by_category", "financial_overview", "get_financial_overview"):
                if period:
                    last_args["period"] = period
                    return {"tool": last_tool, "arguments": last_args}
                if cat:
                    return {"tool": "spending_by_category", "arguments": {"category_name": cat, "period": last_args.get("period", "this_month")}}

            if last_tool in ("transaction_search", "search_transactions"):
                if period:
                    last_args["time_frame"] = period
                    return {"tool": "transaction_search", "arguments": last_args}
                if cat:
                    last_args["category_name"] = cat
                    return {"tool": "transaction_search", "arguments": last_args}
                if w_name:
                    last_args["wallet_name"] = w_name
                    return {"tool": "transaction_search", "arguments": last_args}

        # ─────────────────────────────────────────────────────────────
        # 4.5. ACTION CONTEXT & INTENT PRIORITY (DESTRUCTIVE / UPDATE / CONTEXTUAL REFERENCE)
        # Các hành động XÓA, SỬA, ĐỔI, HỦY hoặc tham chiếu ngữ cảnh BẮT BUỘC ưu tiên trước generic write!
        # ─────────────────────────────────────────────────────────────
        has_destructive_verb = any(re.search(rf"\b{re.escape(w)}\b", raw) for w in ["xóa", "xoa", "hủy", "huy", "gỡ", "go", "bỏ", "bo", "xóa bỏ", "xoa bo"])
        has_update_verb = any(re.search(rf"\b{re.escape(w)}\b", raw) for w in ["sửa", "sua", "đổi", "doi", "cập nhật", "cap nhat", "chỉnh", "chinh", "thay đổi", "thay doi"])
        is_contextual_ref = any(re.search(rf"\b{re.escape(w)}\b", raw) for w in [
            "vừa rồi", "vua roi", "vừa tạo", "vua tao", "vừa ghi", "vua ghi", "vừa làm", "vua lam",
            "vừa chi", "vua chi", "vừa xong", "vua xong", "gần nhất", "gan nhat",
            "khoản đó", "khoan do", "giao dịch đó", "giao dich do", "khoản đấy", "khoan day",
            "nó", "no", "cái đó", "cai do", "cái vừa rồi", "cai vua roi",
            "khoản vừa rồi", "giao dịch vừa rồi", "khoản chi vừa rồi", "khoản thu vừa rồi"
        ])

        # Phân loại thực thể tường minh từ câu nói
        is_explicit_wallet = any(w in raw for w in ["ví", "vi", "túi càn khôn", "tài khoản"])
        is_explicit_goal = any(w in raw for w in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy"])
        is_explicit_budget = any(w in raw for w in ["ngân sách", "ngan sach", "hạn mức", "han muc"])
        is_explicit_debt = any(w in raw for w in ["khoản nợ", "khoan no", "sổ nợ", "so no"]) or (any(w in raw for w in ["nợ", "no"]) and not any(w in raw for w in ["nó", "noi"]))
        is_explicit_txn = any(w in raw for w in [
            "khoản chi", "khoan chi", "khoản thu", "khoan thu", "giao dịch", "giao dich",
            "khoản vừa", "khoan vua", "khoản đó", "khoan do", "khoản đấy", "khoan day",
            "giao dịch vừa", "giao dịch đó", "khoản này", "bỏ khoản", "gỡ khoản", "gỡ giao dịch", "bỏ giao dịch"
        ])

        last_action_entity = self._last_action.get(user_id).entity_type if self._last_action.get(user_id) else None

        # 4.5.A. XÓA THỰC THỂ CÓ HÀNH ĐỘNG PHÁ HỦY (DESTRUCTIVE ACTIONS)
        if has_destructive_verb:
            # 1. Xóa ví tham chiếu ngữ cảnh ("ví vừa tạo", "ví vừa rồi", "ví đó" hoặc last_action_entity == "wallet")
            is_wallet_contextual = (
                (is_explicit_wallet and is_contextual_ref) or
                (is_contextual_ref and last_action_entity == "wallet" and not any([is_explicit_txn, is_explicit_goal, is_explicit_budget, is_explicit_debt]))
            )
            if is_wallet_contextual:
                target_w = await self.resolve_contextual_entity(user_id, "wallet")
                if target_w:
                    return {"tool": "delete_wallet", "arguments": {"wallet_id": target_w["id"], "wallet_name": target_w.get("wallet_name")}}

            # 2. Xóa mục tiêu tiết kiệm tham chiếu ngữ cảnh
            is_goal_contextual = (
                (is_explicit_goal and is_contextual_ref) or
                (is_contextual_ref and last_action_entity == "saving_goal" and not any([is_explicit_txn, is_explicit_wallet, is_explicit_budget, is_explicit_debt]))
            )
            if is_goal_contextual:
                target_g = await self.resolve_contextual_entity(user_id, "saving_goal")
                if target_g:
                    return {"tool": "delete_saving_goal", "arguments": {"goal_id": target_g["id"], "goal_name": target_g.get("target_name")}}

            # 3. Xóa ngân sách tham chiếu ngữ cảnh
            is_budget_contextual = (
                (is_explicit_budget and is_contextual_ref) or
                (is_contextual_ref and last_action_entity == "budget" and not any([is_explicit_txn, is_explicit_wallet, is_explicit_goal, is_explicit_debt]))
            )
            if is_budget_contextual:
                target_b = await self.resolve_contextual_entity(user_id, "budget")
                if target_b:
                    return {"tool": "delete_budget", "arguments": {"category_name": target_b.get("category_name"), "month_year": target_b.get("month_year")}}

            # 4. Xóa nợ tham chiếu ngữ cảnh
            is_debt_contextual = (
                (is_explicit_debt and is_contextual_ref) or
                (is_contextual_ref and last_action_entity == "debt" and not any([is_explicit_txn, is_explicit_wallet, is_explicit_goal, is_explicit_budget]))
            )
            if is_debt_contextual:
                target_d = await self.resolve_contextual_entity(user_id, "debt")
                if target_d:
                    return {"tool": "delete_debt", "arguments": {"debt_id": target_d["id"], "person_name": target_d.get("person_name")}}

            # 5. Xóa giao dịch / khoản chi / khoản thu (mặc định ưu tiên cao nhất cho financial operations)
            is_txn_delete = (
                is_explicit_txn or
                (is_contextual_ref and not any([is_explicit_wallet, is_explicit_goal, is_explicit_budget, is_explicit_debt])) or
                any(w in raw for w in ["nó", "cái đó", "cái vừa rồi"])
            )
            if is_txn_delete:
                m_id = re.search(r"#(\d+)|(?:giao dịch|gd|khoản|id)\s*(?:id|mã|so|số)?\s*#?(\d+)(?!\s*(?:k|nghìn|ngàn|tr|triệu|tỷ|đồng|đ|vnđ|vnd|củ|lít))\b", raw)
                target_txn = None
                if m_id:
                    txn_id = int(m_id.group(1) or m_id.group(2))
                    target_txn = {"id": txn_id}
                else:
                    is_preceding = any(w in raw for w in ["khoản kia", "khoan kia", "khoản trước", "không phải khoản đó", "không phải giao dịch đó"])
                    target_txn = await self.resolve_contextual_entity(user_id, "transaction", amount=amt, date_filter=explicit_dt, offset=1 if is_preceding else 0)

                if target_txn:
                    args = {"transaction_id": target_txn["id"]}
                    if target_txn.get("amount"):
                        args["amount"] = target_txn["amount"]
                    if target_txn.get("note"):
                        args["note"] = target_txn["note"]
                    return {
                        "tool": "delete_transaction",
                        "arguments": args
                    }
                else:
                    return {
                        "intent": "CLARIFICATION_NEEDED",
                        "clarification_message": f"Khí Linh không tìm thấy giao dịch nào phù hợp gần đây để xóa. {user_name} có thể cung cấp mã ID hoặc nội dung giao dịch cụ thể không?"
                    }

        # 4.5.B. SỬA GIAO DỊCH / KHOẢN CHI / KHOẢN THU (UPDATE TRANSACTION)
        if has_update_verb:
            is_txn_update = (
                is_explicit_txn or
                (is_contextual_ref and not any([is_explicit_wallet, is_explicit_goal, is_explicit_budget, is_explicit_debt])) or
                (last_action_entity in (None, "transaction") and not any([is_explicit_wallet, is_explicit_goal, is_explicit_budget, is_explicit_debt]))
            )
            if is_txn_update:
                m_id = re.search(r"#(\d+)|(?:giao dịch|gd|khoản|id)\s*(?:id|mã|so|số)?\s*#?(\d+)(?!\s*(?:k|nghìn|ngàn|tr|triệu|tỷ|đồng|đ|vnđ|vnd|củ|lít))\b", raw)
                target_txn = None
                if m_id:
                    txn_id = int(m_id.group(1) or m_id.group(2))
                    target_txn = {"id": txn_id}
                else:
                    is_preceding = any(w in raw for w in ["khoản kia", "khoan kia", "khoản trước", "không phải khoản đó", "không phải giao dịch đó"])
                    target_txn = await self.resolve_contextual_entity(user_id, "transaction", offset=1 if is_preceding else 0)

                if target_txn:
                    u_args = {"transaction_id": target_txn["id"]}
                    if amt and amt > 0:
                        u_args["amount"] = amt
                    if cat:
                        u_args["category_name"] = cat
                    if w_name:
                        u_args["wallet_name"] = w_name
                    clean_u_note = message
                    for kw in ["sửa", "sua", "đổi", "doi", "cập nhật", "thành", "thanh", "sang", "khoản vừa rồi", "khoản chi vừa rồi", "giao dịch vừa rồi", "khoản đó", "giao dịch đó"]:
                        clean_u_note = re.sub(rf"\b{re.escape(kw)}\b", "", clean_u_note, flags=re.IGNORECASE)
                    clean_u_note = re.sub(r"\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|ngàn|tr|triệu|tỷ|vnđ|đ|đồng)?\b", "", clean_u_note, flags=re.IGNORECASE).strip(" .,-")
                    if clean_u_note and len(clean_u_note) > 1 and clean_u_note != str(amt):
                        u_args["note"] = clean_u_note
                    return {
                        "tool": "update_transaction",
                        "arguments": u_args
                    }
                else:
                    return {
                        "intent": "CLARIFICATION_NEEDED",
                        "clarification_message": "Khí Linh không tìm thấy giao dịch nào gần đây để sửa."
                    }

        # ─────────────────────────────────────────────────────────────
        # 5. SEMANTIC CAPABILITY RESOLUTION (DỰA TRÊN TOOL REGISTRY)
        # ─────────────────────────────────────────────────────────────

        # A. DEBT DOMAIN (Ưu tiên nhận diện nợ trước ví và các thực thể khác)
        if VietnameseFinancialParser.is_debt_create_intent(message):
            debt_args = VietnameseFinancialParser.extract_debt_creation_args(message)
            if debt_args:
                if debt_args.get("amount", 0) > 0:
                    return {
                        "tool": "create_debt",
                        "arguments": debt_args
                    }
                else:
                    d_type = debt_args.get("debt_type", "BORROW")
                    clean_p = debt_args.get("person_name", "Đối tác")
                    return {
                        "intent": "CLARIFICATION_NEEDED",
                        "missing_param": "amount",
                        "tool": "create_debt",
                        "arguments": debt_args,
                        "clarification_message": f"{user_name} cho biết số tiền {('cho ' + clean_p + ' vay') if d_type == 'LEND' else 'đi vay/nợ'} là bao nhiêu Linh Thạch?"
                    }

        # Quyết toán nợ
        if VietnameseFinancialParser.is_debt_settle_intent(message) or any(kw in raw for kw in ["quyết toán nợ", "quyet toan no", "đã trả nợ", "da tra no", "đã thu nợ", "da thu no", "trả hết nợ", "tất toán nợ"]):
            return {"tool": "settle_debt", "arguments": {"person_name": p_name}}

        if VietnameseFinancialParser.is_debt_delete_intent(message) or any(kw in raw for kw in ["xóa nợ", "xoa no", "xóa khoản nợ", "xoa khoan no"]):
            return {"tool": "delete_debt", "arguments": {"person_name": p_name}}

        # B. WALLET DOMAIN
        # Tạo ví mới
        if VietnameseFinancialParser.is_wallet_create_intent(message):
            dyn_wallet_args = VietnameseFinancialParser.extract_dynamic_wallet_creation_args(message)
            if dyn_wallet_args:
                return {
                    "tool": "create_wallet",
                    "arguments": dyn_wallet_args
                }

        # Xóa ví
        if any(kw in raw for kw in ["xóa ví", "xoa vi", "hủy ví", "huy vi", "xóa túi càn khôn", "xóa tài khoản"]):
            clean_del_w = message
            for kw in ["xóa ví", "xoa vi", "hủy ví", "huy vi", "xóa túi càn khôn", "xóa tài khoản", "ví", "túi càn khôn", "tài khoản"]:
                clean_del_w = re.sub(rf"\b{re.escape(kw)}\b", "", clean_del_w, flags=re.IGNORECASE)
            clean_del_w = clean_del_w.strip(" .,-") or w_name or message.strip()
            return {"tool": "delete_wallet", "arguments": {"wallet_name": clean_del_w}}

        # Chuyển tiền liên ví
        if any(kw in raw for kw in ["chuyển", "chuyen"]) and not any(kw in raw for kw in ["chuyển sang tab", "chuyển tab", "chuyển trang"]):
            from_w, to_w = VietnameseFinancialParser.extract_transfer_wallets(message)
            return {
                "tool": "transfer_money",
                "arguments": {
                    "amount": amt,
                    "from_wallet_name": from_w,
                    "to_wallet_name": to_w,
                    "note": message.strip()
                }
            }

        # C. CATEGORY DOMAIN
        if VietnameseFinancialParser.is_category_create_intent(message):
            cat_args = VietnameseFinancialParser.extract_category_creation_args(message)
            c_name = cat_args.get("category_name")
            c_type = cat_args.get("category_type")
            c_icon = resolve_category_icon(c_name, c_type) if (c_name or c_type) else "📦"

            if not c_type and not c_name:
                return {
                    "tool": "create_category",
                    "arguments": {"category_name": None, "category_type": None, "icon": "📦"},
                    "missing_param": "category_type",
                    "clarification_message": f"{user_name} muốn thêm danh mục Thu hay Chi?"
                }
            elif c_name and not c_type:
                return {
                    "tool": "create_category",
                    "arguments": {"category_name": c_name, "category_type": None, "icon": c_icon},
                    "missing_param": "category_type",
                    "clarification_message": f"Danh mục '{c_name}' thuộc Thu hay Chi?"
                }
            elif c_type and not c_name:
                return {
                    "tool": "create_category",
                    "arguments": {"category_name": None, "category_type": c_type, "icon": c_icon},
                    "missing_param": "category_name",
                    "clarification_message": f"{user_name} muốn đặt tên danh mục là gì?"
                }
            else:
                return {
                    "tool": "create_category",
                    "arguments": {"category_name": c_name, "category_type": c_type, "icon": c_icon}
                }

        if VietnameseFinancialParser.is_category_delete_intent(message) or any(kw in raw for kw in ["xóa danh mục", "hủy danh mục"]):
            del_args = VietnameseFinancialParser.extract_category_delete_args(message)
            del_name = del_args.get("category_name") or cat
            if not del_name:
                return {
                    "tool": "delete_category",
                    "arguments": {"category_name": None},
                    "missing_param": "category_name",
                    "clarification_message": f"{user_name} muốn xóa danh mục nào?"
                }

            import main
            with main.get_db() as conn:
                user_cats = [dict(r) for r in conn.execute(
                    "SELECT id, category_name, category_type, icon FROM categories WHERE user_id = ?",
                    (user_id,)
                ).fetchall()]

            clean_del = del_name.strip().lower()
            exact = [c for c in user_cats if c["category_name"].lower() == clean_del]
            if exact:
                matched_cats = exact
            else:
                matched_cats = [c for c in user_cats if clean_del in c["category_name"].lower()]

            if not matched_cats:
                return {
                    "intent": "CLARIFICATION_NEEDED",
                    "clarification_message": f"Khí Linh không tìm thấy danh mục nào tên '{del_name}' trong tiên phủ để xóa."
                }
            elif len(matched_cats) == 1:
                cat_item = matched_cats[0]
                return {
                    "tool": "delete_category",
                    "arguments": {
                        "category_id": cat_item["id"],
                        "category_name": cat_item["category_name"],
                        "category_type": cat_item["category_type"]
                    }
                }
            else:
                options_str = "\n".join(f"{i+1}. {c['category_name']} ({'Khoản Thu' if c['category_type'] == 'INCOME' else 'Khoản Chi'})" for i, c in enumerate(matched_cats))
                return {
                    "tool": "delete_category",
                    "arguments": {"category_name": del_name},
                    "missing_param": "category_selection",
                    "ambiguous_candidates": matched_cats,
                    "clarification_message": f"Có {len(matched_cats)} danh mục phù hợp với '{del_name}':\n{options_str}\n\n{user_name} muốn xóa danh mục nào?"
                }

        # D. BUDGET DOMAIN
        if VietnameseFinancialParser.is_budget_delete_intent(message) or any(kw in raw for kw in ["xóa ngân sách", "hủy ngân sách", "xóa hạn mức"]):
            return {"tool": "delete_budget", "arguments": {"category_name": cat, "month_year": period}}

        if VietnameseFinancialParser.is_budget_update_intent(message):
            return {
                "tool": "update_budget",
                "arguments": {
                    "category_name": cat,
                    "limit_amount": amt or 0,
                    "month_year": period
                }
            }

        if VietnameseFinancialParser.is_budget_create_intent(message):
            b_args = {
                "limit_amount": amt or 0,
                "category_name": cat,
                "month_year": period or "this_month"
            }
            if not cat and (not amt or amt <= 0):
                return {
                    "tool": "create_budget",
                    "arguments": b_args,
                    "missing_param": "category_name",
                    "clarification_message": f"{user_name} muốn đặt hạn mức chi tiêu cho danh mục nào (ví dụ: Ăn Uống, Mua Sắm, Di Chuyển...) và số tiền là bao nhiêu Linh Thạch?"
                }
            elif not cat:
                return {
                    "tool": "create_budget",
                    "arguments": b_args,
                    "missing_param": "category_name",
                    "clarification_message": f"{user_name} muốn đặt hạn mức chi tiêu cho danh mục nào (ví dụ: Ăn Uống, Mua Sắm, Di Chuyển...)?"
                }
            elif not amt or amt <= 0:
                return {
                    "tool": "create_budget",
                    "arguments": b_args,
                    "missing_param": "limit_amount",
                    "clarification_message": f"{user_name} muốn đặt hạn mức chi tiêu cho danh mục '{cat}' là bao nhiêu Linh Thạch?"
                }
            return {
                "tool": "create_budget",
                "arguments": b_args
            }

        # E. RECURRING DOMAIN
        if any(kw in raw for kw in ["đặt định kỳ", "giao dịch định kỳ", "hàng tháng đóng", "hàng tuần đóng", "mỗi tháng tự động", "mỗi tuần tự động", "đặt lịch"]) or (any(kw in raw for kw in ["hàng tháng", "hàng tuần", "mỗi tháng", "mỗi tuần"]) and any(act in raw for act in ["đặt", "tự động", "chi", "thu", "nhắc"])):
            if amt and amt > 0:
                t_type = "INCOME" if any(kw in raw for kw in ["lương", "nhận", "thu"]) else "EXPENSE"
                return {
                    "tool": "create_recurring_transaction",
                    "arguments": {
                        "amount": amt,
                        "transaction_type": t_type,
                        "frequency": freq,
                        "category_name": cat,
                        "wallet_name": w_name,
                        "note": message.strip()
                    }
                }

        if any(kw in raw for kw in ["xóa định kỳ", "hủy giao dịch định kỳ"]):
            m_id = re.search(r"#?(\d+)", raw)
            rec_id = int(m_id.group(1)) if m_id else 1
            return {"tool": "delete_recurring_transaction", "arguments": {"rec_id": rec_id}}

        # F. SAVING GOAL DOMAIN
        if VietnameseFinancialParser.is_saving_goal_create_intent(message):
            goal = VietnameseFinancialParser.extract_goal_name(message)
            if not goal and (not amt or amt <= 0):
                return {
                    "tool": "create_saving_goal",
                    "arguments": {"target_name": None, "target_amount": 0},
                    "missing_param": "goal_details",
                    "clarification_message": f"{user_name} muốn lập mục tiêu tiết kiệm cho việc gì (ví dụ: mua xe, mua nhà, du lịch) và với số tiền bao nhiêu Linh Thạch?"
                }
            elif not goal and amt and amt > 0:
                return {
                    "tool": "create_saving_goal",
                    "arguments": {"target_name": None, "target_amount": amt},
                    "missing_param": "target_name",
                    "clarification_message": f"{user_name} muốn đặt tên cho mục tiêu tiết kiệm {amt:,.0f} VNĐ này là gì (ví dụ: mua xe, mua nhà, du lịch)?"
                }
            elif goal and (not amt or amt <= 0):
                return {
                    "tool": "create_saving_goal",
                    "arguments": {"target_name": goal, "target_amount": 0},
                    "missing_param": "target_amount",
                    "clarification_message": f"{user_name} muốn đặt hạn mức tiết kiệm cho mục tiêu '{goal}' là bao nhiêu Linh Thạch?"
                }
            else:
                return {"tool": "create_saving_goal", "arguments": {"target_name": goal, "target_amount": amt}}

        if any(kw in raw for kw in ["rút", "rut", "lấy", "lay"]) and any(kw in raw for kw in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy", "tich luy"]):
            goal = VietnameseFinancialParser.extract_goal_name(message)
            if amt and amt > 0:
                return {"tool": "saving_goal_withdraw", "arguments": {"amount": amt, "goal_name": goal, "wallet_name": w_name}}

        if any(kw in raw for kw in ["nạp", "nap", "đưa", "dua", "gửi", "gui", "thêm", "them"]) and any(kw in raw for kw in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy", "tich luy"]):
            goal = VietnameseFinancialParser.extract_goal_name(message)
            if amt and amt > 0:
                return {"tool": "saving_goal_deposit", "arguments": {"amount": amt, "goal_name": goal, "wallet_name": w_name}}

        if any(kw in raw for kw in ["xóa mục tiêu", "hủy mục tiêu"]):
            goal = VietnameseFinancialParser.extract_goal_name(message)
            return {"tool": "delete_saving_goal", "arguments": {"goal_name": goal}}

        # G. REPORTS & ANALYTICS DOMAIN (READ)
        if any(kw in raw for kw in ["xu hướng", "xu huong", "biểu đồ chi tiêu", "trend"]):
            return {"tool": "get_trend_report", "arguments": {"months": 6}}

        if any(kw in raw for kw in ["chi tiêu theo tuần", "báo cáo tuần", "weekly"]):
            return {"tool": "get_weekly_report", "arguments": {"month_year": period}}

        if any(kw in raw for kw in ["so sánh tháng", "so sanh thang", "so với tháng trước", "so voi thang truoc", "tháng này so với tháng trước"]):
            return {"tool": "compare_months", "arguments": {}}

        if any(kw in raw for kw in ["xuất báo cáo", "xuat bao cao", "tải sao kê", "tai sao ke", "xuất excel", "xuất csv"]):
            fmt = "csv" if "csv" in raw else "excel"
            return {"tool": "export_reports", "arguments": {"format": fmt, "month_year": period}}

        # H. OCR LOGS
        if any(kw in raw for kw in ["lịch sử quét", "nhật ký ocr", "hóa đơn đã quét", "hóa đơn gần đây"]):
            return {"tool": "get_ocr_logs", "arguments": {"limit": 5}}

        # I. NAVIGATION & PROFILE
        if any(kw in raw for kw in ["mở ", "mo ", "chuyển sang ", "chuyen sang ", "đi đến ", "di den "]) and nav_tab:
            return {"tool": "navigate_to", "arguments": {"target_tab": nav_tab}}

        # Profile & Đạo hiệu:
        if any(kw in raw for kw in ["đổi đạo hiệu thành", "doi dao hieu thanh", "đổi tên thành", "doi ten thanh", "đổi tên hiển thị thành"]):
            new_title = re.sub(r"^(?:vui lòng\s+|hãy\s+)?(?:đổi|doi)\s+(?:đạo hiệu|dao hieu|tên|ten|tên hiển thị)\s+(?:thành|thanh)\s+", "", message, flags=re.IGNORECASE).strip(" .!?:;")
            if new_title:
                return {"tool": "update_user_profile", "arguments": {"full_name": new_title}}

        if any(kw in raw for kw in ["đạo hiệu của ta là", "dao hieu cua ta la", "đặt đạo hiệu", "dat dao hieu", "đổi tên tài khoản"]):
            return {
                "intent": "POLICY_EXPLANATION",
                "policy_message": (
                    f"Đạo hiệu là danh xưng tôn quý gắn liền với căn cốt tu vi. Theo quy định bảo mật của Càn Khôn Linh Thạch Các, "
                    f"Khí Linh không thể tự ý sửa đổi Đạo hiệu qua cuộc trò chuyện để đảm bảo tính toàn vẹn và xác thực. "
                    f"{user_name} vui lòng vào mục Hồ Sơ (Cá nhân) trên giao diện ứng dụng để thiết lập Đạo hiệu nhé!"
                )
            }

        if any(kw in raw for kw in ["hồ sơ", "ho so", "thông tin tài khoản", "đạo hiệu của ta", "dao hieu cua ta"]):
            return {"tool": "get_user_profile", "arguments": {}}

        # J. READ OPERATIONS (BUDGET / DEBT / GOAL / WALLET / CATEGORY / TRANSACTIONS)
        if any(kw in raw for kw in ["hạn mức", "han muc", "ngân sách", "ngan sach", "vượt hạn mức"]):
            tool_target = "get_budget_status" if "hạn mức chi tiêu thế nào" in raw else "budget_status"
            return {"tool": tool_target, "arguments": {"category_name": cat} if cat else {}}

        if any(kw in raw for kw in ["sổ nợ", "so no", "vay", "cho vay", "trái chủ", "trai chu", "nhân quả trái chủ"]) or (any(kw in raw for kw in ["nợ", "no"]) and not amt):
            tool_target = "get_debts" if "xem sổ nợ" in raw else "debt_status"
            return {"tool": tool_target, "arguments": {}}

        if any(kw in raw for kw in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy", "tich luy", "tụ linh trận", "tu linh tran"]) and not amt:
            goal = VietnameseFinancialParser.extract_goal_name(message)
            tool_target = "saving_goal_status" if ("thế nào" in raw or "tiến triển" in raw or "của ta" in raw) else "get_saving_goals"
            return {"tool": tool_target, "arguments": {"goal_name": goal} if goal else {}}

        # Tra cứu danh mục (Read-only Categories)
        has_category_kw = any(kw in raw for kw in ["danh mục", "danh muc", "loại thu chi", "loai thu chi", "các khoản chi tiêu", "cac khoan chi tieu"]) or (
            any(kw in raw for kw in ["các mục", "cac muc", "mục chi tiêu", "muc chi tieu", "mục thu chi", "muc thu chi"]) and not any(w in raw for w in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem"])
        )
        has_action_intent = any(act in raw for act in ["thêm", "them", "tạo", "tao", "ghi", "mới", "moi", "đặt", "dat", "nhập", "nhap"])
        if has_category_kw and not has_action_intent:
            return {"tool": "get_categories", "arguments": {}}

        if any(kw in raw for kw in ["định kỳ", "dinh ky"]):
            return {"tool": "get_recurring_transactions", "arguments": {}}

        if any(kw in raw for kw in ["tiêu nhiều nhất", "tiêu gì nhiều nhất", "chi nhiều nhất", "chi gì nhiều nhất", "khoản nào lớn nhất", "tiêu vào đâu", "phân bổ", "cơ cấu chi tiêu", "theo danh mục", "theo mục", "quá tay", "lỡ tiêu", "tiêu nhiều quá"]):
            return {"tool": "spending_by_category", "arguments": {"category_name": cat, "period": period or "this_month"} if cat else {"period": period or "this_month"}}

        if cat and not any(kw in raw for kw in ["mục tiêu", "muc tieu", "ngân sách", "ngan sach", "hạn mức"]):
            if any(kw in raw for kw in ["tiêu", "chi"]) and any(kw in raw for kw in ["bao nhiêu", "thế nào", "mấy"]) and not amt:
                return {"tool": "spending_by_category", "arguments": {"category_name": cat, "period": period or "this_month"}}

        if any(kw in raw for kw in [
            "hôm nay ta đã tiêu gì", "đã tiêu gì", "ta tiêu bao nhiêu", "hôm nay tiêu", "tuần này tiêu",
            "tuần này chi", "tháng này ta tiêu", "tháng này ta chi", "tổng chi tiêu", "tháng này tiêu bao nhiêu", "tiêu bao nhiêu trong tháng",
            "tháng này tôi đã chi bao nhiêu", "tôi đã chi bao nhiêu", "đã chi bao nhiêu", "đã tiêu bao nhiêu"
        ]):
            return {"tool": "spending_summary", "arguments": {"period": period or "this_month"}}

        if any(kw in raw for kw in ["tổng quan", "tong quan", "tình hình tài chính", "thu chi tháng", "báo cáo", "ngân khố", "ngan kho", "khố phòng", "kho phong", "tháng này tôi tiêu bao nhiêu", "tôi tiêu bao nhiêu", "tiêu bao nhiêu", "chi bao nhiêu", "tình hình thế nào", "tinh hinh the nao", "dạo này thế nào"]):
            tool_target = "financial_overview" if ("tình hình tài chính" in raw or "ngân khố" in raw or "khố phòng" in raw or "của ta" in raw or "thế nào" in raw) else "get_financial_overview"
            return {"tool": tool_target, "arguments": {"period": period or "this_month"}}

        if any(kw in raw for kw in ["bất thường", "bat thuong", "khoản chi bất thường", "đột biến"]):
            return {"tool": "transaction_search", "arguments": {"query": "", "time_frame": period or "this_month"}}

        # Transaction search (Ưu tiên kiểm tra trước get_wallets)
        if any(kw in raw for kw in ["tìm giao dịch", "tim giao dich", "tra cứu giao dịch", "lọc giao dịch", "tìm các khoản", "tìm khoản"]) or (raw.startswith("tìm ") and not amt):
            query_str = message
            for kw in ["tìm giao dịch", "tim giao dich", "tra cứu giao dịch", "lọc giao dịch", "tìm các khoản", "tìm khoản", "tìm", "tim"]:
                query_str = re.sub(rf"\b{re.escape(kw)}\b", "", query_str, flags=re.IGNORECASE)
            for p_kw in ["hôm nay", "hôm qua", "tuần này", "tuần trước", "tháng này", "thang nay", "tháng trước"]:
                query_str = re.sub(rf"\b{re.escape(p_kw)}\b", "", query_str, flags=re.IGNORECASE)
            if cat:
                query_str = re.sub(rf"\b{re.escape(cat)}\b", "", query_str, flags=re.IGNORECASE)
            if w_name:
                query_str = re.sub(rf"\b{re.escape(w_name)}\b", "", query_str, flags=re.IGNORECASE)
            query_str = query_str.strip(" .,!?:;")
            tool_choice = "search_transactions" if ("ăn sáng" in raw or "giao dịch ăn sáng" in raw) else "transaction_search"
            s_args = {}
            if query_str: s_args["query"] = query_str
            if cat: s_args["category_name"] = cat
            if w_name: s_args["wallet_name"] = w_name
            if period: s_args["time_frame"] = period
            return {"tool": tool_choice, "arguments": s_args}

        # 4.4. PRONOUN & ACTIVE ENTITY MEMORY (READ-ONLY)
        is_pronoun, ref_domain = VietnameseFinancialParser.is_pronoun_reference(message)
        if is_pronoun and not has_destructive_verb and not has_update_verb:
            if ref_domain == "wallet":
                active_w = self._active_entities.get(user_id, {}).get("wallet")
                if active_w and active_w.get("name"):
                    return {"tool": "get_wallets", "arguments": {"wallet_name": active_w["name"]}}
            elif ref_domain == "transaction":
                return {"tool": "get_recent_transactions", "arguments": {"limit": 1}}
            elif ref_domain == "debt":
                return {"tool": "debt_list", "arguments": {}}
            elif ref_domain == "budget":
                return {"tool": "budget_status", "arguments": {"month_year": period or "this_month"}}

        if any(kw in raw for kw in ["số dư", "so du", "ví", "vi", "còn bao nhiêu", "con bao nhieu", "túi càn khôn", "bao nhiêu tiền", "còn bao nhiêu tiền"]) and not amt:
            if not w_name and any(w in raw for w in ["nó", "ví đó", "cái đó", "cái ví đó", "ví đấy"]):
                active_w = self._active_entities.get(user_id, {}).get("wallet")
                if active_w and active_w.get("name"):
                    w_name = active_w["name"]
            if w_name:
                self._active_entities.setdefault(user_id, {})["wallet"] = {"name": w_name}
            return {"tool": "get_wallets", "arguments": {"wallet_name": w_name} if w_name else {}}

        if any(kw in raw for kw in [
            "xem khoản vừa rồi", "xem giao dịch vừa rồi", "xem khoản đó", "xem giao dịch đó", "xem khoản vừa tạo",
            "kiểm tra giao dịch vừa rồi", "kiểm tra khoản vừa rồi", "chi tiết khoản vừa rồi",
            "xem khoan vua roi", "xem giao dich vua roi", "xem khoan do", "xem giao dich do", "xem khoan vua tao",
            "kiem tra giao dich vua roi", "kiem tra khoan vua roi", "chi tiet khoan vua roi"
        ]):
            return {"tool": "get_recent_transactions", "arguments": {"limit": 1}}

        if any(kw in raw for kw in ["giao dịch gần đây", "giao dich gan day", "lịch sử", "lich su"]):
            return {"tool": "get_recent_transactions", "arguments": {"limit": 5}}

        if any(kw in raw for kw in ["trợ giúp", "hướng dẫn", "tính năng", "bạn làm được gì"]):
            return {"tool": "get_system_help", "arguments": {}}

        # K. FINANCIAL WRITE: CREATE EXPENSE & INCOME
        expense_verbs = [
            "ăn", "an", "uống", "uong", "hết", "het", "mua", "chi", "tiêu", "tieu",
            "đổ xăng", "do xang", "trả tiền", "tra tien", "đóng tiền", "dong tien",
            "thanh toán", "thanh toan", "khoản chi", "mục chi tiêu", "muc chi tieu",
            "khoản chi tiêu", "tán tài", "tan tai"
        ]
        is_expense_trigger = any(re.search(rf"\b{re.escape(kw)}\b", raw) for kw in expense_verbs)
        is_income_trigger = any(re.search(rf"(?<!ghi\s)\b{re.escape(kw)}\b", raw) for kw in ["thu", "nhận", "lương", "thưởng", "được cho", "được tặng", "bán", "khoản thu", "khoản tiền ta vừa nhận", "tiền vừa nhận", "nạp tài", "nap tai"])
        is_read_query = any(q in raw for q in ["bao nhiêu", "bao nhieu", "thế nào", "the nao", "ra sao", "mấy", "may", "lịch sử", "lich su", "xem", "tra cứu", "tra cuu", "tìm", "tim", "là gì", "la gi", "những gì", "nhung gi", "gồm những", "gom nhung", "liệt kê", "liet ke", "danh sách", "danh sach", "có những", "co nhung"])

        if any(w in raw for w in ["khoản chi", "khoan chi", "mục chi tiêu", "muc chi tieu", "khoản chi tiêu", "khoan chi tieu"]):
            is_expense_trigger = True
            is_income_trigger = False
        elif any(w in raw for w in ["khoản thu", "khoan thu", "khoản tiền ta vừa nhận", "tiền vừa nhận"]):
            is_income_trigger = True
            is_expense_trigger = False

        # QUAN TRỌNG: Các hành động Xóa, Hủy, Gỡ, Bỏ, Sửa, Đổi hoặc Tạo/Xóa Danh Mục Tuyệt đối KHÔNG biến thành Create Expense hay Create Income!
        if has_destructive_verb or has_update_verb or VietnameseFinancialParser.is_category_create_intent(message) or VietnameseFinancialParser.is_category_delete_intent(message):
            is_expense_trigger = False
            is_income_trigger = False

        # Chi tiêu (create_expense)
        if amt is not None and is_expense_trigger and not is_income_trigger and not is_read_query:
            clean_note = message
            for kw in [
                "cho tôi ghi nhận", "ghi nhận", "cho tôi thêm", "tôi vừa", "vừa", "hôm nay", "hôm qua", "hết",
                "thêm khoản chi", "khoản chi", "thêm 1 khoản chi", "thêm một khoản chi", "thêm 1 mục chi tiêu mới",
                "thêm một mục chi tiêu mới", "ghi một khoản chi mới", "ghi giúp ta", "ghi giup ta", "ghi cho ta",
                "ghi hộ ta", "ta vừa", "ta da", "ta đã", "tiền", "năm chục"
            ]:
                clean_note = re.sub(rf"\b{re.escape(kw)}\b", "", clean_note, flags=re.IGNORECASE)
            clean_note = re.sub(r"\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|ngàn|tr|triệu|tỷ|vnđ|vnd|đ|đồng|củ|lít)?\b", "", clean_note, flags=re.IGNORECASE).strip()
            clean_note = re.sub(r"\b(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|trăm|nghìn|ngàn|triệu|chục)\b", "", clean_note, flags=re.IGNORECASE).strip()
            clean_note = clean_note.strip(" .,-")
            if clean_note.lower() in ["tiêu", "chi", "ăn", "uống", "ta tiêu", "ta chi", ""]:
                clean_note = cat or "Chi tiêu"
            return {
                "tool": "create_expense",
                "arguments": {
                    "amount": amt,
                    "note": clean_note,
                    "category_name": cat,
                    "wallet_name": w_name,
                    "transaction_date": dt
                }
            }

        # Thu nhập (create_income)
        if amt is not None and is_income_trigger and not is_expense_trigger and not is_read_query:
            clean_note = message
            for kw in [
                "cho tôi ghi nhận", "ghi nhận", "cho tôi thêm", "tôi vừa", "vừa", "hôm nay", "hôm qua",
                "nhận được", "thêm khoản thu", "khoản thu", "thêm 1 khoản thu", "ghi nhận khoản tiền ta vừa nhận",
                "ghi giúp ta", "ghi giup ta", "ta vừa", "ta da", "ta đã", "tiền", "tiền lương"
            ]:
                clean_note = re.sub(rf"\b{re.escape(kw)}\b", "", clean_note, flags=re.IGNORECASE)
            clean_note = re.sub(r"\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|ngàn|tr|triệu|tỷ|vnđ|vnd|đ|đồng|củ|lít)?\b", "", clean_note, flags=re.IGNORECASE).strip()
            clean_note = re.sub(r"\b(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|trăm|nghìn|ngàn|triệu|chục)\b", "", clean_note, flags=re.IGNORECASE).strip()
            clean_note = clean_note.strip(" .,-")
            if clean_note.lower() in ["thu", "nhận", "lương", "tiền lương", ""]:
                clean_note = cat or "Thu nhập"
            return {
                "tool": "create_income",
                "arguments": {
                    "amount": amt,
                    "note": clean_note,
                    "category_name": cat,
                    "wallet_name": w_name,
                    "transaction_date": dt
                }
            }

        # Cần làm rõ số tiền nếu có trigger nhưng thiếu amount
        if is_expense_trigger and not is_read_query and amt is None:
            clean_n = message
            for kw in ["thêm 1 mục chi tiêu mới", "thêm một mục chi tiêu mới", "thêm 1 khoản chi", "thêm một khoản chi", "ghi một khoản chi mới", "thêm khoản chi", "khoản chi"]:
                clean_n = re.sub(rf"\b{re.escape(kw)}\b", "", clean_n, flags=re.IGNORECASE).strip()
            return {
                "tool": "create_expense",
                "arguments": {
                    "amount": 0,
                    "note": cat or (clean_n.capitalize() if len(clean_n) > 2 else None),
                    "category_name": cat,
                    "wallet_name": w_name,
                    "transaction_date": dt
                },
                "missing_param": "amount",
                "clarification_message": f"{user_name} muốn ghi khoản chi bao nhiêu Linh Thạch?"
            }

        if is_income_trigger and not is_read_query and amt is None:
            return {
                "tool": "create_income",
                "arguments": {
                    "amount": 0,
                    "note": cat or "Thu nhập",
                    "category_name": cat,
                    "wallet_name": w_name,
                    "transaction_date": dt
                },
                "missing_param": "amount",
                "clarification_message": f"{user_name} muốn ghi nhận khoản thu bao nhiêu Linh Thạch?"
            }

        # L. FALLBACK: DÙNG LLM DISCOVERY VỚI SCHEMAS DỰA TRÊN TOOL REGISTRY
        schemas = self.registry.get_schemas(role=user_role)
        tool_definitions = []
        for s in schemas:
            tool_definitions.append({
                "name": s["name"],
                "description": s["description"],
                "domain": s["domain"],
                "parameters": s.get("parameters", {})
            })
        intent_prompt = f"""Người dùng nhắn: "{message}"
Danh sách công cụ khả dụng trong hệ thống cùng định dạng tham số (parameters schema):
{json.dumps(tool_definitions, ensure_ascii=False)}

Hãy xác định công cụ phù hợp nhất và trích xuất đúng tên tham số (arguments) theo schema của công cụ đó. Nếu không cần công cụ nào, trả về tool: null."""
        target_schema = {
            "tool": "tên công cụ hoặc null",
            "arguments": {"key": "value"}
        }
        res = await self.provider.parse_structured_intent(intent_prompt, schema=target_schema)
        if isinstance(res, dict) and res.get("tool") and res["tool"] != "null":
            return res

        return None

    def _validate_tool_args(self, tool: Tool, args: Dict[str, Any]) -> Optional[str]:
        """Kiểm tra tính đầy đủ và hợp lệ của tham số công cụ dựa trên JSON Schema của Tool"""
        required = tool.parameters.get("required", [])
        for r in required:
            if r not in args or args[r] is None:
                return f"thiếu thông tin '{r}'"

        # Kiểm tra các trường số tiền
        for num_field in ("amount", "limit_amount", "target_amount", "balance"):
            if num_field in args and args[num_field] is not None:
                try:
                    val = float(args[num_field])
                    if num_field != "balance" and val <= 0:
                        return "số tiền phải lớn hơn 0"
                    elif num_field == "balance" and val < 0:
                        return "số dư ban đầu không được âm"
                except (ValueError, TypeError):
                    return f"giá trị '{num_field}' không hợp lệ"

        if tool.name == "delete_transaction":
            if not args.get("transaction_id"):
                return "chưa rõ mã ID giao dịch cần xóa"

        if tool.name == "update_transaction":
            if not args.get("transaction_id"):
                return "chưa rõ mã ID giao dịch cần sửa"

        if tool.name == "delete_wallet":
            if not args.get("wallet_name") and not args.get("wallet_id"):
                return "chưa rõ tên hoặc ID Túi Càn Khôn cần xóa"

        if tool.name == "delete_saving_goal":
            if not args.get("goal_name") and not args.get("goal_id") and not args.get("target_name"):
                return "chưa rõ mục tiêu tiết kiệm cần xóa"

        if tool.name == "delete_category":
            if not args.get("category_name") and not args.get("category_id"):
                return "chưa rõ danh mục cần xóa"

        if tool.name == "transfer_money":
            from_w = args.get("from_wallet_name") or args.get("from_wallet_id")
            to_w = args.get("to_wallet_name") or args.get("to_wallet_id")
            if not to_w:
                return "chưa rõ ví đích (ví dụ: Chuyển 500k cho ví Vietcombank hoặc từ ví A sang ví B)"

        if tool.name == "saving_goal_deposit":
            goal = args.get("goal_name") or args.get("goal_id") or args.get("target_name")
            if not goal:
                return "chưa rõ mục tiêu tiết kiệm nào cần tích lũy (ví dụ: Đưa 1 triệu vào mục tiêu mua laptop)"

        return None

    def _canonicalize_and_fill_tool_args(
        self,
        tool: Tool,
        raw_args: Dict[str, Any],
        raw_message: str = ""
    ) -> Dict[str, Any]:
        """Chuẩn hóa tên tham số (alias mapping), trích xuất bổ sung nếu thiếu và gán giá trị mặc định hợp lệ.
        Đảm bảo việc phân giải ngôn ngữ tự nhiên diễn ra trước khi kiểm tra hợp lệ (validation).
        """
        args = dict(raw_args)

        # 1. Alias mapping tổng quát cho các trường phổ biến
        alias_map = {
            "wallet_name": ["name", "wallet", "account_name", "w_name", "target_name", "ten_vi", "vi"],
            "balance": ["initial_balance", "initial_amount", "amount", "money", "so_du", "so_tien"],
            "amount": ["money", "value", "so_tien", "tien", "cost", "price", "deposit_amount"],
            "limit_amount": ["amount", "limit", "budget", "han_muc", "so_tien"],
            "target_amount": ["amount", "target", "muc_tieu", "so_tien", "goal_amount"],
            "category_name": ["category", "cat", "danh_muc", "ten_danh_muc", "loai"],
            "category_type": ["type", "cat_type", "kind", "loai_danh_muc"],
            "goal_name": ["target_name", "goal", "muc_tieu", "ten_muc_tieu"],
            "target_name": ["goal_name", "goal", "muc_tieu", "ten_muc_tieu", "name"],
            "from_wallet_name": ["from_wallet", "source_wallet", "from", "vi_nguon", "nguon"],
            "to_wallet_name": ["to_wallet", "destination_wallet", "to", "vi_dich", "dich"],
            "person_name": ["person", "debtor", "creditor", "name", "nguoi_vay", "nguoi_cho_vay", "doi_tac"],
            "note": ["description", "content", "noi_dung", "ghi_chu"],
            "transaction_date": ["date", "ngay", "ngay_giao_dich"],
            "transaction_id": ["txn_id", "tx_id", "id", "trans_id", "ma_giao_dich"]
        }

        for canonical, aliases in alias_map.items():
            if canonical not in args or args[canonical] is None or args[canonical] == "":
                for alias in aliases:
                    if alias in args and args[alias] is not None and args[alias] != "":
                        args[canonical] = args[alias]
                        break

        # 2. Xử lý đặc thù theo từng công cụ
        if tool.name in ("delete_transaction", "update_transaction"):
            if not args.get("transaction_id") and raw_message:
                m_id = re.search(r"#(\d+)|(?:giao dịch|gd|khoản|id)\s*(?:id|mã|so|số)?\s*#?(\d+)(?!\s*(?:k|nghìn|ngàn|tr|triệu|tỷ|đồng|đ|vnđ|vnd|củ|lít))\b", raw_message, re.IGNORECASE)
                if m_id:
                    args["transaction_id"] = int(m_id.group(1) or m_id.group(2))

        elif tool.name == "create_wallet":
            if not args.get("wallet_name") and raw_message:
                dyn = VietnameseFinancialParser.extract_dynamic_wallet_creation_args(raw_message)
                if dyn and dyn.get("wallet_name"):
                    args["wallet_name"] = dyn["wallet_name"]
                    if "balance" not in args or args["balance"] is None:
                        args["balance"] = dyn.get("balance", 0.0)
                    if "wallet_type" not in args or not args["wallet_type"]:
                        args["wallet_type"] = dyn.get("wallet_type", "cash")
                else:
                    cand = VietnameseFinancialParser.extract_wallet_name(raw_message)
                    if cand:
                        args["wallet_name"] = cand

            # Default balance = 0.0 nếu chưa có
            if "balance" not in args or args["balance"] is None:
                args["balance"] = 0.0

            # Default wallet_type nếu chưa có
            if not args.get("wallet_type"):
                w_lower = (args.get("wallet_name") or "").lower()
                if any(k in w_lower for k in ["momo", "zalopay", "zalo", "shopeepay", "viettelpay", "vnpay"]):
                    args["wallet_type"] = "e-wallet"
                elif any(k in w_lower for k in ["bank", "ngân hàng", "vcb", "mb", "vietcombank", "techcombank", "bidv", "acb", "tpbank", "vpbank"]):
                    args["wallet_type"] = "bank"
                elif any(k in w_lower for k in ["tiền mặt", "tien mat"]):
                    args["wallet_type"] = "cash"
                else:
                    args["wallet_type"] = "cash"

        elif tool.name == "create_saving_goal":
            if not args.get("target_name") and raw_message:
                cand_g = VietnameseFinancialParser.extract_goal_name(raw_message)
                if cand_g:
                    args["target_name"] = cand_g
            if "target_amount" not in args or args["target_amount"] is None:
                amt = VietnameseFinancialParser.parse_amount(raw_message)
                if amt:
                    args["target_amount"] = amt

        elif tool.name == "create_budget":
            if "limit_amount" not in args or args["limit_amount"] is None:
                amt = VietnameseFinancialParser.parse_amount(raw_message)
                if amt:
                    args["limit_amount"] = amt
            if not args.get("category_name") and raw_message:
                cat = VietnameseFinancialParser.guess_category(raw_message)
                if cat:
                    args["category_name"] = cat
            if not args.get("month_year"):
                p = VietnameseFinancialParser.parse_period(raw_message)
                args["month_year"] = p or "this_month"

        elif tool.name == "create_debt":
            if "amount" not in args or args["amount"] is None:
                amt = VietnameseFinancialParser.parse_amount(raw_message)
                if amt:
                    args["amount"] = amt
            if not args.get("person_name") and raw_message:
                p_cand = VietnameseFinancialParser.extract_person_name(raw_message)
                args["person_name"] = p_cand or "Đối tác"
            elif not args.get("person_name"):
                args["person_name"] = "Đối tác"
            if not args.get("debt_type"):
                args["debt_type"] = "BORROW"
            if not args.get("note"):
                args["note"] = raw_message.strip()

        elif tool.name in ("create_expense", "create_income"):
            if "amount" not in args or args["amount"] is None:
                amt = VietnameseFinancialParser.parse_amount(raw_message)
                if amt:
                    args["amount"] = amt
            if not args.get("note"):
                args["note"] = raw_message.strip()
            if not args.get("transaction_date"):
                args["transaction_date"] = VietnameseFinancialParser.parse_date(raw_message)
        elif tool.name == "transfer_money":
            amt = VietnameseFinancialParser.parse_amount(raw_message)
            if amt and amt > 0:
                args["amount"] = amt
            if raw_message:
                fw, tw = VietnameseFinancialParser.extract_transfer_wallets(raw_message)
                if fw:
                    args["from_wallet_name"] = fw
                if tw:
                    args["to_wallet_name"] = tw
            if not args.get("note"):
                args["note"] = raw_message.strip()

        elif tool.name == "create_category":
            if raw_message:
                ext = VietnameseFinancialParser.extract_category_creation_args(raw_message)
                if not args.get("category_name") and ext.get("category_name"):
                    args["category_name"] = ext["category_name"]
                if not args.get("category_type") and ext.get("category_type"):
                    args["category_type"] = ext["category_type"]
            if args.get("category_name") and args.get("category_type"):
                if not args.get("icon") or args.get("icon") == "📦":
                    args["icon"] = resolve_category_icon(args["category_name"], args["category_type"])

        elif tool.name == "delete_category":
            if not args.get("category_name") and raw_message:
                ext = VietnameseFinancialParser.extract_category_delete_args(raw_message)
                if ext.get("category_name"):
                    args["category_name"] = ext["category_name"]

        return args

    def _resolve_wallet_for_transfer(
        self,
        user_id: int,
        wallet_query: Optional[str],
        is_destination: bool = False,
        user_name: str = "Ký Chủ"
    ) -> Dict[str, Any]:
        """Phân giải thực thể ví cho giao dịch chuyển tiền (Transfer Wallet Entity Resolution).
        Trả về dictionary:
        {
            "status": "RESOLVED" | "AMBIGUOUS" | "NOT_FOUND" | "MISSING",
            "wallet": {...},
            "wallets": [...],
            "message": "..."
        }
        """
        import main
        if not wallet_query or not str(wallet_query).strip():
            return {
                "status": "MISSING",
                "message": f"Chưa rõ ví {'đích' if is_destination else 'nguồn'}."
            }

        q = str(wallet_query).strip().lower()
        q_unacc = remove_accents(q)

        with main.get_db() as conn:
            rows = conn.execute(
                "SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE user_id = ?",
                (user_id,)
            ).fetchall()
            wallets = [dict(r) for r in rows]

        if not wallets:
            return {
                "status": "NOT_FOUND",
                "message": f"{user_name} hiện chưa có Túi Càn Khôn nào trong hệ thống."
            }

        # 1. Trực tiếp theo ID nếu chuỗi là số thuần túy
        if q.isdigit():
            target_id = int(q)
            w_by_id = next((w for w in wallets if w["id"] == target_id), None)
            if w_by_id:
                return {"status": "RESOLVED", "wallet": w_by_id}

        # 2. Xử lý từ khóa ví không tồn tại minh thị
        if any(k in q for k in ["không tồn tại", "khong ton tai"]):
            return {
                "status": "NOT_FOUND",
                "is_generic": True,
                "message": f"Không tìm thấy ví '{wallet_query}' trong danh sách ví của bạn."
            }

        # 3. Khớp chính xác hoặc gần đúng theo TÊN VÍ CỤ THỂ trước (MoMo, Vietcombank, MB Bank, ...)
        matched = [w for w in wallets if _match_wallet_name(q, w["wallet_name"])]
        if len(matched) == 1:
            return {"status": "RESOLVED", "wallet": matched[0]}
        elif len(matched) > 1:
            list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched))
            return {
                "status": "AMBIGUOUS",
                "wallets": matched,
                "message": f"Có {len(matched)} ví phù hợp với '{wallet_query}':\n{list_str}\n\n{user_name} muốn chọn ví nào?"
            }

        # 3.b Khớp substring không dấu theo tên ví
        matched_unacc = [
            w for w in wallets
            if q_unacc in remove_accents(w["wallet_name"].lower())
            or remove_accents(w["wallet_name"].lower()) in q_unacc
        ]
        if len(matched_unacc) == 1:
            return {"status": "RESOLVED", "wallet": matched_unacc[0]}
        elif len(matched_unacc) > 1:
            list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched_unacc))
            return {
                "status": "AMBIGUOUS",
                "wallets": matched_unacc,
                "message": f"Có {len(matched_unacc)} ví phù hợp với '{wallet_query}':\n{list_str}\n\n{user_name} muốn chọn ví nào?"
            }

        # 4. Khi không khớp tên ví cụ thể -> Xử lý từ khóa loại ví CHUNG (Generic Categories)
        # 4.a "tiền mặt" (Cash)
        cash_keywords = ["tiền mặt", "tien mat", "ví tiền mặt", "vi tien mat", "tiền mặt cá nhân", "tien mat ca nhan"]
        if q in cash_keywords or q == "tiền mặt" or q == "tien mat":
            matched_cash = [
                w for w in wallets
                if "tiền mặt" in w["wallet_name"].lower()
                or "tien mat" in remove_accents(w["wallet_name"].lower())
            ]
            if len(matched_cash) == 1:
                return {"status": "RESOLVED", "wallet": matched_cash[0]}
            elif len(matched_cash) > 1:
                list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched_cash))
                return {
                    "status": "AMBIGUOUS",
                    "wallets": matched_cash,
                    "message": f"Có {len(matched_cash)} ví tiền mặt:\n{list_str}\n\n{user_name} muốn chuyển tiền {'sang' if is_destination else 'từ'} ví nào?"
                }
            else:
                return {
                    "status": "NOT_FOUND",
                    "is_generic": True,
                    "message": f"Không tìm thấy ví '{wallet_query}' trong danh sách ví của bạn. (Hệ thống không tự ý tạo ví mới)."
                }

        # 4.b "ngân hàng" (Bank)
        bank_keywords = ["ngân hàng", "ngan hang", "ví ngân hàng", "vi ngan hang", "tài khoản ngân hàng", "tai khoan ngan hang", "bank"]
        if q in bank_keywords:
            matched_bank = [
                w for w in wallets
                if (w.get("wallet_type") or "").lower() in ("bank", "ngan_hang")
                or any(k in w["wallet_name"].lower() for k in ["ngân hàng", "ngan hang", "bank", "vcb", "vietcombank", "techcombank", "mb", "bidv", "agribank", "acb", "tpbank", "vpbank"])
            ]
            if len(matched_bank) == 1:
                return {"status": "RESOLVED", "wallet": matched_bank[0]}
            elif len(matched_bank) > 1:
                list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched_bank))
                return {
                    "status": "AMBIGUOUS",
                    "wallets": matched_bank,
                    "message": f"Có {len(matched_bank)} ví ngân hàng:\n{list_str}\n\n{user_name} muốn chọn ví nào?"
                }
            else:
                return {
                    "status": "NOT_FOUND",
                    "is_generic": True,
                    "message": "Không tìm thấy ví ngân hàng nào trong danh sách ví của bạn."
                }

        # 4.c "ví điện tử" (E-Wallet)
        ewallet_keywords = ["ví điện tử", "vi dien tu", "điện tử", "dien tu", "e-wallet", "ewallet"]
        if q in ewallet_keywords:
            matched_ew = [
                w for w in wallets
                if (w.get("wallet_type") or "").lower() in ("e-wallet", "ewallet", "vi_dien_tu", "e_wallet")
                or any(k in w["wallet_name"].lower() for k in ["ví điện tử", "vi dien tu", "momo", "zalopay", "zalo", "shopeepay", "viettelpay", "vnpay"])
            ]
            if len(matched_ew) == 1:
                return {"status": "RESOLVED", "wallet": matched_ew[0]}
            elif len(matched_ew) > 1:
                list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched_ew))
                return {
                    "status": "AMBIGUOUS",
                    "wallets": matched_ew,
                    "message": f"Có {len(matched_ew)} ví điện tử:\n{list_str}\n\n{user_name} muốn chọn ví nào?"
                }
            else:
                return {
                    "status": "NOT_FOUND",
                    "is_generic": True,
                    "message": f"Không tìm thấy ví '{wallet_query}' trong danh sách ví của bạn."
                }

        return {
            "status": "NOT_FOUND",
            "is_generic": False,
            "message": f"Không tìm thấy ví '{wallet_query}' trong danh sách ví của bạn. (Hệ thống không tự ý tạo ví mới)."
        }

    def _check_pending_completeness(
        self,
        user_id: int,
        pending: Dict[str, Any],
        user_name: str = "Ký Chủ"
    ) -> Tuple[bool, Optional[str]]:
        """Kiểm tra xem hành động đang chờ đã đủ tất cả tham số bắt buộc để vào trạng thái CONFIRMING chưa.
        Trả về (is_complete, missing_param_name)
        """
        if not pending or not isinstance(pending, dict):
            return False, None

        tool_name = pending.get("tool_name")
        args = pending.get("args", {})

        if tool_name == "transfer_money":
            amt = args.get("amount")
            if not amt or amt <= 0:
                return False, "amount"

            import main
            from_id = args.get("from_wallet_id")
            from_name = args.get("from_wallet_name")
            to_id = args.get("to_wallet_id")
            to_name = args.get("to_wallet_name")

            if (not from_id and not from_name) and (to_id or to_name):
                res_to = self._resolve_wallet_for_transfer(user_id, to_name or str(to_id), is_destination=True, user_name=user_name)
                if res_to.get("status") == "RESOLVED":
                    args["to_wallet_id"] = res_to["wallet"]["id"]
                    args["to_wallet_name"] = res_to["wallet"]["wallet_name"]
                    with main.get_db() as conn:
                        user_wallets = [dict(r) for r in conn.execute("SELECT id, wallet_name, wallet_type FROM wallets WHERE user_id = ?", (user_id,)).fetchall()]
                    other_wallets = [w for w in user_wallets if w["id"] != res_to["wallet"]["id"]]
                    if len(other_wallets) == 1:
                        args["from_wallet_id"] = other_wallets[0]["id"]
                        args["from_wallet_name"] = other_wallets[0]["wallet_name"]
                        from_id = args["from_wallet_id"]
                        from_name = args["from_wallet_name"]

            elif (from_id or from_name) and (not to_id and not to_name):
                res_from = self._resolve_wallet_for_transfer(user_id, from_name or str(from_id), is_destination=False, user_name=user_name)
                if res_from.get("status") == "RESOLVED":
                    args["from_wallet_id"] = res_from["wallet"]["id"]
                    args["from_wallet_name"] = res_from["wallet"]["wallet_name"]
                    with main.get_db() as conn:
                        user_wallets = [dict(r) for r in conn.execute("SELECT id, wallet_name, wallet_type FROM wallets WHERE user_id = ?", (user_id,)).fetchall()]
                    other_wallets = [w for w in user_wallets if w["id"] != res_from["wallet"]["id"]]
                    if len(other_wallets) == 1:
                        args["to_wallet_id"] = other_wallets[0]["id"]
                        args["to_wallet_name"] = other_wallets[0]["wallet_name"]
                        to_id = args["to_wallet_id"]
                        to_name = args["to_wallet_name"]

            if not from_id:
                if not from_name:
                    return False, "from_wallet_name"
                res_from = self._resolve_wallet_for_transfer(user_id, from_name, is_destination=False, user_name=user_name)
                if res_from["status"] == "RESOLVED":
                    args["from_wallet_id"] = res_from["wallet"]["id"]
                    args["from_wallet_name"] = res_from["wallet"]["wallet_name"]
                elif res_from["status"] == "AMBIGUOUS":
                    pending["ambiguous_candidates"] = res_from.get("wallets")
                    return False, "from_wallet_name"
                else:
                    return False, "from_wallet_name"

            to_id = args.get("to_wallet_id")
            to_name = args.get("to_wallet_name")
            if not to_id:
                if not to_name:
                    return False, "to_wallet_name"
                res_to = self._resolve_wallet_for_transfer(user_id, to_name, is_destination=True, user_name=user_name)
                if res_to["status"] == "RESOLVED":
                    args["to_wallet_id"] = res_to["wallet"]["id"]
                    args["to_wallet_name"] = res_to["wallet"]["wallet_name"]
                elif res_to["status"] == "AMBIGUOUS":
                    pending["ambiguous_candidates"] = res_to.get("wallets")
                    return False, "to_wallet_name"
                else:
                    return False, "to_wallet_name"

            return True, None

        elif tool_name in ("delete_wallet", "update_wallet"):
            if not args.get("wallet_name") and not args.get("wallet_id"):
                return False, "wallet_name"
            return True, None

        elif tool_name in ("create_expense", "create_income"):
            amt = args.get("amount")
            if not amt or float(amt) <= 0:
                return False, "amount"
            if not args.get("note") and not args.get("category_name"):
                return False, "note"
            # Tự động gán note = category_name nếu thiếu note
            if not args.get("note") and args.get("category_name"):
                args["note"] = args["category_name"]
            # Tự động đoán category_name nếu thiếu category_name
            if not args.get("category_name") and args.get("note"):
                guessed = VietnameseFinancialParser.guess_category(args["note"])
                if guessed:
                    args["category_name"] = guessed
            return True, None

        elif tool_name == "create_debt":
            amt = args.get("amount")
            if not amt or amt <= 0:
                return False, "amount"
            return True, None

        elif tool_name == "create_budget":
            cat = args.get("category_name")
            if not cat or not str(cat).strip():
                return False, "category_name"
            amt = args.get("limit_amount")
            if not amt or amt <= 0:
                return False, "limit_amount"
            return True, None

        elif tool_name == "create_saving_goal":
            name = args.get("target_name")
            amt = args.get("target_amount")
            if not name and (not amt or float(amt) <= 0):
                return False, "goal_details"
            if not name or not str(name).strip():
                return False, "target_name"
            if not amt or float(amt) <= 0:
                return False, "target_amount"
            return True, None

        elif tool_name in ("delete_debt", "settle_debt"):
            if not args.get("debt_id") and not args.get("person_name"):
                return False, "debt_selection"
            return True, None

        elif tool_name in ("delete_budget", "update_budget"):
            if not args.get("budget_id") and not args.get("category_name"):
                return False, "budget_selection"
            return True, None

        elif tool_name == "create_category":
            c_type = args.get("category_type")
            c_name = args.get("category_name")
            if not c_type:
                return False, "category_type"
            if not c_name or not str(c_name).strip():
                return False, "category_name"
            if not args.get("icon") or args.get("icon") == "📦":
                args["icon"] = resolve_category_icon(c_name, c_type)
            return True, None

        elif tool_name == "delete_category":
            if not args.get("category_id") and not args.get("category_name"):
                return False, "category_name"
            return True, None

        return True, None

    def _merge_followup_parameter(
        self,
        user_id: int,
        pending: Dict[str, Any],
        text: str,
        user_name: str = "Ký Chủ"
    ) -> Tuple[bool, str]:
        """Trộn tham số trả lời tiếp theo từ người dùng vào hành động đang chờ (Follow-up Parameter Merging).
        Trả về (success, message_or_error)
        """
        if not pending or not isinstance(pending, dict):
            return False, "Không có thao tác nào đang chờ."

        tool_name = pending.get("tool_name")
        args = pending.get("args", {})
        missing = pending.get("missing_param")

        if tool_name in ("delete_wallet", "update_wallet", "get_wallets"):
            import main
            idx = VietnameseFinancialParser.extract_selection_index(text)
            amb_list = pending.get("ambiguous_candidates")
            if idx is not None and amb_list and 1 <= idx <= len(amb_list):
                selected = amb_list[idx - 1]
                args["wallet_id"] = selected["id"]
                args["wallet_name"] = selected["wallet_name"]
                pending["missing_param"] = None
                pending["ambiguous_candidates"] = None
                return True, ""

            clean_w = text
            for kw in ["xóa ví", "xoa vi", "hủy ví", "huy vi", "xóa", "xoa", "chọn", "chon", "ví", "vi", "túi", "tui"]:
                clean_w = re.sub(rf"\b{re.escape(kw)}\b", "", clean_w, flags=re.IGNORECASE)
            clean_w = clean_w.strip(" .,-")

            with main.get_db() as conn:
                rows = conn.execute(
                    "SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE user_id = ?",
                    (user_id,)
                ).fetchall()
                wallets = [dict(r) for r in rows]

            matched = [w for w in wallets if _match_wallet_name(clean_w, w["wallet_name"])]
            if len(matched) == 1:
                args["wallet_id"] = matched[0]["id"]
                args["wallet_name"] = matched[0]["wallet_name"]
                pending["missing_param"] = None
                pending["ambiguous_candidates"] = None
                return True, ""
            elif len(matched) > 1:
                pending["ambiguous_candidates"] = matched
                list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched))
                return False, f"Có {len(matched)} ví tên {clean_w}:\n{list_str}\n\n{user_name} muốn thao tác với ví nào?"

        if tool_name == "transfer_money":
            merged_anything = False
            amt = VietnameseFinancialParser.parse_amount(text)
            if amt and amt > 0:
                args["amount"] = amt
                if missing == "amount":
                    pending["missing_param"] = None
                merged_anything = True

            fw, tw = VietnameseFinancialParser.extract_transfer_wallets(text)
            if fw:
                res_fw = self._resolve_wallet_for_transfer(user_id, fw, is_destination=False, user_name=user_name)
                if res_fw["status"] == "RESOLVED":
                    args["from_wallet_id"] = res_fw["wallet"]["id"]
                    args["from_wallet_name"] = res_fw["wallet"]["wallet_name"]
                    merged_anything = True
            if tw:
                res_tw = self._resolve_wallet_for_transfer(user_id, tw, is_destination=True, user_name=user_name)
                if res_tw["status"] == "RESOLVED":
                    args["to_wallet_id"] = res_tw["wallet"]["id"]
                    args["to_wallet_name"] = res_tw["wallet"]["wallet_name"]
                    merged_anything = True

            idx = VietnameseFinancialParser.extract_selection_index(text)
            amb_list = pending.get("ambiguous_candidates")
            if idx is not None and amb_list and 1 <= idx <= len(amb_list):
                selected = amb_list[idx - 1]
                if missing == "from_wallet_name" or not args.get("from_wallet_id"):
                    args["from_wallet_id"] = selected["id"]
                    args["from_wallet_name"] = selected["wallet_name"]
                elif missing == "to_wallet_name" or not args.get("to_wallet_id"):
                    args["to_wallet_id"] = selected["id"]
                    args["to_wallet_name"] = selected["wallet_name"]
                pending["missing_param"] = None
                pending["ambiguous_candidates"] = None
                return True, ""

            if not fw and not tw and not merged_anything:
                is_dest = (missing == "to_wallet_name")
                res_w = self._resolve_wallet_for_transfer(user_id, text, is_destination=is_dest, user_name=user_name)
                if res_w["status"] == "RESOLVED":
                    w = res_w["wallet"]
                    if is_dest or (args.get("from_wallet_id") and not args.get("to_wallet_id")):
                        args["to_wallet_id"] = w["id"]
                        args["to_wallet_name"] = w["wallet_name"]
                    else:
                        args["from_wallet_id"] = w["id"]
                        args["from_wallet_name"] = w["wallet_name"]
                    pending["missing_param"] = None
                    pending["ambiguous_candidates"] = None
                    return True, ""
                elif res_w["status"] == "AMBIGUOUS":
                    pending["ambiguous_candidates"] = res_w["wallets"]
                    return False, res_w["message"]
                elif res_w["status"] == "NOT_FOUND":
                    return False, res_w["message"]

            if merged_anything:
                pending["ambiguous_candidates"] = None
                return True, ""

        # Debt selection follow-up
        if tool_name in ("delete_debt", "settle_debt") or missing == "debt_selection":
            idx = VietnameseFinancialParser.extract_selection_index(text)
            amb_list = pending.get("ambiguous_candidates")
            if idx is not None and amb_list and 1 <= idx <= len(amb_list):
                selected = amb_list[idx - 1]
                args["debt_id"] = selected["id"]
                args["person_name"] = selected["person_name"]
                args["amount"] = selected.get("amount")
                args["debt_type"] = selected.get("debt_type")
                pending["missing_param"] = None
                pending["ambiguous_candidates"] = None
                return True, ""
            p_cand = VietnameseFinancialParser.extract_person_name(text) or text.strip()
            clean_p = p_cand
            for stop in ["xóa nợ", "xoa no", "khoản nợ", "khoan no", "nợ của", "no cua", "khoản của", "khoan cua"]:
                clean_p = re.sub(rf"\b{re.escape(stop)}\b", "", clean_p, flags=re.IGNORECASE).strip()
            if clean_p and len(clean_p) > 1:
                args["person_name"] = clean_p
                pending["missing_param"] = None
                return True, ""

        # Budget creation follow-up
        if tool_name == "create_budget":
            updated = False
            if missing == "category_name" or not args.get("category_name"):
                cat = VietnameseFinancialParser.guess_category(text)
                if not cat:
                    clean_c = text.strip()
                    for stop in ["danh mục", "mục", "hạn mức", "ngân sách", "cho", "của"]:
                        clean_c = re.sub(rf"\b{re.escape(stop)}\b", "", clean_c, flags=re.IGNORECASE).strip()
                    cat = clean_c.title() if clean_c else None
                if cat:
                    args["category_name"] = cat
                    if missing == "category_name":
                        pending["missing_param"] = None
                    updated = True
            if missing == "limit_amount" or not args.get("limit_amount") or args.get("limit_amount", 0) <= 0:
                amt = VietnameseFinancialParser.parse_amount(text)
                if amt and amt > 0:
                    args["limit_amount"] = amt
                    if missing == "limit_amount":
                        pending["missing_param"] = None
                    updated = True
            if updated:
                return True, ""

        # Saving goal creation follow-up
        if tool_name == "create_saving_goal":
            amt = VietnameseFinancialParser.parse_amount(text)
            existing_name = args.get("target_name")
            existing_amt = args.get("target_amount")

            # Trường hợp 1: Đang chờ số tiền (missing == "target_amount" hoặc đã có tên nhưng chưa có tiền)
            if missing == "target_amount" or (existing_name and (not existing_amt or float(existing_amt) <= 0)):
                if amt and amt > 0:
                    args["target_amount"] = amt
                    pending["missing_param"] = None
                    return True, ""
                return False, f"Khí Linh chưa nhận diện được số tiền. {user_name} vui lòng cho biết số tiền Linh Thạch dự định tiết kiệm (ví dụ: 1 triệu, 20 triệu)."

            # Trường hợp 2: Đang chờ tên mục tiêu (missing == "target_name" hoặc đã có tiền nhưng chưa có tên)
            if missing == "target_name" or (existing_amt and float(existing_amt) > 0 and not existing_name):
                # Nếu người dùng lại nhập số tiền thuần túy mà không có tên mục tiêu -> cập nhật lại số tiền
                if amt and amt > 0 and not any(w in text.lower() for w in ["mua", "xe", "nhà", "nha", "du lịch", "du lich", "laptop", "iphone", "điện thoại", "dien thoai", "hoc", "học", "cưới", "cuoi", "đổi", "doi"]):
                    args["target_amount"] = amt
                    pending["missing_param"] = "target_name"
                    return True, ""

                cand_goal = VietnameseFinancialParser.extract_goal_name(text)
                if not cand_goal:
                    clean_t = text.strip()
                    clean_t = re.sub(r"\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?\b", "", clean_t, flags=re.IGNORECASE).strip(" .,-")
                    for stop in [
                        "mục tiêu là", "mục tiêu", "muc tieu", "tên là", "ten la",
                        "đặt là", "đặt tên là", "muốn", "để", "cho", "nhé", "nha", "đi", "giúp"
                    ]:
                        clean_t = re.sub(rf"\b{re.escape(stop)}\b", "", clean_t, flags=re.IGNORECASE).strip()
                    if clean_t and len(clean_t) >= 2 and not clean_t.isdigit() and not VietnameseFinancialParser.parse_amount(clean_t):
                        cand_goal = clean_t.title() if clean_t.islower() else clean_t

                if cand_goal and cand_goal.lower() not in ["thì", "mới", "nào", "gì"] and not VietnameseFinancialParser.parse_amount(cand_goal):
                    args["target_name"] = cand_goal
                    pending["missing_param"] = None
                    return True, ""
                return False, f"Khí Linh chưa nhận diện được tên mục tiêu. {user_name} muốn đặt tên cho mục tiêu là gì (ví dụ: mua xe, du lịch, mua iphone)?"

            # Trường hợp 3: Chưa có cả tên lẫn số tiền (missing == "goal_details")
            updated = False
            if amt and amt > 0:
                args["target_amount"] = amt
                updated = True

            cand_goal = VietnameseFinancialParser.extract_goal_name(text)
            if not cand_goal:
                clean_t = text.strip()
                clean_t = re.sub(r"\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?\b", "", clean_t, flags=re.IGNORECASE).strip(" .,-")
                for stop in [
                    "mục tiêu là", "mục tiêu", "muc tieu", "tên là", "ten la",
                    "đặt là", "đặt tên là", "muốn", "để", "cho", "nhé", "nha", "đi", "giúp"
                ]:
                    clean_t = re.sub(rf"\b{re.escape(stop)}\b", "", clean_t, flags=re.IGNORECASE).strip()
                if clean_t and len(clean_t) >= 2 and not clean_t.isdigit() and not VietnameseFinancialParser.parse_amount(clean_t):
                    cand_goal = clean_t.title() if clean_t.islower() else clean_t

            if cand_goal and cand_goal.lower() not in ["thì", "mới", "nào", "gì"] and not VietnameseFinancialParser.parse_amount(cand_goal):
                args["target_name"] = cand_goal
                updated = True

            if updated:
                if args.get("target_name") and args.get("target_amount") and float(args.get("target_amount", 0)) > 0:
                    pending["missing_param"] = None
                elif args.get("target_name"):
                    pending["missing_param"] = "target_amount"
                elif args.get("target_amount"):
                    pending["missing_param"] = "target_name"
                return True, ""

        # Expense & Income creation follow-up
        if tool_name in ("create_expense", "create_income"):
            amt = VietnameseFinancialParser.parse_amount(text)
            w_name = VietnameseFinancialParser.extract_wallet_name(text)
            cat_guess = VietnameseFinancialParser.guess_category(text)
            updated = False

            if w_name:
                args["wallet_name"] = w_name
                updated = True

            if amt and amt > 0:
                args["amount"] = amt
                updated = True
                clean_n = text
                clean_n = re.sub(r"\b\d+[\d.,]*\s*(?:chục\s*)?(?:k|nghìn|nghin|ngàn|ngan|tr|triệu|trieu|củ|tỷ|ty|vnđ|vnd|đ|đồng)?\b", "", clean_n, flags=re.IGNORECASE).strip(" .,-")
                for stop in ["tiêu", "chi", "cho", "thu", "nhận", "đồng", "vnđ", "tiền", "năm chục", "ăn", "uống"]:
                    clean_n = re.sub(rf"\b{re.escape(stop)}\b", "", clean_n, flags=re.IGNORECASE).strip()
                if cat_guess:
                    args["category_name"] = cat_guess
                if clean_n and len(clean_n) >= 2 and not clean_n.isdigit() and not VietnameseFinancialParser.parse_amount(clean_n):
                    args["note"] = clean_n.capitalize()
                elif cat_guess and not args.get("note"):
                    args["note"] = cat_guess

            # Nếu người dùng trả lời cho câu hỏi về mục đích/nội dung (ví dụ: "ăn sáng", "mua sắm", "tiền lương")
            if not amt or amt <= 0:
                clean_n = text.strip(" .,-")
                for stop in ["dùng cho việc", "dùng cho", "dùng để", "dùng vào", "cho việc", "cho", "việc", "tiền", "là", "khoản", "mục"]:
                    clean_n = re.sub(rf"\b{re.escape(stop)}\b", "", clean_n, flags=re.IGNORECASE).strip()
                if cat_guess:
                    args["category_name"] = cat_guess
                    updated = True
                if clean_n and len(clean_n) >= 2:
                    args["note"] = clean_n.capitalize()
                    updated = True
                elif cat_guess:
                    args["note"] = cat_guess
                    updated = True

            if updated:
                if args.get("amount") and float(args.get("amount", 0)) > 0:
                    if args.get("note") or args.get("category_name"):
                        pending["missing_param"] = None
                    else:
                        pending["missing_param"] = "note"
                else:
                    pending["missing_param"] = "amount"
                return True, ""

        # Budget selection follow-up
        if tool_name in ("delete_budget", "update_budget") or missing == "budget_selection":
            idx = VietnameseFinancialParser.extract_selection_index(text)
            amb_list = pending.get("ambiguous_candidates")
            if idx is not None and amb_list and 1 <= idx <= len(amb_list):
                selected = amb_list[idx - 1]
                args["budget_id"] = selected["id"]
                args["category_name"] = selected["category_name"]
                args["limit_amount"] = selected.get("limit_amount")
                args["month_year"] = selected.get("month_year")
                pending["missing_param"] = None
                pending["ambiguous_candidates"] = None
                return True, ""
            cat = VietnameseFinancialParser.guess_category(text)
            if not cat:
                clean_c = text.strip()
                for stop in ["xóa hạn mức", "xóa ngân sách", "hạn mức", "ngân sách", "mục", "danh mục"]:
                    clean_c = re.sub(rf"\b{re.escape(stop)}\b", "", clean_c, flags=re.IGNORECASE).strip()
                cat = clean_c.title() if clean_c else None
            if cat:
                args["category_name"] = cat
        # Category creation follow-up
        if tool_name == "create_category":
            raw_t = text.strip()
            lower_t = raw_t.lower()

            is_chi = any(w in lower_t for w in ["chi", "chi tiêu", "khoản chi", "khoan chi", "expense"]) and not any(w in lower_t for w in ["thu chi", "thu/chi", "thu và chi"])
            is_thu = any(w in lower_t for w in ["thu", "thu nhập", "khoản thu", "khoan thu", "income"]) and not any(w in lower_t for w in ["thu chi", "thu/chi", "thu và chi"])

            updated = False
            if is_chi:
                args["category_type"] = "EXPENSE"
                if missing == "category_type":
                    pending["missing_param"] = None
                updated = True
            elif is_thu:
                args["category_type"] = "INCOME"
                if missing == "category_type":
                    pending["missing_param"] = None
                updated = True

            name_cand = raw_t
            for stop in [
                "danh mục", "danh muc", "mục", "muc", "tên là", "ten la", "đặt là", "dat la",
                "tên", "ten", "loại chi", "loai chi", "loại thu", "loai thu", "khoản chi", "khoan chi",
                "khoản thu", "khoan thu", "chi tiêu", "chi tieu", "thu nhập", "thu nhap"
            ]:
                name_cand = re.sub(rf"\b{re.escape(stop)}\b", "", name_cand, flags=re.IGNORECASE).strip(" .,-")

            if name_cand and name_cand.lower() not in ["thu", "chi", "thu chi", "có", "xác nhận", "hủy", "thì", "mới", "nào"]:
                args["category_name"] = name_cand.title()
                if missing == "category_name":
                    pending["missing_param"] = None
                updated = True

            if updated:
                if args.get("category_name") and args.get("category_type"):
                    if not args.get("icon") or args.get("icon") == "📦":
                        args["icon"] = resolve_category_icon(args["category_name"], args["category_type"])
                    pending["missing_param"] = None
                elif not args.get("category_type"):
                    pending["missing_param"] = "category_type"
                elif not args.get("category_name"):
                    pending["missing_param"] = "category_name"
                return True, ""

        # Category delete follow-up
        if tool_name == "delete_category":
            idx = VietnameseFinancialParser.extract_selection_index(text)
            amb_list = pending.get("ambiguous_candidates")
            if idx is not None and amb_list and 1 <= idx <= len(amb_list):
                selected = amb_list[idx - 1]
                args["category_id"] = selected["id"]
                args["category_name"] = selected["category_name"]
                args["category_type"] = selected.get("category_type")
                pending["missing_param"] = None
                pending["ambiguous_candidates"] = None
                return True, ""

            if amb_list:
                is_chi = "chi" in text.lower()
                is_thu = "thu" in text.lower()
                filtered = [c for c in amb_list if (is_chi and c["category_type"] == "EXPENSE") or (is_thu and c["category_type"] == "INCOME")]
                if len(filtered) == 1:
                    args["category_id"] = filtered[0]["id"]
                    args["category_name"] = filtered[0]["category_name"]
                    args["category_type"] = filtered[0]["category_type"]
                    pending["missing_param"] = None
                    pending["ambiguous_candidates"] = None
                    return True, ""

            clean_name = text.strip()
            for stop in ["danh mục", "mục", "xóa", "hủy", "bỏ"]:
                clean_name = re.sub(rf"\b{re.escape(stop)}\b", "", clean_name, flags=re.IGNORECASE).strip(" .,-")
            if clean_name and len(clean_name) >= 2:
                args["category_name"] = clean_name
                pending["missing_param"] = None
                return True, ""

        # Các tool khác (generic amount fallback)
        amt = VietnameseFinancialParser.parse_amount(text)
        if amt and amt > 0:
            for amt_field in ("amount", "limit_amount", "target_amount", "balance"):
                if amt_field in args and (args[amt_field] is None or args[amt_field] <= 0):
                    args[amt_field] = amt
                    pending["missing_param"] = None
                    return True, ""

        return False, "Khí Linh chưa nhận diện được thông tin cung cấp. Ký Chủ vui lòng nêu rõ hơn."

    async def _check_entity_ambiguity(
        self,
        user_id: int,
        tool_name: str,
        args: Dict[str, Any],
        user_name: str = "Ký Chủ"
    ) -> Optional[str]:
        """Kiểm tra và phân giải thực thể động từ cơ sở dữ liệu.
        Nếu tìm thấy duy nhất 1 thực thể -> tự động gắn ID và tên chuẩn hóa.
        Nếu tìm thấy nhiều thực thể trùng khớp -> trả về câu hỏi làm rõ, tuyệt đối không đoán.
        """
        import main

        # A. WALLET ENTITY RESOLUTION
        # Áp dụng cho delete_wallet, update_wallet, get_wallets
        if tool_name in ("delete_wallet", "update_wallet", "get_wallets"):
            w_query = args.get("wallet_name")
            w_id = args.get("wallet_id")
            if w_query and not w_id:
                with main.get_db() as conn:
                    rows = conn.execute(
                        "SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE user_id = ?",
                        (user_id,)
                    ).fetchall()
                    wallets = [dict(r) for r in rows]

                matched = [w for w in wallets if _match_wallet_name(w_query, w["wallet_name"])]
                if len(matched) > 1:
                    list_str = "\n".join(f"{i+1}. {w['wallet_name']}" for i, w in enumerate(matched))
                    return (
                        f"Có {len(matched)} ví tên {w_query}:\n"
                        f"{list_str}\n\n"
                        f"{user_name} muốn thao tác với ví nào?"
                    )
                elif len(matched) == 1:
                    args["wallet_id"] = matched[0]["id"]
                    args["wallet_name"] = matched[0]["wallet_name"]

        # B. TRANSFER WALLETS RESOLUTION
        elif tool_name == "transfer_money":
            from_name = args.get("from_wallet_name")
            from_id = args.get("from_wallet_id")
            to_name = args.get("to_wallet_name")
            to_id = args.get("to_wallet_id")

            if from_name and not from_id:
                res_from = self._resolve_wallet_for_transfer(user_id, from_name, is_destination=False, user_name=user_name)
                if res_from["status"] == "AMBIGUOUS":
                    args["_ambiguous_from"] = res_from.get("wallets")
                    return res_from["message"]
                elif res_from["status"] == "NOT_FOUND" and res_from.get("is_generic"):
                    args["_not_found_wallet"] = from_name
                    return res_from["message"]
                elif res_from["status"] == "RESOLVED":
                    args["from_wallet_id"] = res_from["wallet"]["id"]
                    args["from_wallet_name"] = res_from["wallet"]["wallet_name"]

            if to_name and not to_id:
                res_to = self._resolve_wallet_for_transfer(user_id, to_name, is_destination=True, user_name=user_name)
                if res_to["status"] == "AMBIGUOUS":
                    args["_ambiguous_to"] = res_to.get("wallets")
                    return res_to["message"]
                elif res_to["status"] == "NOT_FOUND" and res_to.get("is_generic"):
                    args["_not_found_wallet"] = to_name
                    return res_to["message"]
                elif res_to["status"] == "RESOLVED":
                    args["to_wallet_id"] = res_to["wallet"]["id"]
                    args["to_wallet_name"] = res_to["wallet"]["wallet_name"]

        # C. SAVING GOAL RESOLUTION
        elif tool_name in ("saving_goal_deposit", "saving_goal_withdraw", "update_saving_goal", "delete_saving_goal"):
            g_name = args.get("goal_name") or args.get("target_name")
            g_id = args.get("goal_id")
            if g_name and not g_id:
                with main.get_db() as conn:
                    rows = conn.execute(
                        "SELECT id, target_name, current_amount, target_amount FROM saving_goals WHERE user_id = ?",
                        (user_id,)
                    ).fetchall()
                    goals = [dict(r) for r in rows]
                matched = [g for g in goals if g_name.lower() in g["target_name"].lower()]
                if len(matched) > 1:
                    list_str = "\n".join(f"{i+1}. {g['target_name']}" for i, g in enumerate(matched))
                    return (
                        f"Có {len(matched)} mục tiêu tiết kiệm phù hợp với '{g_name}':\n"
                        f"{list_str}\n\n"
                        f"{user_name} muốn thao tác với mục tiêu nào?"
                    )
                elif len(matched) == 1:
                    args["goal_id"] = matched[0]["id"]
                    args["goal_name"] = matched[0]["target_name"]
                    args["target_name"] = matched[0]["target_name"]

        # D. DEBT RESOLUTION
        elif tool_name in ("settle_debt", "delete_debt", "repay_debt", "update_debt"):
            p_name = args.get("person_name")
            d_id = args.get("debt_id")
            with main.get_db() as conn:
                if tool_name == "delete_debt":
                    rows = conn.execute(
                        "SELECT id, person_name, debt_type, amount, is_settled FROM debts WHERE user_id = ?",
                        (user_id,)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT id, person_name, debt_type, amount, is_settled FROM debts WHERE user_id = ? AND is_settled = 0",
                        (user_id,)
                    ).fetchall()
                debts = [dict(r) for r in rows]

            if not debts:
                return f"{user_name} hiện không có khoản nợ nào trong sổ nợ để thao tác."

            if d_id:
                target = next((d for d in debts if d["id"] == d_id), None)
                if not target:
                    return f"Không tìm thấy khoản nợ #{d_id} trong sổ nợ của {user_name}."
                args["debt_id"] = target["id"]
                args["person_name"] = target["person_name"]
                args["amount"] = target["amount"]
                args["debt_type"] = target["debt_type"]
                return None

            if p_name and str(p_name).strip() and str(p_name).strip().lower() not in ("đối tác", "người", "ai đó"):
                matched = [d for d in debts if p_name.lower() in d["person_name"].lower()]
            else:
                matched = debts

            if len(matched) == 0:
                return f"Không tìm thấy khoản nợ nào của '{p_name}' trong sổ nợ của {user_name}."
            elif len(matched) == 1:
                args["debt_id"] = matched[0]["id"]
                args["person_name"] = matched[0]["person_name"]
                args["amount"] = matched[0]["amount"]
                args["debt_type"] = matched[0]["debt_type"]
                return None
            else:
                args["_ambiguous_debts"] = matched
                list_str = "\n".join(f"{i+1}. {d['person_name']} ({'Đi vay' if d['debt_type'] == 'BORROW' else 'Cho vay'} {d['amount']:,.0f} VNĐ)" for i, d in enumerate(matched))
                return (
                    f"Hiện tại {user_name} có {len(matched)} khoản nợ:\n"
                    f"{list_str}\n\n"
                    f"{user_name} muốn thao tác với khoản nợ nào? (Vui lòng chọn số thứ tự hoặc nêu tên đối tác)"
                )

        # E. BUDGET RESOLUTION
        elif tool_name in ("delete_budget", "update_budget"):
            cat_name = args.get("category_name")
            b_id = args.get("budget_id")
            with main.get_db() as conn:
                rows = conn.execute(
                    """SELECT b.id, b.category_id, b.limit_amount, b.month_year, c.category_name
                       FROM budgets b
                       JOIN categories c ON b.category_id = c.id
                       WHERE b.user_id = ?""",
                    (user_id,)
                ).fetchall()
                budgets = [dict(r) for r in rows]

            if not budgets:
                return f"{user_name} chưa thiết lập hạn mức chi tiêu nào trong hệ thống."

            if b_id:
                target = next((b for b in budgets if b["id"] == b_id), None)
                if not target:
                    return f"Không tìm thấy hạn mức #{b_id} trong hệ thống của {user_name}."
                args["budget_id"] = target["id"]
                args["category_name"] = target["category_name"]
                if tool_name == "delete_budget" or not args.get("limit_amount") or args["limit_amount"] <= 0:
                    args["limit_amount"] = target["limit_amount"]
                args["month_year"] = target["month_year"]
                return None

            if cat_name and str(cat_name).strip():
                matched = [b for b in budgets if cat_name.lower() in b["category_name"].lower()]
            else:
                matched = budgets

            if len(matched) == 0:
                return f"Không tìm thấy hạn mức chi tiêu nào cho danh mục '{cat_name}'."
            elif len(matched) == 1:
                args["budget_id"] = matched[0]["id"]
                args["category_name"] = matched[0]["category_name"]
                if tool_name == "delete_budget" or not args.get("limit_amount") or args["limit_amount"] <= 0:
                    args["limit_amount"] = matched[0]["limit_amount"]
                args["month_year"] = matched[0]["month_year"]
                return None
            else:
                args["_ambiguous_budgets"] = matched
                list_str = "\n".join(f"{i+1}. {b['category_name']} ({b['limit_amount']:,.0f} VNĐ - {b['month_year']})" for i, b in enumerate(matched))
                return (
                    f"Có {len(matched)} hạn mức ngân sách:\n"
                    f"{list_str}\n\n"
                    f"{user_name} muốn thao tác với hạn mức nào? (Vui lòng chọn số thứ tự hoặc nêu tên danh mục)"
                )

        elif tool_name == "create_budget":
            cat_name = args.get("category_name")
            if cat_name and str(cat_name).strip():
                with main.get_db() as conn:
                    cat_row = conn.execute(
                        "SELECT id, category_name FROM categories WHERE (user_id = ? OR user_id IS NULL) AND LOWER(category_name) = LOWER(?)",
                        (user_id, cat_name.strip())
                    ).fetchone()
                    if not cat_row:
                        cat_row = conn.execute(
                            "SELECT id, category_name FROM categories WHERE (user_id = ? OR user_id IS NULL) AND LOWER(category_name) LIKE LOWER(?)",
                            (user_id, f"%{cat_name.strip()}%")
                        ).fetchone()
                if not cat_row:
                    args["_not_found_category"] = cat_name
                    return f"Không tìm thấy danh mục '{cat_name}' trong hệ thống. {user_name} vui lòng tạo danh mục trước hoặc chọn danh mục đã có."
                else:
                    args["category_name"] = cat_row["category_name"]

        # F. TRANSACTION RESOLUTION & OWNERSHIP AUTHORIZATION
        elif tool_name in ("delete_transaction", "update_transaction"):
            t_id = args.get("transaction_id")
            if t_id:
                with main.get_db() as conn:
                    row = conn.execute(
                        "SELECT id, amount, note, category_id, wallet_id, transaction_date FROM transactions WHERE id = ? AND user_id = ?",
                        (t_id, user_id)
                    ).fetchone()
                    if not row:
                        return f"Không tìm thấy giao dịch #{t_id} hoặc giao dịch không thuộc quyền sở hữu của {user_name}."
                    t_dict = dict(row)
                    if "amount" not in args or not args.get("amount"):
                        args["amount"] = t_dict["amount"]
                    if "note" not in args or not args.get("note"):
                        args["note"] = t_dict.get("note") or "Khoản chi tiêu / Thu nhập"
            else:
                # Phân giải giao dịch gần nhất từ context hoặc DB
                target_txn = await self.resolve_contextual_entity(user_id, "transaction")
                if target_txn:
                    args["transaction_id"] = target_txn["id"]
                    if "amount" not in args or not args.get("amount"):
                        args["amount"] = target_txn.get("amount", 0)
                    if "note" not in args or not args.get("note"):
                        args["note"] = target_txn.get("note") or "Khoản chi tiêu / Thu nhập"
                else:
                    return f"Khí Linh không tìm thấy giao dịch nào gần đây của {user_name} để thao tác."

        # G. CATEGORY RESOLUTION (CREATE_CATEGORY & DELETE_CATEGORY)
        elif tool_name == "create_category":
            c_name = args.get("category_name")
            c_type = args.get("category_type")
            if c_name and c_type:
                if not args.get("icon") or args.get("icon") == "📦":
                    args["icon"] = resolve_category_icon(c_name, c_type)
                with main.get_db() as conn:
                    existing = conn.execute(
                        "SELECT id, category_name, category_type FROM categories WHERE (user_id = ? OR user_id IS NULL) AND LOWER(category_name) = LOWER(?) AND category_type = ?",
                        (user_id, c_name.strip(), c_type)
                    ).fetchone()
                    if existing:
                        type_label = "Chi tiêu" if c_type == "EXPENSE" else "Thu nhập"
                        return f"Danh mục '{existing['category_name']}' ({type_label}) đã tồn tại trong hệ thống của {user_name}."

        elif tool_name == "delete_category":
            c_name = args.get("category_name")
            c_id = args.get("category_id")
            with main.get_db() as conn:
                rows = conn.execute(
                    "SELECT id, category_name, category_type, icon FROM categories WHERE user_id = ?",
                    (user_id,)
                ).fetchall()
                user_cats = [dict(r) for r in rows]

            if not user_cats and not c_id:
                with main.get_db() as conn:
                    global_cats = conn.execute(
                        "SELECT id, category_name, category_type FROM categories WHERE user_id IS NULL"
                    ).fetchall()
                matching_global = [gc for gc in global_cats if c_name and c_name.strip().lower() in gc["category_name"].lower()]
                if matching_global:
                    return f"Danh mục '{matching_global[0]['category_name']}' là danh mục mặc định của hệ thống, không thể xóa."
                return f"{user_name} chưa tạo danh mục tùy chỉnh nào trong hệ thống để xóa."

            if c_id:
                target = next((c for c in user_cats if c["id"] == c_id), None)
                if not target:
                    return f"Không tìm thấy danh mục #{c_id} trong các danh mục tùy chỉnh của {user_name}."
                args["category_id"] = target["id"]
                args["category_name"] = target["category_name"]
                args["category_type"] = target["category_type"]
                return None

            if c_name and str(c_name).strip():
                clean_n = c_name.strip().lower()
                exact = [c for c in user_cats if c["category_name"].lower() == clean_n]
                if len(exact) == 1:
                    matched = exact
                elif len(exact) > 1:
                    matched = exact
                else:
                    matched = [c for c in user_cats if clean_n in c["category_name"].lower()]
            else:
                matched = user_cats

            if len(matched) == 0:
                with main.get_db() as conn:
                    global_cats = conn.execute(
                        "SELECT id, category_name, category_type FROM categories WHERE user_id IS NULL"
                    ).fetchall()
                matching_global = [gc for gc in global_cats if c_name and c_name.strip().lower() in gc["category_name"].lower()]
                if matching_global:
                    return f"Danh mục '{matching_global[0]['category_name']}' là danh mục mặc định của hệ thống, không thể xóa."
                return f"Không tìm thấy danh mục nào có tên '{c_name}' trong danh sách danh mục của {user_name}."
            elif len(matched) == 1:
                args["category_id"] = matched[0]["id"]
                args["category_name"] = matched[0]["category_name"]
                args["category_type"] = matched[0]["category_type"]
                return None
            else:
                args["_ambiguous_categories"] = matched
                list_str = "\n".join(f"{i+1}. {c['category_name']} ({'Chi tiêu' if c['category_type'] == 'EXPENSE' else 'Thu nhập'})" for i, c in enumerate(matched))
                return (
                    f"Có {len(matched)} danh mục phù hợp với '{c_name}':\n"
                    f"{list_str}\n\n"
                    f"{user_name} muốn xóa danh mục nào? (Vui lòng chọn số thứ tự hoặc nêu rõ loại Thu/Chi)"
                )

        return None
