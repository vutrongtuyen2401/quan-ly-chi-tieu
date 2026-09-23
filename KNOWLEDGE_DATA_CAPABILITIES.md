# DATA QUERY CAPABILITY MATRIX — KHÍ LINH LỚN (KNOWLEDGE AGENT)

Dự án: **Càn Khôn Linh Thạch Các**  
Chế độ: **Knowledge Mode (Read-Only System Intelligence)**  
Kiến trúc: **Deterministic Intent & Entity Resolution → ToolRegistry → Authorized Service Query → Verified Response**  
Bảo mật: **Chỉ đọc dữ liệu của người dùng hiện tại (`user_id = current_user.id`), tuyệt đối chặn quyền ghi/biến động dữ liệu (No Mutations)**

---

## 1. Bảng Ma Trận Năng Lực Truy Vấn Dữ Liệu (Read Capabilities Matrix)

| Domain | Question / Câu hỏi mẫu | Intent | Tool | Permission | Verified |
|---|---|---|---|---|---|
| **Transactions** | Giao dịch mới nhất của ta là gì? | `GET_LATEST_TRANSACTION` | `get_latest_transaction` | READ | PASS |
| **Transactions** | Ta vừa tiêu khoản gì gần nhất? | `GET_LATEST_TRANSACTION` | `get_latest_transaction` | READ | PASS |
| **Transactions** | Lịch sử 5 giao dịch gần đây | `GET_RECENT_TRANSACTIONS` | `get_recent_transactions` | READ | PASS |
| **Transactions** | Tìm giao dịch ăn sáng tuần này | `SEARCH_TRANSACTIONS` | `search_transactions` / `transaction_search` | READ | PASS |
| **Transactions** | Giao dịch cuối cùng của ví Túi Momo | `GET_LATEST_TRANSACTION` | `get_latest_transaction` | READ | PASS |
| **Transactions** | Giao dịch có số tiền lớn nhất | `GET_LARGEST_TRANSACTION` | `search_transactions` (`sort_by="amount"`, `limit=1`) | READ | PASS |
| **Transactions** | Tháng này ta chi bao nhiêu? | `GET_SPENDING_SUMMARY` | `spending_summary` | READ | PASS |
| **Transactions** | Tháng này ta thu bao nhiêu? | `GET_INCOME_SUMMARY` | `financial_overview` | READ | PASS |
| **Wallets** | Ta đang có tổng cộng bao nhiêu tiền? | `GET_TOTAL_BALANCE` | `get_wallets` | READ | PASS |
| **Wallets** | Ví nào của ta nhiều tiền nhất? | `GET_HIGHEST_WALLET` | `get_wallets` | READ | PASS |
| **Wallets** | Ví nào của ta ít tiền nhất? | `GET_LOWEST_WALLET` | `get_wallets` | READ | PASS |
| **Wallets** | Túi Momo của ta còn bao nhiêu? | `GET_WALLET_BALANCE` | `get_wallets` (`wallet_name="Túi Momo"`) | READ | PASS |
| **Wallets** | Phân bổ tiền giữa các ví ra sao? | `GET_WALLET_DISTRIBUTION` | `get_wallets` | READ | PASS |
| **Categories** | Danh sách các danh mục thu chi | `GET_CATEGORIES` | `get_categories` | READ | PASS |
| **Categories** | Ta có những danh mục thu nào? | `GET_INCOME_CATEGORIES` | `get_categories` | READ | PASS |
| **Categories** | Ta có những danh mục chi nào? | `GET_EXPENSE_CATEGORIES` | `get_categories` | READ | PASS |
| **Categories** | Ăn uống tháng này hết bao nhiêu? | `GET_CATEGORY_SPENDING` | `spending_by_category` | READ | PASS |
| **Categories** | Danh mục nào ta chi nhiều nhất tháng này? | `GET_TOP_CATEGORY_SPENDING` | `spending_by_category` | READ | PASS |
| **Budgets** | Tình hình hạn mức ngân sách tháng này | `GET_BUDGET_STATUS` | `budget_status` / `get_budget_status` | READ | PASS |
| **Budgets** | Hạn mức ăn uống còn bao nhiêu? | `GET_CATEGORY_BUDGET` | `budget_status` (`category_name="Ăn Uống"`) | READ | PASS |
| **Budgets** | Có danh mục nào vượt ngân sách không? | `GET_EXCEEDED_BUDGETS` | `budget_status` | READ | PASS |
| **Debts** | Sổ nợ hiện tại của ta thế nào? | `GET_DEBT_SUMMARY` | `get_debts` / `debt_status` | READ | PASS |
| **Debts** | Ta còn nợ bao nhiêu? (khoản đi vay) | `GET_BORROW_DEBTS` | `get_debts` (`debt_type="BORROW"`) | READ | PASS |
| **Debts** | Ai đang nợ ta? (khoản cho vay) | `GET_LEND_DEBTS` | `get_debts` (`debt_type="LEND"`) | READ | PASS |
| **Debts** | Có khoản nợ nào sắp đến hạn không? | `GET_UPCOMING_DEBTS` | `debt_list` | READ | PASS |
| **Saving Goals** | Các mục tiêu tiết kiệm của ta | `GET_SAVING_GOALS` | `get_saving_goals` | READ | PASS |
| **Saving Goals** | Mục tiêu mua xe còn thiếu bao nhiêu? | `GET_GOAL_STATUS` | `get_saving_goals` (`goal_name="mua xe"`) | READ | PASS |
| **Saving Goals** | Mục tiêu nào gần hoàn thành nhất? | `GET_CLOSEST_GOAL` | `get_saving_goals` | READ | PASS |
| **Recurring** | Các giao dịch định kỳ của ta | `GET_RECURRING_TRANSACTIONS` | `get_recurring_transactions` | READ | PASS |
| **Analytics** | Tình hình tài chính tổng quan tháng này | `GET_FINANCIAL_OVERVIEW` | `financial_overview` | READ | PASS |
| **Analytics** | So sánh tháng này với tháng trước | `COMPARE_MONTHS` | `compare_months` | READ | PASS |
| **Analytics** | Xu hướng chi tiêu 6 tháng qua | `GET_TREND_REPORT` | `get_trend_report` | READ | PASS |
| **Analytics** | Báo cáo chi tiêu theo tuần | `GET_WEEKLY_REPORT` | `get_weekly_report` | READ | PASS |
| **Profile** | Thông tin hồ sơ / đạo hiệu của ta | `GET_USER_PROFILE` | `get_user_profile` | READ | PASS |

