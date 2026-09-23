"""
Tool Registry & Financial Capabilities — Càn Khôn Linh Thạch Các
Định nghĩa hệ thống công cụ (Tools) có kiểu dữ liệu chặt chẽ và toàn diện cho Khí Linh AI Agent.
Phân định rõ ràng:
- OperationType: READ / WRITE / DELETE / SYSTEM
- RiskLevel: LOW / MEDIUM / HIGH / CRITICAL
- Quản lý phân quyền (role 'user' vs 'admin') và kiểm thực quyền sở hữu (IDOR protection)
- Tự sinh tóm tắt xác nhận (Confirmation Summary)
- Kết nối trực tiếp vào logic nghiệp vụ và DB an toàn, tuyệt đối không cho LLM truy cập SQL trực tiếp.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import datetime
import calendar
import json
import re


def _resolve_period_range(period: Optional[str] = None) -> Tuple[str, str, str]:
    """Chuyển đổi các định dạng thời gian tự nhiên thành (start_date, end_date, label)"""
    today = datetime.date.today()
    p = (period or "this_month").lower().strip()

    if p in ("today", "hôm nay", "hom nay"):
        d_str = today.strftime("%Y-%m-%d")
        return d_str, d_str, "hôm nay"

    if p in ("yesterday", "hôm qua", "hom qua"):
        y_str = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        return y_str, y_str, "hôm qua"

    if p in ("last_week", "tuần trước", "tuan truoc", "tuần vừa rồi", "tuan vua roi"):
        start_curr_week = today - datetime.timedelta(days=today.weekday())
        start_last_week = start_curr_week - datetime.timedelta(days=7)
        end_last_week = start_curr_week - datetime.timedelta(days=1)
        return start_last_week.strftime("%Y-%m-%d"), end_last_week.strftime("%Y-%m-%d"), f"tuần trước ({start_last_week.strftime('%d/%m')} - {end_last_week.strftime('%d/%m')})"

    if p in ("this_week", "tuần này", "tuan nay", "tuần", "tuan"):
        start_week = today - datetime.timedelta(days=today.weekday())
        return start_week.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), "tuần này"

    if p in ("last_7_days", "7 ngày qua", "7 ngày gần đây", "7 ngay qua"):
        start_7d = today - datetime.timedelta(days=6)
        return start_7d.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), "7 ngày qua"

    if p in ("last_30_days", "30 ngày qua", "30 ngày gần đây", "30 ngay qua"):
        start_30d = today - datetime.timedelta(days=29)
        return start_30d.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), "30 ngày qua"

    if p in ("month_to_date", "từ đầu tháng đến giờ", "đầu tháng", "tu dau thang den gio", "dau thang"):
        first_day = today.replace(day=1)
        return first_day.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), f"từ đầu tháng đến nay ({today.strftime('%m/%Y')})"

    if p in ("month_end", "cuối tháng", "cuoi thang"):
        _, last_day = calendar.monthrange(today.year, today.month)
        start_end_phase = today.replace(day=max(1, last_day - 7))
        return start_end_phase.strftime("%Y-%m-%d"), f"{today.year:04d}-{today.month:02d}-{last_day:02d}", f"cuối tháng ({today.strftime('%m/%Y')})"

    if p in ("last_month", "tháng trước", "thang truoc", "tháng vừa rồi", "thang vua roi", "tháng đó", "thang do"):
        first_this_month = today.replace(day=1)
        last_day_prev = first_this_month - datetime.timedelta(days=1)
        start_prev = last_day_prev.replace(day=1)
        return start_prev.strftime("%Y-%m-%d"), last_day_prev.strftime("%Y-%m-%d"), f"tháng trước ({last_day_prev.strftime('%m/%Y')})"

    if p in ("last_3_months", "3 tháng gần đây", "3 thang gan day", "ba tháng gần đây"):
        m_start = today.month - 2
        y_start = today.year
        if m_start <= 0:
            m_start += 12
            y_start -= 1
        start_3m = datetime.date(y_start, m_start, 1)
        return start_3m.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), f"3 tháng gần đây ({m_start:02d}/{y_start} - {today.strftime('%m/%Y')})"

    if p in ("this_quarter", "quý này", "quy nay"):
        curr_q = (today.month - 1) // 3 + 1
        start_m = (curr_q - 1) * 3 + 1
        end_m = start_m + 2
        _, last_d = calendar.monthrange(today.year, end_m)
        return f"{today.year:04d}-{start_m:02d}-01", f"{today.year:04d}-{end_m:02d}-{last_d:02d}", f"quý {curr_q}/{today.year}"

    if p in ("last_quarter", "quý trước", "quy truoc"):
        curr_q = (today.month - 1) // 3 + 1
        prev_q = curr_q - 1 if curr_q > 1 else 4
        prev_y = today.year if curr_q > 1 else today.year - 1
        start_m = (prev_q - 1) * 3 + 1
        end_m = start_m + 2
        _, last_d = calendar.monthrange(prev_y, end_m)
        return f"{prev_y:04d}-{start_m:02d}-01", f"{prev_y:04d}-{end_m:02d}-{last_d:02d}", f"quý {prev_q}/{prev_y}"

    if p in ("this_year", "năm nay", "nam nay"):
        return f"{today.year:04d}-01-01", f"{today.year:04d}-12-31", f"năm {today.year}"

    if p in ("last_year", "năm ngoái", "nam ngoai", "năm trước", "nam truoc"):
        prev_y = today.year - 1
        return f"{prev_y:04d}-01-01", f"{prev_y:04d}-12-31", f"năm ngoái ({prev_y})"

    if p in ("next_month", "tháng sau", "thang sau", "tháng tới", "thang toi", "tháng tiếp", "thang tiep"):
        if today.month == 12:
            next_y, next_m = today.year + 1, 1
        else:
            next_y, next_m = today.year, today.month + 1
        _, last_day = calendar.monthrange(next_y, next_m)
        return f"{next_y:04d}-{next_m:02d}-01", f"{next_y:04d}-{next_m:02d}-{last_day:02d}", f"tháng sau ({next_m:02d}/{next_y:04d})"

    # Pattern YYYY-MM
    m_ym = re.match(r"^(\d{4})-(\d{2})$", p)
    if m_ym:
        year, month = int(m_ym.group(1)), int(m_ym.group(2))
        _, last_day = calendar.monthrange(year, month)
        return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}", f"tháng {month:02d}/{year:04d}"

    # Default: this_month
    first_day = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    return first_day.strftime("%Y-%m-%d"), f"{today.year:04d}-{today.month:02d}-{last_day:02d}", f"tháng này ({today.strftime('%m/%Y')})"


def _match_wallet_name(query: str, target: str) -> bool:
    """Khớp tên ví thông minh, không cắt nhầm từ con như 'vi' hay 'mb' trong 'vietcombank'"""
    q = query.lower().strip()
    t = target.lower().strip()
    if q == t:
        return True
    if re.search(rf"\b{re.escape(q)}\b", t) or re.search(rf"\b{re.escape(t)}\b", q):
        return True
    clean_q = re.sub(r'\b(ví|vi)\b', '', q).strip()
    clean_t = re.sub(r'\b(ví|vi)\b', '', t).strip()
    if clean_q and clean_t:
        if clean_q == clean_t:
            return True
        if re.search(rf"\b{re.escape(clean_q)}\b", clean_t) or re.search(rf"\b{re.escape(clean_t)}\b", clean_q):
            return True
    return False


class AgentMode(str, Enum):
    ACTION = "action"        # Khí Linh Nhỏ (Live System Mode) - Có quyền thực thi thao tác
    KNOWLEDGE = "knowledge"  # Khí Linh AI Lớn (Desktop Chat) - Chỉ tra cứu tri thức & đọc dữ liệu (Read-Only)


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OperationType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    SYSTEM = "SYSTEM"


# Giữ ToolActionType để tương thích ngược 100% với mã nguồn cũ
class ToolActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    SYSTEM = "SYSTEM"


@dataclass
class ToolResult:
    """Kết quả xác thực từ việc thực thi công cụ"""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error
        }


@dataclass
class Tool:
    """Định nghĩa một công cụ có cấu trúc, phân loại rủi ro và tự sinh tóm tắt xác nhận"""
    name: str
    description: str
    parameters: Dict[str, Any]
    action_type: ToolActionType
    risk_level: RiskLevel
    requires_confirmation: bool
    handler: Callable
    domain: str = "general"
    operation_type: Optional[OperationType] = None
    required_role: str = "user"
    expected_result: str = ""
    error_behavior: str = ""
    idempotency_key_field: Optional[str] = None
    summary_generator: Optional[Callable[[Dict[str, Any]], str]] = None

    def __post_init__(self):
        if self.operation_type is None:
            if self.action_type == ToolActionType.READ:
                self.operation_type = OperationType.READ
            elif self.action_type == ToolActionType.DELETE:
                self.operation_type = OperationType.DELETE
            elif self.action_type == ToolActionType.SYSTEM:
                self.operation_type = OperationType.SYSTEM
            else:
                self.operation_type = OperationType.WRITE

    def generate_summary(self, args: Dict[str, Any]) -> str:
        """Sinh bản tóm tắt xác nhận thân thiện với người dùng bằng tiếng Việt"""
        if self.summary_generator:
            try:
                res = self.summary_generator(args)
                if res:
                    return res
            except Exception:
                pass
        return f"👉 Thực thi '{self.description}' với tham số: {args}"

    def to_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "operation_type": self.operation_type.value if self.operation_type else self.action_type.value,
            "action_type": self.action_type.value,
            "risk_level": self.risk_level.value,
            "requires_confirmation": self.requires_confirmation,
            "required_role": self.required_role,
            "parameters": self.parameters,
            "expected_result": self.expected_result,
            "error_behavior": self.error_behavior,
        }


class ToolRegistry:
    """Sổ đăng ký và quản lý năng lực (Capability Registry) an toàn của Khí Linh AI Agent"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(
        self,
        domain: Optional[str] = None,
        operation_type: Optional[OperationType] = None,
        role: Optional[str] = None
    ) -> List[Tool]:
        tools = list(self._tools.values())
        if domain:
            tools = [t for t in tools if t.domain == domain]
        if operation_type:
            tools = [t for t in tools if t.operation_type == operation_type]
        if role:
            if role != "admin":
                tools = [t for t in tools if t.required_role != "admin"]
        return tools

    def get_schemas(self, role: str = "user") -> List[Dict[str, Any]]:
        valid_tools = [t for t in self._tools.values() if role == "admin" or t.required_role != "admin"]
        return [t.to_schema() for t in valid_tools]

    async def execute(
        self,
        tool_name: str,
        user_id: int,
        user_role: str = "user",
        mode: Any = "action",
        **kwargs
    ) -> ToolResult:
        """Thực thi công cụ với ủy quyền, phân quyền vai trò và ranh giới quyền hạn AgentMode"""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Công cụ '{tool_name}' không tồn tại trong sổ đăng ký.",
                message="Khí Linh không tìm thấy pháp bảo tương ứng để thực thi."
            )

        # 1. Ranh giới quyền hạn chế độ Knowledge (Code-level Permission Enforcement)
        # Khí Linh AI Lớn (mode == "knowledge") TUYỆT ĐỐI KHÔNG ĐƯỢC PHÉP gọi các công cụ Mutation!
        is_knowledge_mode = (mode == AgentMode.KNOWLEDGE or str(mode).lower() == "knowledge")
        if is_knowledge_mode and tool.operation_type != OperationType.READ:
            return ToolResult(
                success=False,
                error="PERMISSION_DENIED",
                message="Khí Linh AI lớn chỉ có quyền giải đáp và tra cứu (Knowledge Assistant), không có thẩm quyền thay đổi dữ liệu tài chính. Vui lòng sử dụng Khí Linh (nhỏ / Live System Mode) để thực hiện thao tác này."
            )

        # 2. Kiểm tra phân quyền vai trò (Role Check)
        if tool.required_role == "admin" and user_role != "admin":
            return ToolResult(
                success=False,
                error="Quyền hạn không đủ.",
                message="Chỉ Chưởng Môn (Admin) mới có quyền năng sử dụng pháp bảo này."
            )

        try:
            # Gọi handler với user_id và user_role được tiêm vào bắt buộc
            return await tool.handler(user_id=user_id, user_role=user_role, **kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Thực thi công cụ '{tool_name}' thất bại: {str(e)}"
            )


# ─────────────────────────────────────────────────────────────
# 1. WALLET CAPABILITIES (TÚI CÀN KHÔN)
# ─────────────────────────────────────────────────────────────

