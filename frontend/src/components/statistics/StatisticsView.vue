<template>
  <div class="statistics-realm">
    <!-- Spatial Atmosphere Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ TOP HEADER & FILTER CONTROLS ═══ -->
    <section class="stats-header-card">
      <div class="header-content-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">BÁT QUÁI TÀI PHỔ • CHU KỲ GIÁP THÌN</span>
        </div>
        <h1 class="page-title">Thống Kê Chi Tiêu &amp; Dự Báo Tu Luyện</h1>
        <p class="page-subtitle">
          Báo cáo xu hướng nhiều tháng, chi tiết theo tuần, so sánh chu kỳ và lời khuyên tiết kiệm từ Khí Linh.
        </p>
      </div>

      <!-- Filter Controls & Export Actions -->
      <div class="header-controls-group">
        <!-- Quick Preset Pills (Stitch Celestial Treasury) -->
        <div v-if="presetRanges && presetRanges.length" class="quick-presets-pill-group">
          <button
            v-for="(p, idx) in presetRanges.slice(0, 4)"
            :key="'preset-btn-' + idx"
            type="button"
            class="btn-preset-pill"
            :class="{ active: isPresetActive(p) }"
            @click="applyPreset(p)"
            :title="'Chọn nhanh ' + p.label"
          >
            {{ p.label }}
          </button>
        </div>

        <!-- Datepicker Range Wrapper -->
        <div class="stats-datepicker-wrapper">
          <VueDatePicker
            :model-value="statsDateRange"
            range
            :preset-ranges="presetRanges"
            :format="formatDateRange"
            :enable-time-picker="false"
            :auto-apply="true"
            :locale="viLocale"
            :format-locale="viLocale"
            :select-text="'Áp dụng'"
            :cancel-text="'Hủy'"
            :now-button-label="'Hôm nay'"
            :action-row="{ selectBtnLabel: 'Áp dụng', cancelBtnLabel: 'Hủy', nowBtnLabel: 'Hôm nay' }"
            placeholder="Chọn khoảng thời gian"
            :dark="currentTheme === 'xianxia'"
            :teleport="true"
            :floating="{ placement: 'bottom-end', offset: 8, flip: true, shift: true }"
            @update:model-value="onDateRangeUpdate"
          />
        </div>

        <!-- Export Action Buttons -->
        <div class="export-btn-group">
          <button
            type="button"
            class="btn-stitch-export"
            @click="emitExport('csv')"
            title="Xuất dữ liệu định dạng CSV"
          >
            <span class="material-symbols-outlined icon-xs text-jade">description</span>
            <span>CSV</span>
          </button>
          <button
            type="button"
            class="btn-stitch-export"
            @click="emitExport('excel')"
            title="Xuất dữ liệu định dạng Microsoft Excel"
          >
            <span class="material-symbols-outlined icon-xs text-gold">table_view</span>
            <span>Excel</span>
          </button>
        </div>
      </div>
    </section>

    <!-- ═══ TOP KPI SUMMARY (4 METRIC CARDS) ═══ -->
    <section class="kpi-summary-grid" aria-label="Chỉ số tổng quan tài khóa">
      <!-- KPI 1: Income -->
      <div class="kpi-metric-card card-income">
        <div class="kpi-glow glow-jade"></div>
        <div class="kpi-header-row">
          <span class="kpi-label">Tổng Thu Kỳ Này</span>
          <div class="kpi-icon-box icon-income">
            <span class="material-symbols-outlined icon-sm">south_west</span>
          </div>
        </div>
        <div class="kpi-body-col">
          <div class="kpi-value-text text-jade tabular-num font-bold">
            {{ formatVND(summary.total_income) }}
          </div>
          <div class="kpi-submeta text-jade">
            <span class="material-symbols-outlined icon-xs">arrow_upward</span>
            <span>Linh thạch nhập động thu hoạch</span>
          </div>
        </div>
      </div>

      <!-- KPI 2: Expense -->
      <div class="kpi-metric-card card-expense">
        <div class="kpi-glow glow-error"></div>
        <div class="kpi-header-row">
          <span class="kpi-label">Tổng Chi Kỳ Này</span>
          <div class="kpi-icon-box icon-expense">
            <span class="material-symbols-outlined icon-sm">north_east</span>
          </div>
        </div>
        <div class="kpi-body-col">
          <div class="kpi-value-text text-danger tabular-num font-bold">
            {{ formatVND(summary.total_expense) }}
          </div>
          <div class="kpi-submeta text-danger">
            <span class="material-symbols-outlined icon-xs">arrow_downward</span>
            <span>Tiêu tán linh thạch xuất quán</span>
          </div>
        </div>
      </div>

      <!-- KPI 3: Net Savings -->
      <div class="kpi-metric-card card-savings">
        <div class="kpi-glow glow-gold"></div>
        <div class="kpi-header-row">
          <span class="kpi-label">Thặng Dư Tích Lũy</span>
          <div class="kpi-icon-box icon-savings">
            <span class="material-symbols-outlined icon-sm">savings</span>
          </div>
        </div>
        <div class="kpi-body-col">
          <div
            class="kpi-value-text tabular-num font-bold"
            :class="summary.net_savings >= 0 ? 'text-gold' : 'text-danger'"
          >
            {{ summary.net_savings >= 0 ? '+' : '' }}{{ formatVND(summary.net_savings) }}
          </div>
          <div class="kpi-submeta text-gold">
            <span class="material-symbols-outlined icon-xs">trending_up</span>
            <span>Tỷ lệ giữ lại: {{ savingsRatePct }}% doanh số</span>
          </div>
        </div>
      </div>

      <!-- KPI 4: Total Liquidity / Balance -->
      <div class="kpi-metric-card card-balance">
        <div class="kpi-glow glow-secondary"></div>
        <div class="kpi-header-row">
          <span class="kpi-label">Số Dư Khả Dụng (Ví)</span>
          <div class="kpi-icon-box icon-balance">
            <span class="material-symbols-outlined icon-sm">account_balance_wallet</span>
          </div>
        </div>
        <div class="kpi-body-col">
          <div class="kpi-value-text text-on-surface tabular-num font-bold">
            {{ formatVND(summary.total_balance) }}
          </div>
          <div class="kpi-submeta text-secondary">
            <span class="material-symbols-outlined icon-xs">insights</span>
            <span>Toàn bộ túi càn khôn khả dụng</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ MAIN ANALYTICAL VISUALIZATIONS (2 COLUMNS) ═══ -->
    <div class="stats-charts-grid">
      <!-- Left Column (7 cols): Trend Bar Chart -->
      <div class="stitch-card trend-chart-card">
        <div class="chart-header-row">
          <div>
            <h2 class="chart-title">Xu Hướng Thu - Chi &amp; Tích Lũy</h2>
            <p class="chart-subtitle">Biểu đồ đối chiếu ngạch tài khóa các tháng tu luyện</p>
          </div>
          <div class="chart-legend-row">
            <span class="legend-pill">
              <span class="legend-dot bg-jade"></span>
              <span>Thu Nhập</span>
            </span>
            <span class="legend-pill">
              <span class="legend-dot bg-danger"></span>
              <span>Chi Tiêu</span>
            </span>
          </div>
        </div>

        <!-- Chart Component Wrap -->
        <div class="chart-container-box">
          <div v-if="trendData.trend && trendData.trend.length" class="chart-inner-wrap">
            <ChartComponent
              type="bar"
              :chart-data="trendBarData"
              title=""
            />
          </div>
          <div v-else class="chart-placeholder">
            <span class="material-symbols-outlined icon-lg text-secondary">bar_chart</span>
            <span>Chưa có dữ liệu xu hướng tháng</span>
          </div>
        </div>

        <div class="chart-footer-strip">
          <span class="footer-meta-text">
            Số chu kỳ ghi nhận: <strong class="text-on-surface">{{ trendData.trend ? trendData.trend.length : 0 }} Tháng</strong>
          </span>
          <span class="footer-meta-status text-jade flex-align-center gap-xs">
            <span class="material-symbols-outlined icon-xs">verified</span>
            <span>Đối chiếu tự động theo lịch sử</span>
          </span>
        </div>
      </div>

      <!-- Right Column (5 cols): Weekly Spend Line Chart -->
      <div class="stitch-card weekly-chart-card">
        <div class="chart-header-row">
          <div>
            <h2 class="chart-title">Biến Động Chi Tiêu Theo Tuần</h2>
            <p class="chart-subtitle">Các chu kỳ linh tuần gần đây</p>
          </div>
          <span class="header-tag-pill">
            {{ weeklyData.data ? weeklyData.data.length : 0 }} Tuần Lễ
          </span>
        </div>

        <!-- Line Chart Component Wrap -->
        <div class="chart-container-box">
          <div v-if="weeklyData.data && weeklyData.data.length" class="chart-inner-wrap">
            <ChartComponent
              type="line"
              :chart-data="weeklyLineData"
              title=""
            />
          </div>
          <div v-else class="chart-placeholder">
            <span class="material-symbols-outlined icon-lg text-secondary">show_chart</span>
            <span>Chưa có dữ liệu chi tiêu tuần</span>
          </div>
        </div>

        <!-- Weekly Summary Details Strip -->
        <div v-if="weeklyData.data && weeklyData.data.length" class="weekly-metrics-row">
          <div
            v-for="(w, idx) in weeklyData.data.slice(-4)"
            :key="'w-pill-' + idx"
            class="weekly-metric-pill"
          >
            <span class="weekly-label">T{{ idx + 1 }}</span>
            <span class="weekly-amount tabular-num font-mono">{{ formatVND(w.expense || 0) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ CATEGORY EXPENSE BREAKDOWN (DOUGHNUT + LIST) ═══ -->
    <div
      v-if="summary.expense_by_category && summary.expense_by_category.length"
      class="stitch-card category-breakdown-card"
    >
      <div class="chart-header-row">
        <div>
          <h2 class="chart-title">Tỷ Trọng Chi Tiêu Theo Danh Mục</h2>
          <p class="chart-subtitle">Phân bổ linh thạch tổn hao theo từng linh mục</p>
        </div>
        <span class="header-tag-pill text-jade">
          {{ summary.expense_by_category.length }} Danh Mục Chi
        </span>
      </div>

      <div class="category-breakdown-grid">
        <!-- Doughnut Chart on Left -->
        <div class="doughnut-chart-col">
          <div class="doughnut-canvas-wrap">
            <ChartComponent
              type="doughnut"
              :chart-data="statsDoughnutData"
              title=""
            />
          </div>
        </div>

        <!-- Category Itemized Bars on Right -->
        <div class="category-items-list-col">
          <div
            v-for="(cat, idx) in summary.expense_by_category"
            :key="'cat-item-' + idx"
            class="category-stat-row"
          >
            <div class="cat-row-header">
              <div class="cat-identity">
                <span class="cat-icon">{{ cat.icon || '📦' }}</span>
                <span class="cat-name font-medium">{{ cat.category_name }}</span>
              </div>
              <div class="cat-values">
                <span class="cat-amount tabular-num font-semibold text-danger">
                  {{ formatVND(cat.total) }}
                </span>
                <span class="cat-pct tabular-num font-mono text-secondary">
                  ({{ getCategoryPercentage(cat.total) }}%)
                </span>
              </div>
            </div>
            <div class="cat-progress-track">
              <div
                class="cat-progress-fill"
                :style="{ width: getCategoryPercentage(cat.total) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ MONTH-TO-MONTH COMPARISON (SO SÁNH HAI THÁNG) ═══ -->
    <section class="stitch-card comparison-section">
      <div class="comparison-header">
        <div class="comparison-title-col">
          <div class="inline-flex items-center gap-xs text-jade font-label-sm text-label-sm mb-1">
            <span class="material-symbols-outlined icon-xs">compare_arrows</span>
            <span class="font-semibold uppercase">ĐỐI CHIẾU CHU KỲ</span>
          </div>
          <h2 class="comparison-title">
            So Sánh Chi Tiêu Hai Tháng
            <span v-if="compareData && compareData.month1 && compareData.month2" class="text-secondary font-normal text-sm">
              ({{ compareData.month1.month }} vs {{ compareData.month2.month }})
            </span>
          </h2>
        </div>

        <!-- Month Pickers -->
        <div class="comparison-inputs-row">
          <div class="month-input-box">
            <label class="month-label" for="compare-m1">Tháng 1</label>
            <input
              id="compare-m1"
              :value="compareMonth1"
              type="month"
              class="month-native-input"
              @change="onMonth1Change"
            />
          </div>
          <span class="vs-badge">VS</span>
          <div class="month-input-box">
            <label class="month-label" for="compare-m2">Tháng 2</label>
            <input
              id="compare-m2"
              :value="compareMonth2"
              type="month"
              class="month-native-input"
              @change="onMonth2Change"
            />
          </div>
          <button
            type="button"
            class="btn-stitch-compare"
            @click="emit('load-compare')"
            title="Thực hiện đối chiếu hai tháng"
          >
            <span class="material-symbols-outlined icon-xs">sync</span>
            <span>Đối Chiếu</span>
          </button>
        </div>
      </div>

      <!-- Comparative Matrix (3 Cards) -->
      <div v-if="compareData && compareData.month1 && compareData.month2" class="comparison-matrix-grid">
        <!-- Revenue Compare -->
        <div class="matrix-card">
          <div class="matrix-header">
            <span class="matrix-metric-name">Tổng Thu Nhập</span>
            <span
              class="delta-pill"
              :class="compareData.delta_income >= 0 ? 'delta-positive' : 'delta-negative'"
            >
              {{ compareData.delta_income >= 0 ? '+' : '' }}{{ formatVND(compareData.delta_income) }}
              {{ compareData.delta_income >= 0 ? '▲' : '▼' }}
            </span>
          </div>
          <div class="matrix-body">
            <div class="month-side">
              <span class="side-label font-mono">{{ compareData.month1.month }}</span>
              <span class="side-amount tabular-num">{{ formatVND(compareData.month1.income) }}</span>
            </div>
            <span class="material-symbols-outlined matrix-arrow">arrow_forward</span>
            <div class="month-side text-right">
              <span class="side-label font-mono text-jade">{{ compareData.month2.month }}</span>
              <span class="side-amount tabular-num text-jade font-semibold">{{ formatVND(compareData.month2.income) }}</span>
            </div>
          </div>
        </div>

        <!-- Expense Compare -->
        <div class="matrix-card">
          <div class="matrix-header">
            <span class="matrix-metric-name">Tổng Chi Tiêu</span>
            <span
              class="delta-pill"
              :class="compareData.delta_expense <= 0 ? 'delta-positive' : 'delta-negative'"
            >
              {{ compareData.delta_expense >= 0 ? '+' : '' }}{{ formatVND(compareData.delta_expense) }}
              {{ compareData.delta_expense <= 0 ? '▼ Giảm' : '▲ Tăng' }}
            </span>
          </div>
          <div class="matrix-body">
            <div class="month-side">
              <span class="side-label font-mono">{{ compareData.month1.month }}</span>
              <span class="side-amount tabular-num">{{ formatVND(compareData.month1.expense) }}</span>
            </div>
            <span class="material-symbols-outlined matrix-arrow">arrow_forward</span>
            <div class="month-side text-right">
              <span class="side-label font-mono text-danger">{{ compareData.month2.month }}</span>
              <span class="side-amount tabular-num text-danger font-semibold">{{ formatVND(compareData.month2.expense) }}</span>
            </div>
          </div>
        </div>

        <!-- Savings Compare -->
        <div class="matrix-card">
          <div class="matrix-header">
            <span class="matrix-metric-name">Tích Lũy Ròng</span>
            <span
              class="delta-pill"
              :class="compareData.delta_savings >= 0 ? 'delta-positive' : 'delta-negative'"
            >
              {{ compareData.delta_savings >= 0 ? '+' : '' }}{{ formatVND(compareData.delta_savings) }}
              {{ compareData.delta_savings >= 0 ? '▲ Tăng' : '▼ Giảm' }}
            </span>
          </div>
          <div class="matrix-body">
            <div class="month-side">
              <span class="side-label font-mono">{{ compareData.month1.month }}</span>
              <span class="side-amount tabular-num">{{ formatVND(compareData.month1.savings) }}</span>
            </div>
            <span class="material-symbols-outlined matrix-arrow">arrow_forward</span>
            <div class="month-side text-right">
              <span class="side-label font-mono text-gold">{{ compareData.month2.month }}</span>
              <span class="side-amount tabular-num text-gold font-bold">{{ formatVND(compareData.month2.savings) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Itemized Category Variance Table -->
      <div
        v-if="categoryComparisonRows && categoryComparisonRows.length"
        class="comparison-table-wrapper"
      >
        <div class="table-caption-row">
          <span class="table-caption-title">Biến Động Chi Tiết Từng Linh Mục (Danh Mục)</span>
          <span class="table-caption-hint">Tự động đối chiếu chênh lệch giữa hai tháng</span>
        </div>
        <div class="table-responsive-box">
          <table class="comparison-table">
            <thead>
              <tr>
                <th class="col-cat">Linh Mục (Danh Mục)</th>
                <th class="col-m1 text-right font-mono">{{ compareData.month1.month }}</th>
                <th class="col-m2 text-right font-mono">{{ compareData.month2.month }}</th>
                <th class="col-delta text-right">Chênh Lệch</th>
                <th class="col-status text-right">Đánh Giá Khí Linh</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in categoryComparisonRows"
                :key="'cmp-cat-' + idx"
                class="cmp-row"
              >
                <td class="col-cat">
                  <div class="cat-cell">
                    <span class="cat-badge-icon">{{ row.icon }}</span>
                    <span class="cat-name-text font-medium">{{ row.name }}</span>
                  </div>
                </td>
                <td class="col-m1 text-right tabular-num font-mono text-secondary">
                  {{ formatVND(row.m1Total) }}
                </td>
                <td class="col-m2 text-right tabular-num font-mono text-on-surface font-medium">
                  {{ formatVND(row.m2Total) }}
                </td>
                <td
                  class="col-delta text-right tabular-num font-mono font-semibold"
                  :class="row.delta <= 0 ? 'text-jade' : 'text-danger'"
                >
                  {{ row.delta > 0 ? '+' : '' }}{{ formatVND(row.delta) }}
                  <span class="delta-pct">({{ row.pct > 0 ? '+' : '' }}{{ row.pct }}%)</span>
                </td>
                <td class="col-status text-right">
                  <span
                    class="status-chip"
                    :class="row.delta <= 0 ? 'chip-positive' : 'chip-warning'"
                  >
                    {{ row.delta <= 0 ? 'Đắc pháp tiết kiệm' : 'Tăng chi tiêu' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ═══ KHÍ LINH AI FINANCIAL ADVICE & FORECAST ═══ -->
    <section class="stitch-card ai-advisor-card">
      <div class="ai-advisor-header">
        <div class="advisor-title-row">
          <div class="advisor-avatar-box">
            <span class="material-symbols-outlined icon-md text-secondary">psychology</span>
            <span class="live-dot-ping"></span>
          </div>
          <div>
            <div class="flex-align-center gap-xs">
              <h3 class="advisor-title">Lời Khuyên Tiết Kiệm Từ Khí Linh AI</h3>
              <span class="advisor-tag">BẬC THẦY KHÍ LINH</span>
            </div>
            <p class="advisor-desc">
              Phân tích chuyên sâu kết hợp vận số ngũ hành &amp; dòng tiền tu đạo của Ký Chủ
            </p>
          </div>
        </div>

        <button
          type="button"
          class="btn-stitch-primary"
          :disabled="loadingTips"
          @click="emit('load-saving-tips')"
        >
          <span v-if="loadingTips" class="material-symbols-outlined step-spin icon-xs">sync</span>
          <span v-else class="material-symbols-outlined icon-xs">auto_awesome</span>
          <span>{{ loadingTips ? '🔮 Đang thỉnh khai thị...' : 'Thỉnh Khai Thị Khí Linh' }}</span>
        </button>
      </div>

      <!-- Rendered Tips Content -->
      <div v-if="savingTips" class="advisor-body-box">
        <div class="tips-summary-meta">
          <span class="meta-item">📅 Chu kỳ phân tích: <strong>{{ savingTips.month_year }}</strong></span>
          <span class="meta-item">
            Tỷ lệ tích lũy:
            <strong :class="savingTips.savings_rate >= 20 ? 'text-jade' : 'text-danger'">
              {{ savingTips.savings_rate }}%
            </strong>
          </span>
        </div>
        <div class="tips-html-rendered" v-html="formatChatText(savingTips.tips)"></div>
      </div>
      <div v-else class="advisor-empty-prompt">
        <span class="material-symbols-outlined icon-lg text-secondary">tips_and_updates</span>
        <p class="prompt-text">
          Nhấn nút "Thỉnh Khai Thị Khí Linh" để AI phân tích toàn diện bảng thu chi tháng này và đưa ra phương án tối ưu tài lực.
        </p>
      </div>
    </section>

    <!-- ═══ EMPTY STATE WHEN NO TRANSACTIONS EXIST ═══ -->
    <div
      v-if="!trendData.trend?.length && !weeklyData.data?.length"
      class="stitch-card empty-state-card"
    >
      <span class="material-symbols-outlined icon-hero text-secondary">query_stats</span>
      <h3 class="empty-title">Chưa Có Đủ Dữ Liệu Thống Kê</h3>
      <p class="empty-desc">
        Hệ thống cần ít nhất một vài giao dịch thu chi trong khoảng thời gian đã chọn để vẽ biểu đồ và phân tích tỷ trọng. Hãy tạo thêm giao dịch mới để bắt đầu quan sát tài phổ!
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import ChartComponent from '../ChartComponents.vue'

const props = defineProps({
  trendData: {
    type: Object,
    default: () => ({ trend: [] })
  },
  weeklyData: {
    type: Object,
    default: () => ({ data: [] })
  },
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
  trendBarData: {
    type: Object,
    required: true
  },
  weeklyLineData: {
    type: Object,
    required: true
  },
  statsDoughnutData: {
    type: Object,
    required: true
  },
  statsDateRange: {
    type: Array,
    default: () => [new Date(), new Date()]
  },
  presetRanges: {
    type: Array,
    default: () => []
  },
  compareMonth1: {
    type: String,
    default: ''
  },
  compareMonth2: {
    type: String,
    default: ''
  },
  compareData: {
    type: Object,
    default: null
  },
  savingTips: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingTips: {
    type: Boolean,
    default: false
  },
  currentTheme: {
    type: String,
    default: 'xianxia'
  },
  viLocale: {
    type: Object,
    default: null
  },
  formatVND: {
    type: Function,
    required: true
  },
  formatChatText: {
    type: Function,
    default: (t) => t || ''
  }
})

const emit = defineEmits([
  'update:stats-date-range',
  'stats-date-change',
  'do-export',
  'update:compare-month1',
  'update:compare-month2',
  'load-compare',
  'load-saving-tips'
])

// ─── HANDLERS ─────────────────────
function onDateRangeUpdate(val) {
  emit('update:stats-date-range', val)
  emit('stats-date-change')
}

function emitExport(format) {
  emit('do-export', format)
}

function onMonth1Change(e) {
  emit('update:compare-month1', e.target.value)
  emit('load-compare')
}

function onMonth2Change(e) {
  emit('update:compare-month2', e.target.value)
  emit('load-compare')
}

// ─── DATE RANGE DISPLAY & PRESET HELPERS ───
function formatDateRange(dates) {
  if (!dates || !Array.isArray(dates) || dates.length === 0 || !dates[0]) {
    return 'Chọn khoảng thời gian'
  }
  const toDate = (val) => {
    if (val instanceof Date) return val
    if (typeof val === 'string' || typeof val === 'number') {
      const d = new Date(val)
      return isNaN(d.getTime()) ? null : d
    }
    return null
  }
  const d1 = toDate(dates[0])
  if (!d1) return 'Chọn khoảng thời gian'

  const pad = (n) => String(n).padStart(2, '0')
  const fmt = (d) => `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`

  const d2 = dates[1] ? toDate(dates[1]) : null
  if (!d2) return fmt(d1)
  return `${fmt(d1)} — ${fmt(d2)}`
}

function applyPreset(p) {
  if (typeof p.value === 'function') {
    const dates = p.value()
    emit('update:stats-date-range', dates)
    emit('stats-date-change')
  }
}

function isPresetActive(p) {
  if (!props.statsDateRange || !props.statsDateRange[0] || !props.statsDateRange[1]) return false
  if (typeof p.value !== 'function') return false
  try {
    const [s, e] = p.value()
    const curS = new Date(props.statsDateRange[0])
    const curE = new Date(props.statsDateRange[1])
    return s.toDateString() === curS.toDateString() && e.toDateString() === curE.toDateString()
  } catch {
    return false
  }
}

// ─── COMPUTED ANALYTICS ───────────
const savingsRatePct = computed(() => {
  const income = props.summary?.total_income || 0
  const savings = props.summary?.net_savings || 0
  if (income <= 0) return 0
  return Math.round((savings / income) * 100)
})

const totalExpenseCalculated = computed(() => {
  return (props.summary?.expense_by_category || []).reduce((acc, c) => acc + (c.total || 0), 0)
})

function getCategoryPercentage(val) {
  const total = totalExpenseCalculated.value || props.summary?.total_expense || 0
  if (total <= 0) return 0
  return Math.round(((val || 0) / total) * 100)
}

// Detailed Category comparison matrix rows
const categoryComparisonRows = computed(() => {
  if (!props.compareData?.month1 || !props.compareData?.month2) return []

  const m1Cats = props.compareData.month1.by_category || []
  const m2Cats = props.compareData.month2.by_category || []

  const m1Map = new Map()
  for (const c of m1Cats) {
    m1Map.set(c.category_name, c)
  }

  const m2Map = new Map()
  for (const c of m2Cats) {
    m2Map.set(c.category_name, c)
  }

  const allKeys = new Set([...m1Map.keys(), ...m2Map.keys()])

  return Array.from(allKeys).map(name => {
    const c1 = m1Map.get(name) || { total: 0, icon: '📦' }
    const c2 = m2Map.get(name) || { total: 0, icon: '📦' }
    const delta = (c2.total || 0) - (c1.total || 0)
    const pct = c1.total > 0
      ? Math.round((delta / c1.total) * 100)
      : (c2.total > 0 ? 100 : 0)

    return {
      name,
      icon: c2.icon || c1.icon || '📦',
      m1Total: c1.total || 0,
      m2Total: c2.total || 0,
      delta,
      pct
    }
  }).sort((a, b) => b.m2Total - a.m2Total)
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════
   CELESTIAL TREASURY — STATISTICS VIEW STYLES
   Design tokens from stitch_design/th_ng_k_statistics
   ═══════════════════════════════════════════════════════════ */

.statistics-realm {
  position: relative;
  width: 100%;
  min-height: 100%;
  padding-bottom: 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  color: #dae2fd;
}

/* ─── AMBIENT GLOW ORBS ─── */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.16;
}

.orb-primary {
  top: -40px;
  right: 15%;
  width: 440px;
  height: 440px;
  background: radial-gradient(circle, #7dd6cc 0%, rgba(68, 159, 150, 0) 70%);
}

.orb-secondary {
  top: 480px;
  left: -80px;
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, #444173 0%, rgba(68, 65, 115, 0) 70%);
}

/* ─── STITCH CARD BASE ─── */
.stitch-card {
  position: relative;
  z-index: 1;
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  transition: border-color 0.2s ease;
}

.stitch-card:hover {
  border-color: rgba(125, 214, 204, 0.2);
}

/* ─── TOP HEADER CARD ─── */
.stats-header-card {
  position: relative;
  z-index: 30;
  background: rgba(19, 27, 46, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

@media (min-width: 1024px) {
  .stats-header-card {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.header-content-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  letter-spacing: 0.08em;
  font-weight: 600;
  color: #7dd6cc;
  text-transform: uppercase;
}

.status-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #7dd6cc;
  box-shadow: 0 0 10px #7dd6cc;
  animation: pulseAura 2s infinite ease-in-out;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: #dae2fd;
}

@media (min-width: 640px) {
  .page-title {
    font-size: 28px;
  }
}

.page-subtitle {
  margin: 0;
  max-width: 680px;
  font-size: 13px;
  line-height: 1.5;
  color: #bdc9c6;
}

.header-controls-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 35;
}

/* Quick Presets (Stitch Style) */
.quick-presets-pill-group {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(23, 31, 51, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 4px;
  overflow-x: auto;
}

.btn-preset-pill {
  padding: 6px 12px;
  background: transparent;
  color: #bdc9c6;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.btn-preset-pill:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #dae2fd;
}

.btn-preset-pill.active {
  background: #449f96;
  color: #00302c;
  font-weight: 600;
  box-shadow: 0 0 10px rgba(68, 159, 150, 0.35);
}

.stats-datepicker-wrapper {
  width: 320px;
  min-width: 290px;
  max-width: 100%;
  position: relative;
  z-index: 40;
}

:deep(.dp__main) {
  width: 100%;
}

:deep(.dp__input) {
  width: 100% !important;
  background: rgba(19, 27, 46, 0.95) !important;
  border: 1px solid rgba(125, 214, 204, 0.3) !important;
  color: #dae2fd !important;
  font-family: var(--font-mono, 'JetBrains Mono', monospace), sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  letter-spacing: 0.02em !important;
  border-radius: 10px !important;
  padding: 8px 36px 8px 36px !important;
  height: 42px !important;
  line-height: 24px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
  transition: all 0.2s ease !important;
  white-space: nowrap !important;
  text-overflow: clip !important;
}

:deep(.dp__input:hover),
:deep(.dp__input:focus) {
  border-color: #7dd6cc !important;
  box-shadow: 0 0 0 2px rgba(125, 214, 204, 0.25) !important;
}

:deep(.dp__input_icon) {
  color: #7dd6cc !important;
  padding-left: 10px !important;
}

:deep(.dp__clear_icon) {
  color: #bdc9c6 !important;
  padding-right: 10px !important;
}

:deep(.dp__clear_icon:hover) {
  color: #ffb4ab !important;
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .header-controls-group {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .quick-presets-pill-group {
    width: 100%;
    justify-content: space-between;
  }

  .stats-datepicker-wrapper {
    width: 100% !important;
    min-width: 0 !important;
  }

  .export-btn-group {
    width: 100%;
    justify-content: flex-end;
  }
}

.export-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-stitch-export {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #222a3d;
  color: #dae2fd;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-export:hover {
  background: #31394d;
  border-color: rgba(125, 214, 204, 0.35);
  color: #ffffff;
}

/* ─── TOP KPI SUMMARY (4 CARDS) ─── */
.kpi-summary-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 640px) {
  .kpi-summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .kpi-summary-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.kpi-metric-card {
  position: relative;
  overflow: hidden;
  background: rgba(23, 31, 51, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(125, 214, 204, 0.25);
}

.kpi-glow {
  position: absolute;
  right: -24px;
  bottom: -24px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  filter: blur(28px);
  pointer-events: none;
  opacity: 0.15;
}

.glow-jade { background: #7dd6cc; }
.glow-error { background: #ffb4ab; }
.glow-gold { background: #e3c370; }
.glow-secondary { background: #c4c1fb; }

.kpi-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kpi-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #bdc9c6;
}

.kpi-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-income { background: rgba(125, 214, 204, 0.15); color: #7dd6cc; }
.icon-expense { background: rgba(255, 180, 171, 0.15); color: #ffb4ab; }
.icon-savings { background: rgba(227, 195, 112, 0.15); color: #e3c370; }
.icon-balance { background: rgba(196, 193, 251, 0.15); color: #c4c1fb; }

.kpi-body-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpi-value-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.kpi-submeta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
}

/* ─── CHARTS 2-COL GRID ─── */
.stats-charts-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 1024px) {
  .stats-charts-grid {
    grid-template-columns: repeat(12, 1fr);
  }

  .trend-chart-card {
    grid-column: span 7;
  }

  .weekly-chart-card {
    grid-column: span 5;
  }
}

.chart-header-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

@media (min-width: 640px) {
  .chart-header-row {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #dae2fd;
}

.chart-subtitle {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #bdc9c6;
}

.chart-legend-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: #dae2fd;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.header-tag-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 9999px;
  background: #222a3d;
  color: #c4c1fb;
}

.chart-container-box {
  width: 100%;
  min-height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-inner-wrap {
  width: 100%;
  height: 100%;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #889391;
  font-size: 13px;
  padding: 40px 0;
}

.chart-footer-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(34, 42, 61, 0.5);
  border-radius: 8px;
  margin-top: 14px;
  font-size: 12px;
  color: #bdc9c6;
}

.weekly-metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 14px;
}

.weekly-metric-pill {
  background: rgba(34, 42, 61, 0.6);
  padding: 8px 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 2px;
}

.weekly-label {
  font-size: 10.5px;
  color: #889391;
}

.weekly-amount {
  font-size: 11px;
  font-weight: 600;
  color: #dae2fd;
}

/* ─── CATEGORY BREAKDOWN SECTION ─── */
.category-breakdown-card {
  display: flex;
  flex-direction: column;
}

.category-breakdown-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .category-breakdown-grid {
    grid-template-columns: 320px 1fr;
    align-items: center;
  }
}

.doughnut-chart-col {
  display: flex;
  align-items: center;
  justify-content: center;
}

.doughnut-canvas-wrap {
  width: 100%;
  max-width: 280px;
  height: 260px;
}

.category-items-list-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 6px;
}

.category-stat-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(19, 27, 46, 0.6);
  padding: 10px 14px;
  border-radius: 8px;
}

.cat-row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cat-identity {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cat-icon {
  font-size: 16px;
}

.cat-name {
  font-size: 13px;
  color: #dae2fd;
}

.cat-values {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cat-amount {
  font-size: 13px;
}

.cat-pct {
  font-size: 11.5px;
}

.cat-progress-track {
  width: 100%;
  height: 5px;
  background: #222a3d;
  border-radius: 9999px;
  overflow: hidden;
}

.cat-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7dd6cc, #449f96);
  border-radius: 9999px;
  transition: width 0.3s ease;
}

/* ─── COMPARISON SECTION ─── */
.comparison-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.comparison-header {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

@media (min-width: 1024px) {
  .comparison-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.comparison-title-col {
  display: flex;
  flex-direction: column;
}

.comparison-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #dae2fd;
}

.comparison-inputs-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.month-input-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.month-label {
  font-size: 11px;
  color: #bdc9c6;
  font-weight: 600;
}

.month-native-input {
  height: 38px;
  padding: 0 10px;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #dae2fd;
  font-size: 13px;
  font-family: monospace;
}

.month-native-input:focus {
  outline: none;
  border-color: #7dd6cc;
}

.vs-badge {
  font-size: 13px;
  font-weight: 700;
  color: #e3c370;
  padding-bottom: 8px;
}

.btn-stitch-compare {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 14px;
  background: #222a3d;
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.25);
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-compare:hover {
  background: #31394d;
  color: #ffffff;
}

/* Comparison Matrix Grid */
.comparison-matrix-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 768px) {
  .comparison-matrix-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.matrix-card {
  background: rgba(34, 42, 61, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.matrix-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.matrix-metric-name {
  font-size: 12.5px;
  font-weight: 600;
  color: #bdc9c6;
}

.delta-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.delta-positive {
  background: rgba(125, 214, 204, 0.15);
  color: #7dd6cc;
}

.delta-negative {
  background: rgba(255, 180, 171, 0.15);
  color: #ffb4ab;
}

.matrix-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.month-side {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.side-label {
  font-size: 10.5px;
  color: #889391;
}

.side-amount {
  font-size: 14px;
}

.matrix-arrow {
  color: #889391;
  font-size: 18px;
}

/* Comparison table */
.comparison-table-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.table-caption-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #bdc9c6;
}

.table-caption-title {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.table-responsive-box {
  overflow-x: auto;
  border-radius: 8px;
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.comparison-table th {
  padding: 10px 14px;
  background: rgba(34, 42, 61, 0.5);
  color: #bdc9c6;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
}

.comparison-table td {
  padding: 10px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.cat-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cat-badge-icon {
  font-size: 16px;
}

.delta-pct {
  font-size: 11px;
  font-weight: normal;
  margin-left: 4px;
}

.status-chip {
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
}

.chip-positive {
  background: rgba(125, 214, 204, 0.15);
  color: #7dd6cc;
}

.chip-warning {
  background: rgba(255, 180, 171, 0.15);
  color: #ffb4ab;
}

/* ─── AI ADVISOR CARD ─── */
.ai-advisor-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-advisor-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 640px) {
  .ai-advisor-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.advisor-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.advisor-avatar-box {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(196, 193, 251, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.live-dot-ping {
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7dd6cc;
  animation: pingDot 1.5s infinite;
}

.advisor-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #dae2fd;
}

.advisor-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(227, 195, 112, 0.2);
  color: #e3c370;
}

.advisor-desc {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #bdc9c6;
}

.advisor-body-box {
  background: #131b2e;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tips-summary-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #bdc9c6;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 10px;
}

.tips-html-rendered {
  font-size: 13.5px;
  line-height: 1.6;
  color: #dae2fd;
}

.advisor-empty-prompt {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #131b2e;
  padding: 16px 20px;
  border-radius: 10px;
  color: #889391;
}

.prompt-text {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.5;
}

/* ─── EMPTY STATE CARD ─── */
.empty-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  gap: 12px;
}

.empty-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #dae2fd;
}

.empty-desc {
  margin: 0;
  font-size: 13px;
  color: #bdc9c6;
  max-width: 480px;
  line-height: 1.55;
}

/* ─── BUTTONS & UTILITIES ─── */
.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 16px;
  background: #7dd6cc;
  color: #003733;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 14px rgba(125, 214, 204, 0.35);
  transition: all 0.2s ease;
}

.btn-stitch-primary:hover:not(:disabled) {
  background: #9af2e8;
  transform: translateY(-1px);
}

.btn-stitch-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-jade { color: #7dd6cc; }
.text-gold { color: #e3c370; }
.text-danger { color: #ffb4ab; }
.text-secondary { color: #c4c1fb; }
.text-on-surface { color: #dae2fd; }
.bg-jade { background-color: #7dd6cc; }
.bg-danger { background-color: #ffb4ab; }
.tabular-num { font-variant-numeric: tabular-nums; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.flex-align-center { display: flex; align-items: center; }
.gap-xs { gap: 6px; }

.icon-xs { font-size: 14px; }
.icon-sm { font-size: 18px; }
.icon-md { font-size: 24px; }
.icon-lg { font-size: 32px; }
.icon-hero { font-size: 48px; }

@keyframes pulseAura {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
}

@keyframes pingDot {
  0% { transform: scale(1); opacity: 1; }
  75%, 100% { transform: scale(2.2); opacity: 0; }
}

@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-spin {
  animation: spinSlow 1.5s linear infinite;
}
</style>
