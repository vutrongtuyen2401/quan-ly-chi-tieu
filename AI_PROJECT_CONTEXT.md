# AI_PROJECT_CONTEXT.md

# Càn Khôn Linh Thạch Các --- AI Project Context

> Tài liệu ngữ cảnh kỹ thuật dùng chung cho ChatGPT, coding agents và
> các phiên làm việc phát triển dự án. Cập nhật: 2026-09-17 Phiên bản
> context: 1.0

------------------------------------------------------------------------

## 1. Project Identity

**Tên dự án:** Càn Khôn Linh Thạch Các\
**Mục tiêu:** Hệ thống quản lý chi tiêu cá nhân tích hợp AI, giao diện
Xianxia/Tu Tiên.

### Mục tiêu chức năng

-   Quản lý thu nhập và chi tiêu.
-   Quản lý nhiều ví/tài khoản.
-   Quản lý danh mục.
-   Quản lý ngân sách.
-   Quản lý giao dịch định kỳ.
-   Quản lý công nợ.
-   Quản lý mục tiêu tiết kiệm.
-   Báo cáo và thống kê.
-   OCR hóa đơn.
-   Trợ lý tài chính AI.
-   Mẹo tiết kiệm do AI hỗ trợ.
-   Quản lý tài khoản và admin.

------------------------------------------------------------------------

## 2. Technology Stack

### Backend

-   Python 3.10+
-   FastAPI
-   Uvicorn
-   SQLite
-   PyJWT
-   bcrypt
-   python-dotenv
-   Google Gemini API
-   openpyxl

### Frontend

-   Vue 3
-   Vite
-   Axios
-   Chart.js
-   vue-chartjs
-   @vuepic/vue-datepicker
-   Vanilla CSS

### Development Method

Project đã tích hợp GitHub Spec-Kit / Spec-Driven Development.

Quy trình chuẩn:

`Specification → Technical Plan → Task Breakdown → Implementation → Verification`

------------------------------------------------------------------------

## 3. Repository Structure

Các thành phần quan trọng:

``` text
/
├── main.py
├── test_suite.py
├── requirements.txt
├── app.db
├── app.db.bak
├── app.db.before_reset.bak
├── README.md
├── AGENTS.md
├── .env.example
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       └── main.js
│
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── workflows/
│
├── .agents/
│   ├── rules/
│   └── skills/
│
└── scratch/
```

------------------------------------------------------------------------

## 4. Current Architecture

``` text
Vue 3 / Vite
      │
      │ Axios
      ▼
FastAPI / main.py
      │
      ├── Authentication
      ├── User/Profile
      ├── Wallets
      ├── Categories
      ├── Transactions
      ├── Budgets
      ├── Recurring Transactions
      ├── Debts
      ├── Saving Goals
      ├── Reports
      ├── Admin
      │
      └── AI
           ├── Gemini OCR
           ├── AI Chat
           ├── Budget analysis
           └── Saving tips
      │
      ▼
SQLite / app.db
```

### Architectural observation

Backend logic is heavily concentrated in `main.py`.

Frontend logic is heavily concentrated in `frontend/src/App.vue`.

This is functional but creates high change-risk and maintainability
cost.

**Rule:** Do not perform a large-scale rewrite unless explicitly
planned. Prefer incremental extraction around the feature being changed.

------------------------------------------------------------------------

## 5. Frontend Context

Current primary frontend files:

-   `frontend/src/App.vue`
-   `frontend/src/main.js`
-   `frontend/src/components/ChartComponents.vue`

`App.vue` is a very large monolithic component containing multiple
pages/features, state, API calls, forms, modals and styles.

Known feature areas represented in the frontend include:

-   Login
-   Register
-   Forgot/reset password
-   Dashboard
-   Transactions
-   Debts
-   Wallets
-   Categories
-   OCR
-   Budgets
-   Saving Goals
-   Statistics
-   AI Chat
-   Admin
-   Profile/account management

### Frontend development rules

-   Every state/property referenced by the template must be declared and
    initialized in the same change.
-   Avoid adding substantial new functionality directly to `App.vue`
    when an independent Vue component is appropriate.
