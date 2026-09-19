# UI_REDESIGN_DIRECTION.md — Càn Khôn Linh Thạch Các

> **Purpose**: A design-direction document converting current system capabilities into a concrete UI/UX architecture for the upcoming Stitch redesign.
> **Source of Truth**: `UI_REDESIGN_SPEC.md`
> **Constraint**: DO NOT design UI for unsupported backend features. DO NOT invent capabilities.

---

## A. PRODUCT DESIGN PRINCIPLES

1. **Fintech First, Fantasy Second**: Financial readability and usability ALWAYS have priority over decorative fantasy elements.
2. **Visual Balance**: 
   - 80% Modern Fintech / SaaS (Clean, structured, data-dense, highly legible)
   - 15% Xianxia Atmosphere (Color palette, terminology, subtle gradients)
   - 5% Fantasy Decoration (Icons, minimal particle effects, spirit companion)
3. **AI-Native Operating System**: The system is an intelligent companion, not just a static dashboard.
4. **Trust and Clarity**: All financial operations must be explicitly clear, reversible where possible, and securely confirmed.

---

## B. INFORMATION ARCHITECTURE

The application is structured as a single-page application (SPA) with a top-level tab-based navigation system and an omnipresent AI layer.

**Global Layer (Always Visible):**
- Top Navigation Bar (Logo, Auth State, Profile Access)
- Main Content Area (Tab Views)
- Floating **Small Khí Linh** (Action/Live System companion)
- Global Toasts (Success/Error feedback)

**Tab Hierarchy:**
1. Dashboard (Tổng Quan)
2. Transactions (Giao Dịch)
3. Debts (Sổ Nợ)
4. Saving Goals (Mục Tiêu)
5. Wallets (Túi Càn Khôn)
6. Categories (Danh Mục)
7. OCR (Linh Nhãn OCR)
8. Budgets (Hạn Mức)
9. Statistics (Thống Kê)
10. Khí Linh AI (Chat - Large Khí Linh)
11. Admin (Phân Quyền - Admin Only)

---

## C. NAVIGATION

### Desktop Navigation
- **Primary**: Horizontal top bar or left-aligned sidebar (SaaS standard). Since the current app uses a horizontal scrollable tab bar, we should adapt this to a responsive horizontal nav or a clean sidebar. 
- **User Actions**: Top-right corner for Profile, Soul Lamp, Logout.
- **AI Access**: Persistent floating button bottom-right for the Small Khí Linh.

### Mobile Navigation
- **Primary**: Bottom tab bar for the 4-5 most used features (Dashboard, Transactions, AI, Wallets, Stats).
- **Secondary**: A "More" menu or Hamburger menu for remaining tabs (OCR, Goals, Budgets, Categories, Debts, Admin).
- **AI Access**: Prominent FAB (Floating Action Button) or center item in the bottom tab bar for the Small Khí Linh.

---

## D. SCREEN INVENTORY

1. Authentication (Login, Register, Forgot Password, Reset Password)
2. Dashboard
3. Transactions List & Recurring
4. Debts Management
5. Saving Goals
6. Wallet Management
7. Category Management
8. OCR Scanner
9. Budgets
10. Statistics & Reports
11. Large Khí Linh (Dedicated AI Chat)
12. User Profile / Settings
13. Admin Panel

---

## E. SCREEN-BY-SCREEN UX DIRECTION

### 1. Dashboard (Tổng Quan)
- **Purpose**: At-a-glance financial health.
- **Main Info**: Total balance, monthly net savings, expense doughnut chart, trend bar chart, budget alerts.
- **Primary Actions**: Quick add transaction (if supported via AI).
- **Mobile Behavior**: Stacked cards, swipeable charts.

### 2. Transaction UX (Giao Dịch)
- **Purpose**: Detailed ledger and manual entry.
- **Main Info**: List of transactions, paginated (15/page), recurring section.
- **Primary Actions**: Create Income/Expense, Create Recurring.
- **Secondary Actions**: Filter, Edit (if applicable via modal), Delete.
- **Filters**: Date range, category, wallet, type, keyword.
- **Confirmation**: Delete requires confirmation.

### 3. Wallet UX (Túi Càn Khôn)
- **Purpose**: Manage funding sources.
- **Main Info**: Wallet cards with balances, types (cash, bank, e-wallet, crypto).
- **Primary Actions**: Create wallet, Transfer money.
- **Secondary Actions**: Edit, Delete.
- **Confirmation**: Delete is CRITICAL. Transfer is HIGH.

