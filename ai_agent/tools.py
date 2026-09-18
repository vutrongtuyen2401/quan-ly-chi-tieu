"""
Tool Registry & Financial Tools
Định nghĩa hệ thống công cụ (Tools) có kiểu dữ liệu chặt chẽ cho AI Agent.
Phân định rõ ràng READ và WRITE, mức độ rủi ro, và yêu cầu xác nhận.
Kết nối trực tiếp vào logic dịch vụ backend hiện hữu, tuyệt đối không cho AI query DB tùy tiện.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import datetime
import json
import re


def _match_wallet_name(query: str, target: str) -> bool:
    """Khớp tên ví thông minh, không cắt nhầm từ con như 'vi' trong 'vietcombank'"""
    q = query.lower().strip()
    t = target.lower().strip()
    if q == t or q in t or t in q:
        return True
    clean_q = re.sub(r'\b(ví|vi)\b', '', q).strip()
    clean_t = re.sub(r'\b(ví|vi)\b', '', t).strip()
    if clean_q and (clean_q in t or clean_q in clean_t or clean_t in clean_q):
        return True
    return False


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ToolActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"


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
    """Định nghĩa một công cụ có cấu trúc"""
    name: str
    description: str
    parameters: Dict[str, Any]
    action_type: ToolActionType
    risk_level: RiskLevel
    requires_confirmation: bool
    handler: Callable

    def to_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "action_type": self.action_type.value,
            "risk_level": self.risk_level.value,
            "requires_confirmation": self.requires_confirmation
        }


class ToolRegistry:
    """Sổ đăng ký và quản lý công cụ an toàn của AI Agent"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [t.to_schema() for t in self._tools.values()]

    async def execute(self, tool_name: str, user_id: int, **kwargs) -> ToolResult:
        """Thực thi công cụ với ủy quyền và kiểm thực quyền sở hữu"""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Công cụ '{tool_name}' không tồn tại trong sổ đăng ký.",
                message="Khí Linh không tìm thấy pháp bảo tương ứng để thực thi."
            )
        try:
            # Gọi handler với user_id được tiêm vào bắt buộc
            return await tool.handler(user_id=user_id, **kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Thực thi công cụ '{tool_name}' thất bại: {str(e)}"
            )


# ──────────────────────────────────────────────
# HANDLERS FOR P0 & P1 FINANCIAL TOOLS
# ──────────────────────────────────────────────