-   After changes, verify all major existing pages, not only the changed
    page.
-   Check browser Console for Vue warnings and JavaScript errors.
-   Do not assume an unrelated Console warning is harmless.

------------------------------------------------------------------------

## 6. Backend Context

The backend is primarily implemented in `main.py`.

Major route domains:

``` text
AUTH
- register
- login
- forgot password
- reset password

FINANCE
- wallets
- categories
- transactions
- budgets
- recurring transactions
- debts
- saving goals
- wallet transfers

REPORTING
- summary
- trends
- weekly analysis
- month comparison
- export

AI
- invoice OCR
- budget checking
- AI chat
- chat history
- saving tips

ADMIN
- statistics
- user management
- status/role operations
```

------------------------------------------------------------------------

## 7. Database Context

Current major SQLite tables:

``` text
users
wallets
categories
transactions
budgets
recurring_transactions
debts
saving_goals
invoice_ocr_logs
chat_sessions
password_reset_tokens
```

SQLite is configured with WAL mode and foreign-key enforcement.

### Data integrity principle

Financial data must have a single authoritative source.

The backend/database is authoritative for:

-   balances
-   totals
-   income
-   expenses
-   budgets
-   debt amounts
-   saving goal progress
-   transaction calculations

The LLM must not invent or independently become the source of financial
truth.

------------------------------------------------------------------------

## 8. AI Architecture --- Current State

Current AI functionality uses Google Gemini.

Existing AI areas include:

-   OCR invoice extraction
-   AI chat
-   budget checking
-   saving tips

The current AI chat context contains a relatively small financial
summary and recent conversation context.

### Target AI architecture

The project should evolve toward:

``` text
User question
     ↓
AI Orchestrator
     ↓
Context Builder
     ├── User context
     ├── Financial summary
     ├── Transactions
     ├── Budgets
     ├── Debts
     ├── Saving goals
     └── Recurring obligations
     ↓
Prompt Builder
     ↓
Gemini
     ↓
Structured response
     ↓
Response validator
     ↓
Frontend
```

### Critical AI rule

Do not ask Gemini to calculate authoritative financial figures when the
backend can calculate them deterministically.

Preferred:

``` text
Backend:
remaining = target_amount - saved_amount

Gemini:
Explain what the remaining amount means and provide contextual guidance.
```

Avoid:

``` text
Send raw transactions to Gemini and ask it to calculate the user's exact balance.
```

------------------------------------------------------------------------

## 9. Important Known Risks From Audit v1

### P0 --- Resource ownership validation

For every user-owned resource, verify that referenced IDs belong to the
authenticated user.

Especially audit:

-   wallet_id
-   category_id
-   transaction_id
-   budget_id
-   recurring transaction
-   debt
-   saving goal
-   wallet transfer

Do not trust an ID supplied by the client merely because the
authenticated user is valid.

------------------------------------------------------------------------

### P0 --- JWT stale user state

JWT currently contains user identity/role information.

Authentication/authorization should account for current database state,
especially:

-   `is_active`
-   current role

A still-valid token should not automatically bypass a later account
deactivation.

------------------------------------------------------------------------

### P0 --- OCR failure must not create fake financial data

The current OCR implementation has a fallback path that can return
sample/mock-looking transaction data when Gemini OCR fails.

This must be replaced with explicit failure handling.

Preferred:

``` text
Gemini OCR fails
    ↓
OCR_FAILED
    ↓
Frontend informs user
    ↓
User retries or enters data manually
```

Never silently convert an AI/API failure into a successful-looking
financial transaction.

------------------------------------------------------------------------

### P1 --- Duplicate backend definitions

Audit found duplicate definitions/routes in `main.py`, including:

-   duplicate `get_gemini_models_list(...)`
-   duplicate `/api/user/profile` route definitions

Before expanding the backend substantially, consolidate or remove
dead/duplicated definitions.

------------------------------------------------------------------------

### P1 --- Monolithic frontend

`App.vue` is very large.

Refactor incrementally into:

``` text
views/
components/
services/
composables/
```

