"""
Agent Core — Càn Khôn Linh Thạch Các
Bộ xử lý trung tâm của AI Agent:
- Quản lý trạng thái Agent (IDLE, THINKING, PLANNING, CONFIRMING, EXECUTING, SUCCESS, ERROR)
- Xác định ý định và lựa chọn công cụ
- Cơ chế xác nhận bắt buộc trước khi thực hiện thao tác thay đổi dữ liệu (Write operations)
- Không bao giờ tuyên bố thành công giả mạo nếu công cụ thất bại.
"""

from enum import Enum
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
import datetime
import json

from .provider import AIProvider
from .tools import ToolRegistry, Tool, ToolResult, RiskLevel, ToolActionType
from .parser import VietnameseFinancialParser


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
    """Cấu trúc phản hồi đầy đủ của Agent"""
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


class AgentCore:
    """Trung tâm điều phối Agent của Khí Linh Tiên Trí"""

    def __init__(self, provider: AIProvider, registry: ToolRegistry):
        self.provider = provider
        self.registry = registry
        # Lưu trữ trạng thái chờ xác nhận cho từng user: {user_id: {"tool_name": ..., "args": ..., "summary": ...}}
        self._pending_confirmations: Dict[int, Dict[str, Any]] = {}
        self.current_state: AgentState = AgentState.IDLE

    def get_pending_confirmation(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self._pending_confirmations.get(user_id)

    def clear_pending_confirmation(self, user_id: int):
        if user_id in self._pending_confirmations:
            del self._pending_confirmations[user_id]

    async def process_request(self, user_id: int, user_message: str, recent_history: str = "") -> AgentResponse:
        """Xử lý yêu cầu bằng ngôn ngữ tự nhiên từ người dùng theo quy trình chuẩn của Agent Core"""
        clean_msg = user_message.strip()
        self.current_state = AgentState.THINKING

        # 1. KIỂM TRA LUỒNG XÁC NHẬN (CONFIRMATION / CANCELLATION FLOW)
        pending = self.get_pending_confirmation(user_id)
        if pending:
            # A. Người dùng hủy bỏ (kiểm tra trước để ưu tiên lệnh hủy)
            if VietnameseFinancialParser.is_cancellation(clean_msg):
                self.clear_pending_confirmation(user_id)
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text="Đã hủy bỏ thao tác theo lệnh của đạo hữu. Số dư và sổ sách được giữ nguyên toàn vẹn.",
                    state=self.current_state
                )

            # B. Người dùng sửa đổi số tiền / tham số của thao tác đang chờ
            new_amt = VietnameseFinancialParser.parse_amount(clean_msg)
            if new_amt and new_amt > 0 and any(kw in clean_msg.lower() for kw in ["sửa", "sua", "đổi", "doi", "thành", "thanh", "thôi"]):
                pending["args"]["amount"] = new_amt
                pending["summary"] = self._generate_confirmation_summary(pending["tool_name"], pending["args"])
                self.current_state = AgentState.CONFIRMING
                return AgentResponse(
                    text=(
                        f"🔮 Đã cập nhật số tiền thành **{new_amt:,.0f} VNĐ**.\n"
                        f"{pending['summary']}\n\n"
                        f"Đạo hữu có **Xác nhận** thực hiện biến động tài chính này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
                    ),
                    state=self.current_state,
                    pending_confirmation=pending
                )

            # C. Người dùng xác nhận
            if VietnameseFinancialParser.is_confirmation(clean_msg):
                self.current_state = AgentState.EXECUTING
                tool_name = pending["tool_name"]
                tool_args = pending["args"]

                tool_res = await self.registry.execute(tool_name, user_id=user_id, **tool_args)
                self.clear_pending_confirmation(user_id)

                if tool_res.success:
                    self.current_state = AgentState.SUCCESS
                    return AgentResponse(
                        text=f"✅ {tool_res.message}",
                        state=self.current_state,
                        tool_executed=tool_name,
                        tool_result=tool_res.to_dict()
                    )
                else:
                    self.current_state = AgentState.ERROR
                    return AgentResponse(
                        text=f"❌ Thất bại: {tool_res.error or tool_res.message}",
                        state=self.current_state,
                        tool_executed=tool_name,
                        tool_result=tool_res.to_dict(),
                        error=tool_res.error
                    )

        # 2. XÁC ĐỊNH Ý ĐỊNH BẰNG FAST HEURISTIC PARSER KẾT HỢP LLM (PLANNING)
        self.current_state = AgentState.PLANNING
        planned_action = await self._plan_action(user_id, clean_msg)

        # 3. NẾU KHÔNG CẦN CÔNG CỤ HOẶC KHÔNG PHÁT HIỆN HÀNH ĐỘNG TÀI CHÍNH
        if not planned_action or not planned_action.get("tool"):
            # Trả lời thông thường qua AIProvider
            prompt = f"""Bạn là "Khí Linh Tiên Trí" — trợ lý AI tài chính phong cách tu tiên cho ứng dụng Càn Khôn Linh Thạch Các.
Hãy đàm đạo cùng đạo hữu một cách ngắn gọn, súc tích và hữu ích.
{recent_history}
Câu hỏi của đạo hữu: {clean_msg}"""
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

        # 4. NẾU CÔNG CỤ YÊU CẦU XÁC NHẬN (CÁC THAO TÁC GHI / BIẾN ĐỘNG TÀI CHÍNH)
        if tool.requires_confirmation:
            # Kiểm tra xem có thiếu tham số trọng yếu hay không
            validation_error = self._validate_tool_args(tool, tool_args)
            if validation_error:
                self.current_state = AgentState.IDLE
                return AgentResponse(
                    text=f"Khí Linh chưa rõ thông tin: {validation_error}. Đạo hữu vui lòng cung cấp thêm chi tiết.",
                    state=self.current_state
                )

            self.current_state = AgentState.CONFIRMING
            summary = self._generate_confirmation_summary(tool_name, tool_args)
            self._pending_confirmations[user_id] = {
                "tool_name": tool_name,
                "args": tool_args,
                "summary": summary
            }

            confirm_prompt = (
                f"🔮 **Khí Linh Tiên Trí** đã tiếp nhận ý định:\n"
                f"{summary}\n\n"
                f"Đạo hữu có **Xác nhận** thực hiện biến động tài chính này không? (Trả lời 'Xác nhận' hoặc 'Hủy')"
            )
            return AgentResponse(
                text=confirm_prompt,
                state=self.current_state,
                pending_confirmation=self._pending_confirmations[user_id]
            )

        # 5. CÔNG CỤ ĐỌC / KHÔNG CẦN XÁC NHẬN (READ TOOLS) -> THỰC THI NGAY
        self.current_state = AgentState.EXECUTING
        tool_res = await self.registry.execute(tool_name, user_id=user_id, **tool_args)

        if tool_res.success:
            self.current_state = AgentState.SUCCESS
            # Định dạng câu trả lời mượt mà
            formatted_text = tool_res.message
            return AgentResponse(
                text=formatted_text,
                state=self.current_state,
                tool_executed=tool_name,
                tool_result=tool_res.to_dict()
            )
        else:
            self.current_state = AgentState.ERROR
            return AgentResponse(
                text=f"Không thể tra cứu thông tin: {tool_res.error or tool_res.message}",
                state=self.current_state,
                tool_executed=tool_name,
                tool_result=tool_res.to_dict(),
                error=tool_res.error
            )

    async def _plan_action(self, user_id: int, message: str) -> Optional[Dict[str, Any]]:
        """Lập kế hoạch hành động: phối hợp giữa bộ phân tích nhanh và AI Provider"""
        raw = message.lower().strip()

        # A. Phân tích Heuristic nhanh cho các trường hợp phổ biến
        amt = VietnameseFinancialParser.parse_amount(message)
        dt = VietnameseFinancialParser.parse_date(message)

        # 1. Tra cứu hạn mức (get_budget_status)
        if any(kw in raw for kw in ["hạn mức", "han muc", "ngân sách", "ngan sach", "vượt hạn mức"]):
            return {"tool": "get_budget_status", "arguments": {}}

        # 2. Tra cứu tổng quan thu chi (get_financial_overview)
        if any(kw in raw for kw in ["tổng quan", "tong quan", "tình hình tài chính", "thu chi tháng", "báo cáo", "tiêu bao nhiêu", "chi bao nhiêu", "thu bao nhiêu", "tháng này tiêu", "tháng này chi"]):
            return {"tool": "get_financial_overview", "arguments": {}}

        # 3. Tra cứu số dư ví (get_wallets)
        if any(kw in raw for kw in ["số dư", "so du", "ví", "vi", "còn bao nhiêu", "con bao nhieu", "túi càn khôn"]) and not amt:
            import re
            m_w = re.search(r"(?:ví|túi|vi|tui)\s+([^?.,\n;]+)", message, re.IGNORECASE)
            w_name = None
            if m_w:
                w_candidate = m_w.group(1).strip()
                for stop_w in ["còn bao nhiêu", "con bao nhieu", "của tôi", "nào", "gì", "bao nhiêu", "hiện tại"]:
                    w_candidate = re.sub(rf"\b{re.escape(stop_w)}\b", "", w_candidate, flags=re.IGNORECASE).strip()
                if w_candidate:
                    w_name = w_candidate
            return {"tool": "get_wallets", "arguments": {"wallet_name": w_name} if w_name else {}}

        # 4. Tra cứu / tìm kiếm giao dịch (search_transactions / get_recent_transactions)
        if any(kw in raw for kw in ["tìm giao dịch", "tim giao dich", "tra cứu giao dịch", "lọc giao dịch", "tìm khoản"]):
            import re
            query_str = message
            for kw in ["tìm giao dịch", "tim giao dich", "tra cứu giao dịch", "lọc giao dịch", "tìm khoản", "tìm", "tim"]:
                query_str = re.sub(rf"\b{re.escape(kw)}\b", "", query_str, flags=re.IGNORECASE)
            return {"tool": "search_transactions", "arguments": {"query": query_str.strip()}}

        if any(kw in raw for kw in ["giao dịch gần đây", "giao dich gan day", "lịch sử", "lich su"]):
            return {"tool": "get_recent_transactions", "arguments": {"limit": 5}}

        # 5. Tra cứu sổ nợ (get_debts)
        if any(kw in raw for kw in ["sổ nợ", "so no", "vay", "cho vay"]) or (any(kw in raw for kw in ["nợ", "no"]) and not amt):
            return {"tool": "get_debts", "arguments": {}}

        # 6. Tra cứu danh mục (get_categories)
        if any(kw in raw for kw in ["danh mục", "danh muc", "loại thu chi"]):
            return {"tool": "get_categories", "arguments": {}}

        # 7. Tra cứu giao dịch định kỳ (get_recurring_transactions)
        if any(kw in raw for kw in ["định kỳ", "dinh ky"]):
            return {"tool": "get_recurring_transactions", "arguments": {}}

        # 8. Trợ giúp hệ thống (get_system_help)
        if any(kw in raw for kw in ["trợ giúp", "hướng dẫn", "tính năng", "bạn làm được gì"]):
            return {"tool": "get_system_help", "arguments": {}}

        # 9. Chuyển tiền (transfer_money)
        if any(kw in raw for kw in ["chuyển", "chuyen"]):
            from_w, to_w = VietnameseFinancialParser.extract_transfer_wallets(message)
            return {
                "tool": "transfer_money",
                "arguments": {
                    "amount": amt or 0,
                    "from_wallet_name": from_w,
                    "to_wallet_name": to_w,
                    "note": message.strip()
                }
            }

        # 10. Tích lũy tiết kiệm (saving_goal_deposit / get_saving_goals)
        if any(kw in raw for kw in ["mục tiêu", "muc tieu", "tiết kiệm", "tiet kiem", "tích lũy", "tich luy"]):
            goal = VietnameseFinancialParser.extract_goal_name(message)
            if amt or any(k in raw for k in ["nạp", "nap", "đưa", "dua", "gửi", "gui", "thêm", "them", "vào", "vao"]):
                return {
                    "tool": "saving_goal_deposit",
                    "arguments": {
                        "amount": amt or 0,
                        "goal_name": goal
                    }
                }
            elif not amt:
                return {"tool": "get_saving_goals", "arguments": {}}

        # 11. Chi tiêu (create_expense)
        is_expense_trigger = any(kw in raw for kw in ["chi", "tiêu", "hết", "mua", "ăn", "uống", "trả tiền", "đóng tiền", "đổ xăng"])
        is_income_trigger = any(kw in raw for kw in ["thu", "nhận", "lương", "thưởng", "được cho", "được tặng", "bán"])

        if is_expense_trigger and not is_income_trigger:
            import re
            clean_note = message
            for kw in ["tôi vừa", "vừa", "hôm nay", "hôm qua", "hết", "thêm khoản chi", "khoản chi", "tiền"]:
                clean_note = re.sub(rf"\b{re.escape(kw)}\b", "", clean_note, flags=re.IGNORECASE)
            clean_note = re.sub(r"\b\d+[\d.,]*\s*(?:k|nghìn|ngàn|tr|triệu|tỷ|vnđ|đ)?\b", "", clean_note, flags=re.IGNORECASE).strip()
            clean_note = clean_note.strip(" .,-") or "Ăn uống / Chi tiêu"
            cat = VietnameseFinancialParser.guess_category(message)
            return {
                "tool": "create_expense",
                "arguments": {
                    "amount": amt or 0,
                    "note": clean_note,
                    "category_name": cat,
                    "transaction_date": dt
                }
            }

        # 12. Thu nhập (create_income)
        if is_income_trigger and not is_expense_trigger:
            import re
            clean_note = message
            for kw in ["tôi vừa", "vừa", "hôm nay", "hôm qua", "nhận được", "thêm khoản thu", "khoản thu", "tiền"]:
                clean_note = re.sub(rf"\b{re.escape(kw)}\b", "", clean_note, flags=re.IGNORECASE)
            clean_note = re.sub(r"\b\d+[\d.,]*\s*(?:k|nghìn|ngàn|tr|triệu|tỷ|vnđ|đ)?\b", "", clean_note, flags=re.IGNORECASE).strip()
            clean_note = clean_note.strip(" .,-") or "Thu nhập"
            cat = VietnameseFinancialParser.guess_category(message)
            return {
                "tool": "create_income",
                "arguments": {
                    "amount": amt or 0,
                    "note": clean_note,
                    "category_name": cat,
                    "transaction_date": dt
                }
            }

        # B. Dùng AIProvider để phân tích cấu trúc intent nếu heuristic chưa xác định
        schemas = self.registry.get_schemas()
        intent_prompt = f"""Người dùng nhắn: "{message}"
Danh sách công cụ khả dụng:
{json.dumps([{'name': s['name'], 'description': s['description']} for s in schemas], ensure_ascii=False)}

Hãy xác định công cụ phù hợp nhất và trích xuất tham số. Nếu không cần công cụ nào, trả về tool: null."""
        target_schema = {
            "tool": "tên công cụ hoặc null",
            "arguments": {"key": "value"}
        }
        res = await self.provider.parse_structured_intent(intent_prompt, schema=target_schema)
        if isinstance(res, dict) and res.get("tool") and res["tool"] != "null":
            return res

        return None

    def _validate_tool_args(self, tool: Tool, args: Dict[str, Any]) -> Optional[str]:
        """Kiểm tra tính đầy đủ và hợp lệ của tham số công cụ"""
        required = tool.parameters.get("required", [])
        for r in required:
            if r not in args or args[r] is None:
                return f"thiếu thông tin '{r}'"
        if "amount" in args:
            try:
                amt = float(args["amount"])
                if amt <= 0:
                    return "số tiền phải lớn hơn 0"
            except (ValueError, TypeError):
                return "số tiền không hợp lệ"

        if tool.name == "transfer_money":
            from_w = args.get("from_wallet_name") or args.get("from_wallet_id")
            to_w = args.get("to_wallet_name") or args.get("to_wallet_id")
            if not from_w or not to_w:
                return "chưa rõ ví nguồn và ví đích (ví dụ: Chuyển 500k từ ví A sang ví B)"

        if tool.name == "saving_goal_deposit":
            goal = args.get("goal_name") or args.get("goal_id")
            if not goal:
                return "chưa rõ mục tiêu tiết kiệm nào cần tích lũy (ví dụ: Đưa 1 triệu vào mục tiêu mua laptop)"

        return None

    def _generate_confirmation_summary(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Tạo bản tóm tắt hành động dễ hiểu bằng tiếng Việt để người dùng xác nhận"""
        amt = args.get("amount", 0)
        formatted_amt = f"{amt:,.0f} VNĐ" if isinstance(amt, (int, float)) else str(amt)

        if tool_name == "create_expense":
            note = args.get("note", "Chi tiêu")
            cat = args.get("category_name", "Tự động phân loại")
            return f"👉 **Khoản Chi**: {formatted_amt} — Nội dung: '{note}' (Danh mục: {cat})"

        if tool_name == "create_income":
            note = args.get("note", "Thu nhập")
            return f"👉 **Khoản Thu**: +{formatted_amt} — Nội dung: '{note}'"

        if tool_name == "transfer_money":
            from_w = args.get("from_wallet_name") or "Ví mặc định"
            to_w = args.get("to_wallet_name") or "Ví đích"
            return f"👉 **Chuyển Tiền**: {formatted_amt} từ '{from_w}' sang '{to_w}'"

        if tool_name == "saving_goal_deposit":
            goal = args.get("goal_name") or "Mục tiêu ưu tiên"
            return f"👉 **Nạp Tiết Kiệm**: {formatted_amt} vào mục tiêu '{goal}'"

        return f"👉 Thực thi thao tác {tool_name} với tham số: {args}"