---

## 2. Quy Tắc Phân Luồng Câu Hỏi (Query Routing Architecture)

```
                     ┌─────────────────────────────┐
                     │     User Message In         │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │ Phân loại loại câu hỏi      │
                     └──────────────┬──────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
[CURRENT_USER_DATA]        [SYSTEM_KNOWLEDGE]              [MIXED_QUERY]
Câu hỏi dữ liệu cá nhân    Khái niệm, quy trình tu luyện   Hỏi tính năng + Dữ liệu cá nhân
       │                            │                            │
       ▼                            ▼                            ▼
ToolRegistry (READ ONLY)     Bát Quái RAG Vector           RAG + ToolRegistry (READ)
       │                            │                            │
       ▼                            ▼                            ▼
Database (user_id scoped)    Tài liệu tiên môn             Kết hợp 2 nguồn chuẩn xác
       │                            │                            │
       ▼                            ▼                            ▼
Verified Structured Result   Câu trả lời tài liệu          Câu trả lời súc tích
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │   Format tự nhiên Tiếng Việt│
                     │  Xưng hô: Đạo hiệu / Ký Chủ │
                     │  Font: Tabular Numbers      │
                     └─────────────────────────────┘
```

---

## 3. Negative Routing & Security Enforcement

1. **Negative Routing (RAG vs DATA):**
   - `"giao dịch mới nhất"` → `CURRENT_USER_DATA` → `get_latest_transaction` (Không dùng RAG).
   - `"giao dịch là gì?"` → `SYSTEM_KNOWLEDGE` → `knowledge_rag` (RAG giải thích khái niệm).
   - `"cách hạn mức hoạt động?"` → `SYSTEM_KNOWLEDGE` → `knowledge_rag`.
   - `"hạn mức ăn uống của ta còn bao nhiêu?"` → `CURRENT_USER_DATA` → `budget_status`.
   - `"mục tiêu tiết kiệm là gì?"` → `SYSTEM_KNOWLEDGE` → `knowledge_rag`.
   - `"mục tiêu mua xe của ta tới đâu rồi?"` → `CURRENT_USER_DATA` → `get_saving_goals`.

2. **Quyền Hạn Khí Linh Lớn (Knowledge Mode):**
   - Chỉ cho phép `OperationType.READ` (hoặc `ToolActionType.READ`).
   - Mọi thao tác ghi (`WRITE`, `DELETE`, `MUTATION`) bị chặn ở 2 tầng:
     1. Tầng `AgentCore._plan_action` & `process_request`: Phát hiện mutation intent và trả lời lịch sự yêu cầu chuyển sang Khí Linh Nhỏ (Action Mode).
     2. Tầng `ToolRegistry.execute`: Kiểm tra bằng code cứng `if mode == AgentMode.KNOWLEDGE and tool.operation_type != OperationType.READ: return ToolResult(success=False, error="PERMISSION_DENIED")`.
   - Bảo mật tài khoản: Mọi câu truy vấn SQL đều ràng buộc chặt chẽ `WHERE user_id = ?`, không rò rỉ dữ liệu giữa các người dùng.
