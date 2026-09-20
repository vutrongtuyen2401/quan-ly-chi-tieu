<template>
  <div class="dashboard-realm">
    <!-- Subtle Ambient Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ SECTION A: WELCOME AURA HEADER ═══ -->
    <section class="welcome-card" aria-label="Chào mừng Đạo hữu">
      <div class="welcome-info">
        <div class="welcome-title-row">
          <h1 class="welcome-title">Chào Đạo hữu {{ userName }}</h1>
          <span class="realm-status-pill">
            <span class="status-pulse-dot"></span>
            {{ userRole === 'admin' ? 'Hộ Pháp Trưởng Lão (Admin)' : 'Đệ Tử Bản Môn • Trúc Cơ Sơ Kỳ' }}
          </span>
        </div>
        <p class="welcome-subtitle">
          Tổng quan linh mạch và tài chính {{ currentMonthYear }}. Khí vận hanh thông, tài mạch sung túc.
        </p>
      </div>

      <div class="welcome-actions">
        <div class="date-chip">
          <span class="material-symbols-outlined icon-gold">calendar_month</span>
          <span>{{ currentMonthYear }}</span>
        </div>
        <button
          type="button"
          class="btn-record-action"
          @click="$emit('switch-tab', 'transactions')"
          title="Ghi chép giao dịch mới"
        >
          <span class="material-symbols-outlined">add_circle</span>
          <span>Khắc Ghi Biến Động</span>
        </button>
      </div>
    </section>

    <!-- ═══ SECTION B: TOP KPI METRIC GRID (4 CARDS) ═══ -->
    <section class="metric-grid" aria-label="Chỉ số tài chính tổng quan">
      <!-- Card 1: Tổng Linh Thạch / Số Dư -->
      <div class="kpi-card kpi-balance">
        <div class="kpi-header">
          <span class="kpi-label">Tổng Linh Thạch / Số Dư</span>
          <div class="kpi-icon-wrap icon-jade">
            <span class="material-symbols-outlined">account_balance_wallet</span>
          </div>
        </div>
        <div class="kpi-value tabular-num">
          {{ formatVND(summary.total_balance) }}
        </div>
        <div class="kpi-footer text-jade">
          <span class="material-symbols-outlined icon-sm">shield</span>
          <span>Toàn bộ ngân khố khả dụng</span>
        </div>
      </div>

      <!-- Card 2: Thu Nhập Linh Mạch -->
      <div class="kpi-card kpi-income">
        <div class="kpi-header">
          <span class="kpi-label">Linh Tuyền Thu Vào</span>
          <div class="kpi-icon-wrap icon-jade">
            <span class="material-symbols-outlined">arrow_downward</span>
          </div>
        </div>
        <div class="kpi-value tabular-num text-income">
          {{ formatVND(summary.total_income) }}
        </div>
        <div class="kpi-footer text-muted">
          <span class="material-symbols-outlined icon-sm text-jade">verified</span>
          <span>Tổng thu nạp chu kỳ</span>
        </div>
      </div>

      <!-- Card 3: Tiêu Hao Pháp Bảo -->
      <div class="kpi-card kpi-expense">
        <div class="kpi-header">
          <span class="kpi-label">Tiêu Hao Pháp Bảo</span>
          <div class="kpi-icon-wrap icon-crimson">
            <span class="material-symbols-outlined">arrow_upward</span>
          </div>
        </div>
        <div class="kpi-value tabular-num text-expense">
          {{ formatVND(summary.total_expense) }}
        </div>
        <div class="kpi-footer text-muted">
          <span class="dot-indicator dot-indigo"></span>
          <span>Tổng tiêu phí chu kỳ</span>
        </div>
      </div>

      <!-- Card 4: Tiết Kiệm Thuần (Tích Tụ Chân Nguyên) -->
      <div class="kpi-card kpi-savings">
        <div class="kpi-header">
          <span class="kpi-label">Tích Tụ Chân Nguyên</span>
          <div class="kpi-icon-wrap icon-gold">
            <span class="material-symbols-outlined">savings</span>
          </div>
        </div>
        <div
          class="kpi-value tabular-num"
          :class="summary.net_savings >= 0 ? 'text-gold' : 'text-expense'"
        >
          {{ (summary.net_savings > 0 ? '+' : '') + formatVND(summary.net_savings) }}
        </div>
        <div class="kpi-footer" :class="summary.net_savings >= 0 ? 'text-gold' : 'text-expense'">
          <span class="material-symbols-outlined icon-sm">
            {{ summary.net_savings >= 0 ? 'stars' : 'warning' }}
          </span>
          <span>{{ summary.net_savings >= 0 ? 'Thặng dư tích cực' : 'Thâm hụt cần chú ý' }}</span>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION C: VISUAL ANALYTICS BENTO (8 COLS / 4 COLS) ═══ -->
    <section class="analytics-grid" aria-label="Biểu đồ phân tích linh mạch">
      <!-- 8-Column: Monthly Cashflow Bar Chart -->
      <div class="analytics-card col-span-8">
        <div class="card-title-row">
          <div>
            <h2 class="card-title">Xu Hướng Thu &amp; Chi 6 Tháng Gần Nhất</h2>
            <p class="card-subtitle">Linh mạch thu nạp so với tiêu hao linh khí các chu kỳ qua</p>
          </div>
          <div class="chart-legend-custom">
            <div class="legend-item">
              <span class="legend-box bg-jade"></span>
              <span>Thu Nhập</span>
            </div>
            <div class="legend-item">
              <span class="legend-box bg-indigo"></span>
              <span>Chi Tiêu</span>
            </div>
          </div>
        </div>

        <div class="chart-inner-wrap" v-if="trendData.trend && trendData.trend.length">
          <ChartComponent
            type="bar"
            :chart-data="dashboardBarData"
            title=""
          />
        </div>
        <div v-else class="empty-chart-state">
          <span class="material-symbols-outlined empty-icon">analytics</span>
          <p>Chưa có dữ liệu xu hướng thu/chi 6 tháng gần nhất...</p>
        </div>

        <div class="card-bottom-info">
          <span class="footnote-text">* Quy chuẩn: 1 Linh Ngân = 1.000 VNĐ</span>
          <button
            type="button"
            class="btn-text-action"
            @click="$emit('switch-tab', 'statistics')"
          >
            <span>Xem Thống Kê Toàn Diện</span>
            <span class="material-symbols-outlined icon-xs">arrow_forward</span>
          </button>
        </div>
      </div>

      <!-- 4-Column: Category Expense Doughnut Chart -->
      <div class="analytics-card col-span-4">
        <div class="card-title-row">
          <div>
            <h2 class="card-title">Phân Bổ Chi Tiêu</h2>
            <p class="card-subtitle">Danh mục tiêu hao trong tháng này</p>
          </div>
          <span class="material-symbols-outlined icon-muted">pie_chart</span>
        </div>

        <div class="chart-inner-wrap doughnut-wrap" v-if="summary.expense_by_category && summary.expense_by_category.length">
          <ChartComponent
            type="doughnut"
            :chart-data="dashboardDoughnutData"
            :show-legend="false"
            title=""
          />
        </div>
        <div v-else class="empty-chart-state">
          <span class="material-symbols-outlined empty-icon">pie_chart</span>
          <p>Chưa có khoản chi nào trong tháng này...</p>
        </div>

        <!-- Expense by Category Mini Progress Breakdown -->
        <div
          v-if="summary.expense_by_category && summary.expense_by_category.length"
          class="category-mini-list"
        >
          <div
            v-for="(cat, idx) in summary.expense_by_category"
            :key="cat.category_name || idx"
            class="category-spending-row"
          >
            <div class="cat-identity-col">
              <span class="cat-color-dot" :style="{ backgroundColor: getCategoryColor(idx) }"></span>
              <span class="cat-icon-emoji">{{ cat.icon || '🏷️' }}</span>
            </div>
            <div class="cat-name-col" :title="cat.category_name">
              <span class="cat-name-text">{{ cat.category_name }}</span>
              <div class="progress-track">
                <div
                  class="progress-fill"
                  :style="{
                    width: getCategoryPercentage(cat.total) + '%',
                    backgroundColor: getCategoryColor(idx)
                  }"
                ></div>
              </div>
            </div>
            <div class="cat-value-col">
              <span class="cat-amount tabular-num">{{ formatVND(cat.total) }}</span>
              <span class="cat-percentage tabular-num">{{ getCategoryPercentage(cat.total) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION D: OPERATIONAL MODULES (5 COLS / 7 COLS) ═══ -->
    <section class="operational-grid" aria-label="Cảnh báo và giao dịch gần đây">
      <!-- Left (5 Cols): Spending Alerts & AI Savings Tips -->
      <div class="operational-card col-span-5 flex-col-cards">
        <!-- Budget Alerts (Cảnh Báo Hạn Mức Tâm Ma) -->
        <div class="alerts-subcard">
          <div class="card-title-row mb-space-sm">
            <div class="title-with-icon">
              <span class="material-symbols-outlined text-gold">shield_with_heart</span>
              <h2 class="card-title">Cảnh Báo Tâm Ma Hạn Mức</h2>
            </div>
            <span class="badge-count">{{ budgetAlerts.length }} Định Ngạch</span>
          </div>
          <p class="card-subtitle mb-space-md">
            Theo dõi các định ngạch chi tiêu để tránh hao tổn chân nguyên tài chính.
          </p>

          <div class="alerts-list" v-if="budgetAlerts.length">
            <div
              v-for="alert in budgetAlerts"
              :key="alert.category"
              class="stitch-alert-card"
              :class="alert.level === 'DANGER' ? 'alert-danger' : 'alert-warning'"
            >
              <div class="alert-top">
                <div class="alert-label-group">
                  <span class="alert-cat-name">{{ alert.icon }} {{ alert.category }}</span>
                  <p class="alert-desc">{{ alert.message }}</p>
                </div>
                <span
                  class="alert-pct-badge"
                  :class="alert.level === 'DANGER' ? 'badge-danger' : 'badge-warning'"
                >
                  <span class="material-symbols-outlined icon-xs">
                    {{ alert.level === 'DANGER' ? 'warning' : 'priority_high' }}
                  </span>
                  {{ alert.percent }}%
                </span>
              </div>
              <div class="alert-track">
                <div
                  class="alert-bar"
                  :class="alert.level === 'DANGER' ? 'bar-danger' : 'bar-warning'"
                  :style="{ width: Math.min(100, alert.percent) + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <div v-else class="safe-alert-card">
            <span class="material-symbols-outlined icon-jade">check_circle</span>
            <div class="safe-text">
              <strong>Tâm cảnh an định</strong>
              <p>Mọi hạn mức chi tiêu trong chu kỳ đều trong giới hạn an toàn.</p>
            </div>
          </div>

          <button
            type="button"
            class="btn-outline-action mt-space-md"
            @click="$emit('switch-tab', 'budgets')"
          >
            <span>Điều chỉnh giới luật hạn mức</span>
            <span class="material-symbols-outlined icon-xs">tune</span>
          </button>
        </div>

        <!-- AI Saving Tips (Khai Thị Tiết Kiệm AI) -->
        <div class="tips-subcard">
          <div class="card-title-row mb-space-sm">
            <div class="title-with-icon">
              <span class="material-symbols-outlined text-indigo">auto_awesome</span>
              <h3 class="card-title">Khai Thị Tiết Kiệm AI</h3>
            </div>
            <button
              type="button"
              class="btn-talisman-sm"
              @click="$emit('load-saving-tips')"
              :disabled="loadingTips"
            >
              <span class="material-symbols-outlined icon-xs">
                {{ loadingTips ? 'hourglass_top' : 'psychology' }}
              </span>
              <span>{{ loadingTips ? 'Đang cầu tiên...' : 'Nhận Khai Thị' }}</span>
            </button>
          </div>

          <div v-if="savingTips" class="saving-tips-box">
            <div class="tips-header-meta">
              <span>📅 Tháng: {{ savingTips.month_year }}</span>
              <span class="rate-badge">
                Tỷ lệ tích lũy:
                <strong :class="savingTips.savings_rate >= 20 ? 'text-jade' : 'text-expense'">
                  {{ savingTips.savings_rate }}%
                </strong>
              </span>
            </div>
            <div class="tips-rendered-body" v-html="formatChatText(savingTips.tips)"></div>
          </div>
          <div v-else class="tips-placeholder">
            <p>Bấm "Nhận Khai Thị" để Khí Linh phân tích dòng tiền và mách nước tiết kiệm.</p>
          </div>
        </div>
      </div>

      <!-- Right (7 Cols): Recent Transactions Ledger -->
      <div class="operational-card col-span-7">
        <div class="card-title-row mb-space-sm">
          <div>
            <h2 class="card-title">Giao Dịch Gần Đây</h2>
            <p class="card-subtitle">Các biến động linh thạch mới nhất trong chu kỳ</p>
          </div>
          <button
            type="button"
            class="btn-text-action"
            @click="$emit('switch-tab', 'transactions')"
          >
            <span>Xem toàn bộ sổ cái</span>
            <span class="material-symbols-outlined icon-xs">arrow_forward</span>
          </button>
        </div>

        <!-- Transaction Ledger List -->
        <div class="recent-txn-list" v-if="recentTransactions.length">
          <div
            v-for="txn in recentTransactions"
            :key="txn.id"
            class="recent-txn-row"
          >
            <div class="txn-left">
              <div
                class="txn-icon-container"
                :class="txn.transaction_type === 'INCOME' ? 'icon-bg-income' : 'icon-bg-expense'"
              >
                <span class="material-symbols-outlined">
                  {{ txn.transaction_type === 'INCOME' ? 'payments' : 'shopping_bag' }}
                </span>
              </div>
              <div class="txn-meta-group">
                <span class="txn-title truncate" :title="txn.note || txn.category_name">
                  {{ txn.note || txn.category_name }}
                </span>
                <div class="txn-submeta">
                  <span class="cat-pill">
                    {{ txn.category_icon || '📦' }} {{ txn.category_name }}
                  </span>
                  <span class="sep-dot">•</span>
                  <span class="wallet-name">{{ txn.wallet_name }}</span>
                  <span class="sep-dot">•</span>
                  <span class="date-str">{{ txn.transaction_date }}</span>
                </div>
              </div>
            </div>

            <div class="txn-right">
              <span
                class="txn-amount-display tabular-num"
                :class="txn.transaction_type === 'INCOME' ? 'text-income' : 'text-on-surface'"
              >
                {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
              </span>
            </div>
          </div>
        </div>

        <div v-else class="empty-txn-state">
          <span class="material-symbols-outlined empty-icon">receipt_long</span>
          <p>Chưa có giao dịch nào được ghi chép trong chu kỳ này...</p>
        </div>

        <!-- Quick Summary Bar at Bottom -->
        <div class="ledger-bottom-bar">
          <span class="status-label">Trạng thái đồng bộ linh thạch:</span>
          <div class="sync-status text-jade">
            <span class="status-pulse-dot dot-sm"></span>
            <span>Viên Mãn • Sổ cái toàn vẹn</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ChartComponent from '../ChartComponents.vue'

const props = defineProps({
  summary: {
    type: Object,
    default: () => ({
      total_income: 0,
      total_expense: 0,
      net_savings: 0,
      total_balance: 0,
      expense_by_category: []
    })
  },
  budgetAlerts: {
    type: Array,
    default: () => []
  },
  trendData: {
    type: Object,
    default: () => ({ trend: [] })
  },
  dashboardDoughnutData: {
    type: Object,
    default: () => ({ labels: [], values: [] })
  },
  dashboardBarData: {
    type: Object,
    default: () => ({ labels: [], income: [], expense: [] })
  },
  savingTips: {
    type: Object,
    default: null
  },
  loadingTips: {
    type: Boolean,
    default: false
  },
  transactions: {
    type: Array,
    default: () => []
  },
  userName: {
    type: String,
    default: 'Ký Chủ'
  },
  userRole: {
    type: String,
    default: 'user'
  },
  maxCategoryExpense: {
    type: Number,
    default: 1
  },
  formatVND: {
    type: Function,
    required: true
  },
  formatChatText: {
    type: Function,
    default: (text) => text || ''
  }
})

defineEmits(['load-saving-tips', 'switch-tab'])

const currentMonthYear = computed(() => {
  const now = new Date()
  return `Tháng ${now.getMonth() + 1}, ${now.getFullYear()}`
})

const recentTransactions = computed(() => {
  return (props.transactions || []).slice(0, 8)
})

// Xianxia color palette synchronized with ChartComponents.vue
const XIANXIA_COLORS = [
  '#4fa8a0', '#e8c874', '#8b5cf6', '#ef4444', '#3b82f6',
  '#f97316', '#10b981', '#ec4899', '#f59e0b', '#06b6d4',
  '#a855f7', '#14b8a6', '#f43f5e', '#6366f1', '#fb923c',
]

const getCategoryColor = (idx) => {
  return XIANXIA_COLORS[idx % XIANXIA_COLORS.length]
}

const totalCategoryExpense = computed(() => {
  return (props.summary?.expense_by_category || []).reduce((acc, c) => acc + (c.total || 0), 0)
})

const getCategoryPercentage = (val) => {
  const total = totalCategoryExpense.value || props.summary?.total_expense || 0
  if (total <= 0) return 0
  return Math.min(100, Math.round(((val || 0) / total) * 100))
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC — DASHBOARD VIEW (STITCH CELESTIAL MODERN)
   ═══════════════════════════════════════════════════════════════════════════ */

.dashboard-realm {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl, 32px);
  width: 100%;
}

/* ─── AMBIENT GLOW ORBS ─── */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.orb-primary {
  top: -60px;
  right: 5%;
  width: 380px;
  height: 380px;
  background: rgba(125, 214, 204, 0.08);
}
.orb-secondary {
  top: 35%;
  left: -80px;
  width: 320px;
  height: 320px;
  background: rgba(196, 193, 251, 0.06);
}

/* ─── SECTION A: WELCOME CARD ─── */
.welcome-card {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-md, 16px);
  padding: var(--space-lg, 24px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  border-radius: var(--radius-xl, 16px);
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.welcome-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 4px);
}

.welcome-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 8px);
  flex-wrap: wrap;
}

