# UI_REDESIGN_SPEC.md — Càn Khôn Linh Thạch Các

> **Purpose**: Single source of truth for the existing UI/UX as-implemented.
> **Audience**: Future Stitch UI designer / agent.
> **WARNING**: This document describes the CURRENT system. DO NOT invent new capabilities.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Current Routes / Pages](#2-current-routes--pages)
3. [Navigation Structure](#3-navigation-structure)
4. [User-Facing Modules](#4-user-facing-modules)
5. [Backend API Capabilities](#5-backend-api-capabilities)
6. [Tool Registry Capabilities](#6-tool-registry-capabilities)
7. [AgentCore Capabilities & States](#7-agentcore-capabilities--states)
8. [Financial Entities & Relationships](#8-financial-entities--relationships)
9. [CRUD Operations by Entity](#9-crud-operations-by-entity)
10. [Required Parameters by Operation](#10-required-parameters-by-operation)
11. [Validation & Error States](#11-validation--error-states)
12. [Authorization & Ownership Constraints](#12-authorization--ownership-constraints)
13. [Confirmation Requirements](#13-confirmation-requirements)
14. [Transaction / Transfer / Saving-Goal Behavior](#14-transaction--transfer--saving-goal-behavior)
15. [Wallet / Category / Budget / Debt / Goal / Recurring Functionality](#15-wallet--category--budget--debt--goal--recurring-functionality)
16. [OCR Functionality](#16-ocr-functionality)
17. [Analytics & Reporting](#17-analytics--reporting)
18. [AI Chat / Khí Linh Assistant](#18-ai-chat--khí-linh-assistant)
19. [Knowledge RAG](#19-knowledge-rag)
20. [Admin Panel](#20-admin-panel)
21. [Theme & Design System](#21-theme--design-system)
22. [Component Inventory](#22-component-inventory)
23. [Capability Matrix (Read / Create / Update / Delete / AI / Voice)](#23-capability-matrix)
24. [Known Gaps & UNKNOWN Items](#24-known-gaps--unknown-items)

---

## 1. Architecture Overview

| Layer | Technology | File(s) | Notes |
|---|---|---|---|
| **Frontend** | Vue 3 (Options API via `setup()`) | `frontend/src/App.vue` (~5882 lines), `main.js` | Monolithic SPA, no Vue Router |
| **Components** | Vue SFC | `components/ChartComponents.vue`, `components/KhiLinhAssistant.vue` | Only 2 extracted components |
| **Styling** | Vanilla CSS (embedded in App.vue `<style>`) | Inline in `App.vue` | Xianxia (tu tiên) themed |
| **Backend** | FastAPI (Python) | `main.py` (~2775 lines) | Monolithic API server |
| **Database** | SQLite | `app.db` | WAL mode, foreign keys ON |
| **AI Agent** | Custom agent framework | `ai_agent/core.py`, `ai_agent/tools.py`, `ai_agent/parser.py` | Gemini-powered |
| **AI Provider** | Google Gemini API | `ai_agent/provider.py` | Model fallback chain |
| **Knowledge** | RAG system | `ai_agent/knowledge/rag.py`, `index.json`, `capabilities.json` | TF-IDF based |
| **Auth** | JWT (HS256) + bcrypt | `main.py` | Token versioning for session invalidation |
| **Dev Server** | Vite | `frontend/vite.config.js` | Proxy to `:8000` |
| **Charts** | Chart.js via ChartComponents.vue | `components/ChartComponents.vue` | Doughnut, Bar, Line |

### Monolithic Structure Warning

The entire frontend lives in a single `App.vue` file:
- **Template**: Lines 1–1775 (all HTML/modals)
- **Script `<script>`**: Lines 1777–~5400 (all state + methods)
- **Style `<style>`**: Lines ~5400–5882 (all CSS)

There is **no Vue Router**. Navigation is a **tab-based system** controlled by `activeTab` ref.

---

## 2. Current Routes / Pages

There are **NO URL-based routes**. The SPA uses a single-page tab system.

### Tab IDs (defined in `setup()`, line 1834–1846)

| Tab ID | Icon | Label (Vi) | Visibility | Description |
|---|---|---|---|---|
| `dashboard` | 📊 | Tổng Quan | All users | Financial overview, charts, budget alerts |
| `transactions` | 💸 | Giao Dịch | All users | Transaction list, create, filter, paginate |
| `debts` | 📜 | Sổ Nợ | All users | Debt tracking (borrow/lend) |
| `goals` | 🎯 | Mục Tiêu | All users | Saving goals with deposit/withdraw |
| `wallets` | 💳 | Túi Càn Khôn | All users | Wallet management, transfers |
| `categories` | 🏷️ | Danh Mục | All users | Category CRUD (income/expense) |
| `ocr` | 🧾 | Linh Nhãn OCR | All users | Invoice scanning via AI vision |
| `budgets` | 🎯 | Hạn Mức | All users | Monthly budget limits per category |
| `stats` | 📈 | Thống Kê | All users | Charts: trend, weekly, compare, saving tips |
| `chat` | 💬 | Khí Linh AI | All users | AI chat with financial data access |
| `admin` | 🛡️ | Phân Quyền | `adminOnly: true` | User management (admin role only) |

### Pseudo-Routes (Auth Screens)

| State | Description |
|---|---|
| `authMode === 'login'` | Login form (email + password) |
| `authMode === 'register'` | Registration form (email + password + name + soul_lamp) |
| `authMode === 'forgot'` | Forgot password (email + soul_lamp) |
| `authMode === 'reset'` | Reset password (email + token + new_password) |
| `isLoggedIn === true` | Main application with tab navigation |

---

## 3. Navigation Structure

### Primary Navigation

- **Horizontal scrollable tab bar** at the top of the main content area
- Uses `tabNavEl` ref + scroll state (`canScrollNavLeft`, `canScrollNavRight`)
- Scroll buttons `◀ / ▶` appear conditionally
- Active tab highlighted with CSS class
- Admin tab conditionally rendered: `v-if="isUserAdmin"`

### Secondary Navigation (within tabs)

| Tab | Sub-navigation |
|---|---|
| `transactions` | Recurring section toggle (`showRecurringSection`), Filter bar, Pagination |
| `debts` | Filter bar (type + settlement status) |
| `stats` | Date range picker (VueDatePicker), preset ranges, compare month selectors |
| `budgets` | Month selector (`budgetMonth`) |
| `admin` | Filter bar (search + role + status) |

### Persistent UI Elements (always visible when logged in)

| Element | Description |
|---|---|
| **Header Bar** | App title + user name + profile button + logout |
| **KhiLinhAssistant** | Floating AI companion button (bottom-right), Teleport to `<body>` |
| **Toast Notification** | Global toast with success/error types |
| **Profile Modal** | Accessible from header, shows profile + soul lamp forms |

---

## 4. User-Facing Modules

### 4.1 Authentication Module
- Login (email + password)
- Registration (email + password + full_name + soul_lamp)
- Forgot Password (email + soul_lamp verification → generates reset token)
- Reset Password (email + token + new_password)
- Dev reset token display (visible in forgot flow response)

### 4.2 Dashboard Module
- Total balance across all wallets
- Monthly income / expense / net savings summary
- Expense-by-category doughnut chart
- Monthly trend bar chart (income vs expense)
- Budget alert cards (warning/danger levels)

### 4.3 Transaction Module
- Create transaction form (type, amount, wallet, category, date, note)
- Transaction list with filtering (date range, category, wallet, type, keyword)
- Pagination (15 per page)
- Recurring transactions section (collapsible)
  - Create/edit/delete recurring transactions
  - Active/paused status toggle

### 4.4 Debt Module (Sổ Nợ)
- Create debt (BORROW/LEND, person_name, amount, due_date, wallet_id, note)
- Debt list with filter (type, settlement status)
- Summary stats (total unsettled borrow/lend, settled borrow/lend)
- Settle/unsettle toggle button
- Edit debt modal
- Delete debt

### 4.5 Saving Goals Module (Mục Tiêu)
- Create goal (name, target_amount, current_amount, target_date, icon)
- Goal cards with progress bars (percent, remaining_amount, days_left)
- Summary stats (total_target, total_saved, completed_count, active_count)
- Deposit modal (amount, optional wallet source)
- Withdraw modal (amount, optional wallet destination)
- Edit goal modal
- Delete goal

### 4.6 Wallet Module (Túi Càn Khôn)
- Create wallet (name, balance, type: cash/bank/e-wallet/crypto)
- Wallet cards with balance display
- Edit wallet modal (name, type)
- Delete wallet
- Transfer between wallets form (from_wallet, to_wallet, amount, note)

### 4.7 Category Module (Danh Mục)
- Create category (name, type: INCOME/EXPENSE, icon)
- Category list grouped by type
- Edit category modal (name, icon)
- Delete category
- Icon picker (20 emoji options)

### 4.8 OCR Module (Linh Nhãn)
- File upload (image: JPEG/PNG/WEBP/HEIC, max 5MB)
- Image preview
- OCR result display (store_name, total_amount, items, date)
- Confirm form to save as transaction (pre-populated from OCR)

### 4.9 Budget Module (Hạn Mức)
- Create budget (category, limit_amount, month_year)
- Budget cards with progress bars (spent vs limit)
- Edit budget modal (limit_amount)
- Delete budget
- Month selector to view different months
- Auto budget check alerts

### 4.10 Statistics Module (Thống Kê)
- Date range picker with preset ranges (7d, 30d, this month, last month, 3m, 6m)
- Expense-by-category doughnut chart
- Monthly trend bar chart (income vs expense)
- Weekly trend line chart
- Month-to-month comparison
- AI saving tips (Gemini-powered analysis)

### 4.11 Chat Module (Khí Linh AI)
- Message-based chat interface
- Chat history display
- Suggested questions
- Action/Knowledge mode toggle
- Confirmation flow for write/delete operations
- Cancel pending action button

### 4.12 Admin Module (Phân Quyền)
- System stats (total users, active, locked)
- User list with search/filter (name, email, role, status)
- Toggle user active/locked
- Change user role (admin/user)

### 4.13 KhiLinh Assistant (Persistent Companion)
- Floating chibi spirit SVG button (bottom-right corner)
- "Live System Mode" overlay (Teleported to `<body>`)
- Dark overlay with system frame dialog
- Action mode (can execute financial operations)
- Knowledge mode (read-only, advisory)
- Chat input with voice support (UNKNOWN: actual voice implementation status)
- Confirmation/cancel flow for pending actions
- Tab switching command (`@switch-tab` event)
- Transaction completion callback (`@transaction-completed` event)

---

## 5. Backend API Capabilities

### 5.1 Authentication APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | User registration | None |
| POST | `/api/auth/login` | User login → JWT token | None |
| POST | `/api/auth/forgot-password` | Generate reset token (soul lamp verification) | None |
| POST | `/api/auth/reset-password` | Reset password with token | None |
| POST | `/api/auth/change-password` | Change password (invalidates old JWTs) | JWT |

### 5.2 User Profile APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/user/profile` | Get current user profile | JWT |
| PUT | `/api/user/profile` | Update display name | JWT |
| PUT | `/api/user/soul-lamp` | Update soul lamp (requires current password) | JWT |
| PUT | `/api/user/password` | Change password (alias) | JWT |

### 5.3 Wallet APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/wallets` | List user's wallets | JWT |
| POST | `/api/wallets` | Create wallet | JWT |
| PUT | `/api/wallets/{id}` | Update wallet name/type | JWT |
| DELETE | `/api/wallets/{id}` | Delete wallet (cascades to transactions) | JWT |
| POST | `/api/wallets/transfer` | Transfer between wallets (atomic, 2-sided) | JWT |

### 5.4 Category APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/categories` | List user's categories | JWT |
| POST | `/api/categories` | Create category | JWT |
| PUT | `/api/categories/{id}` | Update category | JWT |
| DELETE | `/api/categories/{id}` | Delete category | JWT |

### 5.5 Transaction APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/transactions` | List transactions (filtered, paginated) | JWT |
| POST | `/api/transactions` | Create transaction | JWT |
| PUT | `/api/transactions/{id}` | Update transaction (adjusts wallet balance) | JWT |
| DELETE | `/api/transactions/{id}` | Delete transaction (restores wallet balance) | JWT |
| GET | `/api/transactions/summary` | Monthly summary (income, expense, by-category) | JWT |

### 5.6 Budget APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/budgets` | List budgets with spending progress | JWT |
| POST | `/api/budgets` | Create/upsert budget | JWT |
| PUT | `/api/budgets/{id}` | Update budget limit | JWT |
| DELETE | `/api/budgets/{id}` | Delete budget | JWT |

### 5.7 Recurring Transaction APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/recurring-transactions` | List recurring txns (triggers pending processing) | JWT |
| POST | `/api/recurring-transactions` | Create recurring transaction | JWT |
| PUT | `/api/recurring-transactions/{id}` | Update recurring transaction | JWT |
| DELETE | `/api/recurring-transactions/{id}` | Delete recurring transaction | JWT |

### 5.8 Debt APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/debts` | List debts with summary stats | JWT |
| POST | `/api/debts` | Create debt | JWT |
| PUT | `/api/debts/{id}` | Update debt | JWT |
| POST | `/api/debts/{id}/settle` | Toggle settle/unsettle | JWT |
| DELETE | `/api/debts/{id}` | Delete debt | JWT |

### 5.9 Saving Goal APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/saving-goals` | List goals with progress | JWT |
| POST | `/api/saving-goals` | Create saving goal | JWT |
| PUT | `/api/saving-goals/{id}` | Update saving goal | JWT |
| POST | `/api/saving-goals/{id}/deposit` | Deposit to goal (opt. from wallet) | JWT |
| POST | `/api/saving-goals/{id}/withdraw` | Withdraw from goal (opt. to wallet) | JWT |
| DELETE | `/api/saving-goals/{id}` | Delete saving goal | JWT |

### 5.10 AI & OCR APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/ai/chat` | AI agent chat (action or knowledge mode) | JWT |
| POST | `/api/ai/cancel-pending` | Cancel pending agent action | JWT |
| GET | `/api/ai/pending-action` | Get pending action status | JWT |
| GET | `/api/ai/chat-history` | Get chat history (30 most recent) | JWT |
| GET | `/api/chat/suggested-questions` | Get 5 recent distinct questions | JWT |
| POST | `/api/ai/scan-invoice` | OCR invoice scan (image upload) | JWT |
| POST | `/api/ai/check-budget` | Budget overspend check | JWT |
| POST | `/api/ai/saving-tips` | AI saving tips analysis | JWT |

### 5.11 Reports APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/reports/trend` | Monthly trend (N months) | JWT |
| GET | `/api/reports/weekly` | Weekly breakdown (N weeks) | JWT |
| GET | `/api/reports/compare` | Compare 2 months | JWT |
| GET | `/api/reports/export` | Export CSV/Excel | JWT |

### 5.12 Admin APIs

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/admin/stats` | System stats | Admin JWT |
| GET | `/api/admin/users` | List all users | Admin JWT |
| PUT | `/api/admin/users/{id}/toggle-active` | Lock/unlock user | Admin JWT |
| PUT | `/api/admin/users/{id}/role` | Change user role | Admin JWT |

---

## 6. Tool Registry Capabilities

The AI Agent has **44 registered tools** across **11 domains**:

### Domain: `wallet` (6 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_wallets` | READ | LOW | ❌ | List wallets + balances |
| `wallet_status` | READ | LOW | ❌ | Alias for get_wallets |
| `create_wallet` | WRITE | MEDIUM | ✅ | Create new wallet |
| `update_wallet` | WRITE | MEDIUM | ✅ | Update wallet name/type |
| `delete_wallet` | DELETE | CRITICAL | ✅ | Delete wallet + linked txns |
| `transfer_money` | WRITE | HIGH | ✅ | Transfer between wallets |

### Domain: `category` (4 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_categories` | READ | LOW | ❌ | List categories |
| `create_category` | WRITE | LOW | ✅ | Create category |
| `update_category` | WRITE | LOW | ✅ | Update name/icon |
| `delete_category` | DELETE | HIGH | ✅ | Delete category |

### Domain: `transaction` (6 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_recent_transactions` | READ | LOW | ❌ | Last N transactions |
| `transaction_search` | READ | LOW | ❌ | Search/filter transactions |
| `search_transactions` | READ | LOW | ❌ | Alias for transaction_search |
| `create_expense` | WRITE | MEDIUM | ✅ | Add expense |
| `create_income` | WRITE | MEDIUM | ✅ | Add income |
| `update_transaction` | WRITE | MEDIUM | ✅ | Edit transaction |
| `delete_transaction` | DELETE | HIGH | ✅ | Delete + restore balance |

### Domain: `budget` (5 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `budget_status` | READ | LOW | ❌ | Budget progress/alerts |
| `get_budget_status` | READ | LOW | ❌ | Alias |
| `create_budget` | WRITE | MEDIUM | ✅ | Create/upsert budget |
| `update_budget` | WRITE | MEDIUM | ✅ | Update limit |
| `delete_budget` | DELETE | MEDIUM | ✅ | Remove budget |

### Domain: `recurring` (4 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_recurring_transactions` | READ | LOW | ❌ | List recurring |
| `create_recurring_transaction` | WRITE | HIGH | ✅ | Create recurring |
| `update_recurring_transaction` | WRITE | MEDIUM | ✅ | Edit recurring |
| `delete_recurring_transaction` | DELETE | HIGH | ✅ | Delete recurring |

### Domain: `debt` (6 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `debt_status` | READ | LOW | ❌ | Debt summary |
| `get_debts` | READ | LOW | ❌ | Alias |
| `create_debt` | WRITE | HIGH | ✅ | Record debt |
| `update_debt` | WRITE | MEDIUM | ✅ | Edit debt |
| `settle_debt` | WRITE | HIGH | ✅ | Mark settled |
| `delete_debt` | DELETE | HIGH | ✅ | Remove debt |

### Domain: `saving_goal` (7 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `saving_goal_status` | READ | LOW | ❌ | Goal progress |
| `get_saving_goals` | READ | LOW | ❌ | Alias |
| `create_saving_goal` | WRITE | MEDIUM | ✅ | Create goal |
| `update_saving_goal` | WRITE | MEDIUM | ✅ | Edit goal |
| `saving_goal_deposit` | WRITE | HIGH | ✅ | Deposit to goal |
| `saving_goal_withdraw` | WRITE | HIGH | ✅ | Withdraw from goal |
| `delete_saving_goal` | DELETE | HIGH | ✅ | Delete goal |

### Domain: `reports` (6 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `financial_overview` | READ | LOW | ❌ | Financial summary by period |
| `get_financial_overview` | READ | LOW | ❌ | Alias |
| `spending_summary` | READ | LOW | ❌ | Spending by period |
| `spending_by_category` | READ | LOW | ❌ | Category breakdown |
| `get_trend_report` | READ | LOW | ❌ | Multi-month trends |
| `get_weekly_report` | READ | LOW | ❌ | Weekly breakdown |
| `compare_months` | READ | LOW | ❌ | 2-month comparison |
| `export_reports` | SYSTEM | LOW | ❌ | CSV/Excel export |

### Domain: `ocr` (1 tool)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_ocr_logs` | READ | LOW | ❌ | OCR scan history |

### Domain: `user` / `navigation` / `system` (4 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_user_profile` | READ | LOW | ❌ | User info |
| `update_user_profile` | WRITE | LOW | ✅ | Update display name |
| `navigate_to` | SYSTEM | LOW | ❌ | Switch UI tab |
| `get_system_help` | READ | LOW | ❌ | Feature guide |

### Domain: `admin` (4 tools)

| Tool Name | Operation | Risk | Confirmation | Description |
|---|---|---|---|---|
| `get_admin_stats` | READ | LOW | ❌ | System stats |
| `list_admin_users` | READ | LOW | ❌ | User list |
| `toggle_user_status` | WRITE | HIGH | ✅ | Lock/unlock user |
| `change_user_role` | WRITE | CRITICAL | ✅ | Admin ↔ user role |

---

## 7. AgentCore Capabilities & States

### 7.1 Agent States (`AgentState` enum)

| State | Description |
|---|---|
| `IDLE` | Default, waiting for user input |
| `THINKING` | Processing user message, identifying intent |
| `PLANNING` | Determining which tool + arguments to use |
| `CONFIRMING` | Awaiting user confirmation for write/delete ops |
| `EXECUTING` | Tool handler is running |
| `SUCCESS` | Operation completed successfully |
| `ERROR` | Operation failed |

### 7.2 Core Capabilities

| Capability | Description |
|---|---|
| **Intent Classification** | 3-tier: General Chat, Advisory (read-only), Financial Action (write/delete) |
| **Vietnamese NLP Parser** | Parses amounts (50k, 1tr5, 2 tỷ), dates (hôm nay, ngày mai), confirm/cancel keywords |
| **Confirmation Flow** | Mandatory for all WRITE/DELETE ops. Generates summary, waits for user confirm/cancel |
| **Modification Support** | User can modify pending args before confirming |
| **Cancellation Support** | User can cancel pending actions via natural language |
| **Orphan Protection** | Cannot confirm/cancel without a pending action |
| **Verified Result Invariant** | Never claims success without actual DB result |
| **Action Context Memory** | Tracks last action, action history, entity-by-type per user |
| **Contextual Entity Resolution** | References like "cái vừa tạo" resolve to last entity |
| **Multi-turn Context** | 3 most recent conversation turns loaded as history |
| **Knowledge RAG** | TF-IDF based retrieval for domain knowledge augmentation |
| **Dual Mode** | `action` mode (full capabilities), `knowledge` mode (read-only) |
| **Role-based Tool Access** | Admin tools only available to `role=admin` users |
| **Idempotency** | `operation_id` prevents duplicate financial operations |

### 7.3 AgentResponse Structure

```
{
  "response": str,           // AI response text
  "state": str,              // AgentState value
  "tool_executed": str|null,  // Tool name if executed
  "tool_result": dict|null,   // Tool execution result
  "pending_confirmation": dict|null  // Pending action awaiting confirm
}
```

### 7.4 Vietnamese Financial Parser

| Parse Type | Examples |
|---|---|
| **Amount** | `50k` → 50,000 · `1tr5` → 1,500,000 · `2 tỷ` → 2,000,000,000 · `50 nghìn` → 50,000 |
| **Date** | `hôm nay` → today · `hôm qua` → yesterday · `ngày mai` → tomorrow · `DD/MM/YYYY` |
| **Confirmation** | `ok`, `được`, `làm đi`, `xác nhận`, `chuẩn`, `duyệt`, `yes` |
| **Cancellation** | `hủy`, `thôi`, `không`, `bỏ qua`, `đừng`, `stop`, `no` |
| **Modification** | (Detected contextually when pending action exists + user changes params) |

---

## 8. Financial Entities & Relationships

### Database Schema (10 tables)

```
users ──────────────────────── (1:N) → wallets
  │                                        │
  ├─ (1:N) → categories                    ├── (1:N) → transactions
  │              │                         │
  │              ├── (1:N) → transactions ──┘
  │              └── (1:N) → budgets
  │
  ├─ (1:N) → transactions
  ├─ (1:N) → budgets
  ├─ (1:N) → recurring_transactions ──→ wallets, categories
  ├─ (1:N) → debts ──→ wallets (optional)
  ├─ (1:N) → saving_goals
  ├─ (1:N) → chat_sessions
  ├─ (1:N) → invoice_ocr_logs
  └─ password_reset_tokens (by email)
```

### Entity Definitions

| Entity | Table | Key Fields | Ownership |
|---|---|---|---|
| **User** | `users` | id, email, password_hash, full_name, soul_lamp_hash, role, is_active, token_version | Self |
| **Wallet** | `wallets` | id, user_id, wallet_name, balance, wallet_type | user_id |
| **Category** | `categories` | id, user_id, category_name, category_type, icon | user_id |
| **Transaction** | `transactions` | id, user_id, wallet_id, category_id, amount, transaction_type, transaction_date, note, operation_id | user_id |
| **Budget** | `budgets` | id, user_id, category_id, limit_amount, month_year | user_id |
| **Recurring Txn** | `recurring_transactions` | id, user_id, wallet_id, category_id, amount, transaction_type, frequency, next_run_date, is_active | user_id |
| **Debt** | `debts` | id, user_id, wallet_id, debt_type, person_name, amount, due_date, is_settled | user_id |
| **Saving Goal** | `saving_goals` | id, user_id, target_name, target_amount, current_amount, target_date, icon, is_completed | user_id |
| **Chat Session** | `chat_sessions` | id, user_id, prompt_question, ai_response | user_id |
| **OCR Log** | `invoice_ocr_logs` | id, user_id, image_path, extracted_json | user_id |
| **Reset Token** | `password_reset_tokens` | id, email, token, expires_at, used | email |

---

## 9. CRUD Operations by Entity

### Wallet

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/wallets` | `create_wallet` | Wallets tab form |
| **R** | `GET /api/wallets` | `get_wallets` / `wallet_status` | Wallets tab list |
| **U** | `PUT /api/wallets/{id}` | `update_wallet` | Edit wallet modal |
| **D** | `DELETE /api/wallets/{id}` | `delete_wallet` | Delete button on card |
| **Transfer** | `POST /api/wallets/transfer` | `transfer_money` | Transfer form |

### Category

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/categories` | `create_category` | Categories tab form |
| **R** | `GET /api/categories` | `get_categories` | Categories tab list |
| **U** | `PUT /api/categories/{id}` | `update_category` | Edit category modal |
| **D** | `DELETE /api/categories/{id}` | `delete_category` | Delete button |

### Transaction

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/transactions` | `create_expense` / `create_income` | Transactions tab form |
| **R** | `GET /api/transactions` | `get_recent_transactions` / `transaction_search` | Transactions tab list |
| **U** | `PUT /api/transactions/{id}` | `update_transaction` | UNKNOWN (no edit modal visible in template) |
| **D** | `DELETE /api/transactions/{id}` | `delete_transaction` | Delete button on row |

### Budget

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/budgets` | `create_budget` | Budgets tab form |
| **R** | `GET /api/budgets` | `budget_status` / `get_budget_status` | Budgets tab list |
| **U** | `PUT /api/budgets/{id}` | `update_budget` | Edit budget modal |
| **D** | `DELETE /api/budgets/{id}` | `delete_budget` | Delete button |

### Recurring Transaction

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/recurring-transactions` | `create_recurring_transaction` | Recurring section form |
| **R** | `GET /api/recurring-transactions` | `get_recurring_transactions` | Recurring section list |
| **U** | `PUT /api/recurring-transactions/{id}` | `update_recurring_transaction` | Edit recurring modal |
| **D** | `DELETE /api/recurring-transactions/{id}` | `delete_recurring_transaction` | Delete button |

### Debt

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/debts` | `create_debt` | Debts tab form |
| **R** | `GET /api/debts` | `debt_status` / `get_debts` | Debts tab list |
| **U** | `PUT /api/debts/{id}` | `update_debt` | Edit debt modal |
| **D** | `DELETE /api/debts/{id}` | `delete_debt` | Delete button |
| **Settle** | `POST /api/debts/{id}/settle` | `settle_debt` | Settle toggle button |

### Saving Goal

| Op | API | AI Tool | UI Location |
|---|---|---|---|
| **C** | `POST /api/saving-goals` | `create_saving_goal` | Goals tab form |
| **R** | `GET /api/saving-goals` | `saving_goal_status` / `get_saving_goals` | Goals tab list |
| **U** | `PUT /api/saving-goals/{id}` | `update_saving_goal` | Edit goal modal |
| **D** | `DELETE /api/saving-goals/{id}` | `delete_saving_goal` | Delete button |
| **Deposit** | `POST /api/saving-goals/{id}/deposit` | `saving_goal_deposit` | Deposit modal |
| **Withdraw** | `POST /api/saving-goals/{id}/withdraw` | `saving_goal_withdraw` | Withdraw modal |

---

## 10. Required Parameters by Operation

### Registration
| Param | Type | Required | Validation |
|---|---|---|---|
| `email` | string | ✅ | Must contain `@`, unique |
| `password` | string | ✅ | Min 4 chars |
| `full_name` | string | ✅ | Non-empty after trim |
| `soul_lamp` | string | ✅ | Min 3 chars (Bản Mệnh Hồn Đăng) |

### Create Transaction
| Param | Type | Required | Validation |
|---|---|---|---|
| `amount` | number | ✅ | > 0 |
| `transaction_type` | enum | ✅ | `INCOME` or `EXPENSE` |
| `wallet_id` | int | ✅ | Must exist, must belong to user |
| `category_id` | int | ✅ | Must exist, must belong to user |
| `transaction_date` | string | ✅ | YYYY-MM-DD format |
| `note` | string | ❌ | Default empty |

### Create Wallet
| Param | Type | Required | Validation |
|---|---|---|---|
| `wallet_name` | string | ✅ | Non-empty |
| `balance` | number | ❌ | Default 0 |
| `wallet_type` | enum | ❌ | `cash`, `bank`, `e-wallet`, `crypto`. Default `cash` |

### Transfer
| Param | Type | Required | Validation |
|---|---|---|---|
| `from_wallet_id` | int | ✅ | Must exist, must belong to user |
| `to_wallet_id` | int | ✅ | Must exist, must belong to user, ≠ from |
| `amount` | number | ✅ | > 0, ≤ source balance |
| `note` | string | ❌ | |
| `operation_id` | string | ❌ | Idempotency key |

### Create Debt
| Param | Type | Required | Validation |
|---|---|---|---|
| `debt_type` | enum | ✅ | `BORROW` or `LEND` |
| `person_name` | string | ✅ | Non-empty after trim |
| `amount` | number | ✅ | > 0 |
| `due_date` | string | ❌ | YYYY-MM-DD |
| `wallet_id` | int | ❌ | If set, must belong to user |
| `note` | string | ❌ | |

### Create Saving Goal
| Param | Type | Required | Validation |
|---|---|---|---|
| `target_name` | string | ✅ | Non-empty after trim |
| `target_amount` | number | ✅ | > 0 |
| `current_amount` | number | ❌ | Default 0, ≥ 0 |
| `target_date` | string | ❌ | YYYY-MM-DD |
| `icon` | string | ❌ | Default `🎯` |

### Saving Goal Deposit
| Param | Type | Required | Validation |
|---|---|---|---|
| `amount` | number | ✅ | > 0 |
| `wallet_id` | int | ❌ | If set: must belong to user, balance ≥ amount |
| `operation_id` | string | ❌ | Idempotency key |

### Create Budget
| Param | Type | Required | Validation |
|---|---|---|---|
| `category_id` | int | ✅ | Must exist, must belong to user |
| `limit_amount` | number | ✅ | > 0 |
| `month_year` | string | ✅ | YYYY-MM format |

### Create Recurring Transaction
| Param | Type | Required | Validation |
|---|---|---|---|
| `amount` | number | ✅ | > 0 |
| `transaction_type` | enum | ✅ | `INCOME` or `EXPENSE` |
| `wallet_id` | int | ✅ | Must exist, must belong to user |
| `category_id` | int | ✅ | Must exist, must belong to user |
| `frequency` | enum | ✅ | `weekly` or `monthly` |
| `next_run_date` | string | ✅ | YYYY-MM-DD |
| `note` | string | ❌ | |

---

## 11. Validation & Error States

### HTTP Error Codes Used

| Code | Usage |
|---|---|
| `400` | Validation failure (invalid params, insufficient balance, self-transfer, etc.) |
| `401` | Missing/invalid/expired JWT, inactive account |
| `403` | Admin-only endpoint accessed by non-admin |
| `404` | Resource not found or not owned by user |
| `413` | OCR file too large (> 5MB) |
| `415` | OCR unsupported file type |
| `422` | OCR parsing failure |
| `429` | Rate limit exceeded (login/forgot-password) |
| `500` | Internal server error, AI provider failure |
| `504` | AI timeout (all Gemini models failed) |

### Client-Side Validation (App.vue)

- Amount > 0 checks before API call
- Required field presence checks
- Loading state prevents double-submit (`loading` ref)
- Toast notifications for success/error feedback

### Rate Limiting

| Endpoint | Max Attempts | Lockout |
|---|---|---|
| `/api/auth/login` | 5 attempts | 15 minutes |
| `/api/auth/forgot-password` | 5 attempts | 15 minutes |

---

## 12. Authorization & Ownership Constraints

### JWT Token Structure

```json
{
  "user_id": int,
  "email": string,
  "role": "user" | "admin",
  "token_version": int,
  "exp": timestamp
}
```

### Ownership Checks (IDOR Protection)

**Every** data-modifying or data-reading API verifies `user_id` ownership:

| Entity | Check |
|---|---|
| Wallets | `WHERE id = ? AND user_id = ?` |
| Categories | `WHERE id = ? AND user_id = ?` |
| Transactions | `WHERE id = ? AND user_id = ?` |
| Budgets | `WHERE id = ? AND user_id = ?` |
| Recurring | `WHERE id = ? AND user_id = ?` |
| Debts | `WHERE id = ? AND user_id = ?` |
| Saving Goals | `WHERE id = ? AND user_id = ?` |
| Chat History | `WHERE user_id = ?` |

### Admin Constraints

- Admin check via `require_admin` dependency (`role == 'admin'`)
- Cannot self-lock (`user_id == admin.user_id` → 400)
- Cannot self-demote (`user_id == admin.user_id && role != 'admin'` → 400)

### Token Versioning

- Password change increments `token_version`
- JWT with old `token_version` rejected → forced re-login

### Account Status

- `is_active == 0` → JWT validation rejects with 401

---

## 13. Confirmation Requirements

### UI Confirmation (Frontend)

The frontend currently uses `window.confirm()` (or simple conditional checks) for delete operations. Modals are used for edit operations.

### AI Agent Confirmation (Backend)

All tools with `requires_confirmation: true` go through a 2-step flow:

1. **Agent identifies tool + args** → State: `CONFIRMING`
2. **Agent generates summary** (via `summary_generator`) → Returns `pending_confirmation`
3. **User sends confirm/cancel** → Parser detects intent
4. **On confirm** → Agent executes tool → State: `SUCCESS` or `ERROR`
5. **On cancel** → Agent clears pending → State: `IDLE`

### Operations Requiring Confirmation

| Risk Level | Operations |
|---|---|
| **CRITICAL** | `delete_wallet`, `change_user_role` |
| **HIGH** | `transfer_money`, `create_recurring_transaction`, `delete_recurring_transaction`, `create_debt`, `settle_debt`, `delete_debt`, `saving_goal_deposit`, `saving_goal_withdraw`, `delete_saving_goal`, `delete_transaction`, `delete_category`, `toggle_user_status` |
| **MEDIUM** | `create_wallet`, `update_wallet`, `create_expense`, `create_income`, `update_transaction`, `create_budget`, `update_budget`, `delete_budget`, `create_saving_goal`, `update_saving_goal`, `update_recurring_transaction`, `update_debt` |
| **LOW (with confirm)** | `create_category`, `update_category`, `update_user_profile` |

### Operations NOT Requiring Confirmation

All READ and SYSTEM operations: queries, searches, reports, navigation, help.

---

## 14. Transaction / Transfer / Saving-Goal Behavior

### Transaction Creation

1. Validate amount > 0, wallet ownership, category ownership
2. For EXPENSE: deduct wallet balance
3. For INCOME: add to wallet balance
4. Insert into `transactions` table
5. Return transaction_id

### Transaction Deletion

1. Verify ownership
2. **Reverse** balance change:
   - If EXPENSE: **add** amount back to wallet
   - If INCOME: **deduct** amount from wallet
3. Delete from `transactions`

### Transaction Update

1. Verify ownership
2. Calculate balance adjustment (difference between old and new amounts / types)
3. Update wallet balance atomically
4. Update transaction record

### Wallet Transfer

1. Verify both wallets belong to user
2. Check source has sufficient balance
3. **Idempotency check**: If `operation_id` exists → return early with `already_processed: true`
4. **Duplicate check**: If no `operation_id`, check for recent (5s) identical transaction
5. Create system categories ("Chuyển Khoản" EXPENSE + INCOME) if not exist
6. Deduct from source, add to destination
7. Insert 2 transaction records (EXPENSE from source, INCOME to destination)
8. Both operations within same `get_db()` context → atomic

### Saving Goal Deposit

1. Verify goal ownership
2. If `wallet_id` provided:
   - Verify wallet ownership + sufficient balance
   - Idempotency check (operation_id or 5s dedup)
   - Deduct from wallet
   - Create EXPENSE transaction with system category "Mục Tiêu Tiết Kiệm"
3. Increment `current_amount` on goal
4. Auto-mark `is_completed = 1` if `current_amount >= target_amount`

### Saving Goal Withdraw

1. Verify goal ownership
2. Check goal has sufficient `current_amount`
3. If `wallet_id` provided: add to wallet balance
4. Decrement `current_amount` on goal
5. Reset `is_completed` if dropped below target

### Recurring Transaction Processing

- Triggered on `GET /api/recurring-transactions`
- For each active recurring where `next_run_date <= today`:
  - Uses `SAVEPOINT` for atomic per-item processing
  - Creates transaction, adjusts wallet balance
  - Advances `next_run_date` (weekly: +7 days, monthly: +1 month)

---

## 15. Wallet / Category / Budget / Debt / Goal / Recurring Functionality

### Wallet Types

| Type | Label |
|---|---|
| `cash` | Tiền Mặt |
| `bank` | Ngân Hàng |
| `e-wallet` | Ví Điện Tử |
| `crypto` | Crypto |

### Category Types

| Type | Label |
|---|---|
| `INCOME` | Khoản Thu (income categories) |
| `EXPENSE` | Khoản Chi (expense categories) |

### System Categories (Auto-created)

| Name | Type | Icon | Created By |
|---|---|---|---|
| Chuyển Khoản | EXPENSE | 🔄 | Wallet transfer (source side) |
| Chuyển Khoản | INCOME | 🔄 | Wallet transfer (destination side) |
| Mục Tiêu Tiết Kiệm | EXPENSE | 🎯 | Saving goal deposit |

### Budget Alerts

| Level | Condition | Icon |
|---|---|---|
| DANGER | Spent ≥ 100% of limit | 🔥 "TẨU HỎA NHẬP MA!" |
| WARNING | Spent ≥ 80% of limit | ⚠️ "CẢNH BÁO TÂM MA!" |

### Debt Types

| Type | Vietnamese | Description |
|---|---|---|
| `BORROW` | Tôi Vay Nợ | User borrowed from someone (needs to repay) |
| `LEND` | Tôi Cho Vay | User lent to someone (needs to collect) |

### Debt Settlement

- Toggle via `POST /api/debts/{id}/settle`
- Flips `is_settled` between 0 and 1
- Does NOT automatically affect wallet balances

### Recurring Frequencies

| Frequency | Increment |
|---|---|
| `weekly` | +7 days |
| `monthly` | +1 calendar month |

### Saving Goal Icons (Frontend Options)

🎯 💻 🚗 🏠 ✈️ 🛡️ 🎓 🎁

---

## 16. OCR Functionality

### Flow

1. User uploads image (JPEG, PNG, WEBP, HEIC, max 5MB)
2. Frontend shows preview
3. Backend sends to Gemini Vision API with structured prompt
4. Response parsed as JSON, validated against strict schema
5. Validated result stored in `invoice_ocr_logs`
6. Frontend displays result + pre-populated transaction form
7. User confirms to save as transaction

### OCR Response Schema (enforced)

```json
{
  "store_name": "string (required, non-empty)",
  "total_amount": "number (required, >= 0, finite)",
  "items": [
    {"name": "string", "price": "number >= 0", "quantity": "int > 0"}
  ],
  "date": "YYYY-MM-DD (required, valid ISO date)",
  "currency": "string (default VND)"
}
```

### OCR Validation Rules

- Rejects non-receipt status ("not a receipt", "invalid", "error", etc.)
- Rejects `is_receipt: false` / `is_invoice: false`
- Rejects if AI returns `error` field
- All item prices must be non-negative finite numbers
- All item names must be non-empty strings
- **Never fabricates financial data on OCR failure** — returns 422 error

### File Restrictions

| Constraint | Value |
|---|---|
| Max file size | 5 MB (configurable via `MAX_OCR_FILE_SIZE` env var) |
| Allowed MIME types | `image/jpeg`, `image/jpg`, `image/png`, `image/webp`, `image/heic`, `image/heif` |
| Allowed extensions | `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.heif` |

---

## 17. Analytics & Reporting

### Dashboard Summary (`/api/transactions/summary`)

| Metric | Description |
|---|---|
| `total_income` | Sum of INCOME transactions for the month |
| `total_expense` | Sum of EXPENSE transactions for the month |
| `net_savings` | income - expense |
| `total_balance` | Sum of all wallet balances |
| `expense_by_category` | Grouped by category with name, icon, total |

### Trend Report (`/api/reports/trend`)

- N months (1-12, default 6) of income/expense/savings aggregated monthly
- Used for bar chart

### Weekly Report (`/api/reports/weekly`)

- N weeks (1-12, default 4) of expense/income/txn_count aggregated weekly
- Used for line chart

### Month Comparison (`/api/reports/compare`)

- Compares 2 specific months (YYYY-MM format)
- Returns income, expense, savings, by_category for each
- Calculates delta_income, delta_expense, delta_savings

### Report Export (`/api/reports/export`)

| Format | Content |
|---|---|
| CSV | UTF-8 BOM, columns: Date, Category, Type, Amount, Wallet, Note |
| Excel | Styled headers (teal fill, white font, centered), auto-width columns, number formatting |

### AI Saving Tips (`/api/ai/saving-tips`)

- Analyzes current month's spending
- Sends to Gemini: income/expense summary, by-category breakdown, top 5 largest expenses
- Returns 5 saving tips in Xianxia prose style

### Chart Types (ChartComponents.vue)

| Chart Type | Component Prop | Used In |
|---|---|---|
| Doughnut | `type="doughnut"` | Dashboard expense breakdown, Stats page |
| Bar | `type="bar"` | Dashboard trend, Stats trend |
| Line | `type="line"` | Stats weekly |

### Stats Date Range Presets

| Label | Range |
|---|---|
| 7 ngày qua | Last 7 days |
| 30 ngày qua | Last 30 days |
| Tháng này | First of current month → today |
| Tháng trước | Full previous month |
| 3 tháng gần đây | Last 3 months |
| 6 tháng gần đây | Last 6 months |

---

## 18. AI Chat / Khí Linh Assistant

### Two Interfaces

| Interface | Location | Component |
|---|---|---|
| **Chat Tab** | `activeTab === 'chat'` | Inline in `App.vue` |
| **KhiLinh Assistant** | Floating overlay | `KhiLinhAssistant.vue` (1705 lines, 53KB) |

### Chat Tab Features

- Message list with user/AI bubbles
- Text input
- Suggested questions (5 most recent)
- Chat history (30 most recent)
- Loading indicator

### KhiLinh Assistant Features

- **Floating Spirit Button**: Chibi celestial SVG, bottom-right, state-colored badge
- **Live System Mode**: Full-screen overlay with system frame
- **Modes**:
  - `action` (Khí Linh Nhỏ / Live System): Can execute financial operations
  - `knowledge` (Khí Linh AI Lớn / Desktop Chat): Read-only, advisory
- **Confirmation UI**: Shows pending action summary, confirm/cancel buttons
- **Tab Navigation**: Can switch main app tabs via `@switch-tab` event
- **Transaction Callback**: Triggers data reload via `@transaction-completed`

### Chat History

- Stored in `chat_sessions` table
- 3 most recent turns used as context for next request
- 30 most recent returned in history API

---

## 19. Knowledge RAG

### Architecture

- **Builder** (`knowledge/builder.py`): Processes documents → TF-IDF index
- **RAG** (`knowledge/rag.py`): Retrieves relevant knowledge chunks
- **Index** (`knowledge/index.json`): Pre-built search index (654KB)
- **Capabilities** (`knowledge/capabilities.json`): System capability descriptions (28KB)
- **Docs** (`knowledge/docs/`): Source documentation files
- Text normalization includes Vietnamese accent removal (`remove_accents`)

### Integration

- Instantiated in `AgentCore.__init__()` as `self.rag = KnowledgeRAG()`
- Used to augment AI prompts with relevant domain knowledge
- Supports Vietnamese language queries

---

## 20. Admin Panel

### Visibility

- Only shown when `isUserAdmin === true` (computed from `userRole.value === 'admin'`)
- `userRole` stored in `localStorage('xianxia_role')`
- Tab has `adminOnly: true` → filtered from navigation for non-admins

### Admin Stats

| Metric | Source |
|---|---|
| Total Users | `COUNT(*) FROM users` |
| Active Users | `COUNT(*) FROM users WHERE is_active = 1` |
| Locked Users | `COUNT(*) FROM users WHERE is_active = 0` |

### Admin User Management

| Action | API | Protection |
|---|---|---|
| List all users | `GET /api/admin/users` | Admin only |
| Lock/Unlock user | `PUT /api/admin/users/{id}/toggle-active` | Admin only, cannot self-lock |
| Change role | `PUT /api/admin/users/{id}/role` | Admin only, cannot self-demote |

### Admin Filters (Frontend)

| Filter | Options |
|---|---|
| Search | Text search (name/email) |
| Role | All / Admin / User |
| Status | All / Active / Locked |

---

## 21. Theme & Design System

### Theme Identity

| Attribute | Value |
|---|---|
| Theme Name | Xianxia (Tu Tiên / Cultivation) |
| Primary Color | Jade/Teal (`#2B8A82` header fill, jade gradients) |
| Accent | Purple/Violet (`#7c3aed`, `#6d28d9`) for AI/spirit elements |
| Gold Accent | `#e8c874` for sigils/decorative |
| Background | Dark gradient (dark blues/purples) |
| Text | Light on dark |
| Font | UNKNOWN (embedded in CSS, likely system defaults) |

### CSS Architecture

- All CSS in `<style>` section of `App.vue` (lines ~5400-5882)
- No CSS modules, no CSS-in-JS, no utility framework
- Class naming: `.modal-backdrop`, `.modal-card`, `.btn-jade-sm`, `.btn-secondary`, `.input-group-xianxia`, `.form-grid`, etc.
- Xianxia-themed class names (e.g., `.spirit-chibi-body`, `.cloud-wing`, `.spirit-halo`)

### Theme Switching

- `currentTheme` ref stored in `localStorage('app_theme')`, defaults to `'xianxia'`
- UNKNOWN: Whether multiple theme CSS sets are actually implemented or if only Xianxia exists

### Decorative Elements

- Animated particles/backdrop (top section of main layout)
- SVG chibi spirit character for KhiLinh button
- Floating cloud wings, halo aura animations
- Yin-Yang forehead sigil on spirit
- Celestial blush marks

### Modal Pattern

All modals follow consistent structure:
```html
<div v-if="showXxxModal" class="modal-backdrop" @click.self="showXxxModal = false">
  <div class="modal-card">
    <div class="modal-header">
      <h3 class="modal-title">Title</h3>
      <button class="modal-close" @click="showXxxModal = false">✕</button>
    </div>
    <div class="modal-body">...</div>
    <div class="modal-footer">
      <button class="btn-secondary">Hủy</button>
      <button class="btn-jade-sm" :disabled="loading">Action</button>
    </div>
  </div>
</div>
```

---

## 22. Component Inventory

### Vue Components

| Component | File | Size | Purpose |
|---|---|---|---|
| `CankKhonApp` | `App.vue` | 5882 lines / 221KB | Main monolithic app |
| `ChartComponent` | `ChartComponents.vue` | ~300 lines / 9.6KB | Chart.js wrapper (doughnut/bar/line) |
| `KhiLinhAssistant` | `KhiLinhAssistant.vue` | 1705 lines / 53KB | Floating AI companion overlay |
| `VueDatePicker` | External (`@vuepic/vue-datepicker`) | — | Date range picker |

### Modals (defined inline in App.vue template)

| Modal | Toggle State | Purpose |
|---|---|---|
| Profile Modal | `showProfileModal` | View/edit profile, change soul lamp |
| Edit Wallet Modal | `showEditWalletModal` | Edit wallet name/type |
| Edit Category Modal | `showEditCatModal` | Edit category name/icon |
| Edit Budget Modal | `showEditBudgetModal` | Edit budget limit |
| Edit Recurring Modal | `showEditRecurringModal` | Edit recurring transaction |
| Edit Debt Modal | `showEditDebtModal` | Edit debt details |
| Edit Saving Goal Modal | `showEditGoalModal` | Edit saving goal |
| Deposit/Withdraw Modal | `showDepositModal` | Deposit or withdraw from saving goal |

### External Dependencies (Frontend)

| Package | Usage |
|---|---|
| `vue` (3.x) | Framework |
| `axios` | HTTP client |
| `chart.js` | Chart rendering |
| `@vuepic/vue-datepicker` | Date range picker |
| `date-fns/locale` (vi) | Vietnamese locale for date picker |

---

## 23. Capability Matrix

Legend: ✅ = Supported | ❌ = Not supported | 🤖 = Via AI agent only | ⚠️ = Partial

| Entity | Read | Create | Update | Delete | AI Tool | Voice | Notes |
|---|---|---|---|---|---|---|---|
| **User Auth** | ✅ | ✅ (register) | ✅ (profile, password, soul_lamp) | ❌ | 🤖 (profile read/update) | UNKNOWN | |
| **Wallet** | ✅ | ✅ | ✅ | ✅ | ✅ (all CRUD + transfer) | UNKNOWN | Delete cascading unclear |
| **Category** | ✅ | ✅ | ✅ | ✅ | ✅ (all CRUD) | UNKNOWN | System categories auto-created |
| **Transaction** | ✅ | ✅ | ✅ (API) | ✅ | ✅ (create/search/update/delete) | UNKNOWN | UI edit modal: UNKNOWN |
| **Budget** | ✅ | ✅ | ✅ | ✅ | ✅ (all CRUD) | UNKNOWN | Upsert behavior on create |
| **Recurring** | ✅ | ✅ | ✅ | ✅ | ✅ (all CRUD) | UNKNOWN | Auto-processing on list |
| **Debt** | ✅ | ✅ | ✅ | ✅ | ✅ (all CRUD + settle) | UNKNOWN | Settle ≠ balance change |
| **Saving Goal** | ✅ | ✅ | ✅ | ✅ | ✅ (CRUD + deposit/withdraw) | UNKNOWN | Deposit links to wallet |
| **OCR** | ✅ (logs) | ✅ (scan) | ❌ | ❌ | 🤖 (logs read) | UNKNOWN | Confirm to create txn |
| **Chat** | ✅ (history) | ✅ (implicit) | ❌ | ❌ | ✅ (core feature) | UNKNOWN | 30 history limit |
| **Reports** | ✅ | ❌ (generated) | ❌ | ❌ | ✅ (all reports) | UNKNOWN | Export CSV/Excel |
| **AI Tips** | ✅ | ❌ (generated) | ❌ | ❌ | ❌ (separate endpoint) | UNKNOWN | Gemini-powered |
| **Admin** | ✅ | ❌ | ✅ (role, status) | ❌ | ✅ (stats, list, toggle, role) | UNKNOWN | Admin-only |
| **Navigation** | ✅ | ❌ | ❌ | ❌ | ✅ (`navigate_to`) | UNKNOWN | Tab switching |

---

## 24. Known Gaps & UNKNOWN Items

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Transaction edit UI modal | UNKNOWN | API exists (`PUT /api/transactions/{id}`), AI tool exists, but no `showEditTransactionModal` found in App.vue template scan |
| 2 | Voice input | UNKNOWN | KhiLinh Assistant mentions voice in tooltip but implementation not verified in script section |
| 3 | Theme switching | UNKNOWN | `currentTheme` ref exists but only 'xianxia' theme CSS verified |
| 4 | Wallet delete cascade | UNKNOWN | Backend does `DELETE FROM wallets WHERE id = ?` — unclear if transactions are cascade-deleted or orphaned (SQLite FK ON DELETE not specified) |
| 5 | User account deletion | NOT IMPLEMENTED | No API endpoint for user self-deletion |
| 6 | Password strength validation | PARTIAL | Only min 4 chars enforced |
| 7 | Email verification | NOT IMPLEMENTED | Registration does not verify email |
| 8 | Session management | PARTIAL | JWT with 24h expiry, token_version for forced invalidation, but no refresh token mechanism |
| 9 | Dark/Light mode toggle | UNKNOWN | Only one embedded theme observed |
| 10 | Mobile responsive layout | UNKNOWN | No explicit responsive breakpoints found in initial CSS scan; scrollable nav suggests some mobile awareness |
| 11 | Offline support / PWA | NOT IMPLEMENTED | No service worker, no manifest.json observed |
| 12 | Data export from UI | PARTIAL | Report export exists but only accessible via Stats tab context |
| 13 | Notification system | PARTIAL | Toast only, no push/email notifications |
| 14 | Multi-currency | NOT IMPLEMENTED | VND hardcoded throughout; OCR returns currency field but not used |
| 15 | Attachment/image on transactions | PARTIAL | `image_url` column exists in DB but no upload UI observed |
| 16 | Chat message editing/deletion | NOT IMPLEMENTED | No API for modifying chat history |
| 17 | Bulk operations | NOT IMPLEMENTED | No bulk delete/edit for transactions or other entities |
| 18 | Search across all entities | NOT IMPLEMENTED | Search only within transactions; no global search |
| 19 | Categories reorder / custom sort | NOT IMPLEMENTED | Fixed order |
| 20 | Budget rollover | NOT IMPLEMENTED | Each month is independent |

---

> **End of UI_REDESIGN_SPEC.md**
> Generated from actual code inspection of:
> - `main.py` (2775 lines)
> - `frontend/src/App.vue` (5882 lines)
> - `ai_agent/core.py` (2398 lines)
> - `ai_agent/tools.py` (3097 lines)
> - `ai_agent/parser.py` (1125 lines)
> - `ai_agent/__init__.py` (28 lines)
> - `ai_agent/provider.py`
> - `ai_agent/knowledge/` (RAG system)
> - `frontend/src/components/KhiLinhAssistant.vue` (1705 lines)
> - `frontend/src/components/ChartComponents.vue`