### 4. Budget UX (Hạn Mức)
- **Purpose**: Control spending.
- **Main Info**: Progress bars (spent vs limit) per category.
- **Primary Actions**: Create budget.
- **Secondary Actions**: Month selector, Edit, Delete.
- **Important States**: Warning (≥80%), Danger (≥100%).

### 5. Saving Goal UX (Mục Tiêu)
- **Purpose**: Track long-term savings.
- **Main Info**: Progress bars, remaining amounts, days left.
- **Primary Actions**: Create goal, Deposit, Withdraw.
- **Secondary Actions**: Edit, Delete.
- **API Constraints**: Deposit/Withdraw can optionally link to a wallet.

### 6. Debt UX (Sổ Nợ)
- **Purpose**: Track borrow/lend status.
- **Main Info**: Unsettled vs settled totals, list of debts.
- **Primary Actions**: Create debt, Mark Settled.
- **Filters**: Type (Borrow/Lend), Status.

### 7. Category UX (Danh Mục)
- **Purpose**: Organize transactions.
- **Main Info**: Income/Expense categories with icons.
- **Primary Actions**: Create category.

### 8. Statistics/Report UX (Thống Kê)
- **Purpose**: Deep financial analysis.
- **Main Info**: Trend charts, weekly breakdowns, month comparisons.
- **Primary Actions**: Change date range presets.
- **AI Capabilities**: Generate AI saving tips.

### 9. OCR UX (Linh Nhãn)
- **Purpose**: Automated invoice entry.
- **Main Info**: Image preview, extracted JSON data (store, total, items, date).
- **Primary Actions**: Upload (max 5MB), Confirm to create transaction.
- **Constraints**: No multi-currency (VND only).

### 10. Profile/Settings UX
- **Purpose**: Manage identity and security.
- **Main Info**: Đạo hiệu (name), Role, Soul Lamp hash status.
- **Primary Actions**: Update name, Change password/Soul Lamp.

### 11. Admin UX (Phân Quyền)
- **Purpose**: Manage users.
- **Main Info**: Total/active/locked user stats, user list.
- **Primary Actions**: Lock/Unlock, Change Role.
- **Confirmation**: Change role is CRITICAL.

---

## F. KHÍ LINH UX ARCHITECTURE

### Large Khí Linh (Dedicated Chat Tab)
- **Purpose**: Knowledge, explanation, advisory, read-only personal information.
- **UX**: Full-screen or large dedicated chat interface.
- **Layout**: Message bubbles, suggested questions, chat history (30 items limit).
- **Permissions**: **READ-ONLY**. Must not execute financial mutations. 

### Small Khí Linh (Floating / Action / Live System)
- **Purpose**: Action, financial mutation, voice interface, live system overlay.
- **UX**: Floating Chibi SVG button that expands into a "Live System Mode" dark overlay / dialog frame.
- **Permissions**: **ACTION**. The only AI interface allowed to execute WRITE/DELETE financial actions.
- **Interaction**: Can trigger tab navigation (`@switch-tab`), execute tools, and ask for confirmation.

---

## G. AI INTERACTION MODEL

### 1. AI States
- **IDLE**: Waiting for input. Chibi rests.
- **THINKING**: Processing NLP/Intent. Glowing aura.
- **PLANNING**: Resolving arguments/tools. Fast pulses.
- **CONFIRMING**: UI shows summary card. Waiting for user Yes/No.
- **EXECUTING**: Backend tool is running.
- **SUCCESS**: Operation completed. Positive animation / Toast.
- **ERROR**: Operation failed. Alert / Shake animation.

### 2. Confirmation UX
- A specialized UI card injected into the chat or overlay when state is `CONFIRMING`.
- Must display parsed parameters clearly (e.g., Amount, Wallet, Category).
- Clear "Xác Nhận" (Confirm) and "Hủy" (Cancel) buttons.
- Allows user to type modification instructions (e.g., "đổi thành 500k").

### 3. Voice/Wake-word UX
- (UNKNOWN if fully implemented backend, but UI should support microphone toggle state).
- Visual feedback for listening (audio waveforms or pulsing halo).

---

## H. DESIGN SYSTEM