Do not perform a big-bang rewrite.

------------------------------------------------------------------------

### P1 --- Password reset development behavior

Forgot-password/reset behavior currently exposes development-oriented
reset information.

For production:

-   send reset/OTP information through a proper delivery mechanism;
-   do not expose reset tokens in ordinary API responses;
-   consider storing a hash/digest of reset tokens rather than
    plaintext;
-   expire and invalidate tokens after use.

------------------------------------------------------------------------

## 10. Security Rules

Never commit or expose:

-   `GEMINI_API_KEY`
-   `JWT_SECRET`
-   production credentials
-   reset tokens
-   user passwords

Use `.env.example` for placeholders.

Do not place API keys in frontend code.

For user-owned resources, always enforce ownership on the backend.

------------------------------------------------------------------------

## 11. UI / Product Language

The project uses an Xianxia/Tu Tiên theme.

Preferred terminology:

``` text
Income       → Thu nhập / Khai Thác Linh Mạch
Expense      → Chi tiêu / Tiêu Hao Linh Thạch
Wallet       → Túi Càn Khôn
Budget       → Hạn Mức Tu Luyện
AI Assistant → Khí Linh Tiên Trí
OCR          → Linh Nhãn OCR
Statistics   → Thiên Cơ Thống Kê
```

The theme should remain understandable: combine fantasy terminology with
normal financial terminology instead of replacing all practical labels
with obscure terms.

------------------------------------------------------------------------

## 12. Coding Rules

Follow `AGENTS.md` and `.specify/memory/constitution.md`.

Core rules:

1.  Do not push to GitHub unless explicitly requested.
2.  Initialize every frontend state/property used by the template.
3.  Search all usages before changing shared variables/functions/APIs.
4.  Prefer migrations for database changes; do not destroy existing
    data.
5.  Run frontend build after relevant changes.
6.  Run backend tests after relevant changes.
7.  Manually verify important UI flows.
8.  Check browser Console.
9.  Report exactly what was tested.
10. Report known limitations honestly.

------------------------------------------------------------------------

## 13. Standard Feature Development Workflow

For any medium/large feature:

``` text
1. Understand requirement
2. Inspect existing implementation
3. Identify affected files/API/database
4. Write specification
5. Write technical plan
6. Break into tasks
7. Implement incrementally
8. Run tests/build
9. Manually verify UI
10. Review security/data integrity
11. Update project context if architecture changed
12. Record known issues
```

------------------------------------------------------------------------

## 14. Prompt Contract For Coding Agents

Every implementation prompt should contain, when applicable:

``` text
ROLE
PROJECT CONTEXT
CURRENT ARCHITECTURE
EXISTING FILES
CURRENT BEHAVIOR
REQUIREMENT
BUSINESS RULES
DATABASE IMPACT
API CONTRACT
FRONTEND REQUIREMENTS
AI REQUIREMENTS
SECURITY REQUIREMENTS
NON-GOALS
IMPLEMENTATION CONSTRAINTS
ACCEPTANCE CRITERIA
TEST REQUIREMENTS
VERIFICATION REQUIREMENTS
```

The agent must inspect the existing code before creating duplicate
functionality.

The agent must prefer reuse of existing services/functions/routes over
parallel implementations.

------------------------------------------------------------------------

## 15. Current Development Strategy

Priority order:

``` text
P0
Security + financial data integrity

P1
Backend/frontend stabilization

P1
AI foundation

P2
Advanced AI intelligence

P2
UX refinement

P3
Production hardening and deployment
```

------------------------------------------------------------------------

## 16. How ChatGPT Should Work With This Project

When the user asks for a feature:

1.  Treat this document as baseline context.
2.  Inspect the current source before proposing exact file changes.
3.  Do not invent existing functions, APIs or database columns.
4.  Distinguish confirmed implementation from proposed architecture.
5.  For financial calculations, prefer deterministic backend logic.
6.  For AI behavior, define input context and structured output.
7.  Preserve existing working functionality.
8.  Give exact test/verification steps.
9.  If a major architectural decision is required, explain the trade-off
    before implementation.
