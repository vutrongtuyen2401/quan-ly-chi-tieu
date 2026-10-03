<template>
  <!-- ═══════ TAB 1: DASHBOARD ═══════ -->
  <section class="tab-panel">
    <h2 class="section-title">📊 Đạo Đường Tổng Quan</h2>

    <!-- Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card jade">
        <div class="metric-icon">💰</div>
        <div class="metric-info">
          <span class="metric-label">Thu Nhập Linh Mạch</span>
          <span class="metric-value">{{ formatVND(summary.total_income) }}</span>
        </div>
      </div>
      <div class="metric-card crimson">
        <div class="metric-icon">🔥</div>
        <div class="metric-info">
          <span class="metric-label">Tiêu Hao Linh Thạch</span>
          <span class="metric-value">{{ formatVND(summary.total_expense) }}</span>
        </div>
      </div>
      <div class="metric-card gold">
        <div class="metric-icon">⚖️</div>
        <div class="metric-info">
          <span class="metric-label">Tiết Kiệm Thuần</span>
          <span class="metric-value" :class="summary.net_savings >= 0 ? 'positive' : 'negative'">
            {{ formatVND(summary.net_savings) }}
          </span>
        </div>
      </div>
      <div class="metric-card purple">
        <div class="metric-icon">👛</div>
        <div class="metric-info">
          <span class="metric-label">Tổng Túi Càn Khôn</span>
          <span class="metric-value">{{ formatVND(summary.total_balance) }}</span>
        </div>
      </div>
    </div>

    <!-- Budget Alerts -->
    <div v-if="budgetAlerts.length" class="alerts-section">
      <h3 class="sub-title">⚠️ Cảnh Báo Tâm Ma Chi Tiêu</h3>
      <div v-for="alert in budgetAlerts" :key="alert.category"
           :class="['alert-card', alert.level === 'DANGER' ? 'danger' : 'warning']">
        <span class="alert-icon">{{ alert.icon }}</span>
        <span class="alert-msg">{{ alert.message }}</span>
        <span class="alert-pct">{{ alert.percent }}%</span>
      </div>
    </div>

    <!-- Dashboard Charts Row -->
    <div class="dashboard-charts-row">
      <div class="chart-card" v-if="summary.expense_by_category && summary.expense_by_category.length">
        <ChartComponent
          type="doughnut"
          :chart-data="dashboardDoughnutData"
          title="🥧 Phân Bổ Chi Tiêu Tháng Này"
        />
      </div>
      <div class="chart-card" v-if="hasTrendData">
        <ChartComponent
          type="bar"
          :chart-data="dashboardBarData"
          :title="`📊 Thu/Chi ${trendData.months || 6} Tháng Gần Đây`"
        />
      </div>
    </div>

    <!-- AI Saving Tips -->
    <div class="saving-tips-section">
      <div class="saving-tips-header">
        <h3 class="sub-title">🔮 Khai Thị Tiết Kiệm AI</h3>
        <button class="btn-jade-sm" @click="loadSavingTips" :disabled="loadingTips">
          {{ loadingTips ? '🔮 Đang cầu tiên...' : '✨ Nhận Khai Thị' }}
        </button>
      </div>
      <div v-if="savingTips" class="saving-tips-card">
        <div class="tips-meta">
          <span>📅 Tháng: {{ savingTips.month_year }}</span>
          <span>📈 Tỷ lệ tiết kiệm: <strong :class="savingTips.savings_rate >= 20 ? 'positive' : 'negative'">{{ savingTips.savings_rate }}%</strong></span>
        </div>
        <div class="tips-content" v-html="formatChatText(savingTips.tips)"></div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <h3 class="sub-title">📜 Giao Dịch Linh Thạch Gần Đây</h3>
    <div class="table-scroll">
      <table class="xianxia-table">
        <thead>
          <tr>
            <th>Ngày</th>
            <th>Danh Mục</th>
            <th>Ghi Chú</th>
            <th>Ví</th>
            <th>Số Tiền</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="txn in transactions.slice(0, 10)" :key="txn.id">
            <td>{{ txn.transaction_date }}</td>
            <td><span class="cat-badge">{{ txn.category_icon }} {{ txn.category_name }}</span></td>
            <td>{{ txn.note || '—' }}</td>
            <td>{{ txn.wallet_name }}</td>
            <td :class="txn.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
              {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
            </td>
          </tr>
          <tr v-if="!transactions.length">
            <td colspan="5" class="empty-row">Chưa có giao dịch nào...</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Expense by Category (bar breakdown) -->
    <div v-if="summary.expense_by_category && summary.expense_by_category.length" class="category-breakdown">
      <h3 class="sub-title">📈 Phân Bổ Tiêu Hao Theo Danh Mục</h3>
      <div class="cat-bars">
        <div v-for="cat in summary.expense_by_category" :key="cat.category_name" class="cat-bar-row">
          <span class="cat-bar-label">{{ cat.icon }} {{ cat.category_name }}</span>
          <div class="cat-bar-track">
            <div class="cat-bar-fill"
                 :style="{ width: Math.min(100, (cat.total / maxCategoryExpense * 100)) + '%' }"></div>
          </div>
          <span class="cat-bar-value">{{ formatVND(cat.total) }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'
import ChartComponent from '../components/ChartComponents.vue'

export default {
  name: 'DashboardView',
  components: { ChartComponent },
  setup() {
    return useAppBindings()
  },
}
</script>