.welcome-title {
  font-family: var(--font-body);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
  letter-spacing: -0.01em;
}

.realm-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 9999px;
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-primary, #7dd6cc);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.status-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 8px var(--color-primary, #7dd6cc);
  animation: pulseDot 2s infinite ease-in-out;
}
.dot-sm { width: 5px; height: 5px; }

@keyframes pulseDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.welcome-subtitle {
  font-size: 13.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

.welcome-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 8px);
  flex-wrap: wrap;
}

.date-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container, #171f33);
  color: var(--color-on-surface, #dae2fd);
  font-size: 13px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-record-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  font-size: 13px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(125, 214, 204, 0.25);
  transition: all 0.2s ease;
}
.btn-record-action:hover {
  background: var(--color-primary-container, #449f96);
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(125, 214, 204, 0.35);
}

/* ─── SECTION B: KPI METRICS GRID (4 CARDS) ─── */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--gutter, 24px);
  z-index: 1;
}

.kpi-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-lg, 24px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  border-radius: var(--radius-xl, 16px);
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.25s ease;
}
.kpi-card:hover {
  border-color: rgba(125, 214, 204, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-sm, 8px);
}

.kpi-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.kpi-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-DEFAULT, 8px);
}
.icon-jade {
  background: rgba(125, 214, 204, 0.12);
  color: var(--color-primary, #7dd6cc);
}
.icon-crimson {
  background: rgba(255, 180, 171, 0.12);
  color: var(--color-error, #ffb4ab);
}
.icon-gold {
  background: rgba(227, 195, 112, 0.12);
  color: var(--color-tertiary, #e3c370);
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-xs, 4px);
  word-break: break-word;
}
.text-income { color: var(--color-primary, #7dd6cc); }
.text-expense { color: var(--color-error, #ffb4ab); }
.text-gold { color: var(--color-tertiary, #e3c370); }
.text-jade { color: var(--color-primary, #7dd6cc); }
.text-muted { color: var(--color-on-surface-variant, #bdc9c6); }

.kpi-footer {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
}

.dot-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}
.dot-indigo { background: var(--color-secondary, #c4c1fb); }

/* ─── SECTION C: VISUAL ANALYTICS (8 COLS / 4 COLS) ─── */
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--gutter, 24px);
  z-index: 1;
}

.col-span-8 { grid-column: span 8; }
.col-span-4 { grid-column: span 4; }
.col-span-5 { grid-column: span 5; }
.col-span-7 { grid-column: span 7; }

.analytics-card {
  display: flex;
  flex-direction: column;
  padding: var(--space-lg, 24px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  border-radius: var(--radius-xl, 16px);
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  min-height: 440px;
}

.card-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-sm, 8px);
  margin-bottom: var(--space-md, 16px);
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.card-subtitle {
  font-size: 12.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 2px 0 0 0;
}

.chart-legend-custom {
  display: flex;
  align-items: center;
  gap: var(--space-md, 16px);
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-box {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
.bg-jade { background: var(--color-primary, #7dd6cc); }
.bg-indigo { background: var(--color-secondary, #c4c1fb); }

.chart-inner-wrap {
  width: 100%;
  height: 260px;
  position: relative;
}

.doughnut-wrap {
  height: 180px;
  min-height: 180px;
  max-height: 180px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chart-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 180px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 13px;
  text-align: center;
}
.empty-icon {
  font-size: 36px;
  opacity: 0.4;
}

.card-bottom-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: var(--space-sm, 8px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.btn-text-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: var(--color-primary, #7dd6cc);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
}
.btn-text-action:hover {
  color: var(--color-primary-fixed, #9af2e8);
  text-decoration: underline;
}

/* Category Mini Breakdown in Doughnut Card */
.category-mini-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: var(--space-sm, 12px);
  padding-top: var(--space-sm, 12px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

.category-mini-list::-webkit-scrollbar {
  width: 4px;
}
.category-mini-list::-webkit-scrollbar-track {
  background: transparent;
}
.category-mini-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}
.category-mini-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary, #7dd6cc);
}

.category-spending-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-height: 32px;
  padding: 2px 0;
}

.cat-identity-col {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.cat-color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cat-icon-emoji {
  font-size: 14px;
  line-height: 1;
  flex-shrink: 0;
}

.cat-name-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  overflow: hidden;
}

.cat-name-text {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--color-on-surface, #dae2fd);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.progress-track {
  width: 100%;
  height: 4px;
  border-radius: 9999px;
  background: var(--color-surface-container-highest, #2d3449);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.cat-value-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  flex-shrink: 0;
  text-align: right;
  white-space: nowrap;
}

.cat-amount {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  white-space: nowrap;
  line-height: 1.3;
}

.cat-percentage {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  white-space: nowrap;
  line-height: 1.2;
}

/* ─── SECTION D: OPERATIONAL MODULES (5 COLS / 7 COLS) ─── */
.operational-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--gutter, 24px);
  z-index: 1;
}

.operational-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-lg, 24px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  border-radius: var(--radius-xl, 16px);
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.flex-col-cards {
  gap: var(--space-lg, 24px);
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge-count {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  background: var(--color-surface-container-high, #222a3d);
  padding: 2px 8px;
  border-radius: 9999px;
}

/* Alerts List */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stitch-alert-card {
  padding: 12px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  border: 1px solid transparent;
}
.alert-danger {
  background: rgba(147, 0, 10, 0.25);
  border-color: rgba(255, 180, 171, 0.25);
}
.alert-warning {
  background: rgba(198, 168, 88, 0.15);
  border-color: rgba(227, 195, 112, 0.25);
}

.alert-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.alert-cat-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.alert-desc {
  font-size: 11.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 2px 0 0 0;
}

.alert-pct-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 7px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 700;
}
.badge-danger {
  background: var(--color-error, #ffb4ab);
  color: var(--color-on-error, #690005);
}
.badge-warning {
  background: var(--color-tertiary-container, #c6a858);
  color: var(--color-on-tertiary-container, #4f3d00);
}

.alert-track {
  width: 100%;
  height: 4px;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.3);
  overflow: hidden;
}
.alert-bar {
  height: 100%;
  border-radius: 9999px;
}
.bar-danger { background: var(--color-error, #ffb4ab); }
.bar-warning { background: var(--color-tertiary, #e3c370); }

.safe-alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: rgba(125, 214, 204, 0.08);
  border: 1px solid rgba(125, 214, 204, 0.2);
}
.safe-text strong {
  display: block;
  font-size: 13px;
  color: var(--color-primary, #7dd6cc);
}
.safe-text p {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 2px 0 0 0;
}

.btn-outline-action {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-high, #222a3d);
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-outline-action:hover {
  background: var(--color-surface-bright, #31394d);
  border-color: var(--color-primary, #7dd6cc);
}

/* AI Saving Tips Subcard */
.tips-subcard {
  padding-top: var(--space-md, 16px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.btn-talisman-sm {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: rgba(196, 193, 251, 0.15);
  color: var(--color-secondary, #c4c1fb);
  border: 1px solid rgba(196, 193, 251, 0.3);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-talisman-sm:hover:not(:disabled) {
  background: var(--color-secondary, #c4c1fb);
  color: var(--color-on-secondary, #2d2a5b);
}
.btn-talisman-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.saving-tips-box {
  padding: 12px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: var(--radius-DEFAULT, 8px);
  border: 1px solid rgba(227, 195, 112, 0.2);
  margin-top: 8px;
}

.tips-header-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
}

.tips-rendered-body {
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--color-on-surface, #dae2fd);
}

.tips-placeholder {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-style: italic;
  margin-top: 8px;
}

/* Recent Transactions Ledger List */
.recent-txn-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: var(--space-sm, 8px) 0;
}

.recent-txn-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm, 8px);
  padding: 10px 12px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: transparent;
  transition: background 0.2s ease;
}
.recent-txn-row:hover {
  background: var(--color-surface-container, #171f33);
}

.txn-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.txn-icon-container {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-DEFAULT, 8px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-bg-income {
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
}
.icon-bg-expense {
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-secondary, #c4c1fb);
}

.txn-meta-group {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.txn-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.txn-submeta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: 2px;
  flex-wrap: wrap;
}

.cat-pill {
  color: var(--color-on-surface, #dae2fd);
}
.sep-dot {
  opacity: 0.4;
}
.wallet-name {
  color: var(--color-secondary, #c4c1fb);
}

.txn-right {
  text-align: right;
  flex-shrink: 0;
}

.txn-amount-display {
  font-size: 14px;
  font-weight: 600;
}

.empty-txn-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 16px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 13px;
  text-align: center;
}

.ledger-bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-high, #222a3d);
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: var(--space-md, 16px);
}

.sync-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 500;
}

/* ─── UTILITY ICONS & SIZES ─── */
.icon-sm { font-size: 16px; }
.icon-xs { font-size: 14px; }
.icon-muted {
  font-size: 20px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

/* ─── RESPONSIVE BREAKPOINTS ─── */
@media (max-width: 1200px) {
  .metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .col-span-8, .col-span-4,
  .col-span-5, .col-span-7 {
    grid-column: span 12;
  }
}

@media (max-width: 768px) {
  .dashboard-realm {
    gap: var(--space-lg, 24px);
  }
  .metric-grid {
    grid-template-columns: 1fr;
    gap: var(--gutter-mobile, 16px);
  }
  .welcome-card {
    padding: var(--space-md, 16px);
  }
  .welcome-title {
    font-size: 20px;
  }
  .welcome-actions {
    width: 100%;
    justify-content: space-between;
  }
  .analytics-card, .operational-card {
    padding: var(--space-md, 16px);
  }
  .kpi-value {
    font-size: 20px;
  }
}
</style>
