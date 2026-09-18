# ROADMAP.md

# Càn Khôn Linh Thạch Các --- Development Roadmap

> Roadmap được xây dựng từ audit source hiện tại. Ngày khởi tạo:
> 2026-09-17 Phiên bản: 1.0

------------------------------------------------------------------------

# 0. Nguyên tắc

Mục tiêu không phải là thêm thật nhiều chức năng càng nhanh càng tốt.

Mục tiêu là biến hệ thống hiện tại thành một nền tảng quản lý tài chính
có:

-   dữ liệu đáng tin cậy;
-   kiến trúc dễ mở rộng;
-   AI có context tài chính đầy đủ;
-   AI không tự bịa số liệu;
-   UI nhất quán;
-   khả năng kiểm thử và bảo trì tốt.

Ưu tiên:

`Data Integrity → Security → Architecture → AI Foundation → AI Intelligence → UX → Production`

------------------------------------------------------------------------

# PHASE 0 --- STABILIZATION

**Mục tiêu:** ổn định nền tảng hiện tại trước khi thêm tính năng AI lớn.

## 0.1 Resource ownership

Audit toàn bộ endpoint nhận các ID tài nguyên từ client.

Đảm bảo:

``` text
wallet.user_id == current_user.id
category.user_id == current_user.id
transaction.user_id == current_user.id
budget.user_id == current_user.id
...
```

### Acceptance criteria

-   User A không thể đọc/sửa/xóa resource của User B chỉ bằng cách đổi
    ID.
-   Có test cho các trường hợp ID hợp lệ nhưng không thuộc user.
-   API trả lỗi phù hợp, không rò rỉ dữ liệu.

------------------------------------------------------------------------

## 0.2 JWT/current-user state

Kiểm tra cơ chế:

-   account active/inactive;
-   role;
-   token expiration;
-   thay đổi quyền sau khi token đã cấp.

### Acceptance criteria

-   User bị deactivate không tiếp tục sử dụng API bằng token cũ trong
    trạng thái không hợp lệ.
-   Thay đổi role không tạo quyền sai do dữ liệu cũ trong token.
-   Không phá login hiện tại.

------------------------------------------------------------------------

## 0.3 OCR failure handling

Loại bỏ fallback tạo dữ liệu tài chính giả khi OCR thất bại.

### Acceptance criteria

``` text
OCR success → return extracted data

OCR failure → explicit error

No fabricated transaction data.
```

------------------------------------------------------------------------

## 0.4 Backend cleanup

Audit `main.py`:

-   duplicate functions;
-   duplicate routes;
-   dead code;
-   inconsistent error responses;
-   repeated database logic.

### Acceptance criteria

Không còn duplicate route/definition không có chủ đích.

------------------------------------------------------------------------

## 0.5 Test/build baseline

Thiết lập baseline:

``` bash
pip install -r requirements.txt
python test_suite.py

cd frontend
npm install
npm run build
```

Ghi lại:

-   pass/fail;
-   test count;
-   known environment problems.

------------------------------------------------------------------------

# PHASE 1 --- ARCHITECTURE CLEANUP

**Mục tiêu:** giảm rủi ro do `main.py` và `App.vue` quá lớn.

Không rewrite toàn bộ.

## 1.1 Backend modularization

Định hướng:

``` text
backend/
├── main.py
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── wallets.py
│   ├── transactions.py
│   ├── budgets.py
│   ├── reports.py
│   ├── debts.py
│   ├── saving_goals.py
│   └── ai.py
│
├── services/
│   ├── financial_service.py
│   ├── ai_service.py
│   ├── ocr_service.py
│   └── auth_service.py
│
├── repositories/
├── schemas/
└── db/
```

Chỉ thực hiện từng module khi có feature chạm vào module đó.

------------------------------------------------------------------------

## 1.2 Frontend modularization

Định hướng:

``` text
frontend/src/
├── views/
├── components/
│   ├── dashboard/
│   ├── transactions/
│   ├── wallets/
│   ├── budgets/
│   ├── ai/
│   └── common/
│
├── services/
├── composables/
└── App.vue
```

Ưu tiên tách những khu vực lớn hoặc thay đổi thường xuyên.

------------------------------------------------------------------------

# PHASE 2 --- FINANCIAL DATA FOUNDATION

**Mục tiêu:** tạo một lớp tài chính chuẩn để AI và UI cùng sử dụng.

## 2.1 Financial service

Backend nên có các hàm chuẩn hóa:

``` text
get_total_income()
get_total_expense()
get_net_savings()
get_wallet_balance()
get_category_spending()
get_budget_usage()
get_debt_summary()
get_saving_goal_progress()
get_recurring_obligations()
```

Các phép tính quan trọng phải thực hiện ở backend.

------------------------------------------------------------------------

## 2.2 Financial context schema

Thiết kế object chuẩn:

``` json
{
  "period": {},
  "income": {},
  "expenses": {},
  "net_savings": {},
  "wallets": [],
  "budgets": [],
  "debts": [],
  "saving_goals": [],
  "recurring_transactions": [],
  "spending_by_category": [],
  "large_transactions": []
}
```

AI không truy cập database trực tiếp.

------------------------------------------------------------------------

# PHASE 3 --- AI FOUNDATION

**Mục tiêu:** biến AI từ các prompt rời rạc thành một hệ thống AI có
kiến trúc.

## 3.1 AI Orchestrator

Luồng:

``` text
Question
  ↓
Intent detection
  ↓
Required context
  ↓
Financial context builder
  ↓
Prompt builder
  ↓
Gemini
  ↓
Response validator
  ↓
UI
```

------------------------------------------------------------------------