# 1. READ: get_wallets
async def handle_get_wallets(user_id: int, wallet_name: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute(
            "SELECT id, wallet_name, wallet_type, balance FROM wallets WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
        ).fetchall()
        wallets = [dict(r) for r in rows]
        total_balance = sum(w["balance"] for w in wallets)

        if wallet_name:
            matched = [w for w in wallets if _match_wallet_name(wallet_name, w["wallet_name"])]
            if matched:
                target = matched[0]
                return ToolResult(
                    success=True,
                    data={"wallets": [target], "total_balance": total_balance, "target_wallet": target},
                    message=f"Số dư trong '{target['wallet_name']}' của đạo hữu hiện còn {target['balance']:,.0f} VNĐ."
                )

        return ToolResult(
            success=True,
            data={"wallets": wallets, "total_balance": total_balance},
            message=f"Đạo hữu hiện có {len(wallets)} Túi Càn Khôn, tổng số dư là {total_balance:,.0f} VNĐ."
        )


# 2. READ: get_recent_transactions
async def handle_get_recent_transactions(user_id: int, limit: int = 5, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        limit = min(max(1, int(limit)), 20)
        rows = conn.execute("""
            SELECT t.id, t.amount, t.transaction_type, t.transaction_date, t.note,
                   w.wallet_name, c.category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN wallets w ON t.wallet_id = w.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.transaction_date DESC, t.id DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        txns = [dict(r) for r in rows]
        return ToolResult(
            success=True,
            data={"transactions": txns, "count": len(txns)},
            message=f"Tìm thấy {len(txns)} giao dịch gần nhất của đạo hữu."
        )


# 3. READ: get_financial_overview
async def handle_get_financial_overview(user_id: int, month_year: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    if not month_year:
        month_year = datetime.date.today().strftime("%Y-%m")
    with main.get_db() as conn:
        main.process_recurring_transactions(conn, user_id)
        summary = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type='INCOME' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN transaction_type='EXPENSE' THEN amount ELSE 0 END), 0) as expense
            FROM transactions WHERE user_id = ? AND strftime('%Y-%m', transaction_date) = ?
        """, (user_id, month_year)).fetchone()

        total_balance = conn.execute(
            "SELECT COALESCE(SUM(balance), 0) as total FROM wallets WHERE user_id = ?",
            (user_id,)
        ).fetchone()["total"]

        inc = summary["income"]
        exp = summary["expense"]
        net = inc - exp
        return ToolResult(
            success=True,
            data={
                "month_year": month_year,
                "income": inc,
                "expense": exp,
                "net_savings": net,
                "total_balance": total_balance
            },
            message=f"Tổng quan tháng {month_year}: Thu {inc:,.0f}đ, Chi {exp:,.0f}đ, Tiết kiệm thuần {net:,.0f}đ, Số dư hiện tại {total_balance:,.0f}đ."
        )


# 4. READ: get_budget_status
async def handle_get_budget_status(user_id: int, **kwargs) -> ToolResult:
    import main
    month_year = datetime.date.today().strftime("%Y-%m")
    with main.get_db() as conn:
        budgets = conn.execute("""
            SELECT b.*, c.category_name, c.icon,
                   COALESCE((SELECT SUM(t.amount) FROM transactions t
                             WHERE t.category_id = b.category_id
                             AND t.user_id = b.user_id
                             AND t.transaction_type = 'EXPENSE'
                             AND strftime('%Y-%m', t.transaction_date) = b.month_year), 0) as spent
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ? AND b.month_year = ?
        """, (user_id, month_year)).fetchall()

        items = []
        for b in budgets:
            b = dict(b)
            pct = (b["spent"] / b["limit_amount"] * 100) if b["limit_amount"] > 0 else 0
            items.append({
                "category_name": b["category_name"],
                "icon": b["icon"],
                "limit_amount": b["limit_amount"],
                "spent": b["spent"],
                "percent": round(pct, 1),
                "is_exceeded": pct >= 100
            })
        return ToolResult(
            success=True,
            data={"month_year": month_year, "budgets": items},
            message=f"Đạo hữu đã thiết lập {len(items)} hạn mức chi tiêu trong tháng {month_year}."
        )


# 5. WRITE: create_expense
async def handle_create_expense(user_id: int, amount: float, note: str, wallet_id: Optional[int] = None, category_name: Optional[str] = None, transaction_date: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền chi tiêu phải lớn hơn 0.")

    today_str = transaction_date or datetime.date.today().strftime("%Y-%m-%d")
    with main.get_db() as conn:
        # Chọn ví: nếu không truyền wallet_id, chọn ví đầu tiên của user
        if wallet_id:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
            if not w:
                return ToolResult(success=False, error="Túi Càn Khôn được chọn không tồn tại hoặc không thuộc quyền sở hữu của bạn.")
        else:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
            if not w:
                return ToolResult(success=False, error="Bạn chưa tạo Túi Càn Khôn nào. Hãy tạo ví trước khi ghi nhận chi tiêu.")

        # Chọn hoặc tạo danh mục
        cat_name = category_name.strip() if category_name and category_name.strip() else "Chi Tiêu Chung"
        cat_row = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_type = 'EXPENSE' AND LOWER(category_name) = LOWER(?)", (user_id, cat_name)).fetchone()
        if cat_row:
            cat_id = cat_row["id"]
        else:
            cat_id = main.get_or_create_system_category(conn, user_id, cat_name, "EXPENSE", "💸")

        clean_note = (note or "Chi tiêu qua Khí Linh").strip()

        # Thực thi thêm giao dịch và cập nhật ví
        conn.execute("""
            INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
            VALUES (?, ?, ?, ?, 'EXPENSE', ?, ?)
        """, (user_id, w["id"], cat_id, amount, today_str, clean_note))
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


# 6. WRITE: create_income
async def handle_create_income(user_id: int, amount: float, note: str, wallet_id: Optional[int] = None, category_name: Optional[str] = None, transaction_date: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền thu nhập phải lớn hơn 0.")

    today_str = transaction_date or datetime.date.today().strftime("%Y-%m-%d")
    with main.get_db() as conn:
        if wallet_id:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE id = ? AND user_id = ?", (wallet_id, user_id)).fetchone()
            if not w:
                return ToolResult(success=False, error="Túi Càn Khôn không tồn tại hoặc không thuộc quyền sở hữu của bạn.")
        else:
            w = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ? ORDER BY id ASC LIMIT 1", (user_id,)).fetchone()
            if not w:
                return ToolResult(success=False, error="Bạn chưa tạo Túi Càn Khôn nào.")

        cat_name = category_name.strip() if category_name and category_name.strip() else "Thu Nhập Khác"
        cat_row = conn.execute("SELECT id FROM categories WHERE user_id = ? AND category_type = 'INCOME' AND LOWER(category_name) = LOWER(?)", (user_id, cat_name)).fetchone()
        if cat_row:
            cat_id = cat_row["id"]
        else:
            cat_id = main.get_or_create_system_category(conn, user_id, cat_name, "INCOME", "💰")

        clean_note = (note or "Thu nhập qua Khí Linh").strip()

        conn.execute("""
            INSERT INTO transactions (user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note)
            VALUES (?, ?, ?, ?, 'INCOME', ?, ?)
        """, (user_id, w["id"], cat_id, amount, today_str, clean_note))
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


# 7. WRITE: transfer_money
async def handle_transfer_money(user_id: int, amount: float, from_wallet_id: Optional[int] = None, to_wallet_id: Optional[int] = None, from_wallet_name: Optional[str] = None, to_wallet_name: Optional[str] = None, note: Optional[str] = None, **kwargs) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số lượng Linh Thạch chuyển phải lớn hơn 0.")

    with main.get_db() as conn:
        all_wallets = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
        if len(all_wallets) < 2:
            return ToolResult(success=False, error="Đạo hữu cần có ít nhất 2 Túi Càn Khôn để thực hiện chuyển tiền.")

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
                error=f"Số dư {w_from['wallet_name']} không đủ (Còn {w_from['balance']:,.0f} VNĐ). Đạo hữu có muốn thử lại với số tiền tối đa {w_from['balance']:,.0f} VNĐ không?"
            )

        # Gọi hàm logic nghiệp vụ hiện hữu
        body = main.TransferBody(
            from_wallet_id=w_from["id"],
            to_wallet_id=w_to["id"],
            amount=amount,
            note=note or "Chuyển tiền qua Khí Linh AI"
        )
        res = main.transfer_between_wallets(body, user={"user_id": user_id})
        return ToolResult(
            success=True,
            data=res,
            message=f"Đã chuyển thành công {amount:,.0f} VNĐ từ '{w_from['wallet_name']}' sang '{w_to['wallet_name']}'!"
        )


# 8. WRITE: saving_goal_deposit
async def handle_saving_goal_deposit(user_id: int, amount: float, goal_id: Optional[int] = None, goal_name: Optional[str] = None, wallet_id: Optional[int] = None, **kwargs) -> ToolResult:
    import main
    if amount <= 0:
        return ToolResult(success=False, error="Số tiền tích lũy phải lớn hơn 0.")

    with main.get_db() as conn:
        goals = conn.execute("SELECT id, target_name, target_amount, current_amount, is_completed FROM saving_goals WHERE user_id = ?", (user_id,)).fetchall()
        if not goals:
            return ToolResult(success=False, error="Đạo hữu chưa có mục tiêu tiết kiệm nào. Hãy tạo mục tiêu trước.")

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
            # Chọn mục tiêu chưa hoàn thành đầu tiên
            target_goal = next((g for g in goals if not g["is_completed"]), goals[0])

        if not target_goal:
            return ToolResult(success=False, error="Không tìm thấy mục tiêu tiết kiệm phù hợp.")

        # Chọn ví nguồn
        wallets = conn.execute("SELECT id, wallet_name, balance FROM wallets WHERE user_id = ?", (user_id,)).fetchall()
        if not wallets:
            return ToolResult(success=False, error="Không tìm thấy ví tiền.")

        w = next((w for w in wallets if w["id"] == wallet_id), wallets[0]) if wallet_id else wallets[0]
        if w["balance"] < amount:
            return ToolResult(
                success=False,
                error=f"Số dư trong {w['wallet_name']} không đủ (Còn {w['balance']:,.0f} VNĐ). Đạo hữu có muốn thử lại với số tiền tối đa {w['balance']:,.0f} VNĐ không?"
            )

        body = main.SavingGoalDepositBody(
            amount=amount,
            wallet_id=w["id"]
        )
        res = main.deposit_saving_goal(target_goal["id"], body, user={"user_id": user_id})
        return ToolResult(
            success=True,
            data=res,
            message=f"Đã tích lũy thêm {amount:,.0f} VNĐ từ '{w['wallet_name']}' vào mục tiêu '{target_goal['target_name']}'!"
        )


# ──────────────────────────────────────────────
# P1 TOOLS: CATEGORIES, GOALS, DEBTS, SEARCH
# ──────────────────────────────────────────────

# 9. READ: get_categories
async def handle_get_categories(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute("SELECT id, category_name, category_type, icon FROM categories WHERE user_id = ?", (user_id,)).fetchall()
        cats = [dict(r) for r in rows]
        return ToolResult(
            success=True,
            data={"categories": cats, "count": len(cats)},
            message=f"Đạo hữu có {len(cats)} danh mục thu chi."
        )


# 10. READ: get_saving_goals
async def handle_get_saving_goals(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        rows = conn.execute("SELECT * FROM saving_goals WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
        goals = [dict(r) for r in rows]
        return ToolResult(
            success=True,
            data={"saving_goals": goals, "count": len(goals)},
            message=f"Đạo hữu có {len(goals)} mục tiêu tiết kiệm."
        )


# 11. READ: get_debts
async def handle_get_debts(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        debts = conn.execute("SELECT * FROM debts WHERE user_id = ? ORDER BY is_settled ASC, id DESC", (user_id,)).fetchall()
        debt_list = [dict(d) for d in debts]
        i_owe = sum(d["amount"] for d in debt_list if d["debt_type"] == "BORROW" and not d["is_settled"])
        they_owe = sum(d["amount"] for d in debt_list if d["debt_type"] == "LEND" and not d["is_settled"])
        return ToolResult(
            success=True,
            data={
                "debts": debt_list,
                "total_borrowing": i_owe,
                "total_lending": they_owe
            },
            message=f"Sổ nợ: Đạo hữu đang nợ {i_owe:,.0f} VNĐ và được người khác nợ {they_owe:,.0f} VNĐ."
        )


# 12. READ: get_recurring_transactions
async def handle_get_recurring_transactions(user_id: int, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        recs = conn.execute("SELECT * FROM recurring_transactions WHERE user_id = ? AND is_active = 1", (user_id,)).fetchall()
        items = [dict(r) for r in recs]
        return ToolResult(
            success=True,
            data={"recurring": items, "count": len(items)},
            message=f"Đạo hữu có {len(items)} giao dịch định kỳ đang hoạt động."
        )


# 13. READ: search_transactions
async def handle_search_transactions(user_id: int, query: Optional[str] = None, txn_type: Optional[str] = None, limit: int = 10, **kwargs) -> ToolResult:
    import main
    with main.get_db() as conn:
        where_clauses = ["t.user_id = ?"]
        params = [user_id]
        if query:
            where_clauses.append("(t.note LIKE ? OR c.category_name LIKE ? OR w.wallet_name LIKE ?)")
            q_like = f"%{query.strip()}%"
            params.extend([q_like, q_like, q_like])
        if txn_type in ("INCOME", "EXPENSE"):
            where_clauses.append("t.transaction_type = ?")
            params.append(txn_type)

        limit_val = min(max(1, int(limit)), 50)
        sql = f"""
            SELECT t.*, w.wallet_name, c.category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN wallets w ON t.wallet_id = w.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE {' AND '.join(where_clauses)}
            ORDER BY t.transaction_date DESC, t.id DESC
            LIMIT {limit_val}
        """
        rows = conn.execute(sql, params).fetchall()
        txns = [dict(r) for r in rows]
        return ToolResult(
            success=True,
            data={"results": txns, "count": len(txns)},
            message=f"Tìm thấy {len(txns)} giao dịch phù hợp với yêu cầu."
        )


# 14. READ: get_system_help
async def handle_get_system_help(user_id: int, **kwargs) -> ToolResult:
    features = [
        "Quản lý Túi Càn Khôn (ví tiền mặt, ngân hàng, tiết kiệm)",
        "Ghi nhận thu chi tự động qua ngôn ngữ tự nhiên",
        "Chuyển tiền liên ví có lịch sử và chống trùng lặp",
        "Tích lũy vào Mục Tiêu Tiết Kiệm",
        "Theo dõi Sổ Nợ (cho vay và đi vay)",
        "Giao dịch định kỳ tự động hóa",
        "Quét hóa đơn bằng Linh Nhãn OCR",
        "Báo cáo và phân tích thu chi trực quan"
    ]
    return ToolResult(
        success=True,
        data={"features": features},
        message="Càn Khôn Linh Thạch Các hỗ trợ toàn diện các tính năng quản lý tài chính cá nhân."
    )


# ──────────────────────────────────────────────
# BUILD THE DEFAULT TOOL REGISTRY
# ──────────────────────────────────────────────
def build_default_tool_registry() -> ToolRegistry:
    reg = ToolRegistry()

    # P0 Tools
    reg.register(Tool(
        name="get_wallets",
        description="Lấy danh sách các Túi Càn Khôn (ví) và số dư hiện có của đạo hữu.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_wallets
    ))

    reg.register(Tool(
        name="get_recent_transactions",
        description="Xem các giao dịch thu/chi gần đây nhất trong sổ sách.",
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
        name="get_financial_overview",
        description="Xem báo cáo tổng quan tài chính tháng này: Tổng thu, tổng chi, tiết kiệm thuần và số dư.",
        parameters={
            "type": "object",
            "properties": {
                "month_year": {"type": "string", "description": "Tháng năm cần xem dạng YYYY-MM (để trống lấy tháng hiện tại)"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_financial_overview
    ))

    reg.register(Tool(
        name="get_budget_status",
        description="Xem tiến độ và cảnh báo các hạn mức chi tiêu trong tháng.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_budget_status
    ))

    reg.register(Tool(
        name="create_expense",
        description="Thêm một khoản chi tiêu mới vào ví. (YÊU CẦU XÁC NHẬN TỪ NGƯỜI DÙNG)",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền chi tiêu (VNĐ)"},
                "note": {"type": "string", "description": "Nội dung chi tiêu (ví dụ: Ăn sáng, Đổ xăng)"},
                "wallet_id": {"type": "integer", "description": "ID ví chi tiêu (tùy chọn)"},
                "category_name": {"type": "string", "description": "Tên danh mục chi (ví dụ: Ăn Uống, Đi Lại)"},
                "transaction_date": {"type": "string", "description": "Ngày giao dịch YYYY-MM-DD (mặc định hôm nay)"}
            },
            "required": ["amount", "note"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        handler=handle_create_expense
    ))

    reg.register(Tool(
        name="create_income",
        description="Thêm một khoản thu nhập mới vào ví. (YÊU CẦU XÁC NHẬN TỪ NGƯỜI DÙNG)",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền thu nhập (VNĐ)"},
                "note": {"type": "string", "description": "Nội dung thu nhập (ví dụ: Tiền lương, Bán đồ)"},
                "wallet_id": {"type": "integer", "description": "ID ví nhận tiền (tùy chọn)"},
                "category_name": {"type": "string", "description": "Tên danh mục thu (ví dụ: Lương, Thưởng)"},
                "transaction_date": {"type": "string", "description": "Ngày giao dịch YYYY-MM-DD"}
            },
            "required": ["amount", "note"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        handler=handle_create_income
    ))

    reg.register(Tool(
        name="transfer_money",
        description="Chuyển tiền giữa hai Túi Càn Khôn (ví). (YÊU CẦU XÁC NHẬN TỪ NGƯỜI DÙNG)",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền chuyển (VNĐ)"},
                "from_wallet_name": {"type": "string", "description": "Tên hoặc từ khóa của ví nguồn"},
                "to_wallet_name": {"type": "string", "description": "Tên hoặc từ khóa của ví đích"},
                "from_wallet_id": {"type": "integer", "description": "ID ví nguồn (tùy chọn)"},
                "to_wallet_id": {"type": "integer", "description": "ID ví đích (tùy chọn)"},
                "note": {"type": "string", "description": "Ghi chú chuyển tiền"}
            },
            "required": ["amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        handler=handle_transfer_money
    ))

    reg.register(Tool(
        name="saving_goal_deposit",
        description="Nạp tiền vào một mục tiêu tiết kiệm. (YÊU CẦU XÁC NHẬN TỪ NGƯỜI DÙNG)",
        parameters={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền nạp (VNĐ)"},
                "goal_name": {"type": "string", "description": "Tên hoặc từ khóa của mục tiêu tiết kiệm"},
                "goal_id": {"type": "integer", "description": "ID mục tiêu tiết kiệm (tùy chọn)"},
                "wallet_id": {"type": "integer", "description": "ID ví nguồn trích tiền (tùy chọn)"}
            },
            "required": ["amount"]
        },
        action_type=ToolActionType.WRITE,
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        handler=handle_saving_goal_deposit
    ))

    # P1 Tools
    reg.register(Tool(
        name="get_categories",
        description="Lấy danh sách các danh mục thu chi của đạo hữu.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_categories
    ))

    reg.register(Tool(
        name="get_saving_goals",
        description="Lấy danh sách các mục tiêu tiết kiệm và tiến độ tích lũy.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_saving_goals
    ))

    reg.register(Tool(
        name="get_debts",
        description="Xem sổ nợ: các khoản nợ phải trả và nợ người khác nợ mình.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_debts
    ))

    reg.register(Tool(
        name="get_recurring_transactions",
        description="Xem danh sách các giao dịch định kỳ đang hoạt động.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_recurring_transactions
    ))

    reg.register(Tool(
        name="search_transactions",
        description="Tìm kiếm hoặc lọc các giao dịch theo từ khóa hoặc loại thu/chi.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Từ khóa tìm kiếm (tên ghi chú, danh mục, ví)"},
                "txn_type": {"type": "string", "enum": ["INCOME", "EXPENSE"], "description": "Loại giao dịch"},
                "limit": {"type": "integer", "description": "Số kết quả tối đa"}
            }
        },
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_search_transactions
    ))

    reg.register(Tool(
        name="get_system_help",
        description="Xem hướng dẫn tính năng và các pháp bảo trong Càn Khôn Linh Thạch Các.",
        parameters={"type": "object", "properties": {}},
        action_type=ToolActionType.READ,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        handler=handle_get_system_help
    ))

    return reg