# READ: get_wallets
async def handle_get_wallets(user_id: int, wallet_name: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute(
            "SELECT id, wallet_name, wallet_type, balance FROM wallets WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
        ).fetchall()
        wallets = [dict(r) for r in rows]
        total_balance = sum(w["balance"] for w in wallets)
        for w in wallets:
            w["percentage"] = round((w["balance"] / total_balance * 100), 1) if total_balance > 0 else 0.0

        if wallet_name:
            matched = [w for w in wallets if _match_wallet_name(wallet_name, w["wallet_name"])]
            if matched:
                target = matched[0]
                return ToolResult(
                    success=True,
                    data={"wallets": [target], "total_balance": total_balance, "target_wallet": target},
                    message=f"Số dư trong '{target['wallet_name']}' của Ký Chủ hiện còn {target['balance']:,.0f} VNĐ."
                )

        top_wallet = max(wallets, key=lambda w: w["balance"]) if wallets else None
        lowest_wallet = min(wallets, key=lambda w: w["balance"]) if wallets else None
        top_msg = f" Túi Càn Khôn dồi dào nhất hiện tại là '{top_wallet['wallet_name']}' với {top_wallet['balance']:,.0f} VNĐ." if top_wallet else ""

        return ToolResult(
            success=True,
            data={
                "wallets": wallets,
                "total_balance": total_balance,
                "top_wallet": top_wallet,
                "lowest_wallet": lowest_wallet
            },
            message=f"Ký Chủ hiện có {len(wallets)} Túi Càn Khôn, tổng số dư là {total_balance:,.0f} VNĐ.{top_msg}"
        )


# WRITE: create_wallet
async def handle_create_wallet(user_id: int, wallet_name: str, balance: float = 0, wallet_type: str = "cash", **kwargs) -> ToolResult:
    import main
    clean_name = (wallet_name or "").strip()
    if not clean_name:
        return ToolResult(success=False, error="Tên Túi Càn Khôn không được để trống.")
    if balance < 0:
        return ToolResult(success=False, error="Số dư ban đầu không được âm.")

    w_type = (wallet_type or "cash").lower()
    if w_type not in ("cash", "bank", "e-wallet", "crypto"):
        w_type = "cash"

    with main.get_db() as conn:
        # Kiểm tra trùng tên ví
        existing = conn.execute(
            "SELECT id FROM wallets WHERE user_id = ? AND LOWER(wallet_name) = LOWER(?)",
            (user_id, clean_name)
        ).fetchone()
        if existing:
            return ToolResult(success=False, error=f"Túi Càn Khôn '{clean_name}' đã tồn tại trong sổ của Ký Chủ.")

        conn.execute(
            "INSERT INTO wallets (user_id, wallet_name, balance, wallet_type) VALUES (?, ?, ?, ?)",
            (user_id, clean_name, float(balance), w_type)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    return ToolResult(
        success=True,
        data={"wallet_id": new_id, "wallet_name": clean_name, "balance": float(balance), "wallet_type": w_type},
        message=f"Khí Linh đã tạo thành công Túi Càn Khôn '{clean_name}' với số dư ban đầu {balance:,.0f} VNĐ."
    )


# WRITE: update_wallet
async def handle_update_wallet(
    user_id: int,
    wallet_id: Optional[int] = None,
    wallet_name: Optional[str] = None,
    new_name: Optional[str] = None,
    balance: Optional[float] = None,
    wallet_type: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        target = None
        if wallet_id:
            target = conn.execute("SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
        elif wallet_name:
            all_w = conn.execute("SELECT id, wallet_name, balance, wallet_type FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
            matched = [w for w in all_w if _match_wallet_name(wallet_name, w["wallet_name"])]
            if len(matched) > 1:
                return ToolResult(
                    success=False,
                    error=f"Có {len(matched)} Túi Càn Khôn trùng khớp với '{wallet_name}'. Vui lòng chỉ định chính xác tên ví cần cập nhật."
                )
            elif matched:
                target = matched[0]

        if not target:
            return ToolResult(success=False, error=f"Không tìm thấy Túi Càn Khôn '{wallet_name or wallet_id}'.")

        updated_name = new_name.strip() if new_name and new_name.strip() else target["wallet_name"]
        updated_balance = float(balance) if balance is not None else target["balance"]
        updated_type = wallet_type if wallet_type in ("cash", "bank", "e-wallet", "crypto") else target["wallet_type"]

        conn.execute(
            "UPDATE wallets SET wallet_name = ?, balance = ?, wallet_type = ? WHERE id = ? AND user_id = ?",
            (updated_name, updated_balance, updated_type, target["id"], user_id)
        )

    return ToolResult(
        success=True,
        data={"wallet_id": target["id"], "wallet_name": updated_name, "balance": updated_balance, "wallet_type": updated_type},
        message=f"Đã cập nhật Túi Càn Khôn '{updated_name}' (Số dư: {updated_balance:,.0f} VNĐ)."
    )


# DELETE: delete_wallet
async def handle_delete_wallet(user_id: int, wallet_id: Optional[int] = None, wallet_name: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        all_w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
        if len(all_w) <= 1:
            return ToolResult(success=False, error="Ký Chủ chỉ còn lại 1 Túi Càn Khôn duy nhất, không thể xóa bỏ.")

        target = None
        if wallet_id:
            target = next((w for w in all_w if w["id"] == wallet_id), None)
        elif wallet_name:
            matched = [w for w in all_w if _match_wallet_name(wallet_name, w["wallet_name"])]
            if len(matched) > 1:
                return ToolResult(
                    success=False,
                    error=f"Có {len(matched)} Túi Càn Khôn trùng khớp với '{wallet_name}'. Vui lòng chỉ định chính xác tên ví cần xóa."
                )
            elif matched:
                target = matched[0]

        if not target:
            return ToolResult(success=False, error=f"Không tìm thấy Túi Càn Khôn '{wallet_name or wallet_id}' để xóa.")

        # Xóa các giao dịch liên quan hoặc chặn xóa nếu có giao dịch
        tx_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE wallet_id = ? AND user_id = ?", (target["id"], user_id)).fetchone()[0]
        if tx_count > 0:
            # Xóa các giao dịch theo ví để đảm bảo toàn vẹn
            conn.execute("DELETE FROM transactions WHERE wallet_id = ? AND user_id = ?", (target["id"], user_id))

        conn.execute("DELETE FROM wallets WHERE id = ? AND user_id = ?", (target["id"], user_id))

        # Post-action DB verification
        verify_del = conn.execute("SELECT id FROM wallets WHERE id = ? AND user_id = ?", (target["id"], user_id)).fetchone()
        if verify_del:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Túi Càn Khôn #{target['id']} vẫn còn tồn tại."
            )

    return ToolResult(
        success=True,
        data={"deleted_wallet_id": target["id"], "deleted_wallet_name": target["wallet_name"]},
        message=f"Đã xóa vĩnh viễn Túi Càn Khôn '{target['wallet_name']}' khỏi tiên phủ của Ký Chủ."
    )


# WRITE: transfer_money
async def handle_transfer_money(
    user_id: int,
    amount: float,
    from_wallet_id: Optional[int] = None,
    to_wallet_id: Optional[int] = None,
    from_wallet_name: Optional[str] = None,
    to_wallet_name: Optional[str] = None,
    note: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số lượng Linh Thạch chuyển phải lớn hơn 0.")

    with main.get_db() as conn:
        all_wallets = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
        if len(all_wallets) < 2:
            return ToolResult(success=False, error="Ký Chủ cần có ít nhất 2 Túi Càn Khôn để thực hiện chuyển tiền.")

        # Tìm from_wallet
        w_from = None
        if from_wallet_id:
            w_from = next((w for w in all_wallets if w["id"] == from_wallet_id), None)
            if not w_from:
                return ToolResult(success=False, error="Không tìm thấy ví nguồn theo ID đã cung cấp.")
        elif from_wallet_name:
            w_from = next((w for w in all_wallets if _match_wallet_name(from_wallet_name, w["wallet_name"])), None)
            if not w_from:
                return ToolResult(success=False, error=f"Không tìm thấy ví nguồn '{from_wallet_name}' trong danh sách ví của bạn.")
        else:
            w_from = all_wallets[0]

        # Tìm to_wallet
        w_to = None
        if to_wallet_id:
            w_to = next((w for w in all_wallets if w["id"] == to_wallet_id), None)
            if not w_to:
                return ToolResult(success=False, error="Không tìm thấy ví đích theo ID đã cung cấp.")
        elif to_wallet_name:
            w_to = next((w for w in all_wallets if _match_wallet_name(to_wallet_name, w["wallet_name"])), None)
            if not w_to:
                return ToolResult(success=False, error=f"Không tìm thấy ví đích '{to_wallet_name}' trong danh sách ví của bạn.")
        else:
            w_to = next((w for w in all_wallets if w["id"] != (w_from["id"] if w_from else None)), None)

        if not w_from or not w_to:
            return ToolResult(success=False, error="Không xác định được ví nguồn hoặc ví đích hợp lệ.")
        if w_from["id"] == w_to["id"]:
            return ToolResult(success=False, error="Không thể chuyển cho chính chiếc ví đó.")
        if w_from["balance"] < amount:
            return ToolResult(
                success=False,
                error=f"Số dư {w_from['wallet_name']} không đủ (Còn {w_from['balance']:,.0f} VNĐ). Ký Chủ có muốn thử lại với số tiền tối đa {w_from['balance']:,.0f} VNĐ không?"
            )

        body = main.TransferBody(
            from_wallet_id=w_from["id"],
            to_wallet_id=w_to["id"],
            amount=amount,
            note=note or "Chuyển tiền qua Khí Linh AI",
            operation_id=kwargs.get("operation_id")
        )
        res = main.transfer_between_wallets(body, user={"user_id": user_id})
        return ToolResult(
            success=True,
            data=res,
            message=f"Đã chuyển thành công {amount:,.0f} VNĐ từ '{w_from['wallet_name']}' sang '{w_to['wallet_name']}'!"
        )


# ─────────────────────────────────────────────────────────────
# 2. CATEGORY CAPABILITIES (DANH MỤC THU CHI)
# ─────────────────────────────────────────────────────────────

# READ: get_categories
async def handle_get_categories(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute(
            "SELECT id, category_name, category_type, icon FROM categories WHERE user_id = ? ORDER BY category_type ASC, id ASC",
            (user_id,)
        ).fetchall()
        cats = [dict(r) for r in rows]
        exp_cats = [c for c in cats if c["category_type"] == "EXPENSE"]
        inc_cats = [c for c in cats if c["category_type"] == "INCOME"]
        return ToolResult(
            success=True,
            data={"categories": cats, "expense_categories": exp_cats, "income_categories": inc_cats, "count": len(cats)},
            message=f"Ký Chủ có {len(cats)} danh mục thu chi ({len(exp_cats)} khoản chi, {len(inc_cats)} khoản thu)."
        )


def resolve_category_icon(name: Optional[str], cat_type: Optional[str] = None) -> str:
    """Tự động chọn biểu tượng emoji phù hợp với tên danh mục."""
    if not name:
        return "💰" if (cat_type or "").upper() == "INCOME" else "📦"

    clean = name.lower()
    mapping = [
        (["ăn", "uống", "cơm", "phở", "bún", "lẩu", "nhậu", "tiệc", "buffet", "cafe", "cà phê", "trà", "bánh", "nước"], "🍽️"),
        (["di chuyển", "xe", "xăng", "grab", "taxi", "bus", "xe buýt", "tàu", "đi lại", "vé máy bay", "vé tàu"], "🚗"),
        (["mua sắm", "shopping", "quần áo", "giày", "dép", "mỹ phẩm", "đồ đạc", "siêu thị", "chợ"], "🛍️"),
        (["lương", "thưởng", "thu nhập", "tiền lương", "hoa hồng", "tiền thưởng", "lãi", "bán đồ"], "💰"),
        (["du lịch", "máy bay", "vé máy bay", "khách sạn", "resort", "tour", "nghỉ dưỡng"], "✈️"),
        (["điện", "tiền điện", "hóa đơn điện", "hóa đơn nước"], "💡"),
        (["nhà", "tiền nhà", "phòng", "nước", "internet", "wifi", "thuê nhà", "chung cư"], "🏠"),
        (["học", "học phí", "sách", "vở", "khóa học", "đào tạo", "giáo dục"], "📚"),
        (["sức khỏe", "y tế", "thuốc", "bệnh viện", "khám", "bác sĩ", "nha khoa"], "💊"),
        (["giải trí", "game", "phim", "ca nhạc", "karaoke", "dã ngoại", "chơi"], "🎮"),
        (["quà", "tặng", "biếu", "mừng", "đám cưới", "sinh nhật"], "🎁"),
        (["đầu tư", "tiết kiệm", "chứng khoán", "vàng", "bất động sản", "coin", "crypto"], "📈"),
        (["gia đình", "con cái", "bố mẹ", "vợ chồng", "hiếu hỉ"], "👨‍👩‍👦"),
        (["thú cưng", "chó", "mèo", "pet"], "🐾"),
        (["từ thiện", "quyên góp", "công đức", "giúp đỡ"], "❤️"),
    ]
    for kws, icon in mapping:
        if any(kw in clean for kw in kws):
            return icon

    return "💰" if (cat_type or "").upper() == "INCOME" else "📦"


# WRITE: create_category
async def handle_create_category(
    user_id: int,
    category_name: str,
    category_type: str = "EXPENSE",
    icon: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    clean_name = (category_name or "").strip()
    if not clean_name:
        return ToolResult(success=False, error="Tên danh mục không được để trống.")

    c_type = category_type.upper() if category_type else "EXPENSE"
    if c_type not in ("EXPENSE", "INCOME"):
        c_type = "EXPENSE"

    final_icon = icon if icon and icon != "📦" else resolve_category_icon(clean_name, c_type)

    with main.get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM categories WHERE user_id = ? AND category_type = ? AND LOWER(category_name) = LOWER(?)",
            (user_id, c_type, clean_name)
        ).fetchone()
        if existing:
            return ToolResult(success=False, error=f"Danh mục '{clean_name}' ({c_type}) đã tồn tại.")

        conn.execute(
            "INSERT INTO categories (user_id, category_name, category_type, icon) VALUES (?, ?, ?, ?)",
            (user_id, clean_name, c_type, final_icon)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    label = "Chi tiêu" if c_type == "EXPENSE" else "Thu nhập"
    return ToolResult(
        success=True,
        data={"category_id": new_id, "category_name": clean_name, "category_type": c_type, "icon": final_icon},
        message=f"Đã tạo danh mục {label} mới: '{clean_name}' {final_icon} thành công!"
    )


# WRITE: update_category
async def handle_update_category(
    user_id: int,
    category_id: Optional[int] = None,
    category_name: Optional[str] = None,
    new_name: Optional[str] = None,
    icon: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        cat = None
        if category_id:
            cat = conn.execute("SELECT * FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id)).fetchone()
        elif category_name:
            cat = conn.execute(
                "SELECT * FROM categories WHERE user_id = ? AND LOWER(category_name) LIKE ?",
                (user_id, f"%{category_name.strip().lower()}%")
            ).fetchone()

        if not cat:
            return ToolResult(success=False, error=f"Không tìm thấy danh mục '{category_name or category_id}'.")

        updated_name = new_name.strip() if new_name and new_name.strip() else cat["category_name"]
        updated_icon = icon.strip() if icon and icon.strip() else cat["icon"]

        conn.execute(
            "UPDATE categories SET category_name = ?, icon = ? WHERE id = ? AND user_id = ?",
            (updated_name, updated_icon, cat["id"], user_id)
        )

    return ToolResult(
        success=True,
        data={"category_id": cat["id"], "category_name": updated_name, "icon": updated_icon},
        message=f"Đã cập nhật danh mục thành '{updated_name}' {updated_icon} thành công!"
    )


# DELETE: delete_category
async def handle_delete_category(
    user_id: int,
    category_id: Optional[int] = None,
    category_name: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    import sqlite3
    with main.get_db() as conn:
        cat = None
        if category_id:
            cat = conn.execute("SELECT * FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id)).fetchone()
        elif category_name:
            cat = conn.execute(
                "SELECT * FROM categories WHERE user_id = ? AND LOWER(category_name) LIKE ?",
                (user_id, f"%{category_name.strip().lower()}%")
            ).fetchone()

        if not cat:
            return ToolResult(success=False, error=f"Không tìm thấy danh mục '{category_name or category_id}' để xóa.")

        # Kiểm tra ràng buộc phụ thuộc (giao dịch, ngân sách, giao dịch định kỳ)
        cat_id = cat["id"]
        txn_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ? AND user_id = ?", (cat_id, user_id)).fetchone()[0]
        budget_count = conn.execute("SELECT COUNT(*) FROM budgets WHERE category_id = ? AND user_id = ?", (cat_id, user_id)).fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM recurring_transactions WHERE category_id = ? AND user_id = ?", (cat_id, user_id)).fetchone()[0]

        if txn_count > 0 or budget_count > 0 or rec_count > 0:
            reasons = []
            if txn_count > 0:
                reasons.append(f"{txn_count} giao dịch")
            if budget_count > 0:
                reasons.append(f"{budget_count} hạn mức tu luyện")
            if rec_count > 0:
                reasons.append(f"{rec_count} giao dịch định kỳ")
            detail_msg = f"Không thể xóa Danh mục '{cat['category_name']}' vì vẫn còn dữ liệu liên kết ({', '.join(reasons)}). Vui lòng chuyển hoặc xóa các dữ liệu này trước."
            return ToolResult(success=False, error=detail_msg)

        try:
            conn.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", (cat_id, user_id))
        except sqlite3.IntegrityError:
            return ToolResult(success=False, error=f"Không thể xóa Danh mục '{cat['category_name']}' do ràng buộc toàn vẹn dữ liệu.")

        # Post-action DB verification
        verify_del = conn.execute("SELECT id FROM categories WHERE id = ? AND user_id = ?", (cat_id, user_id)).fetchone()
        if verify_del:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Danh mục #{cat_id} vẫn còn tồn tại."
            )

    return ToolResult(
        success=True,
        data={"deleted_category_id": cat["id"], "deleted_category_name": cat["category_name"]},
        message=f"Đã xóa danh mục '{cat['category_name']}' khỏi tiên phủ."
    )


# ─────────────────────────────────────────────────────────────
# 3. TRANSACTION CAPABILITIES (SỔ GIAO DỊCH)
# ─────────────────────────────────────────────────────────────

# READ: get_recent_transactions
async def handle_get_recent_transactions(user_id: int, limit: int = 5, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        limit_val = min(max(1, int(limit)), 20)
        rows = conn.execute("""
            SELECT t.id, t.amount, t.transaction_type, t.transaction_date, t.note,
                   w.wallet_name, c.category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN wallets w ON t.wallet_id = w.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.transaction_date DESC, t.id DESC
            LIMIT ?
        """, (user_id, limit_val)).fetchall()
        txns = [dict(r) for r in rows]
        return ToolResult(
            success=True,
            data={"transactions": txns, "count": len(txns)},
            message=f"Tìm thấy {len(txns)} giao dịch gần nhất của Ký Chủ."
        )


# READ: search_transactions / transaction_search
async def handle_search_transactions(
    user_id: int,
    query: Optional[str] = None,
    category_name: Optional[str] = None,
    wallet_name: Optional[str] = None,
    time_frame: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    txn_type: Optional[str] = None,
    limit: int = 15,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        where_clauses = ["t.user_id = ?"]
        params = [user_id]
        if query:
            where_clauses.append("(t.note LIKE ? OR c.category_name LIKE ? OR w.wallet_name LIKE ?)")
            q_like = f"%{query.strip()}%"
            params.extend([q_like, q_like, q_like])
        if category_name:
            where_clauses.append("c.category_name LIKE ?")
            params.append(f"%{category_name.strip()}%")
        if wallet_name:
            where_clauses.append("w.wallet_name LIKE ?")
            params.append(f"%{wallet_name.strip()}%")
        if time_frame:
            s_date, e_date, _ = _resolve_period_range(time_frame)
            where_clauses.append("t.transaction_date >= ? AND t.transaction_date <= ?")
            params.extend([s_date, e_date])
        if min_amount is not None and float(min_amount) > 0:
            where_clauses.append("t.amount >= ?")
            params.append(float(min_amount))
        if max_amount is not None and float(max_amount) > 0:
            where_clauses.append("t.amount <= ?")
            params.append(float(max_amount))
        if not txn_type and kwargs.get("transaction_type"):
            txn_type = str(kwargs.get("transaction_type")).upper()
        elif txn_type:
            txn_type = str(txn_type).upper()
        if txn_type in ("INCOME", "EXPENSE"):
            where_clauses.append("t.transaction_type = ?")
            params.append(txn_type)

        limit_val = min(max(1, int(limit)), 50)
        sort_by = kwargs.get("sort_by") or ("amount" if kwargs.get("order_by_amount") else "date")
        order_dir = "ASC" if str(kwargs.get("order", "DESC")).upper() == "ASC" else "DESC"
        if sort_by == "amount":
            order_clause = f"t.amount {order_dir}, t.transaction_date DESC, t.id DESC"
        else:
            order_clause = f"t.transaction_date {order_dir}, t.id {order_dir}"

        sql = f"""
            SELECT t.id, t.amount, t.transaction_type, t.transaction_date, t.note,
                   w.wallet_name, c.category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN wallets w ON t.wallet_id = w.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE {' AND '.join(where_clauses)}
            ORDER BY {order_clause}
            LIMIT {limit_val}
        """
        rows = conn.execute(sql, params).fetchall()
        txns = [dict(r) for r in rows]

        if not txns:
            return ToolResult(
                success=True,
                data={"results": [], "transactions": [], "count": 0, "time_frame": time_frame},
                message="Khí Linh đã tra soát sổ sách nhưng không tìm thấy giao dịch nào phù hợp với yêu cầu."
            )

        total_val = sum(t["amount"] for t in txns)
        sample = txns[:3]
        sample_str = "; ".join([f"{t['transaction_date']}: {t['note']} ({t['amount']:,.0f}đ)" for t in sample])
        return ToolResult(
            success=True,
            data={"results": txns, "transactions": txns, "count": len(txns), "total_amount": total_val, "time_frame": time_frame},
            message=f"Tìm thấy {len(txns)} giao dịch phù hợp (Tổng số tiền: {total_val:,.0f} VNĐ). Tiêu biểu: {sample_str}."
        )


# WRITE: create_expense
async def handle_create_expense(
    user_id: int,
    amount: float,
    note: str,
    wallet_id: Optional[int] = None,
    wallet_name: Optional[str] = None,
    category_name: Optional[str] = None,
    transaction_date: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền chi tiêu phải lớn hơn 0.")

    today_str = transaction_date or datetime.date.today().strftime("%Y-%m-%d")
    with main.get_db() as conn:
        w = None
        if wallet_id:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
        elif wallet_name:
            all_w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
            matched = [x for x in all_w if _match_wallet_name(wallet_name, x["wallet_name"])]
            if matched:
                w = matched[0]

        if not w:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
            if not w:
                return ToolResult(success=False, error="Bạn chưa tạo Túi Càn Khôn nào. Hãy tạo ví trước khi ghi nhận chi tiêu.")

        cat_name = category_name.strip() if category_name and category_name.strip() else "Chi Tiêu Chung"
        cat_row = conn.execute(
            "SELECT id FROM categories WHERE user_id = ? AND category_type = 'EXPENSE' AND LOWER(category_name) = LOWER(?)",
            (user_id, cat_name)
        ).fetchone()
        if cat_row:
            cat_id = cat_row["id"]
        else:
            cat_id = main.get_or_create_system_category(conn, user_id, cat_name, "EXPENSE", "💸")

        clean_note = (note or "Chi tiêu qua Khí Linh").strip()
        op_id = kwargs.get("operation_id")
        if op_id:
            existing = conn.execute("SELECT id FROM transactions WHERE user_id = ? AND operation_id = ?", (user_id, op_id)).fetchone()
            if existing:
                return ToolResult(
                    success=True,
                    data={"transaction_id": existing["id"], "amount": amount, "wallet_name": w["wallet_name"], "already_processed": True},
                    message=f"Khoản chi {amount:,.0f} VNĐ cho '{clean_note}' đã được ghi nhận trước đó."
                )

        conn.execute("""
            INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note, operation_id)
            VALUES (?, ?, ?, ?, 'EXPENSE', ?, ?, ?)
        """, (user_id, w["id"], cat_id, amount, today_str, clean_note, op_id))
        conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?", (amount, w["id"], user_id))
        txn_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    return ToolResult(
        success=True,
        data={
            "transaction_id": txn_id,
            "amount": amount,
            "wallet_name": w["wallet_name"],
            "category_name": cat_name,
            "transaction_date": today_str,
            "note": clean_note
        },
        message=f"Đã ghi nhận khoản chi {amount:,.0f} VNĐ cho '{clean_note}' vào {w['wallet_name']} thành công!"
    )


# WRITE: create_income
async def handle_create_income(
    user_id: int,
    amount: float,
    note: str,
    wallet_id: Optional[int] = None,
    wallet_name: Optional[str] = None,
    category_name: Optional[str] = None,
    transaction_date: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền thu nhập phải lớn hơn 0.")

    today_str = transaction_date or datetime.date.today().strftime("%Y-%m-%d")
    with main.get_db() as conn:
        w = None
        if wallet_id:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
        elif wallet_name:
            all_w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
            matched = [x for x in all_w if _match_wallet_name(wallet_name, x["wallet_name"])]
            if matched:
                w = matched[0]

        if not w:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
            if not w:
                return ToolResult(success=False, error="Bạn chưa tạo Túi Càn Khôn nào.")

        cat_name = category_name.strip() if category_name and category_name.strip() else "Thu Nhập Khác"
        cat_row = conn.execute(
            "SELECT id FROM categories WHERE user_id = ? AND category_type = 'INCOME' AND LOWER(category_name) = LOWER(?)",
            (user_id, cat_name)
        ).fetchone()
        if cat_row:
            cat_id = cat_row["id"]
        else:
            cat_id = main.get_or_create_system_category(conn, user_id, cat_name, "INCOME", "💰")

        clean_note = (note or "Thu nhập qua Khí Linh").strip()
        op_id = kwargs.get("operation_id")
        if op_id:
            existing = conn.execute("SELECT id FROM transactions WHERE user_id = ? AND operation_id = ?", (user_id, op_id)).fetchone()
            if existing:
                return ToolResult(
                    success=True,
                    data={"transaction_id": existing["id"], "amount": amount, "wallet_name": w["wallet_name"], "already_processed": True},
                    message=f"Khoản thu {amount:,.0f} VNĐ từ '{clean_note}' đã được ghi nhận trước đó."
                )

        conn.execute("""
            INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note, operation_id)
            VALUES (?, ?, ?, ?, 'INCOME', ?, ?, ?)
        """, (user_id, w["id"], cat_id, amount, today_str, clean_note, op_id))
        conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?", (amount, w["id"], user_id))
        txn_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    return ToolResult(
        success=True,
        data={
            "transaction_id": txn_id,
            "amount": amount,
            "wallet_name": w["wallet_name"],
            "category_name": cat_name,
            "transaction_date": today_str,
            "note": clean_note
        },
        message=f"Đã ghi nhận khoản thu {amount:,.0f} VNĐ từ '{clean_note}' vào {w['wallet_name']} thành công!"
    )


# WRITE: update_transaction
async def handle_update_transaction(
    user_id: int,
    transaction_id: int,
    amount: Optional[float] = None,
    note: Optional[str] = None,
    transaction_date: Optional[str] = None,
    category_name: Optional[str] = None,
    wallet_name: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        txn = conn.execute(
            "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id)
        ).fetchone()
        if not txn:
            return ToolResult(success=False, error=f"Không tìm thấy giao dịch ID #{transaction_id} của bạn.")

        old_wallet_id = txn["wallet_id"]
        old_amount = txn["amount"]
        txn_type = txn["transaction_type"]

        new_amount = float(amount) if amount is not None and float(amount) > 0 else old_amount
        new_note = note.strip() if note and note.strip() else txn["note"]
        new_date = transaction_date.strip() if transaction_date and transaction_date.strip() else txn["transaction_date"]

        new_wallet_id = old_wallet_id
        if wallet_name:
            w_row = conn.execute(
                "SELECT id FROM wallets WHERE user_id = ? AND LOWER(wallet_name) LIKE ?",
                (user_id, f"%{wallet_name.strip().lower()}%")
            ).fetchone()
            if w_row:
                new_wallet_id = w_row["id"]

        new_cat_id = txn["category_id"]
        if category_name:
            c_row = conn.execute(
                "SELECT id FROM categories WHERE user_id = ? AND category_type = ? AND LOWER(category_name) LIKE ?",
                (user_id, txn_type, f"%{category_name.strip().lower()}%")
            ).fetchone()
            if c_row:
                new_cat_id = c_row["id"]

        # Hoàn lại số dư cũ
        if txn_type == "EXPENSE":
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?", (old_amount, old_wallet_id, user_id))
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?", (new_amount, new_wallet_id, user_id))
        else:
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?", (old_amount, old_wallet_id, user_id))
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?", (new_amount, new_wallet_id, user_id))

        conn.execute("""
            UPDATE transactions
            SET amount = ?, note = ?, transaction_date = ?, wallet_id = ?, category_id = ?
            WHERE id = ? AND user_id = ?
        """, (new_amount, new_note, new_date, new_wallet_id, new_cat_id, transaction_id, user_id))

    return ToolResult(
        success=True,
        data={"transaction_id": transaction_id, "amount": new_amount, "note": new_note, "transaction_date": new_date},
        message=f"Đã cập nhật giao dịch #{transaction_id}: {new_amount:,.0f} VNĐ ('{new_note}')."
    )


# DELETE: delete_transaction
async def handle_delete_transaction(user_id: int, transaction_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        txn = conn.execute(
            "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id)
        ).fetchone()
        if not txn:
            return ToolResult(success=False, error=f"Không tìm thấy giao dịch ID #{transaction_id} để xóa.")

        # Hoàn lại số dư ví
        amt = txn["amount"]
        w_id = txn["wallet_id"]
        if txn["transaction_type"] == "EXPENSE":
            conn.execute("UPDATE wallets SET balance = balance + ? WHERE id = ? AND user_id = ?", (amt, w_id, user_id))
        else:
            conn.execute("UPDATE wallets SET balance = balance - ? WHERE id = ? AND user_id = ?", (amt, w_id, user_id))

        conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))

        # Post-action DB verification
        verify_del = conn.execute("SELECT id FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id)).fetchone()
        if verify_del:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Giao dịch #{transaction_id} vẫn còn tồn tại."
            )

    return ToolResult(
        success=True,
        data={"deleted_transaction_id": transaction_id, "amount": amt, "note": txn["note"]},
        message=f"Đã xóa giao dịch #{transaction_id} ('{txn['note']}') và hoàn lại {amt:,.0f} VNĐ vào số dư ví."
    )


# ─────────────────────────────────────────────────────────────
# 4. BUDGET CAPABILITIES (HẠN MỨC NGÂN SÁCH)
# ─────────────────────────────────────────────────────────────

# READ: get_budget_status / budget_status
async def handle_get_budget_status(
    user_id: int,
    category_name: Optional[str] = None,
    month_year: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    today = datetime.date.today()
    if not month_year or month_year in ("this_month", "tháng này", "thang nay"):
        month_year = today.strftime("%Y-%m")
    elif month_year in ("next_month", "tháng sau", "thang sau", "tháng tới", "thang toi"):
        if today.month == 12:
            next_y, next_m = today.year + 1, 1
        else:
            next_y, next_m = today.year, today.month + 1
        month_year = f"{next_y:04d}-{next_m:02d}"

    with main.get_db() as conn:
        rows = conn.execute("""
            SELECT b.id, b.limit_amount, b.month_year, c.category_name, c.icon,
                   COALESCE(SUM(t.amount), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            LEFT JOIN transactions t ON t.category_id = c.id
                 AND t.user_id = b.user_id
                 AND t.transaction_type = 'EXPENSE'
                 AND strftime('%Y-%m', t.transaction_date) = b.month_year
            WHERE b.user_id = ? AND b.month_year = ?
            GROUP BY b.id
        """, (user_id, month_year)).fetchall()

        items = []
        for r in rows:
            b = dict(r)
            pct = (b["spent"] / b["limit_amount"] * 100) if b["limit_amount"] > 0 else 0
            items.append({
                "budget_id": b["id"],
                "category_name": b["category_name"],
                "icon": b["icon"],
                "limit_amount": b["limit_amount"],
                "spent": b["spent"],
                "remaining": max(0, b["limit_amount"] - b["spent"]),
                "percent": round(pct, 1),
                "is_exceeded": pct >= 100
            })

        if category_name:
            clean_c = category_name.lower().strip()
            matched = [it for it in items if clean_c in it["category_name"].lower()]
            if matched:
                target = matched[0]
                warn = " ⚠️ ĐÃ VƯỢT HẠN MỨC!" if target["is_exceeded"] else f" (Còn lại {target['remaining']:,.0f} VNĐ, đạt {target['percent']}%)"
                return ToolResult(
                    success=True,
                    data={"category_name": target["category_name"], "month_year": month_year, "category_budget": target, "budgets": items},
                    message=f"Ngân sách '{target['category_name']}' tháng {month_year}: Hạn mức {target['limit_amount']:,.0f} VNĐ, Đã chi {target['spent']:,.0f} VNĐ{warn}."
                )

        exceeded_cnt = sum(1 for it in items if it["is_exceeded"])
        exceeded_note = f", có {exceeded_cnt} danh mục vượt hạn mức!" if exceeded_cnt > 0 else ""
        details = ": " + ", ".join(f"{it['category_name']} ({it['spent']:,.0f}/{it['limit_amount']:,.0f} VNĐ)" for it in items) if items else ""
        return ToolResult(
            success=True,
            data={"month_year": month_year, "budgets": items, "exceeded_count": exceeded_cnt},
            message=f"Ký Chủ đã thiết lập {len(items)} hạn mức chi tiêu trong tháng {month_year}{details}{exceeded_note}." if items else f"Ký Chủ chưa thiết lập hạn mức chi tiêu nào trong tháng {month_year}."
        )


# WRITE: create_budget
async def handle_create_budget(
    user_id: int,
    limit_amount: float,
    category_name: Optional[str] = None,
    category_id: Optional[int] = None,
    month_year: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if limit_amount <= 0:
        return ToolResult(success=False, error="Hạn mức ngân sách phải lớn hơn 0.")

    today = datetime.date.today()
    if not month_year or month_year in ("this_month", "tháng này", "thang nay", "hôm nay"):
        month_year = today.strftime("%Y-%m")
    elif month_year in ("next_month", "tháng sau", "thang sau", "tháng tới", "thang toi"):
        if today.month == 12:
            next_y, next_m = today.year + 1, 1
        else:
            next_y, next_m = today.year, today.month + 1
        month_year = f"{next_y:04d}-{next_m:02d}"

    with main.get_db() as conn:
        cat_id = None
        target_cat_name = (category_name or "Ăn Uống").strip()
        if category_id:
            cat_row = conn.execute("SELECT id, category_name FROM categories WHERE id = ? AND (user_id = ? OR user_id IS NULL)", (category_id, user_id)).fetchone()
            if cat_row:
                cat_id = cat_row["id"]
                target_cat_name = cat_row["category_name"]

        if not cat_id:
            cat_row = conn.execute(
                "SELECT id, category_name FROM categories WHERE (user_id = ? OR user_id IS NULL) AND category_type = 'EXPENSE' AND LOWER(category_name) = LOWER(?)",
                (user_id, target_cat_name)
            ).fetchone()
            if cat_row:
                cat_id = cat_row["id"]
                target_cat_name = cat_row["category_name"]
            else:
                like_row = conn.execute(
                    "SELECT id, category_name FROM categories WHERE (user_id = ? OR user_id IS NULL) AND category_type = 'EXPENSE' AND LOWER(category_name) LIKE LOWER(?)",
                    (user_id, f"%{target_cat_name}%")
                ).fetchone()
                if like_row:
                    cat_id = like_row["id"]
                    target_cat_name = like_row["category_name"]
                else:
                    # Principle 9: Nếu entity không tồn tại: báo không tìm thấy. KHÔNG tự tạo entity thay thế.
                    return ToolResult(
                        success=False,
                        error=f"Không tìm thấy danh mục '{target_cat_name}' trong hệ thống. Ký Chủ vui lòng tạo danh mục trước hoặc chọn danh mục đã có."
                    )

        existing = conn.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category_id = ? AND month_year = ?",
            (user_id, cat_id, month_year)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE budgets SET limit_amount = ? WHERE id = ? AND user_id = ?",
                (limit_amount, existing["id"], user_id)
            )
            b_id = existing["id"]
        else:
            conn.execute(
                "INSERT INTO budgets (user_id, category_id, limit_amount, month_year) VALUES (?, ?, ?, ?)",
                (user_id, cat_id, limit_amount, month_year)
            )
            b_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Post-action DB verification
        verify_row = conn.execute(
            "SELECT id, limit_amount, month_year FROM budgets WHERE id = ? AND user_id = ?",
            (b_id, user_id)
        ).fetchone()
        if not verify_row or verify_row["limit_amount"] != limit_amount:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Hạn mức #{b_id} chưa được lưu thành công vào Càn Khôn Các."
            )

    return ToolResult(
        success=True,
        data={
            "budget_id": b_id,
            "category_id": cat_id,
            "category_name": target_cat_name,
            "limit_amount": limit_amount,
            "month_year": month_year
        },
        message=f"Đã thiết lập hạn mức ngân sách {limit_amount:,.0f} VNĐ cho danh mục '{target_cat_name}' trong tháng {month_year} thành công!"
    )


# WRITE: update_budget
async def handle_update_budget(
    user_id: int,
    budget_id: Optional[int] = None,
    category_name: Optional[str] = None,
    limit_amount: float = 0,
    month_year: Optional[str] = None,
    **kwargs
) -> ToolResult:
    if limit_amount <= 0:
        return ToolResult(success=False, error="Hạn mức ngân sách mới phải lớn hơn 0.")
    return await handle_create_budget(user_id, limit_amount, category_name=category_name, category_id=budget_id, month_year=month_year, **kwargs)


# DELETE: delete_budget
async def handle_delete_budget(
    user_id: int,
    budget_id: Optional[int] = None,
    category_name: Optional[str] = None,
    month_year: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        target = None
        if budget_id:
            target = conn.execute("SELECT b.id, c.category_name, b.month_year FROM budgets b JOIN categories c ON b.category_id = c.id WHERE b.id = ? AND b.user_id = ?", (budget_id, user_id)).fetchone()
        elif category_name:
            m_y = month_year or datetime.date.today().strftime("%Y-%m")
            target = conn.execute("""
                SELECT b.id, c.category_name, b.month_year
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                WHERE b.user_id = ? AND b.month_year = ? AND LOWER(c.category_name) LIKE ?
            """, (user_id, m_y, f"%{category_name.strip().lower()}%")).fetchone()

        if not target:
            return ToolResult(success=False, error=f"Không tìm thấy ngân sách '{category_name or budget_id}' để xóa.")

        conn.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (target["id"], user_id))

        # Post-action DB verification
        verify_del = conn.execute("SELECT id FROM budgets WHERE id = ? AND user_id = ?", (target["id"], user_id)).fetchone()
        if verify_del:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Hạn mức #{target['id']} vẫn còn tồn tại trong hệ thống."
            )

    return ToolResult(
        success=True,
        data={"deleted_budget_id": target["id"], "category_name": target["category_name"], "month_year": target["month_year"]},
        message=f"Đã xóa hạn mức ngân sách '{target['category_name']}' tháng {target['month_year']} thành công!"
    )


# ─────────────────────────────────────────────────────────────
# 5. RECURRING CAPABILITIES (GIAO DỊCH ĐỊNH KỲ)
# ─────────────────────────────────────────────────────────────

# READ: get_recurring_transactions
async def handle_get_recurring_transactions(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        recs = conn.execute("""
            SELECT r.*, w.wallet_name, c.category_name, c.icon
            FROM recurring_transactions r
            LEFT JOIN wallets w ON r.wallet_id = w.id
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE r.user_id = ? AND r.is_active = 1
            ORDER BY r.next_run_date ASC
        """, (user_id,)).fetchall()
        items = [dict(r) for r in recs]
        details = ": " + ", ".join(f"'{r.get('note') or 'Giao dịch'}' ({float(r.get('amount', 0)):,.0f} VNĐ, {r.get('frequency', 'monthly')})" for r in items) if items else ""
        return ToolResult(
            success=True,
            data={"recurring": items, "count": len(items)},
            message=f"Ký Chủ có {len(items)} giao dịch định kỳ đang hoạt động{details}." if items else "Ký Chủ chưa có giao dịch định kỳ nào."
        )


# WRITE: create_recurring_transaction
async def handle_create_recurring_transaction(
    user_id: int,
    amount: float,
    transaction_type: str = "EXPENSE",
    frequency: str = "monthly",
    next_run_date: Optional[str] = None,
    category_name: Optional[str] = None,
    wallet_name: Optional[str] = None,
    note: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền định kỳ phải lớn hơn 0.")

    txn_type = transaction_type.upper() if transaction_type else "EXPENSE"
    if txn_type not in ("EXPENSE", "INCOME"):
        txn_type = "EXPENSE"

    freq = frequency.lower() if frequency in ("weekly", "monthly") else "monthly"
    run_date = next_run_date or datetime.date.today().strftime("%Y-%m-%d")

    with main.get_db() as conn:
        # Chọn ví
        w = None
        if wallet_name:
            all_w = conn.execute("SELECT id, wallet_name FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
            matched = [x for x in all_w if _match_wallet_name(wallet_name, x["wallet_name"])]
            if matched:
                w = matched[0]
        if not w:
            w = conn.execute("SELECT id, wallet_name FROM wallets WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
            if not w:
                return ToolResult(success=False, error="Ký Chủ chưa có Túi Càn Khôn nào.")

        # Chọn danh mục
        cat_name = category_name or ("Chi Phí Cố Định" if txn_type == "EXPENSE" else "Thu Nhập Định Kỳ")
        cat_row = conn.execute(
            "SELECT id FROM categories WHERE user_id = ? AND category_type = ? AND LOWER(category_name) = LOWER(?)",
            (user_id, txn_type, cat_name)
        ).fetchone()
        if cat_row:
            cat_id = cat_row["id"]
        else:
            cat_id = main.get_or_create_system_category(conn, user_id, cat_name, txn_type, "🔄")

        clean_note = (note or "Giao dịch định kỳ Khí Linh").strip()
        conn.execute("""
            INSERT INTO recurring_transactions (user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, note, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (user_id, w["id"], cat_id, amount, txn_type, freq, run_date, clean_note))
        rec_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    freq_label = "hàng tháng" if freq == "monthly" else "hàng tuần"
    return ToolResult(
        success=True,
        data={"recurring_id": rec_id, "amount": amount, "frequency": freq, "next_run_date": run_date, "note": clean_note},
        message=f"Đã lập lịch giao dịch định kỳ {amount:,.0f} VNĐ {freq_label} cho '{clean_note}' (Bắt đầu: {run_date}) thành công!"
    )


# WRITE: update_recurring_transaction
async def handle_update_recurring_transaction(
    user_id: int,
    rec_id: int,
    amount: Optional[float] = None,
    frequency: Optional[str] = None,
    is_active: Optional[int] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        r = conn.execute("SELECT * FROM recurring_transactions WHERE id = ? AND user_id = ?", (rec_id, user_id)).fetchone()
        if not r:
            return ToolResult(success=False, error=f"Không tìm thấy giao dịch định kỳ ID #{rec_id}.")

        new_amt = float(amount) if amount is not None and float(amount) > 0 else r["amount"]
        new_freq = frequency if frequency in ("weekly", "monthly") else r["frequency"]
        new_active = int(is_active) if is_active is not None else r["is_active"]

        conn.execute(
            "UPDATE recurring_transactions SET amount = ?, frequency = ?, is_active = ? WHERE id = ? AND user_id = ?",
            (new_amt, new_freq, new_active, rec_id, user_id)
        )

    return ToolResult(
        success=True,
        data={"recurring_id": rec_id, "amount": new_amt, "frequency": new_freq, "is_active": new_active},
        message=f"Đã cập nhật giao dịch định kỳ #{rec_id} thành công!"
    )


# DELETE: delete_recurring_transaction
async def handle_delete_recurring_transaction(user_id: int, rec_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        r = conn.execute("SELECT id, note FROM recurring_transactions WHERE id = ? AND user_id = ?", (rec_id, user_id)).fetchone()
        if not r:
            return ToolResult(success=False, error=f"Không tìm thấy giao dịch định kỳ ID #{rec_id} để xóa.")

        conn.execute("DELETE FROM recurring_transactions WHERE id = ? AND user_id = ?", (rec_id, user_id))

    return ToolResult(
        success=True,
        data={"deleted_recurring_id": rec_id},
        message=f"Đã xóa giao dịch định kỳ #{rec_id} ('{r['note']}') thành công!"
    )


# ─────────────────────────────────────────────────────────────
# 6. DEBT CAPABILITIES (SỔ NỢ & VAY MƯỢN)
# ─────────────────────────────────────────────────────────────

# READ: get_debts / debt_status
async def handle_get_debts(user_id: int, debt_type: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        debts = conn.execute("SELECT * FROM debts WHERE user_id = ? ORDER BY is_settled ASC, id DESC", (user_id,)).fetchall()
        debt_list = [dict(d) for d in debts]
        unsettled_borrow = [d for d in debt_list if d["debt_type"] == "BORROW" and not d["is_settled"]]
        unsettled_lend = [d for d in debt_list if d["debt_type"] == "LEND" and not d["is_settled"]]
        i_owe = sum(d["amount"] for d in unsettled_borrow)
        they_owe = sum(d["amount"] for d in unsettled_lend)
        net = they_owe - i_owe

        if debt_type == "BORROW":
            return ToolResult(
                success=True,
                data={"debts": unsettled_borrow, "total_borrowing": i_owe},
                message=f"Ký Chủ hiện đang nợ người khác tổng cộng {i_owe:,.0f} VNĐ qua {len(unsettled_borrow)} khoản chưa thanh toán."
            )
        if debt_type == "LEND":
            return ToolResult(
                success=True,
                data={"debts": unsettled_lend, "total_lending": they_owe},
                message=f"Người khác hiện đang nợ Ký Chủ tổng cộng {they_owe:,.0f} VNĐ qua {len(unsettled_lend)} khoản chưa thu hồi."
            )

        return ToolResult(
            success=True,
            data={
                "debts": debt_list,
                "total_borrowing": i_owe,
                "total_lending": they_owe,
                "net_balance": net,
                "unsettled_borrow_count": len(unsettled_borrow),
                "unsettled_lend_count": len(unsettled_lend)
            },
            message=f"Sổ nợ: Ký Chủ đang nợ {i_owe:,.0f} VNĐ ({len(unsettled_borrow)} khoản) và được người khác nợ {they_owe:,.0f} VNĐ ({len(unsettled_lend)} khoản). Chênh lệch thực tế là {net:+,.0f} VNĐ."
        )


# WRITE: create_debt
async def handle_create_debt(
    user_id: int,
    debt_type: str,
    person_name: str,
    amount: float,
    due_date: Optional[str] = None,
    note: Optional[str] = None,
    wallet_name: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    clean_person = (person_name or "").strip()
    if not clean_person:
        return ToolResult(success=False, error="Tên đối tác vay mượn không được để trống.")
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền vay mượn phải lớn hơn 0.")

    d_type = debt_type.upper() if debt_type else "LEND"
    if d_type not in ("BORROW", "LEND"):
        d_type = "LEND"

    with main.get_db() as conn:
        w_id = None
        if wallet_name:
            all_w = conn.execute("SELECT id, wallet_name FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
            matched = [x for x in all_w if _match_wallet_name(wallet_name, x["wallet_name"])]
            if matched:
                w_id = matched[0]["id"]
        if not w_id:
            w_first = conn.execute("SELECT id FROM wallets WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
            if w_first:
                w_id = w_first["id"]

        conn.execute("""
            INSERT INTO debts (user_id, wallet_id, debt_type, person_name, amount, due_date, is_settled, note)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (user_id, w_id, d_type, clean_person, amount, due_date or "", note or ""))
        debt_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Post-action DB verification
        verify_row = conn.execute("SELECT id, amount, is_settled FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id)).fetchone()
        if not verify_row:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Khoản nợ #{debt_id} chưa được ghi nhận vào sổ nợ."
            )

    label = "cho vay" if d_type == "LEND" else "đi vay"
    return ToolResult(
        success=True,
        data={"debt_id": debt_id, "debt_type": d_type, "person_name": clean_person, "amount": amount, "due_date": due_date},
        message=f"Đã ghi vào sổ nợ: Khoản {label} '{clean_person}' số tiền {amount:,.0f} VNĐ thành công!"
    )


# WRITE: update_debt
async def handle_update_debt(
    user_id: int,
    debt_id: Optional[int] = None,
    person_name: Optional[str] = None,
    amount: Optional[float] = None,
    due_date: Optional[str] = None,
    note: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        d = None
        if debt_id:
            d = conn.execute("SELECT * FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id)).fetchone()
        elif person_name:
            d = conn.execute("SELECT * FROM debts WHERE user_id = ? AND LOWER(person_name) LIKE ? ORDER BY id DESC LIMIT 1", (user_id, f"%{person_name.strip().lower()}%")).fetchone()

        if not d:
            return ToolResult(success=False, error=f"Không tìm thấy khoản nợ của '{person_name or debt_id}'.")

        new_amt = float(amount) if amount is not None and float(amount) > 0 else d["amount"]
        new_due = due_date.strip() if due_date else d["due_date"]
        new_note = note.strip() if note else d["note"]

        conn.execute(
            "UPDATE debts SET amount = ?, due_date = ?, note = ? WHERE id = ? AND user_id = ?",
            (new_amt, new_due, new_note, d["id"], user_id)
        )

        # Post-action DB verification
        verify_row = conn.execute("SELECT amount FROM debts WHERE id = ? AND user_id = ?", (d["id"], user_id)).fetchone()
        if not verify_row or verify_row["amount"] != new_amt:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Khoản nợ #{d['id']} chưa được cập nhật trong sổ nợ."
            )

    return ToolResult(
        success=True,
        data={"debt_id": d["id"], "person_name": d["person_name"], "amount": new_amt, "due_date": new_due},
        message=f"Đã cập nhật khoản nợ của '{d['person_name']}' thành {new_amt:,.0f} VNĐ."
    )


# WRITE: settle_debt
async def handle_settle_debt(
    user_id: int,
    debt_id: Optional[int] = None,
    person_name: Optional[str] = None,
    wallet_id: Optional[int] = None,
    wallet_name: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        d = None
        if debt_id:
            d = conn.execute("SELECT * FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id)).fetchone()
        elif person_name:
            d = conn.execute(
                "SELECT * FROM debts WHERE user_id = ? AND LOWER(person_name) LIKE ? AND is_settled = 0 ORDER BY id DESC LIMIT 1",
                (user_id, f"%{person_name.strip().lower()}%")
            ).fetchone()

        if not d:
            return ToolResult(success=False, error=f"Không tìm thấy khoản nợ chưa quyết toán của '{person_name or debt_id}'.")

        conn.execute("UPDATE debts SET is_settled = 1 WHERE id = ? AND user_id = ?", (d["id"], user_id))

        # Post-action DB verification
        verify_row = conn.execute("SELECT is_settled FROM debts WHERE id = ? AND user_id = ?", (d["id"], user_id)).fetchone()
        if not verify_row or not verify_row["is_settled"]:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Khoản nợ #{d['id']} chưa được chuyển sang trạng thái tất toán."
            )

    action_label = "thu hồi nợ từ" if d["debt_type"] == "LEND" else "hoàn trả nợ cho"
    return ToolResult(
        success=True,
        data={"settled_debt_id": d["id"], "person_name": d["person_name"], "amount": d["amount"]},
        message=f"Đã quyết toán thành công khoản {action_label} '{d['person_name']}' số tiền {d['amount']:,.0f} VNĐ!"
    )


# DELETE: delete_debt
async def handle_delete_debt(user_id: int, debt_id: Optional[int] = None, person_name: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        d = None
        if debt_id:
            d = conn.execute("SELECT * FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id)).fetchone()
        elif person_name:
            d = conn.execute("SELECT * FROM debts WHERE user_id = ? AND LOWER(person_name) LIKE ? ORDER BY id DESC LIMIT 1", (user_id, f"%{person_name.strip().lower()}%")).fetchone()

        if not d:
            return ToolResult(success=False, error=f"Không tìm thấy khoản nợ của '{person_name or debt_id}' để xóa.")

        conn.execute("DELETE FROM debts WHERE id = ? AND user_id = ?", (d["id"], user_id))

        # Post-action DB verification
        verify_del = conn.execute("SELECT id FROM debts WHERE id = ? AND user_id = ?", (d["id"], user_id)).fetchone()
        if verify_del:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Khoản nợ #{d['id']} vẫn còn tồn tại trong sổ nợ."
            )

    return ToolResult(
        success=True,
        data={"deleted_debt_id": d["id"], "person_name": d["person_name"]},
        message=f"Đã xóa khoản nợ của '{d['person_name']}' khỏi sổ sách."
    )


# ─────────────────────────────────────────────────────────────
# 7. SAVING GOAL CAPABILITIES (MỤC TIÊU TIẾT KIỆM)
# ─────────────────────────────────────────────────────────────

# READ: get_saving_goals / saving_goal_status
async def handle_get_saving_goals(user_id: int, goal_name: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute("SELECT * FROM saving_goals WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
        goals = [dict(r) for r in rows]
        for g in goals:
            pct = (g["current_amount"] / g["target_amount"] * 100) if g["target_amount"] > 0 else 0
            g["percent"] = round(pct, 1)
            g["remaining_amount"] = max(0, g["target_amount"] - g["current_amount"])

        if goal_name:
            clean_g = goal_name.lower().replace("mục tiêu", "").replace("muc tieu", "").strip()
            matched = [g for g in goals if clean_g in g["target_name"].lower()]
            if matched:
                target = matched[0]
                status_txt = "Đã hoàn thành xuất sắc! 🎉" if target["is_completed"] else f"Còn thiếu {target['remaining_amount']:,.0f} VNĐ"
                return ToolResult(
                    success=True,
                    data={"target_goal": target, "saving_goals": goals},
                    message=f"Mục tiêu '{target['target_name']}': Đã tích lũy {target['current_amount']:,.0f} / {target['target_amount']:,.0f} VNĐ ({target['percent']}%). {status_txt}."
                )

        total_target = sum(g["target_amount"] for g in goals)
        total_saved = sum(g["current_amount"] for g in goals)
        overall_pct = round(total_saved / total_target * 100, 1) if total_target > 0 else 0
        uncompleted_goals = [g for g in goals if not g.get("is_completed")]
        closest_goal = max(uncompleted_goals, key=lambda g: g["percent"]) if uncompleted_goals else None
        total_remaining = sum(g["remaining_amount"] for g in uncompleted_goals)
        return ToolResult(
            success=True,
            data={
                "saving_goals": goals,
                "count": len(goals),
                "total_target": total_target,
                "total_saved": total_saved,
                "total_remaining": total_remaining,
                "overall_percent": overall_pct,
                "closest_goal": closest_goal
            },
            message=f"Ký Chủ có {len(goals)} mục tiêu tiết kiệm, đã tích lũy {total_saved:,.0f} / {total_target:,.0f} VNĐ ({overall_pct}%)."
        )


# WRITE: create_saving_goal
async def handle_create_saving_goal(
    user_id: int,
    target_name: str,
    target_amount: float,
    current_amount: float = 0,
    target_date: Optional[str] = None,
    icon: str = "🎯",
    **kwargs
) -> ToolResult:
    import main
    clean_name = (target_name or "").strip()
    if not clean_name:
        return ToolResult(success=False, error="Tên mục tiêu tiết kiệm không được để trống.")
    if target_amount <= 0:
        return ToolResult(success=False, error="Mục tiêu tài chính phải lớn hơn 0.")

    with main.get_db() as conn:
        conn.execute("""
            INSERT INTO saving_goals (user_id, target_name, target_amount, current_amount, target_date, icon, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, clean_name, target_amount, max(0, current_amount), target_date or "", icon or "🎯", 1 if current_amount >= target_amount else 0))
        g_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    return ToolResult(
        success=True,
        data={"goal_id": g_id, "target_name": clean_name, "target_amount": target_amount, "current_amount": current_amount},
        message=f"Đã lập mục tiêu tiết kiệm '{clean_name}' với hạn mức {target_amount:,.0f} VNĐ thành công!"
    )


# WRITE: update_saving_goal
async def handle_update_saving_goal(
    user_id: int,
    goal_id: Optional[int] = None,
    target_name: Optional[str] = None,
    target_amount: Optional[float] = None,
    target_date: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    with main.get_db() as conn:
        g = None
        if goal_id:
            g = conn.execute("SELECT * FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user_id)).fetchone()
        elif target_name:
            g = conn.execute("SELECT * FROM saving_goals WHERE user_id = ? AND LOWER(target_name) LIKE ?", (user_id, f"%{target_name.strip().lower()}%")).fetchone()

        if not g:
            return ToolResult(success=False, error=f"Không tìm thấy mục tiêu '{target_name or goal_id}'.")

        new_target = float(target_amount) if target_amount is not None and float(target_amount) > 0 else g["target_amount"]
        new_date = target_date.strip() if target_date else g["target_date"]
        is_comp = 1 if g["current_amount"] >= new_target else 0

        conn.execute(
            "UPDATE saving_goals SET target_amount = ?, target_date = ?, is_completed = ? WHERE id = ? AND user_id = ?",
            (new_target, new_date, is_comp, g["id"], user_id)
        )

    return ToolResult(
        success=True,
        data={"goal_id": g["id"], "target_name": g["target_name"], "target_amount": new_target},
        message=f"Đã cập nhật mục tiêu '{g['target_name']}' thành {new_target:,.0f} VNĐ."
    )


# WRITE: saving_goal_deposit
async def handle_saving_goal_deposit(
    user_id: int,
    amount: float,
    goal_id: Optional[int] = None,
    goal_name: Optional[str] = None,
    wallet_id: Optional[int] = None,
    wallet_name: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền tích lũy phải lớn hơn 0.")

    with main.get_db() as conn:
        goals = conn.execute("SELECT id, target_name, target_amount, current_amount, is_completed FROM saving_goals WHERE user_id = ?", (user_id,)).fetchall()
        if not goals:
            return ToolResult(success=False, error="Ký Chủ chưa có mục tiêu tiết kiệm nào. Hãy tạo mục tiêu trước.")

        target_goal = None
        if goal_id:
            target_goal = next((g for g in goals if g["id"] == goal_id), None)
            if not target_goal:
                return ToolResult(success=False, error="Không tìm thấy mục tiêu tiết kiệm theo ID đã cung cấp.")
        elif goal_name:
            clean_goal = goal_name.lower().replace("mục tiêu", "").replace("muc tieu", "").strip()
            target_goal = next((g for g in goals if clean_goal in g["target_name"].lower() or g["target_name"].lower() in clean_goal), None)
            if not target_goal:
                return ToolResult(success=False, error=f"Không tìm thấy mục tiêu tiết kiệm '{goal_name}' của bạn.")
        else:
            target_goal = next((g for g in goals if not g["is_completed"]), goals[0])

        if not target_goal:
            return ToolResult(success=False, error="Không tìm thấy mục tiêu tiết kiệm phù hợp.")

        wallets = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
        if not wallets:
            return ToolResult(success=False, error="Không tìm thấy ví tiền.")

        w = None
        if wallet_id:
            w = next((x for x in wallets if x["id"] == wallet_id), None)
        elif wallet_name:
            matched = [x for x in wallets if _match_wallet_name(wallet_name, x["wallet_name"])]
            if matched:
                w = matched[0]
        if not w:
            w = wallets[0]

        if w["balance"] < amount:
            return ToolResult(
                success=False,
                error=f"Số dư trong {w['wallet_name']} không đủ (Còn {w['balance']:,.0f} VNĐ). Ký Chủ có muốn thử lại với số tiền tối đa {w['balance']:,.0f} VNĐ không?"
            )

        body = main.SavingGoalDepositBody(
            amount=amount,
            wallet_id=w["id"],
            operation_id=kwargs.get("operation_id")
        )
        res = main.deposit_saving_goal(target_goal["id"], body, user={"user_id": user_id})
        res_data = dict(res) if isinstance(res, dict) else {}
        res_data["goal_id"] = target_goal["id"]
        res_data["goal_name"] = target_goal["target_name"]
        return ToolResult(
            success=True,
            data=res_data,
            message=f"Đã tích lũy thêm {amount:,.0f} VNĐ từ '{w['wallet_name']}' vào mục tiêu '{target_goal['target_name']}'!"
        )


# WRITE: saving_goal_withdraw
async def handle_saving_goal_withdraw(
    user_id: int,
    amount: float,
    goal_id: Optional[int] = None,
    goal_name: Optional[str] = None,
    wallet_id: Optional[int] = None,
    wallet_name: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền rút phải lớn hơn 0.")

    with main.get_db() as conn:
        goals = conn.execute("SELECT id, target_name, target_amount, current_amount FROM saving_goals WHERE user_id = ?", (user_id,)).fetchall()
        target_goal = None
        if goal_id:
            target_goal = next((g for g in goals if g["id"] == goal_id), None)
        elif goal_name:
            clean_goal = goal_name.lower().replace("mục tiêu", "").replace("muc tieu", "").strip()
            target_goal = next((g for g in goals if clean_goal in g["target_name"].lower() or g["target_name"].lower() in clean_goal), None)

        if not target_goal:
            return ToolResult(success=False, error=f"Không tìm thấy mục tiêu tiết kiệm '{goal_name or goal_id}'.")

        if target_goal["current_amount"] < amount:
            return ToolResult(
                success=False,
                error=f"Số tiền đã tích lũy trong mục tiêu '{target_goal['target_name']}' chỉ còn {target_goal['current_amount']:,.0f} VNĐ, không đủ để rút {amount:,.0f} VNĐ."
            )

        wallets = conn.execute("SELECT id, wallet_name FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
        w = None
        if wallet_id:
            w = next((x for x in wallets if x["id"] == wallet_id), None)
        elif wallet_name:
            matched = [x for x in wallets if _match_wallet_name(wallet_name, x["wallet_name"])]
            if matched:
                w = matched[0]
        if not w:
            w = wallets[0]

        body = main.SavingGoalDepositBody(
            amount=amount,
            wallet_id=w["id"],
            operation_id=kwargs.get("operation_id")
        )
        res = main.withdraw_saving_goal(target_goal["id"], body, user={"user_id": user_id})

    return ToolResult(
        success=True,
        data={"goal_id": target_goal["id"], "withdrawn_amount": amount, "wallet_name": w["wallet_name"]},
        message=f"Đã rút {amount:,.0f} VNĐ từ mục tiêu '{target_goal['target_name']}' về '{w['wallet_name']}' thành công!"
    )


# DELETE: delete_saving_goal
async def handle_delete_saving_goal(user_id: int, goal_id: Optional[int] = None, goal_name: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        g = None
        if goal_id:
            g = conn.execute("SELECT id, target_name, current_amount FROM saving_goals WHERE id = ? AND user_id = ?", (goal_id, user_id)).fetchone()
        elif goal_name:
            g = conn.execute("SELECT id, target_name, current_amount FROM saving_goals WHERE user_id = ? AND LOWER(target_name) LIKE ?", (user_id, f"%{goal_name.strip().lower()}%")).fetchone()

        if not g:
            return ToolResult(success=False, error=f"Không tìm thấy mục tiêu tiết kiệm '{goal_name or goal_id}' để xóa.")

        conn.execute("DELETE FROM saving_goals WHERE id = ? AND user_id = ?", (g["id"], user_id))

        # Post-action DB verification
        verify_del = conn.execute("SELECT id FROM saving_goals WHERE id = ? AND user_id = ?", (g["id"], user_id)).fetchone()
        if verify_del:
            return ToolResult(
                success=False,
                error=f"Xác minh cơ sở dữ liệu thất bại: Mục tiêu #{g['id']} vẫn còn tồn tại."
            )

    return ToolResult(
        success=True,
        data={"deleted_goal_id": g["id"], "target_name": g["target_name"]},
        message=f"Đã xóa mục tiêu tiết kiệm '{g['target_name']}'."
    )


# ─────────────────────────────────────────────────────────────
# 8. REPORTS & ANALYTICS CAPABILITIES (THIÊN CƠ THỐNG KÊ)
# ─────────────────────────────────────────────────────────────

# READ: financial_overview / get_financial_overview
async def handle_get_financial_overview(
    user_id: int,
    month_year: Optional[str] = None,
    period: Optional[str] = None,
    **kwargs
) -> ToolResult:
    import main
    start_date, end_date, period_label = _resolve_period_range(period or month_year)
    with main.get_db() as conn:
        main.process_recurring_transactions(conn, user_id)
        summary = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type='INCOME' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN transaction_type='EXPENSE' THEN amount ELSE 0 END), 0) as expense
            FROM transactions
            WHERE user_id = ? AND transaction_date >= ? AND transaction_date <= ?
        """, (user_id, start_date, end_date)).fetchone()

        total_balance = conn.execute(
            "SELECT COALESCE(SUM(balance), 0) as total FROM wallets WHERE user_id = ?",
            (user_id,)
        ).fetchone()["total"]

        wallets_count = conn.execute(
            "SELECT COUNT(*) as count FROM wallets WHERE user_id = ?",
            (user_id,)
        ).fetchone()["count"]

        inc = summary["income"]
        exp = summary["expense"]
        net = inc - exp
        return ToolResult(
            success=True,
            data={
                "month_year": month_year or start_date[:7],
                "period": period_label,
                "start_date": start_date,
                "end_date": end_date,
                "income": inc,
                "expense": exp,
                "net_savings": net,
                "total_balance": total_balance,
                "wallets_count": wallets_count
            },
            message=f"Tổng quan tài chính {period_label}: Thu {inc:,.0f}đ, Chi {exp:,.0f}đ, Tiết kiệm thuần {net:,.0f}đ, Số dư hiện tại {total_balance:,.0f}đ (qua {wallets_count} Túi Càn Khôn)."
        )


# READ: spending_summary
async def handle_spending_summary(user_id: int, period: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    start_date, end_date, period_label = _resolve_period_range(period)
    with main.get_db() as conn:
        main.process_recurring_transactions(conn, user_id)
        agg = conn.execute("""
            SELECT
                COALESCE(SUM(amount), 0) as total_spent,
                COUNT(*) as tx_count,
                COALESCE(MAX(amount), 0) as max_spent
            FROM transactions
            WHERE user_id = ? AND transaction_type = 'EXPENSE'
            AND transaction_date >= ? AND transaction_date <= ?
        """, (user_id, start_date, end_date)).fetchone()

        total_spent = agg["total_spent"]
        tx_count = agg["tx_count"]

        d_start = datetime.date.fromisoformat(start_date)
        d_end = datetime.date.fromisoformat(end_date)
        today = datetime.date.today()
        calc_end = min(d_end, today)
        days_count = max(1, (calc_end - d_start).days + 1)
        daily_avg = total_spent / days_count

        top_txns = conn.execute("""
            SELECT t.id, t.amount, t.transaction_date, t.note, c.category_name, w.wallet_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN wallets w ON t.wallet_id = w.id
            WHERE t.user_id = ? AND t.transaction_type = 'EXPENSE'
            AND t.transaction_date >= ? AND t.transaction_date <= ?
            ORDER BY t.amount DESC
            LIMIT 3
        """, (user_id, start_date, end_date)).fetchall()
        top_list = [dict(r) for r in top_txns]

        msg = f"Trong {period_label}, Ký Chủ đã chi tổng cộng {total_spent:,.0f} VNĐ qua {tx_count} giao dịch (Trung bình khoảng {daily_avg:,.0f} VNĐ/ngày)."
        if top_list:
            biggest = top_list[0]
            cat_str = f" [{biggest['category_name']}]" if biggest['category_name'] else ""
            msg += f" Khoản chi lớn nhất là '{biggest['note']}'{cat_str} với số tiền {biggest['amount']:,.0f} VNĐ."

        return ToolResult(
            success=True,
            data={
                "period": period_label,
                "start_date": start_date,
                "end_date": end_date,
                "total_spent": total_spent,
                "transaction_count": tx_count,
                "daily_average": daily_avg,
                "top_transactions": top_list
            },
            message=msg
        )


# READ: spending_by_category
async def handle_spending_by_category(user_id: int, category_name: Optional[str] = None, period: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    start_date, end_date, period_label = _resolve_period_range(period)
    with main.get_db() as conn:
        main.process_recurring_transactions(conn, user_id)
        if category_name:
            clean_cat = category_name.strip()
            cat_row = conn.execute("""
                SELECT c.id, c.category_name, c.icon,
                       COALESCE(SUM(t.amount), 0) as total_spent,
                       COUNT(t.id) as tx_count
                FROM categories c
                LEFT JOIN transactions t ON c.id = t.category_id
                     AND t.user_id = ? AND t.transaction_type = 'EXPENSE'
                     AND t.transaction_date >= ? AND t.transaction_date <= ?
                WHERE c.user_id = ? AND LOWER(c.category_name) LIKE ?
                GROUP BY c.id
            """, (user_id, start_date, end_date, user_id, f"%{clean_cat.lower()}%")).fetchone()

            if not cat_row or cat_row["total_spent"] == 0:
                direct_txns = conn.execute("""
                    SELECT COALESCE(SUM(amount), 0) as total_spent, COUNT(*) as tx_count
                    FROM transactions
                    WHERE user_id = ? AND transaction_type = 'EXPENSE'
                    AND transaction_date >= ? AND transaction_date <= ?
                    AND LOWER(note) LIKE ?
                """, (user_id, start_date, end_date, f"%{clean_cat.lower()}%")).fetchone()

                spent = direct_txns["total_spent"]
                cnt = direct_txns["tx_count"]
                return ToolResult(
                    success=True,
                    data={"category_name": clean_cat, "total_spent": spent, "count": cnt, "period": period_label},
                    message=f"Trong {period_label}, Ký Chủ đã chi {spent:,.0f} VNĐ cho các khoản liên quan đến '{clean_cat}' ({cnt} giao dịch)."
                )

            return ToolResult(
                success=True,
                data={
                    "category_name": cat_row["category_name"],
                    "total_spent": cat_row["total_spent"],
                    "count": cat_row["tx_count"],
                    "icon": cat_row["icon"],
                    "period": period_label
                },
                message=f"Trong {period_label}, danh mục '{cat_row['category_name']}' {cat_row['icon']} đã tiêu hao {cat_row['total_spent']:,.0f} VNĐ qua {cat_row['tx_count']} lần giao dịch."
            )

        rows = conn.execute("""
            SELECT c.category_name, c.icon,
                   COALESCE(SUM(t.amount), 0) as total_spent,
                   COUNT(t.id) as tx_count
            FROM categories c
            LEFT JOIN transactions t ON c.id = t.category_id
                 AND t.user_id = ? AND t.transaction_type = 'EXPENSE'
                 AND t.transaction_date >= ? AND t.transaction_date <= ?
            WHERE c.user_id = ? AND c.category_type = 'EXPENSE'
            GROUP BY c.id
            HAVING total_spent > 0
            ORDER BY total_spent DESC
        """, (user_id, start_date, end_date, user_id)).fetchall()

        items = [dict(r) for r in rows]
        total_all = sum(it["total_spent"] for it in items)
        for it in items:
            it["percent"] = round(it["total_spent"] / total_all * 100, 1) if total_all > 0 else 0

        top = items[0] if items else None
        top_msg = f" Chi nhiều nhất vào '{top['category_name']}' {top['icon']} chiếm {top['percent']}% ({top['total_spent']:,.0f} VNĐ)." if top else " Chưa phát sinh chi tiêu trong kỳ."
        return ToolResult(
            success=True,
            data={"categories": items, "breakdown": items, "total_spent": total_all, "period": period_label, "top_category": top},
            message=f"Cơ cấu chi tiêu {period_label}:{top_msg}"
        )


# READ: get_trend_report
async def handle_get_trend_report(user_id: int, months: int = 6, **kwargs) -> ToolResult:
    import main
    res = main.get_trend_report(months=min(max(2, int(months)), 12), user={"user_id": user_id})
    return ToolResult(
        success=True,
        data=res,
        message=f"Báo cáo xu hướng tài chính {months} tháng gần nhất: Tổng thu {res.get('total_income', 0):,.0f} VNĐ, Tổng chi {res.get('total_expense', 0):,.0f} VNĐ."
    )


# READ: get_weekly_report
async def handle_get_weekly_report(user_id: int, month_year: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    m_y = month_year or datetime.date.today().strftime("%Y-%m")
    res = main.get_weekly_report(month_year=m_y, user={"user_id": user_id})
    return ToolResult(
        success=True,
        data=res,
        message=f"Báo cáo chi tiêu theo 4 tuần của tháng {m_y}: Tổng chi tháng là {res.get('total_expense', 0):,.0f} VNĐ."
    )


# READ: compare_months
async def handle_compare_months(user_id: int, month1: Optional[str] = None, month2: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    today = datetime.date.today()
    m2 = month2 or today.strftime("%Y-%m")
    if not month1:
        first_this = today.replace(day=1)
        prev = first_this - datetime.timedelta(days=1)
        m1 = prev.strftime("%Y-%m")
    else:
        m1 = month1

    res = main.compare_months(month1=m1, month2=m2, user={"user_id": user_id})
    diff = res.get("expense_diff", 0)
    pct = res.get("expense_pct_change", 0)
    trend_txt = f"tăng {diff:+,.0f} VNĐ ({pct:+.1f}%)" if diff > 0 else f"giảm {abs(diff):,.0f} VNĐ ({pct:.1f}%)"
    return ToolResult(
        success=True,
        data=res,
        message=f"So sánh chi tiêu tháng {m1} và {m2}: Chi tiêu đã {trend_txt}."
    )


# SYSTEM / READ: export_reports
async def handle_export_reports(user_id: int, format: str = "excel", month_year: Optional[str] = None, **kwargs) -> ToolResult:
    m_y = month_year or datetime.date.today().strftime("%Y-%m")
    fmt = format.lower() if format in ("excel", "csv") else "excel"
    return ToolResult(
        success=True,
        data={"format": fmt, "month_year": m_y, "download_url": f"/api/reports/export?format={fmt}&month_year={m_y}"},
        message=f"Ký Chủ có thể tải về sổ sách sao kê định dạng {fmt.upper()} cho tháng {m_y} tại mục Thiên Cơ Thống Kê."
    )


# ─────────────────────────────────────────────────────────────
# 9. OCR & INVOICE CAPABILITIES (LINH NHÃN OCR)
# ─────────────────────────────────────────────────────────────

# READ: get_ocr_logs
async def handle_get_ocr_logs(user_id: int, limit: int = 5, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute(
            "SELECT id, image_path, extracted_json, created_at FROM invoice_ocr_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, min(max(1, int(limit)), 20))
        ).fetchall()
        items = [dict(r) for r in rows]
        return ToolResult(
            success=True,
            data={"ocr_logs": items, "count": len(items)},
            message=f"Tìm thấy {len(items)} hóa đơn đã quét gần đây qua Linh Nhãn OCR."
        )


# ─────────────────────────────────────────────────────────────
# 10. USER & NAVIGATION & SYSTEM CAPABILITIES
# ─────────────────────────────────────────────────────────────

# READ: get_user_profile
async def handle_get_user_profile(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        u = conn.execute("SELECT id, email, full_name, role, is_active, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        if not u:
            return ToolResult(success=False, error="Không tìm thấy thông tin Ký Chủ.")

        stats = conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM wallets WHERE user_id = ?) as wallet_count,
                (SELECT COUNT(*) FROM transactions WHERE user_id = ?) as tx_count,
                (SELECT COUNT(*) FROM saving_goals WHERE user_id = ?) as goal_count
        """, (user_id, user_id, user_id)).fetchone()

        role_label = "Chưởng Môn (Admin)" if u["role"] == "admin" else "Đệ Tử (User)"
        return ToolResult(
            success=True,
            data={"profile": dict(u), "stats": dict(stats)},
            message=f"Đạo hiệu: '{u['full_name']}' | Thân phận: {role_label} | Tiên phủ: {stats['wallet_count']} túi càn khôn, {stats['tx_count']} giao dịch đã ghi chép."
        )


# WRITE: update_user_profile
async def handle_update_user_profile(user_id: int, full_name: str, **kwargs) -> ToolResult:
    import main
    clean_name = (full_name or "").strip()
    if not clean_name:
        return ToolResult(success=False, error="Đạo hiệu không được để trống.")

    with main.get_db() as conn:
        conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (clean_name, user_id))

    return ToolResult(
        success=True,
        data={"user_id": user_id, "full_name": clean_name},
        message=f"Đã đổi đạo hiệu thành '{clean_name}' thành công!"
    )


# SYSTEM: navigate_to
async def handle_navigate_to(user_id: int, target_tab: str, **kwargs) -> ToolResult:
    clean_tab = target_tab.lower().strip()
    tab_map = {
        "dashboard": ("dashboard", "Tổng Quan Tu Tiên"),
        "tổng quan": ("dashboard", "Tổng Quan Tu Tiên"),
        "transactions": ("transactions", "Sổ Giao Dịch"),
        "giao dịch": ("transactions", "Sổ Giao Dịch"),
        "debts": ("debts", "Sổ Nợ & Vay Mượn"),
        "nợ": ("debts", "Sổ Nợ & Vay Mượn"),
        "wallets": ("wallets", "Túi Càn Khôn"),
        "ví": ("wallets", "Túi Càn Khôn"),
        "categories": ("categories", "Danh Mục Thu Chi"),
        "danh mục": ("categories", "Danh Mục Thu Chi"),
        "ocr": ("ocr", "Linh Nhãn OCR"),
        "hóa đơn": ("ocr", "Linh Nhãn OCR"),
        "budgets": ("budgets", "Hạn Mức Tu Luyện"),
        "ngân sách": ("budgets", "Hạn Mức Tu Luyện"),
        "goals": ("goals", "Mục Tiêu Tiết Kiệm"),
        "tiết kiệm": ("goals", "Mục Tiêu Tiết Kiệm"),
        "stats": ("stats", "Thiên Cơ Thống Kê"),
        "thống kê": ("stats", "Thiên Cơ Thống Kê"),
        "báo cáo": ("stats", "Thiên Cơ Thống Kê"),
        "chat": ("chat", "Khí Linh Tiên Trí"),
        "admin": ("admin", "Phân Quyền & Quản Trị"),
    }
    target = tab_map.get(clean_tab, ("dashboard", "Tổng Quan"))
    return ToolResult(
        success=True,
        data={"target_tab": target[0], "tab_name": target[1]},
        message=f"Đã mở giao diện '{target[1]}' cho Ký Chủ."
    )


# READ: get_system_help
async def handle_get_system_help(user_id: int, **kwargs) -> ToolResult:
    features = [
        "Quản lý Túi Càn Khôn (ví tiền mặt, ngân hàng, tiết kiệm, thêm/sửa/xóa)",
        "Ghi nhận thu chi tự động qua ngôn ngữ tự nhiên hoặc sửa/xóa giao dịch",
        "Chuyển tiền liên ví có lịch sử và phòng chống trùng lặp",
        "Tích lũy hoặc rút tiền từ Mục Tiêu Tiết Kiệm",
        "Theo dõi Sổ Nợ (cho vay, đi vay, quyết toán nợ)",
        "Giao dịch định kỳ tự động hóa hàng tuần, hàng tháng",
        "Quét hóa đơn thông minh bằng Linh Nhãn OCR",
        "Báo cáo và phân tích thu chi trực quan, so sánh tháng, xu hướng",
        "Điều hướng hệ thống thông qua đối thoại cùng Khí Linh"
    ]
    return ToolResult(
        success=True,
        data={"features": features},
        message="Càn Khôn Linh Thạch Các hỗ trợ toàn diện các tính năng quản lý tài chính cá nhân."
    )


# ─────────────────────────────────────────────────────────────
# 11. ADMIN CAPABILITIES (QUẢN TRỊ TÔNG MÔN - ROLE: ADMIN)
# ─────────────────────────────────────────────────────────────

# READ: get_admin_stats
async def handle_get_admin_stats(user_id: int, user_role: str = "user", **kwargs) -> ToolResult:
    if user_role != "admin":
        return ToolResult(success=False, error="Chỉ Chưởng Môn (Admin) mới có quyền xem thông số toàn môn.")
    import main
    res = main.get_admin_stats(admin={"user_id": user_id, "role": user_role})
    return ToolResult(
        success=True,
        data=res,
        message=f"Thông số Tông Môn: Tổng {res.get('total_users', 0)} đệ tử ({res.get('active_users', 0)} hoạt động, {res.get('locked_users', 0)} bị phong ấn)."
    )


# READ: list_admin_users
async def handle_list_admin_users(user_id: int, user_role: str = "user", search: Optional[str] = None, role: Optional[str] = None, status: Optional[str] = None, **kwargs) -> ToolResult:
    if user_role != "admin":
        return ToolResult(success=False, error="Chỉ Chưởng Môn (Admin) mới có quyền truy cập danh sách đệ tử.")
    import main
    res = main.get_admin_users(search=search, role=role, status=status, admin={"user_id": user_id, "role": user_role})
    return ToolResult(
        success=True,
        data={"users": res, "count": len(res)},
        message=f"Tìm thấy {len(res)} đệ tử trong Tông Môn."
    )


# WRITE: toggle_user_status
async def handle_toggle_user_status(user_id: int, target_user_id: int, user_role: str = "user", **kwargs) -> ToolResult:
    if user_role != "admin":
        return ToolResult(success=False, error="Chỉ Chưởng Môn (Admin) mới có quyền phong ấn tài khoản.")
    import main
    res = main.toggle_user_active(user_id=target_user_id, admin={"user_id": user_id, "role": user_role})
    action_txt = "Kích hoạt" if res.get("is_active") == 1 else "Phong ấn (Khóa)"
    return ToolResult(
        success=True,
        data=res,
        message=f"Đã {action_txt} đệ tử ID #{target_user_id} thành công!"
    )


# WRITE: change_user_role
async def handle_change_user_role(user_id: int, target_user_id: int, new_role: str, user_role: str = "user", **kwargs) -> ToolResult:
    if user_role != "admin":
        return ToolResult(success=False, error="Chỉ Chưởng Môn (Admin) mới có quyền thay đổi vai trò đệ tử.")
    import main
    body = main.RoleUpdateBody(role=new_role)
    res = main.change_user_role(user_id=target_user_id, body=body, admin={"user_id": user_id, "role": user_role})
    return ToolResult(
        success=True,
        data=res,
        message=f"Đã chuyển vai trò đệ tử ID #{target_user_id} sang '{new_role}' thành công!"
    )


# ─────────────────────────────────────────────────────────────
# BUILD THE FULL CAPABILITY TOOL REGISTRY
# ─────────────────────────────────────────────────────────────

def build_default_tool_registry() -> ToolRegistry:
    reg = ToolRegistry()

    # 1. WALLET DOMAIN
    reg.register(Tool(
        name="get_wallets",
        description="Lấy danh sách các Túi Càn Khôn (ví) và số dư hiện có của Ký Chủ.",
        domain="wallet",
        parameters={
            "type": "object",
            "properties": {
                "wallet_name": {"type": "string", "description": "Tên hoặc từ khóa ví cần xem số dư"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_wallets
    ))
    reg.register(Tool(
        name="wallet_status",
        description="Tra cứu số dư và danh sách các Túi Càn Khôn.",
        domain="wallet",
        parameters={"type": "object", "properties": {"wallet_name": {"type": "string"}}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_wallets
    ))
    reg.register(Tool(
        name="create_wallet",
        description="Tạo một Túi Càn Khôn (ví) mới với số dư ban đầu.",
        domain="wallet",
        parameters={
            "type": "object",
            "properties": {
                "wallet_name": {"type": "string", "description": "Tên Túi Càn Khôn mới (ví dụ: MB Bank, Tiền Mặt, Momo)"},
                "balance": {"type": "number", "description": "Số dư ban đầu (VNĐ, mặc định 0)"},
                "wallet_type": {"type": "string", "enum": ["cash", "bank", "e-wallet", "crypto"], "description": "Loại ví"}
            },
            "required": ["wallet_name"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Tạo Túi Càn Khôn mới**: '{a.get('wallet_name')}' với số dư ban đầu {float(a.get('balance', 0)):,.0f} VNĐ",
        handler=handle_create_wallet
    ))
    reg.register(Tool(
        name="update_wallet",
        description="Cập nhật thông tin hoặc tên của Túi Càn Khôn.",
        domain="wallet",
        parameters={
            "type": "object",
            "properties": {
                "wallet_name": {"type": "string", "description": "Tên ví hiện tại"},
                "new_name": {"type": "string", "description": "Tên mới của ví"},
                "balance": {"type": "number", "description": "Số dư điều chỉnh"},
                "wallet_type": {"type": "string", "description": "Loại ví mới"}
            }
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Cập nhật Túi Càn Khôn**: '{a.get('wallet_name') or a.get('wallet_id')}' thành '{a.get('new_name')}'",
        handler=handle_update_wallet
    ))
    reg.register(Tool(
        name="delete_wallet",
        description="Xóa bỏ một Túi Càn Khôn khỏi hệ thống. (RỦI RO CAO)",
        domain="wallet",
        parameters={
            "type": "object",
            "properties": {
                "wallet_name": {"type": "string", "description": "Tên ví cần xóa"},
                "wallet_id": {"type": "integer", "description": "ID ví cần xóa"}
            }
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.CRITICAL,
        requires_confirmation=True,
        summary_generator=lambda a: f"⚠️ **XÓA Túi Càn Khôn**: '{a.get('wallet_name') or a.get('wallet_id')}'. Hành động này sẽ xóa bỏ toàn bộ giao dịch liên kết!",
        handler=handle_delete_wallet
    ))
    reg.register(Tool(
        name="transfer_money",
        description="Chuyển tiền giữa hai Túi Càn Khôn (ví). (YÊU CẦU XÁC NHẬN)",
        domain="wallet",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền chuyển (VNĐ)"},
                "from_wallet_name": {"type": "string", "description": "Tên ví nguồn"},
                "to_wallet_name": {"type": "string", "description": "Tên ví đích"},
                "from_wallet_id": {"type": "integer", "description": "ID ví nguồn"},
                "to_wallet_id": {"type": "integer", "description": "ID ví đích"},
                "note": {"type": "string", "description": "Ghi chú chuyển tiền"}
            },
            "required": ["amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Chuyển Tiền**: {float(a.get('amount') or 0):,.0f} VNĐ từ '{a.get('from_wallet_name', 'Ví nguồn')}' sang '{a.get('to_wallet_name', 'Ví đích')}'",
        handler=handle_transfer_money
    ))

    # 2. CATEGORY DOMAIN
    reg.register(Tool(
        name="get_categories",
        description="Lấy danh sách các danh mục thu chi của Ký Chủ.",
        domain="category",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_categories
    ))
    reg.register(Tool(
        name="create_category",
        description="Tạo một danh mục thu chi mới.",
        domain="category",
        parameters={
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Tên danh mục"},
                "category_type": {"type": "string", "enum": ["EXPENSE", "INCOME"], "description": "Loại: EXPENSE hoặc INCOME"},
                "icon": {"type": "string", "description": "Icon biểu tượng emoji"}
            },
            "required": ["category_name"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.LOW,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Tạo Danh Mục mới**: '{a.get('category_name')}' ({'Khoản Thu' if a.get('category_type') == 'INCOME' else 'Khoản Chi'}) {a.get('icon') if a.get('icon') and a.get('icon') != '📦' else resolve_category_icon(a.get('category_name'), a.get('category_type'))}",
        handler=handle_create_category
    ))
    reg.register(Tool(
        name="update_category",
        description="Cập nhật tên hoặc biểu tượng của danh mục.",
        domain="category",
        parameters={
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Tên danh mục hiện tại"},
                "new_name": {"type": "string", "description": "Tên mới"},
                "icon": {"type": "string", "description": "Biểu tượng emoji mới"}
            }
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.LOW,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Sửa Danh Mục**: '{a.get('category_name') or a.get('category_id')}' thành '{a.get('new_name')}'",
        handler=handle_update_category
    ))
    reg.register(Tool(
        name="delete_category",
        description="Xóa bỏ một danh mục thu chi.",
        domain="category",
        parameters={
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Tên danh mục cần xóa"}
            },
            "required": ["category_name"]
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"⚠️ **XÓA Danh Mục**: '{a.get('category_name') or a.get('category_id')}'",
        handler=handle_delete_category
    ))

    # 3. TRANSACTION DOMAIN
    reg.register(Tool(
        name="get_recent_transactions",
        description="Xem các giao dịch thu/chi gần đây nhất trong sổ sách.",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Số lượng giao dịch cần xem (mặc định 5)"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_recent_transactions
    ))
    reg.register(Tool(
        name="get_latest_transaction",
        description="Xem giao dịch thu/chi mới nhất hoặc khoản tiền vừa thu/chi gần nhất của Ký Chủ.",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "wallet_name": {"type": "string", "description": "Tên ví nếu muốn lọc theo ví cụ thể"},
                "category_name": {"type": "string", "description": "Tên danh mục nếu muốn lọc theo danh mục cụ thể"},
                "txn_type": {"type": "string", "enum": ["INCOME", "EXPENSE"], "description": "Loại thu hoặc chi"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=lambda user_id, wallet_name=None, category_name=None, txn_type=None, **kw: handle_search_transactions(
            user_id=user_id, wallet_name=wallet_name, category_name=category_name, txn_type=txn_type, limit=1, **kw
        )
    ))
    search_tool = Tool(
        name="transaction_search",
        description="Tìm kiếm và tra soát giao dịch theo từ khóa, danh mục, ví tiền, thời gian hoặc số tiền.",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Từ khóa tìm kiếm"},
                "category_name": {"type": "string", "description": "Tên danh mục"},
                "wallet_name": {"type": "string", "description": "Tên ví tiền"},
                "time_frame": {"type": "string", "description": "today, this_week, this_month, last_month, hoặc YYYY-MM"},
                "min_amount": {"type": "number", "description": "Số tiền tối thiểu"},
                "max_amount": {"type": "number", "description": "Số tiền tối đa"},
                "txn_type": {"type": "string", "enum": ["INCOME", "EXPENSE"], "description": "Loại thu/chi"},
                "limit": {"type": "integer", "description": "Số kết quả tối đa"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_search_transactions
    )
    reg.register(search_tool)
    reg.register(Tool(
        name="search_transactions",
        description="Tìm kiếm hoặc lọc các giao dịch theo từ khóa hoặc loại thu/chi.",
        domain="transaction",
        parameters=search_tool.parameters,
        action_type=search_tool.action_type,
        risk_level=search_tool.risk_level,
        requires_confirmation=search_tool.requires_confirmation,
        handler=handle_search_transactions
    ))
    reg.register(Tool(
        name="create_expense",
        description="Thêm một khoản chi tiêu mới vào ví. (YÊU CẦU XÁC NHẬN)",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền chi tiêu (VNĐ)"},
                "note": {"type": "string", "description": "Nội dung chi tiêu (ví dụ: Ăn sáng, Đổ xăng)"},
                "wallet_name": {"type": "string", "description": "Tên ví chi tiêu (tùy chọn)"},
                "wallet_id": {"type": "integer", "description": "ID ví chi tiêu (tùy chọn)"},
                "category_name": {"type": "string", "description": "Tên danh mục chi"},
                "transaction_date": {"type": "string", "description": "Ngày giao dịch YYYY-MM-DD"}
            },
            "required": ["amount", "note"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Khoản Chi**: {float(a.get('amount', 0)):,.0f} VNĐ — Nội dung: '{a.get('note', 'Chi tiêu')}' (Danh mục: {a.get('category_name', 'Tự động')})",
        handler=handle_create_expense
    ))
    reg.register(Tool(
        name="create_income",
        description="Thêm một khoản thu nhập mới vào ví. (YÊU CẦU XÁC NHẬN)",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền thu nhập (VNĐ)"},
                "note": {"type": "string", "description": "Nội dung thu nhập (ví dụ: Tiền lương, Bán đồ)"},
                "wallet_name": {"type": "string", "description": "Tên ví nhận tiền"},
                "wallet_id": {"type": "integer", "description": "ID ví nhận tiền"},
                "category_name": {"type": "string", "description": "Tên danh mục thu"},
                "transaction_date": {"type": "string", "description": "Ngày giao dịch YYYY-MM-DD"}
            },
            "required": ["amount", "note"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Khoản Thu**: +{float(a.get('amount', 0)):,.0f} VNĐ — Nội dung: '{a.get('note', 'Thu nhập')}'",
        handler=handle_create_income
    ))
    reg.register(Tool(
        name="update_transaction",
        description="Cập nhật hoặc chỉnh sửa một giao dịch đã lưu.",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "transaction_id": {"type": "integer", "description": "ID giao dịch cần sửa"},
                "amount": {"type": "number", "description": "Số tiền mới"},
                "note": {"type": "string", "description": "Ghi chú mới"},
                "transaction_date": {"type": "string", "description": "Ngày giao dịch mới YYYY-MM-DD"}
            },
            "required": ["transaction_id"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: (
            f"👉 **Sửa Giao Dịch ID #{a.get('transaction_id')}**: Cập nhật số tiền thành {float(a.get('amount', 0)):,.0f} VNĐ"
            if a.get('amount')
            else f"👉 **Sửa Giao Dịch ID #{a.get('transaction_id')}**: Cập nhật thông tin giao dịch"
        ),
        handler=handle_update_transaction
    ))
    reg.register(Tool(
        name="delete_transaction",
        description="Xóa bỏ một giao dịch và hoàn lại số dư ví.",
        domain="transaction",
        parameters={
            "type": "object",
            "properties": {
                "transaction_id": {"type": "integer", "description": "ID giao dịch cần xóa"}
            },
            "required": ["transaction_id"]
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: (
            f"⚠️ **XÓA Giao Dịch ID #{a.get('transaction_id')}**: Xóa '{a.get('note') or 'khoản giao dịch'}' ({float(a.get('amount', 0)):,.0f} VNĐ) và hoàn lại số dư ví."
            if a.get('amount')
            else f"⚠️ **XÓA Giao Dịch ID #{a.get('transaction_id')}**: Xóa bỏ bản ghi và hoàn lại số dư ví."
        ),
        handler=handle_delete_transaction
    ))

    # 4. BUDGET DOMAIN
    budget_tool = Tool(
        name="budget_status",
        description="Xem tiến độ và cảnh báo các hạn mức ngân sách chi tiêu trong tháng.",
        domain="budget",
        parameters={
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Tên danh mục cần kiểm tra hạn mức"},
                "month_year": {"type": "string", "description": "Tháng năm YYYY-MM"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_budget_status
    )
    reg.register(budget_tool)
    reg.register(Tool(
        name="get_budget_status",
        description="Xem tiến độ và cảnh báo các hạn mức chi tiêu trong tháng.",
        domain="budget",
        parameters=budget_tool.parameters,
        action_type=budget_tool.action_type,
        risk_level=budget_tool.risk_level,
        requires_confirmation=budget_tool.requires_confirmation,
        handler=handle_get_budget_status
    ))
    reg.register(Tool(
        name="create_budget",
        description="Thiết lập hoặc cập nhật hạn mức ngân sách chi tiêu cho danh mục. (YÊU CẦU XÁC NHẬN)",
        domain="budget",
        parameters={
            "type": "object",
            "properties": {
                "limit_amount": {"type": "number", "description": "Hạn mức ngân sách tối đa (VNĐ)"},
                "category_name": {"type": "string", "description": "Tên danh mục chi tiêu"},
                "category_id": {"type": "integer", "description": "ID danh mục"},
                "month_year": {"type": "string", "description": "Tháng áp dụng YYYY-MM"}
            },
            "required": ["limit_amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Đặt Ngân Sách**: {float(a.get('limit_amount', 0)):,.0f} VNĐ cho danh mục '{a.get('category_name', 'Ăn Uống')}' ({a.get('month_year', 'tháng này')})",
        handler=handle_create_budget
    ))
    reg.register(Tool(
        name="update_budget",
        description="Chỉnh sửa hạn mức ngân sách đã đặt.",
        domain="budget",
        parameters={
            "type": "object",
            "properties": {
                "limit_amount": {"type": "number", "description": "Hạn mức mới"},
                "category_name": {"type": "string", "description": "Tên danh mục"},
                "budget_id": {"type": "integer", "description": "ID ngân sách"},
                "month_year": {"type": "string", "description": "Tháng áp dụng"}
            },
            "required": ["limit_amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Sửa Ngân Sách**: Hạn mức mới {float(a.get('limit_amount', 0)):,.0f} VNĐ cho '{a.get('category_name') or a.get('budget_id')}'",
        handler=handle_update_budget
    ))
    reg.register(Tool(
        name="delete_budget",
        description="Xóa bỏ một hạn mức ngân sách.",
        domain="budget",
        parameters={
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Tên danh mục"},
                "budget_id": {"type": "integer", "description": "ID ngân sách"}
            }
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"⚠️ **XÓA Ngân Sách**: Hủy hạn mức chi tiêu của danh mục '{a.get('category_name') or a.get('budget_id')}'",
        handler=handle_delete_budget
    ))

    # 5. RECURRING DOMAIN
    reg.register(Tool(
        name="get_recurring_transactions",
        description="Xem danh sách các giao dịch định kỳ đang hoạt động.",
        domain="recurring",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_recurring_transactions
    ))
    reg.register(Tool(
        name="create_recurring_transaction",
        description="Tạo một giao dịch định kỳ tự động (hàng tuần hoặc hàng tháng).",
        domain="recurring",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền định kỳ (VNĐ)"},
                "transaction_type": {"type": "string", "enum": ["EXPENSE", "INCOME"], "description": "Loại thu/chi"},
                "frequency": {"type": "string", "enum": ["weekly", "monthly"], "description": "Tần suất"},
                "category_name": {"type": "string", "description": "Tên danh mục"},
                "wallet_name": {"type": "string", "description": "Tên ví"},
                "note": {"type": "string", "description": "Nội dung giao dịch định kỳ"},
                "next_run_date": {"type": "string", "description": "Ngày chạy đầu tiên YYYY-MM-DD"}
            },
            "required": ["amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Tạo Giao Dịch Định Kỳ**: {float(a.get('amount', 0)):,.0f} VNĐ ({'Hàng tuần' if a.get('frequency') == 'weekly' else 'Hàng tháng'}) — '{a.get('note', 'Giao dịch định kỳ')}'",
        handler=handle_create_recurring_transaction
    ))
    reg.register(Tool(
        name="update_recurring_transaction",
        description="Chỉnh sửa hoặc bật/tắt giao dịch định kỳ.",
        domain="recurring",
        parameters={
            "type": "object",
            "properties": {
                "rec_id": {"type": "integer", "description": "ID giao dịch định kỳ"},
                "amount": {"type": "number", "description": "Số tiền mới"},
                "frequency": {"type": "string", "description": "weekly hoặc monthly"},
                "is_active": {"type": "integer", "description": "1 là kích hoạt, 0 là tạm dừng"}
            },
            "required": ["rec_id"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Sửa Giao Dịch Định Kỳ ID #{a.get('rec_id')}**",
        handler=handle_update_recurring_transaction
    ))
    reg.register(Tool(
        name="delete_recurring_transaction",
        description="Xóa bỏ một giao dịch định kỳ.",
        domain="recurring",
        parameters={
            "type": "object",
            "properties": {
                "rec_id": {"type": "integer", "description": "ID giao dịch định kỳ cần xóa"}
            },
            "required": ["rec_id"]
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"⚠️ **XÓA Giao Dịch Định Kỳ ID #{a.get('rec_id')}**",
        handler=handle_delete_recurring_transaction
    ))

    # 6. DEBT DOMAIN
    debt_tool = Tool(
        name="debt_status",
        description="Xem sổ nợ: tổng nợ phải trả, nợ người khác nợ mình và các khoản chưa quyết toán.",
        domain="debt",
        parameters={
            "type": "object",
            "properties": {
                "debt_type": {"type": "string", "enum": ["BORROW", "LEND"], "description": "BORROW hoặc LEND"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_debts
    )
    reg.register(debt_tool)
    reg.register(Tool(
        name="get_debts",
        description="Xem sổ nợ: các khoản nợ phải trả và nợ người khác nợ mình.",
        domain="debt",
        parameters=debt_tool.parameters,
        action_type=debt_tool.action_type,
        risk_level=debt_tool.risk_level,
        requires_confirmation=debt_tool.requires_confirmation,
        handler=handle_get_debts
    ))
    reg.register(Tool(
        name="debt_list",
        description="Xem danh sách các khoản nợ phải trả và nợ người khác nợ mình.",
        domain="debt",
        parameters=debt_tool.parameters,
        action_type=debt_tool.action_type,
        risk_level=debt_tool.risk_level,
        requires_confirmation=debt_tool.requires_confirmation,
        handler=handle_get_debts
    ))
    reg.register(Tool(
        name="create_debt",
        description="Ghi nhận khoản vay mượn mới (cho vay hoặc đi vay).",
        domain="debt",
        parameters={
            "type": "object",
            "properties": {
                "debt_type": {"type": "string", "enum": ["BORROW", "LEND"], "description": "BORROW (đi vay) hoặc LEND (cho vay)"},
                "person_name": {"type": "string", "description": "Tên người vay hoặc cho vay"},
                "amount": {"type": "number", "description": "Số tiền (VNĐ)"},
                "due_date": {"type": "string", "description": "Hạn trả YYYY-MM-DD"},
                "note": {"type": "string", "description": "Ghi chú"}
            },
            "required": ["debt_type", "person_name", "amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Ghi Nợ**: {'Cho ' + str(a.get('person_name')) + ' vay' if a.get('debt_type') == 'LEND' else 'Vay của ' + str(a.get('person_name'))} số tiền {float(a.get('amount', 0)):,.0f} VNĐ",
        handler=handle_create_debt
    ))
    reg.register(Tool(
        name="update_debt",
        description="Cập nhật thông tin khoản nợ.",
        domain="debt",
        parameters={
            "type": "object",
            "properties": {
                "person_name": {"type": "string", "description": "Tên người vay/nợ"},
                "amount": {"type": "number", "description": "Số tiền mới"},
                "due_date": {"type": "string", "description": "Hạn trả mới"}
            }
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Cập nhật Khoản Nợ**: Đối tác '{a.get('person_name') or a.get('debt_id')}'",
        handler=handle_update_debt
    ))
    reg.register(Tool(
        name="settle_debt",
        description="Đánh dấu đã hoàn tất / thanh toán xong một khoản nợ.",
        domain="debt",
        parameters={
            "type": "object",
            "properties": {
                "person_name": {"type": "string", "description": "Tên người vay/nợ"},
                "debt_id": {"type": "integer", "description": "ID khoản nợ"}
            }
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Quyết Toán Khoản Nợ**: Đánh dấu đã tất toán xong khoản nợ của '{a.get('person_name') or a.get('debt_id')}'",
        handler=handle_settle_debt
    ))
    reg.register(Tool(
        name="delete_debt",
        description="Xóa bỏ một khoản nợ khỏi sổ sách.",
        domain="debt",
        parameters={
            "type": "object",
            "properties": {
                "person_name": {"type": "string", "description": "Tên người nợ"},
                "debt_id": {"type": "integer", "description": "ID khoản nợ"}
            }
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"⚠️ **XÓA Khoản Nợ**: Xóa khoản nợ của '{a.get('person_name') or a.get('debt_id')}'",
        handler=handle_delete_debt
    ))

    # 7. SAVING GOAL DOMAIN
    saving_tool = Tool(
        name="saving_goal_status",
        description="Tra cứu tiến độ tích lũy các mục tiêu tiết kiệm.",
        domain="saving_goal",
        parameters={
            "type": "object",
            "properties": {
                "goal_name": {"type": "string", "description": "Tên mục tiêu tiết kiệm cần kiểm tra"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_saving_goals
    )
    reg.register(saving_tool)
    reg.register(Tool(
        name="get_saving_goals",
        description="Lấy danh sách các mục tiêu tiết kiệm và tiến độ tích lũy.",
        domain="saving_goal",
        parameters=saving_tool.parameters,
        action_type=saving_tool.action_type,
        risk_level=saving_tool.risk_level,
        requires_confirmation=saving_tool.requires_confirmation,
        handler=handle_get_saving_goals
    ))
    reg.register(Tool(
        name="create_saving_goal",
        description="Tạo một mục tiêu tiết kiệm mới.",
        domain="saving_goal",
        parameters={
            "type": "object",
            "properties": {
                "target_name": {"type": "string", "description": "Tên mục tiêu (ví dụ: Mua Laptop, Du Lịch)"},
                "target_amount": {"type": "number", "description": "Số tiền mục tiêu (VNĐ)"},
                "current_amount": {"type": "number", "description": "Số tiền đã có sẵn (mặc định 0)"},
                "target_date": {"type": "string", "description": "Hạn hoàn thành YYYY-MM-DD"},
                "icon": {"type": "string", "description": "Icon biểu tượng"}
            },
            "required": ["target_name", "target_amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Tạo Mục Tiêu Tiết Kiệm**: '{a.get('target_name')}' — Đích đến: {float(a.get('target_amount', 0)):,.0f} VNĐ",
        handler=handle_create_saving_goal
    ))
    reg.register(Tool(
        name="update_saving_goal",
        description="Chỉnh sửa mục tiêu tiết kiệm.",
        domain="saving_goal",
        parameters={
            "type": "object",
            "properties": {
                "target_name": {"type": "string", "description": "Tên mục tiêu"},
                "target_amount": {"type": "number", "description": "Hạn mức mới"},
                "target_date": {"type": "string", "description": "Hạn mới"}
            }
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Sửa Mục Tiêu Tiết Kiệm**: '{a.get('target_name') or a.get('goal_id')}'",
        handler=handle_update_saving_goal
    ))
    reg.register(Tool(
        name="saving_goal_deposit",
        description="Nạp tiền vào một mục tiêu tiết kiệm. (YÊU CẦU XÁC NHẬN)",
        domain="saving_goal",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền nạp (VNĐ)"},
                "goal_name": {"type": "string", "description": "Tên mục tiêu tiết kiệm"},
                "goal_id": {"type": "integer", "description": "ID mục tiêu tiết kiệm"},
                "wallet_name": {"type": "string", "description": "Tên ví nguồn trích tiền"},
                "wallet_id": {"type": "integer", "description": "ID ví nguồn"}
            },
            "required": ["amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Nạp Tiết Kiệm**: {float(a.get('amount', 0)):,.0f} VNĐ vào mục tiêu '{a.get('goal_name', 'Mục tiêu')}'",
        handler=handle_saving_goal_deposit
    ))
    reg.register(Tool(
        name="saving_goal_withdraw",
        description="Rút tiền từ mục tiêu tiết kiệm trở lại ví tiền. (YÊU CẦU XÁC NHẬN)",
        domain="saving_goal",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền rút (VNĐ)"},
                "goal_name": {"type": "string", "description": "Tên mục tiêu tiết kiệm"},
                "goal_id": {"type": "integer", "description": "ID mục tiêu"},
                "wallet_name": {"type": "string", "description": "Tên ví nhận tiền"}
            },
            "required": ["amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Rút Tiền Tiết Kiệm**: Rút {float(a.get('amount', 0)):,.0f} VNĐ từ mục tiêu '{a.get('goal_name', 'Mục tiêu')}' về ví",
        handler=handle_saving_goal_withdraw
    ))
    reg.register(Tool(
        name="delete_saving_goal",
        description="Xóa bỏ một mục tiêu tiết kiệm.",
        domain="saving_goal",
        parameters={
            "type": "object",
            "properties": {
                "goal_name": {"type": "string", "description": "Tên mục tiêu cần xóa"}
            },
            "required": ["goal_name"]
        },
        action_type=ToolActionType.DELETE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        summary_generator=lambda a: f"⚠️ **XÓA Mục Tiêu Tiết Kiệm**: '{a.get('goal_name') or a.get('goal_id')}'",
        handler=handle_delete_saving_goal
    ))

    # 8. REPORTS & ANALYTICS DOMAIN
    fin_overview_tool = Tool(
        name="financial_overview",
        description="Xem báo cáo tổng quan tài chính (tổng thu, tổng chi, tiết kiệm thuần, số dư) theo chu kỳ.",
        domain="reports",
        parameters={
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "Khoảng thời gian: today, this_week, this_month, last_month, hoặc YYYY-MM"},
                "month_year": {"type": "string", "description": "Tháng năm YYYY-MM"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_financial_overview
    )
    reg.register(fin_overview_tool)
    reg.register(Tool(
        name="get_financial_overview",
        description="Xem báo cáo tổng quan tài chính tháng này.",
        domain="reports",
        parameters=fin_overview_tool.parameters,
        action_type=fin_overview_tool.action_type,
        risk_level=fin_overview_tool.risk_level,
        requires_confirmation=fin_overview_tool.requires_confirmation,
        handler=handle_get_financial_overview
    ))
    reg.register(Tool(
        name="spending_summary",
        description="Tổng hợp chi tiêu thực tế theo ngày, tuần, tháng.",
        domain="reports",
        parameters={"type": "object", "properties": {"period": {"type": "string"}}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_spending_summary
    ))
    reg.register(Tool(
        name="spending_by_category",
        description="Phân tích cơ cấu chi tiêu theo danh mục hoặc một mục cụ thể.",
        domain="reports",
        parameters={
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Tên danh mục cần xem"},
                "period": {"type": "string", "description": "Thời gian"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_spending_by_category
    ))
    reg.register(Tool(
        name="get_trend_report",
        description="Báo cáo xu hướng tài chính qua nhiều tháng liên tiếp.",
        domain="reports",
        parameters={"type": "object", "properties": {"months": {"type": "integer", "description": "Số tháng phân tích (2-12)"}}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_trend_report
    ))
    reg.register(Tool(
        name="get_weekly_report",
        description="Báo cáo chi tiết chi tiêu theo 4 tuần trong một tháng.",
        domain="reports",
        parameters={"type": "object", "properties": {"month_year": {"type": "string", "description": "Tháng YYYY-MM"}}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_weekly_report
    ))
    reg.register(Tool(
        name="compare_months",
        description="So sánh biến động thu chi giữa hai tháng cụ thể.",
        domain="reports",
        parameters={
            "type": "object",
            "properties": {
                "month1": {"type": "string", "description": "Tháng thứ nhất YYYY-MM"},
                "month2": {"type": "string", "description": "Tháng thứ hai YYYY-MM"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_compare_months
    ))
    reg.register(Tool(
        name="export_reports",
        description="Xuất sao kê và báo cáo tài chính định dạng Excel hoặc CSV.",
        domain="reports",
        parameters={
            "type": "object",
            "properties": {
                "format": {"type": "string", "enum": ["excel", "csv"], "description": "Định dạng tải về"},
                "month_year": {"type": "string", "description": "Tháng xuất báo cáo"}
            }
        },
        action_type=ToolActionType.SYSTEM,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_export_reports
    ))

    # 9. OCR DOMAIN
    reg.register(Tool(
        name="get_ocr_logs",
        description="Xem lịch sử các hóa đơn đã được quét qua Linh Nhãn OCR.",
        domain="ocr",
        parameters={"type": "object", "properties": {"limit": {"type": "integer"}}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_ocr_logs
    ))

    # 10. USER PROFILE & NAVIGATION DOMAIN
    reg.register(Tool(
        name="get_user_profile",
        description="Xem thông tin đạo hiệu, vai trò và thống kê tiên phủ của bản thân.",
        domain="user",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_user_profile
    ))
    reg.register(Tool(
        name="update_user_profile",
        description="Cập nhật đạo hiệu hoặc họ tên người dùng.",
        domain="user",
        parameters={
            "type": "object",
            "properties": {
                "full_name": {"type": "string", "description": "Đạo hiệu mới"}
            },
            "required": ["full_name"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.LOW,
        requires_confirmation=True,
        summary_generator=lambda a: f"👉 **Cập nhật Đạo Hiệu**: Đổi tên thành '{a.get('full_name')}'",
        handler=handle_update_user_profile
    ))
    reg.register(Tool(
        name="navigate_to",
        description="Điều hướng hoặc mở một trang/tab chức năng cụ thể trên website.",
        domain="navigation",
        parameters={
            "type": "object",
            "properties": {
                "target_tab": {"type": "string", "description": "Tab đích: dashboard, transactions, debts, wallets, categories, ocr, budgets, goals, stats, chat, admin"}
            },
            "required": ["target_tab"]
        },
        action_type=ToolActionType.SYSTEM,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_navigate_to
    ))
    reg.register(Tool(
        name="get_system_help",
        description="Xem hướng dẫn tính năng và các pháp bảo trong Càn Khôn Linh Thạch Các.",
        domain="system",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_system_help
    ))

    # 11. ADMIN DOMAIN (Chưởng Môn - Role protected)
    reg.register(Tool(
        name="get_admin_stats",
        description="Xem thông số toàn môn: tổng đệ tử, tài khoản hoạt động, tài khoản bị khóa. (DÀNH RIÊNG ADMIN)",
        domain="admin",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_role="admin",
        handler=handle_get_admin_stats
    ))
    reg.register(Tool(
        name="list_admin_users",
        description="Tra cứu danh sách tất cả đệ tử trong Tông Môn. (DÀNH RIÊNG ADMIN)",
        domain="admin",
        parameters={
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Từ khóa tìm kiếm tên hoặc email"},
                "role": {"type": "string", "description": "Lọc theo vai trò (admin hoặc user)"},
                "status": {"type": "string", "description": "Lọc theo trạng thái (active hoặc locked)"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_role="admin",
        handler=handle_list_admin_users
    ))
    reg.register(Tool(
        name="toggle_user_status",
        description="Khóa hoặc mở khóa tài khoản đệ tử. (DÀNH RIÊNG ADMIN, YÊU CẦU XÁC NHẬN)",
        domain="admin",
        parameters={
            "type": "object",
            "properties": {
                "target_user_id": {"type": "integer", "description": "ID đệ tử cần khóa hoặc mở khóa"}
            },
            "required": ["target_user_id"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        required_role="admin",
        summary_generator=lambda a: f"⚠️ **QUẢN TRỊ - Khóa/Mở Khóa Tài Khoản**: User ID #{a.get('target_user_id')}",
        handler=handle_toggle_user_status
    ))
    reg.register(Tool(
        name="change_user_role",
        description="Thăng cấp hoặc giáng chức vai trò đệ tử (admin / user). (DÀNH RIÊNG ADMIN, YÊU CẦU XÁC NHẬN)",
        domain="admin",
        parameters={
            "type": "object",
            "properties": {
                "target_user_id": {"type": "integer", "description": "ID đệ tử"},
                "new_role": {"type": "string", "enum": ["admin", "user"], "description": "Vai trò mới"}
            },
            "required": ["target_user_id", "new_role"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.CRITICAL,
        requires_confirmation=True,
        required_role="admin",
        summary_generator=lambda a: f"⚠️ **QUẢN TRỊ - Thay Đổi Phân Quyền**: Gán vai trò '{a.get('new_role')}' cho User ID #{a.get('target_user_id')}",
        handler=handle_change_user_role
    ))

    return reg