## 3.2 Intent types

Ban đầu có thể chuẩn hóa:

``` text
GENERAL_CHAT
SPENDING_ANALYSIS
BUDGET_ANALYSIS
SAVING_PLAN
GOAL_ANALYSIS
DEBT_ANALYSIS
AFFORDABILITY
MONTHLY_REVIEW
TRANSACTION_EXPLANATION
OCR
```

Không cần làm tất cả cùng lúc.

------------------------------------------------------------------------

## 3.3 Structured AI response

Ưu tiên JSON/schema thay vì text tự do khi UI cần dữ liệu.

Ví dụ:

``` json
{
  "type": "spending_analysis",
  "summary": "...",
  "observations": [],
  "recommendations": [],
  "metrics": []
}
```

Backend validate trước khi trả frontend.

------------------------------------------------------------------------

# PHASE 4 --- AI FINANCIAL INTELLIGENCE

## 4.1 Monthly Financial Review

AI tạo báo cáo:

``` text
Tổng quan
Điểm nổi bật
Danh mục tăng/giảm
Khoản chi đáng chú ý
Ngân sách
Tiết kiệm
Gợi ý hành động
```

------------------------------------------------------------------------

## 4.2 Spending Analysis

Ví dụ:

> "Tháng này tôi tiêu tiền vào đâu nhiều nhất?"

Backend tính:

-   tổng chi;
-   nhóm danh mục;
-   tỷ trọng;
-   thay đổi so với tháng trước.

AI diễn giải.

------------------------------------------------------------------------

## 4.3 Budget Coach

AI phân tích:

``` text
budget
actual
remaining
days_remaining
```

và giải thích nguy cơ vượt ngân sách.

------------------------------------------------------------------------

## 4.4 Saving Planner

Input:

``` text
target
current_saved
deadline
income
fixed_expenses
variable_expenses
```

Backend tính khả năng tiết kiệm theo các kịch bản.

AI diễn giải kế hoạch.

------------------------------------------------------------------------

## 4.5 Affordability Assistant

Ví dụ:

> "Tôi có thể mua laptop 25 triệu không?"

Không trả lời chỉ dựa vào số dư.

Context nên gồm:

``` text
current balance
monthly income
monthly expenses
debts
recurring expenses
saving goals
budget
target purchase
```

AI phải nêu rõ các dữ kiện được dùng và giả định nếu có.

------------------------------------------------------------------------

## 4.6 Anomaly Detection

Tìm:

-   giao dịch lớn bất thường;
-   chi tiêu tăng mạnh;
-   danh mục tăng bất thường;
-   giao dịch lặp đáng chú ý.

Phần phát hiện số liệu nên ưu tiên deterministic/statistical logic; AI
dùng để giải thích.

------------------------------------------------------------------------

# PHASE 5 --- UX / DASHBOARD

Sau khi foundation ổn định:

-   Dashboard cá nhân hóa.
-   AI insight cards.
-   Spending trends.
-   Budget health.
-   Saving progress.
-   Financial calendar.
-   Mobile responsive.
-   Empty states.
-   Loading/error states.

Không để AI làm UI rối hoặc thay thế các số liệu gốc.

------------------------------------------------------------------------

# PHASE 6 --- PRODUCTION HARDENING

-   Secret management.
-   CORS production configuration.
-   Rate limiting toàn diện.
-   Password reset production flow.
-   Database backup strategy.
-   Migration strategy.
-   Logging.
-   Error monitoring.
-   API documentation.
-   Automated tests.
-   Frontend production build.
-   Deployment documentation.

------------------------------------------------------------------------

# TASK PRIORITY QUEUE

Thứ tự dự kiến:

``` text
[ P0 ] Ownership validation
[ P0 ] JWT active/role validation
[ P0 ] OCR failure handling

[ P1 ] Duplicate route/function cleanup
[ P1 ] Baseline test/build
[ P1 ] Financial service
[ P1 ] AI context builder

[ P2 ] AI orchestrator
[ P2 ] Structured AI response
[ P2 ] Monthly review
[ P2 ] Spending analysis
[ P2 ] Budget coach

[ P3 ] Saving planner
[ P3 ] Affordability assistant
[ P3 ] Anomaly detection
[ P3 ] Prediction/forecasting

[ P4 ] UX refinement
[ P4 ] Production hardening
```

------------------------------------------------------------------------

# Definition of Done

Một task chỉ được coi là hoàn thành khi:

## Code

-   Đúng requirement.
-   Không tạo duplicate implementation.
-   Không phá chức năng cũ.
-   Không làm lộ secret.

## Data

-   Có ownership validation nếu liên quan user resource.
-   Migration không phá dữ liệu cũ nếu có database change.
-   Financial calculations được thực hiện ở backend.

## AI

-   Context được xác định rõ.
-   Không yêu cầu LLM tự phát minh dữ liệu.
-   Structured output nếu frontend cần parse.
-   Có xử lý AI/API failure.

## Verification

-   Backend tests liên quan pass.
-   Frontend build pass.
-   UI flow đã được kiểm tra.
-   Browser Console không có lỗi/warning mới liên quan.
-   Báo cáo test phải ghi rõ những gì đã kiểm tra.

------------------------------------------------------------------------

# Prompt Development Protocol

Mỗi feature mới sẽ được phát triển theo:

``` text
Requirement
    ↓
Inspect source
    ↓
Specification
    ↓
Technical plan
    ↓
Task breakdown
    ↓
Implementation prompt
    ↓
Implementation
    ↓
Review
    ↓
Verification
```

ChatGPT phải dựa trên source hiện tại trước khi đưa ra tên file,
function, route hoặc schema cụ thể.