### 1. Color Tokens
- **Primary (Jade/Teal)**: `#2B8A82` (Trust, Wealth, Cultivation Core)
- **Accent (Purple/Violet)**: `#7C3AED`, `#6D28D9` (AI, Spirit, Magic)
- **Gold**: `#E8C874` (Warnings, Premium accents, Sigils - use sparingly 5%)
- **Background**: Dark mode default. Deep blues/purples (`#0F172A`, `#1E1B4B`).
- **Surface**: Translucent panels (`rgba(255, 255, 255, 0.05)`) with backdrop blur.
- **Text**: High contrast light text (`#F8FAFC`, `#CBD5E1`).

### 2. Typography
- **Sans-serif**: Modern, highly legible (e.g., Inter, Roboto). No fantasy fonts for data.
- Numbers must use tabular figures (monospaced numbers) for perfect alignment in tables and lists.

### 3. Spacing, Radius, Shadows
- **Spacing**: 8pt grid system.
- **Radius**: Soft curves (8px for cards, 999px for pills/badges).
- **Shadows**: Soft, colored glows for active AI states; standard drop shadows for SaaS panels.

---

## I. RESPONSIVE SYSTEM

- **Breakpoints**: Mobile (<768px), Tablet (768px-1024px), Desktop (>1024px).
- **Tables**: On mobile, convert tables to stacked card lists.
- **AI Overlay**: On mobile, the Live System Mode becomes a full-screen bottom sheet.

---

## J. UI STATE SYSTEM

- **Loading**: Skeleton loaders for data. Subtle pulsing sigil for AI.
- **Empty**: Xianxia-themed empty state illustrations (e.g., an empty scroll or meditating chibi), but clear text on what to do next.
- **Error**: Red/Gold alert boxes. Non-blocking toasts for transient errors.
- **Success**: Jade green toasts.

---

## K. COMPONENT SYSTEM

- **Buttons**: `btn-jade` (Primary), `btn-secondary` (Ghost/Outline).
- **Forms**: Clean inputs, clear labels, focus states with subtle purple/jade glows.
- **Cards**: Glassmorphism or solid dark surface with 1px subtle border.
- **Tables**: Clean rows, hover states, clear alignment (numbers right-aligned).
- **Charts**: Chart.js defaults customized with theme colors.
- **Modals**: Centered dialogs with close (X) buttons, clear header, body, footer (Cancel/Action).
- **Toasts**: Top-right or bottom-center.

---

## L. BACKEND/CAPABILITY CONSTRAINTS

- **No Multi-Currency**: Do not design currency selectors. VND only.
- **No Global Search**: Do not design a global search bar. Search is limited to Transactions.
- **No Custom Categories Sorting**: Do not design drag-and-drop reordering.
- **No Budget Rollover**: Do not design rollover toggles.
- **No User Account Deletion**: Do not design a "Delete Account" button.
- **No File Attachments (UI)**: Backend supports `image_url` on transactions, but no upload API exists outside of OCR.

---

## M. STITCH DESIGN RULES

- **80% Modern Fintech**: The data, forms, and charts must look like a high-end financial app.
- **15% Xianxia**: Use the color palette, localized terms (Túi Càn Khôn, Linh Nhãn), and subtle gradients to set the mood.
- **5% Fantasy**: Keep the Small Khí Linh chibi SVG, particle backgrounds (restricted to headers/empty states), and occasional sigils.
- **Avoid**: Excessive neon, heavy gold borders, unreadable fantasy fonts, over-ornamentation that distracts from reading numbers.

---

## N. IMPLEMENTATION HANDOFF NOTES

1. Preserve the single-page tab mechanism (`activeTab`) unless migrating to Vue Router is explicitly requested later.
2. The `KhiLinhAssistant.vue` component is large (1705 lines) and holds significant logic. Ensure its state machine (`agentState`) maps directly to the UI states defined here.
3. Modals are currently hardcoded in `App.vue`. A redesign might extract these into separate components, but the UX flow (trigger → modal → confirm → toast) remains the same.

---

## DO NOT DESIGN

The following capabilities are unsupported or unknown in the current backend and **MUST NOT** be included in the UI redesign:

1. Global app-wide search bar.
2. Multi-currency support or currency toggle.
3. "Delete My Account" functionality.
4. Email verification flows.
5. Dark/Light mode toggle (Assume Dark/Xianxia mode only).
6. Push notification settings.
7. Budget rollover configurations.
8. Drag-and-drop category reordering.
9. Manual file attachments to transactions (aside from the OCR scanning flow).
10. Editing or deleting chat history messages.
11. Bulk edit / bulk delete actions for transactions or entities.
12. Offline mode / PWA install prompts.

---
> **End of UI_REDESIGN_DIRECTION.md**
