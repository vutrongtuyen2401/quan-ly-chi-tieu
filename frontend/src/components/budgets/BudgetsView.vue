<template>
  <div class="budgets-realm">
    <!-- Spatial Atmosphere Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & CONTROLS ═══ -->
    <section class="budgets-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">ĐỊNH MỨC GIỚI CƯƠNG • CHU KỲ TU LUYỆN TRĂNG TRÒN</span>
        </div>
        <h1 class="page-title">Hạn Mức Chi Tiêu (Budgets)</h1>
        <p class="page-subtitle">
          Thiết lập giới cương chi tiêu theo từng linh mục, trấn áp tâm ma hao tài và giữ vững chân nguyên tài chính.
        </p>
      </div>

      <div class="header-controls-group">
        <!-- Month Navigation Switcher -->
        <div class="month-switcher-card" aria-label="Bộ chọn chu kỳ tháng">
          <button
            type="button"
            class="btn-month-nav"
            @click="prevMonth"
            title="Tháng trước"
            aria-label="Tháng trước"
          >
            <span class="material-symbols-outlined">chevron_left</span>
          </button>

          <div class="month-display-wrap">
            <span class="material-symbols-outlined month-icon">calendar_month</span>
            <span class="month-label">{{ formattedMonthLabel }}</span>
            <input
              type="month"
              :value="budgetMonth"
              @input="onMonthInput"
              class="hidden-month-input"
              title="Chọn tháng cụ thể"
            />
          </div>

          <button
            type="button"
            class="btn-month-nav"
            @click="nextMonth"
            title="Tháng sau"
            aria-label="Tháng sau"
          >
            <span class="material-symbols-outlined">chevron_right</span>
          </button>

          <button
            v-if="!isCurrentMonth"
            type="button"
            class="btn-month-today"
            @click="resetToCurrentMonth"
            title="Quay lại tháng hiện tại"
          >
            Hiện tại
          </button>
        </div>

        <!-- Quick Action Trigger -->
        <button
          type="button"
          class="btn-stitch-primary"
          @click="focusCreateForm"
          title="Thiết lập hạn mức mới"
        >
          <span class="material-symbols-outlined">add_circle</span>
          <span>+ Thiết Lập Hạn Mức Mới</span>
        </button>
      </div>
    </section>

    <!-- ═══ SUMMARY METRICS ROW (4 CARDS) ═══ -->
    <section class="budget-metrics-grid" aria-label="Thống kê tổng quan hạn mức">
      <!-- Metric 1: Total Cap -->
      <div class="budget-metric-card card-total">
        <div class="metric-card-glow glow-primary"></div>
        <div class="metric-header-row">
          <span class="metric-label">Tổng Hạn Mức Tháng</span>
          <div class="metric-icon-box icon-jade">
            <span class="material-symbols-outlined icon-sm">account_balance_wallet</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-jade tabular-num font-bold">
            {{ formatVND(totalBudgetAmount) }}
          </div>
          <div class="metric-submeta">
            <span class="ping-dot bg-jade"></span>
            <span>{{ budgets.length }} linh mục đã kích hoạt giới cương</span>
          </div>
        </div>
      </div>

      <!-- Metric 2: Total Spent -->
      <div class="budget-metric-card card-spent">
        <div class="metric-card-glow glow-gold"></div>
        <div class="metric-header-row">
          <span class="metric-label">Đã Chi Tiêu</span>
          <div class="metric-icon-box icon-gold">
            <span class="material-symbols-outlined icon-sm">trending_up</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-gold tabular-num font-bold">
            {{ formatVND(totalSpentAmount) }}
          </div>
          <div class="metric-submeta" :class="overallSpentPct >= 100 ? 'text-danger' : overallSpentPct >= 80 ? 'text-gold' : 'text-on-surface-variant'">
            <span class="material-symbols-outlined icon-xs">
              {{ overallSpentPct >= 100 ? 'local_fire_department' : overallSpentPct >= 80 ? 'warning' : 'check_circle' }}
            </span>
            <span>{{ overallSpentPct.toFixed(1) }}% • {{ overallStatusText }}</span>
          </div>
        </div>
      </div>

      <!-- Metric 3: Remaining Cap -->
      <div class="budget-metric-card card-remaining">
        <div class="metric-card-glow" :class="totalRemainingAmount < 0 ? 'glow-error' : 'glow-primary'"></div>
        <div class="metric-header-row">
          <span class="metric-label">Hạn Mức Khả Dụng Còn Lại</span>
          <div class="metric-icon-box" :class="totalRemainingAmount < 0 ? 'icon-error' : 'icon-jade'">
            <span class="material-symbols-outlined icon-sm">savings</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div
            class="metric-value-text tabular-num font-bold"
            :class="totalRemainingAmount < 0 ? 'text-danger' : 'text-jade'"
          >
            {{ totalRemainingAmount < 0 ? 'Vượt ' + formatVND(Math.abs(totalRemainingAmount)) : formatVND(totalRemainingAmount) }}
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs text-jade">timelapse</span>
            <span>{{ daysRemainingInMonth }} ngày còn lại trong chu kỳ</span>
          </div>
        </div>
      </div>

      <!-- Metric 4: Health Overview & Segmented Gauge -->
      <div class="budget-metric-card card-health">
        <div class="metric-card-glow glow-secondary"></div>
        <div class="metric-header-row">
          <span class="metric-label">Trạng Thái Tổng Cương</span>
          <div class="metric-icon-box icon-indigo">
            <span class="material-symbols-outlined icon-sm">verified_user</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="health-breakdown-row">
            <span class="health-pill pill-danger" v-if="dangerCount > 0 || budgets.length === 0">
              <span class="w-2 h-2 rounded-full bg-danger animate-ping"></span>
              {{ dangerCount }} Nguy Cấp
            </span>
            <span class="health-pill pill-warning" v-if="warningCount > 0 || budgets.length === 0">
              <span class="w-2 h-2 rounded-full bg-gold"></span>
              {{ warningCount }} Cảnh Báo
            </span>
            <span class="health-pill pill-safe">
              <span class="w-2 h-2 rounded-full bg-jade"></span>
              {{ safeCount }} An Toàn
            </span>
          </div>
          <!-- Micro Multi-Segment Progress Gauge -->
          <div class="health-gauge-track" title="Tỷ lệ trạng thái ngân sách">
            <div
              v-if="dangerRatio > 0"
              class="health-gauge-segment bg-danger"
              :style="{ width: (dangerRatio * 100) + '%' }"
            ></div>
            <div
              v-if="warningRatio > 0"
              class="health-gauge-segment bg-gold"
              :style="{ width: (warningRatio * 100) + '%' }"
            ></div>
            <div
              v-if="safeRatio > 0"
              class="health-gauge-segment bg-jade"
              :style="{ width: (safeRatio * 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ MAIN BENTO WORKSPACE (8 COLS / 4 COLS) ═══ -->
    <div class="budgets-bento-grid">
      <!-- ─── LEFT COLUMN: CATEGORY BUDGET CARDS (8 COLS) ─── -->
      <div class="bento-left-col">
        <!-- Filter & Search Toolbar -->
        <div class="budget-toolbar-card">
          <div class="toolbar-title-row">
            <div class="flex items-center gap-2">
              <h2 class="toolbar-title">Linh Mục Quản Trị Hạn Mức</h2>
              <span class="count-chip">{{ filteredBudgets.length }} Hạn Định</span>
            </div>

            <!-- Legend Pills (Desktop) -->
            <div class="status-legend-group">
              <span class="legend-item text-danger">
                <span class="legend-dot bg-danger"></span> ≥100%
              </span>
              <span class="legend-item text-gold">
                <span class="legend-dot bg-gold"></span> ≥80%
              </span>
              <span class="legend-item text-jade">
                <span class="legend-dot bg-jade"></span> &lt;80%
              </span>
            </div>
          </div>

          <div class="toolbar-actions-row">
            <!-- Search Input -->
            <div class="search-input-wrap">
              <span class="material-symbols-outlined search-icon">search</span>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Tìm linh mục chi tiêu..."
                class="stitch-search-input"
              />
              <button
                v-if="searchQuery"
                type="button"
                class="search-clear-btn"
                @click="searchQuery = ''"
                title="Xóa tìm kiếm"
              >
                ✕
              </button>
            </div>

            <!-- Status Filter Pills -->
            <div class="filter-pills-row">
              <button
                type="button"
                class="filter-pill"
                :class="{ active: activeFilter === 'ALL' }"
                @click="activeFilter = 'ALL'"
              >
                Tất cả ({{ budgets.length }})
              </button>
              <button
                type="button"
                class="filter-pill pill-error"
                :class="{ active: activeFilter === 'DANGER' }"
                @click="activeFilter = 'DANGER'"
              >
                🔥 Nguy Cấp ({{ dangerCount }})
              </button>
              <button
                type="button"
                class="filter-pill pill-gold"
                :class="{ active: activeFilter === 'WARNING' }"
                @click="activeFilter = 'WARNING'"
              >
                ⚠️ Cảnh Báo ({{ warningCount }})
              </button>
              <button
                type="button"
                class="filter-pill pill-jade"
                :class="{ active: activeFilter === 'SAFE' }"
                @click="activeFilter = 'SAFE'"
              >
                🛡️ An Toàn ({{ safeCount }})
              </button>
            </div>
          </div>
        </div>

        <!-- Budget Cards Grid -->
        <div v-if="filteredBudgets.length" class="budget-cards-grid">
          <div
            v-for="b in filteredBudgets"
            :key="b.id"
            class="spiritual-budget-card"
            :class="getCardStatusClass(b)"
          >
            <!-- Atmospheric Gradient Glow -->
            <div class="card-inner-glow" :class="getGlowClass(b)"></div>

            <div class="card-content-wrap">
              <!-- Top Row: Icon, Category Name, Limit & Status Badge -->
              <div class="card-top-row">
                <div class="category-meta-group">
                  <div class="category-avatar-box" :class="getAvatarClass(b)">
                    <span class="category-icon">{{ b.category_icon || '🎯' }}</span>
                  </div>
                  <div class="category-text-col">
                    <h3 class="category-name">{{ b.category_name || 'Linh Mục Chưa Đặt Tên' }}</h3>
                    <div class="category-limit-subtext">
                      Giới hạn: <strong class="tabular-num">{{ formatVND(b.limit_amount) }}</strong>
                    </div>
                  </div>
                </div>

                <!-- Status Badge -->
                <div class="status-badge" :class="getBadgeClass(b)">
                  <span class="material-symbols-outlined badge-icon">
                    {{ getBudgetStatusIcon(b) }}
                  </span>
                  <span class="badge-text-label">{{ getBudgetStatusLabel(b) }}</span>
                </div>
              </div>

              <!-- Spending Gauge & Figures -->
              <div class="card-spending-section">
                <div class="spending-figures-row">
                  <div class="spent-value-wrap">
                    <span class="spent-amount tabular-num" :class="getSpentTextClass(b)">
                      {{ formatVND(b.spent || 0) }}
                    </span>
                    <span class="spent-currency">₫</span>
                  </div>

                  <div class="spent-pct-wrap" :class="getSpentTextClass(b)">
                    <span class="pct-number tabular-num font-semibold">{{ calculateBudgetPct(b).toFixed(1) }}%</span>
                    <span class="delta-text tabular-num">
                      {{ getDeltaLabel(b) }}
                    </span>
                  </div>
                </div>

                <!-- Custom Progress Bar -->
                <div class="progress-track-wrapper">
                  <div
                    class="progress-fill-bar"
                    :class="getProgressFillClass(b)"
                    :style="{ width: Math.min(100, calculateBudgetPct(b)) + '%' }"
                  ></div>
                </div>
              </div>

              <!-- Contextual Spiritual Alert / Status Box -->
              <div class="spiritual-alert-box" :class="getAlertBoxClass(b)">
                <span class="material-symbols-outlined alert-box-icon">
                  {{ getAlertBoxIcon(b) }}
                </span>
                <p class="alert-box-text">
                  {{ getAlertBoxMessage(b) }}
                </p>
              </div>

              <!-- Card Actions Row -->
              <div class="card-footer-actions">
                <button
                  type="button"
                  class="btn-card-action btn-edit"
                  @click="$emit('open-edit-budget', b)"
                  title="Chỉnh sửa hạn mức này"
                >
                  <span class="material-symbols-outlined icon-xs">tune</span>
                  <span>Điều Chỉnh Hạn Mức</span>
                </button>

                <button
                  type="button"
                  class="btn-card-icon-danger"
                  @click="$emit('delete-budget', b.id)"
                  title="Xóa hạn mức này"
                  aria-label="Xóa hạn mức"
                >
                  <span class="material-symbols-outlined icon-sm">delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="budget-empty-state">
          <div class="empty-icon-box">
            <span class="material-symbols-outlined empty-symbol">shield_with_heart</span>
          </div>
          <h3 class="empty-title">
            {{ searchQuery || activeFilter !== 'ALL' ? 'Không Tìm Thấy Hạn Mức Phù Hợp' : 'Chưa Thiết Lập Hạn Mức Cho Tháng Này' }}
          </h3>
          <p class="empty-desc">
            {{ searchQuery || activeFilter !== 'ALL'
              ? 'Vui lòng kiểm tra lại từ khóa tìm kiếm hoặc chuyển sang bộ lọc khác.'
              : 'Hãy thiết lập giới cương chi tiêu cho từng linh mục để giữ vững chân nguyên ngân khố và ngăn ngừa tâm ma hao tài.' }}
          </p>
          <button
            v-if="!searchQuery && activeFilter === 'ALL'"
            type="button"
            class="btn-stitch-primary"
            @click="focusCreateForm"
          >
            <span class="material-symbols-outlined">add_circle</span>
            <span>+ Thiết Lập Hạn Mức Đầu Tiên</span>
          </button>
          <button
            v-else
            type="button"
            class="btn-stitch-secondary"
            @click="resetFilters"
          >
            <span class="material-symbols-outlined">restart_alt</span>
            <span>Đặt Lại Bộ Lọc</span>
          </button>
        </div>
      </div>

      <!-- ─── RIGHT COLUMN: QUICK SETUP CARD & KHÍ LINH (4 COLS) ─── -->
      <div class="bento-right-col">
        <!-- Quick Formulation / Create Budget Card -->
        <div class="formulation-card" ref="createFormRef" id="budget-formulation-card">
          <div class="form-header-row">
            <div class="form-title-group">
              <div class="form-icon-box">
                <span class="material-symbols-outlined">edit_note</span>
              </div>
              <div>
                <h3 class="form-card-title">Thiết Lập Hạn Mức Mới</h3>
                <span class="form-card-subtitle">Khóa cương thổ tài chính</span>
              </div>
            </div>
            <span class="period-badge">{{ formattedMonthBadge }}</span>
          </div>

          <form class="budget-create-form" @submit.prevent="handleSubmitCreate">
            <!-- Category Select -->
            <div class="form-field-group">
              <label class="field-label" for="budget-category-select">
                <span>Linh Mục Chi Tiêu</span>
                <span class="field-required-hint">Bắt buộc</span>
              </label>
              <div class="select-wrapper">
                <select
                  id="budget-category-select"
                  v-model="budgetForm.category_id"
                  class="stitch-select"
                  required
                >
                  <option :value="null" disabled>— Chọn linh mục chi tiêu —</option>
                  <option
                    v-for="c in expenseCategories"
                    :key="'cat-' + c.id"
                    :value="c.id"
                  >
                    {{ c.icon }} {{ c.category_name }}
                  </option>
                </select>
                <span class="material-symbols-outlined select-chevron">expand_more</span>
              </div>
            </div>

            <!-- Spending Limit Input -->
            <div class="form-field-group">
              <label class="field-label" for="budget-amount-input">
                <span>Mức Giới Hạn Chi Tiêu (VNĐ)</span>
                <span class="field-info-hint">Định mức tháng</span>
              </label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon text-jade">payments</span>
                <input
                  id="budget-amount-input"
                  v-model.number="budgetForm.limit_amount"
                  type="number"
                  placeholder="Ví dụ: 5000000"
                  min="1"
                  step="1000"
                  class="stitch-input-prefixed tabular-num"
                  required
                />
              </div>
            </div>

            <!-- Applicable Month Period (Read-only view synced with budgetMonth) -->
            <div class="form-field-group">
              <label class="field-label" for="budget-period-input">
                <span>Chu Kỳ Áp Dụng</span>
                <span class="field-info-hint">Theo chu kỳ trăng</span>
              </label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon">lock</span>
                <input
                  id="budget-period-input"
                  :value="budgetMonth"
                  type="text"
                  class="stitch-input-prefixed readonly-input"
                  readonly
                />
              </div>
            </div>

            <!-- Policy Disclaimer -->
            <div class="policy-note-card">
              <span class="policy-bold text-jade">Quy Ước Linh Môn:</span>
              <span> Hạn mức độc lập theo từng chu kỳ tháng, không tự động chuyển dồn số dư sang tháng tiếp theo để đảm bảo tính kỷ luật chân nguyên.</span>
            </div>

            <!-- Form Actions -->
            <div class="form-actions-row">
              <button
                type="button"
                class="btn-stitch-secondary"
                @click="resetCreateForm"
                title="Xóa thông tin đã nhập"
              >
                Làm Lại
              </button>

              <button
                type="submit"
                class="btn-stitch-submit"
                :disabled="loading || !budgetForm.category_id || !budgetForm.limit_amount || budgetForm.limit_amount <= 0"
              >
                <span class="material-symbols-outlined icon-sm">shield</span>
                <span>{{ loading ? 'Đang lưu...' : 'Lưu Hạn Mức' }}</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Khí Linh Companion Analytical Box -->
        <div class="companion-wisdom-card">
          <div class="companion-header-row">
            <div class="companion-avatar-wrap">
              <span class="material-symbols-outlined avatar-icon">psychology</span>
              <span class="companion-live-dot"></span>
            </div>
            <div>
              <h4 class="companion-title">Khí Linh Khuyên Dạy</h4>
              <span class="companion-role">Tâm Pháp Điều Tiết Ngân Khố</span>
            </div>
          </div>

          <p class="companion-quote-text">
            {{ companionInsightText }}
          </p>

          <!-- Donut SVG Micro-Chart -->
          <div class="companion-donut-box">
            <div class="donut-chart-wrap">
              <svg class="donut-svg" viewBox="0 0 36 36">
                <!-- Background track -->
                <circle
                  class="donut-track"
                  cx="18"
                  cy="18"
                  r="15"
                ></circle>
                <!-- Progress ring -->
                <circle
                  class="donut-fill"
                  :class="donutStrokeClass"
                  cx="18"
                  cy="18"
                  r="15"
                  :stroke-dasharray="100"
                  :stroke-dashoffset="donutDashOffset"
                ></circle>
              </svg>
              <div class="donut-center-pct tabular-num font-semibold">
                {{ Math.min(100, Math.round(overallSpentPct)) }}%
              </div>
            </div>

            <div class="donut-caption-col">
              <div class="donut-title font-semibold">
                {{ overallSpentPct.toFixed(1) }}% Tổng Cương
              </div>
              <div class="donut-subtitle tabular-num">
                {{ totalRemainingAmount < 0 ? 'Vượt ' + formatVND(Math.abs(totalRemainingAmount)) : formatVND(totalRemainingAmount) + ' khả dụng' }}
              </div>
            </div>

            <span class="material-symbols-outlined spark-icon">auto_awesome</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  budgets: {
    type: Array,
    default: () => []
  },
  budgetMonth: {
    type: String,
    required: true
  },
  expenseCategories: {
    type: Array,
    default: () => []
  },
  budgetForm: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  formatVND: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'update:budget-month',
  'create-budget',
  'open-edit-budget',
  'delete-budget',
  'load-budgets'
])

// UI-only state
const searchQuery = ref('')
const activeFilter = ref('ALL') // 'ALL' | 'DANGER' | 'WARNING' | 'SAFE'
const createFormRef = ref(null)

// ─── MONTH NAVIGATION ───
const now = new Date()
const currentMonthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`

const isCurrentMonth = computed(() => {
  return props.budgetMonth === currentMonthStr
})

const formattedMonthLabel = computed(() => {
  if (!props.budgetMonth) return 'Chu kỳ tháng'
  const [year, month] = props.budgetMonth.split('-')
  return `Tháng ${parseInt(month, 10)}/${year}`
})

const formattedMonthBadge = computed(() => {
  if (!props.budgetMonth) return ''
  const [year, month] = props.budgetMonth.split('-')
  return `Tháng ${month}/${year}`
})

function onMonthInput(e) {
  const val = e.target.value
  if (val) {
    emit('update:budget-month', val)
  }
}

function prevMonth() {
  if (!props.budgetMonth) return
  const [yearStr, monthStr] = props.budgetMonth.split('-')
  let y = parseInt(yearStr, 10)
  let m = parseInt(monthStr, 10) - 1
  if (m < 1) {
    m = 12
    y -= 1
  }
  const newMonth = `${y}-${String(m).padStart(2, '0')}`
  emit('update:budget-month', newMonth)
}

function nextMonth() {
  if (!props.budgetMonth) return
  const [yearStr, monthStr] = props.budgetMonth.split('-')
  let y = parseInt(yearStr, 10)
  let m = parseInt(monthStr, 10) + 1
  if (m > 12) {
    m = 1
    y += 1
  }
  const newMonth = `${y}-${String(m).padStart(2, '0')}`
  emit('update:budget-month', newMonth)
}

function resetToCurrentMonth() {
  emit('update:budget-month', currentMonthStr)
}

// Days remaining calculation
const daysRemainingInMonth = computed(() => {
  if (!props.budgetMonth) return 0
  const [yearStr, monthStr] = props.budgetMonth.split('-')
  const y = parseInt(yearStr, 10)
  const m = parseInt(monthStr, 10)
  const totalDays = new Date(y, m, 0).getDate()

  if (isCurrentMonth.value) {
    const today = now.getDate()
    return Math.max(0, totalDays - today)
  }
  // If in future month
  if (props.budgetMonth > currentMonthStr) {
    return totalDays
  }
  // Past month
  return 0
})

// ─── AGGREGATE CALCULATIONS ───
function calculateBudgetPct(b) {
  if (!b || !b.limit_amount || b.limit_amount <= 0) return 0
  return (Number(b.spent || 0) / Number(b.limit_amount)) * 100
}

const totalBudgetAmount = computed(() => {
  return (props.budgets || []).reduce((sum, b) => sum + Number(b.limit_amount || 0), 0)
})

const totalSpentAmount = computed(() => {
  return (props.budgets || []).reduce((sum, b) => sum + Number(b.spent || 0), 0)
})

const totalRemainingAmount = computed(() => {
  return totalBudgetAmount.value - totalSpentAmount.value
})

const overallSpentPct = computed(() => {
  if (totalBudgetAmount.value <= 0) return 0
  return (totalSpentAmount.value / totalBudgetAmount.value) * 100
})

const overallStatusText = computed(() => {
  if (overallSpentPct.value >= 100) return 'Tẩu Hỏa Nhập Ma'
  if (overallSpentPct.value >= 80) return 'Cảnh Báo Cấp Độ 2'
  return 'Tâm Cảnh An Định'
})

// Status counts
const dangerCount = computed(() => {
  return (props.budgets || []).filter(b => calculateBudgetPct(b) >= 100).length
})

const warningCount = computed(() => {
  return (props.budgets || []).filter(b => {
    const pct = calculateBudgetPct(b)
    return pct >= 80 && pct < 100
  }).length
})

const safeCount = computed(() => {
  return (props.budgets || []).filter(b => calculateBudgetPct(b) < 80).length
})

// Ratios for multi-segment gauge
const totalCount = computed(() => (props.budgets || []).length)

const dangerRatio = computed(() => {
  if (totalCount.value === 0) return 0
  return dangerCount.value / totalCount.value
})

const warningRatio = computed(() => {
  if (totalCount.value === 0) return 0
  return warningCount.value / totalCount.value
})

const safeRatio = computed(() => {
  if (totalCount.value === 0) return 1
  return safeCount.value / totalCount.value
})

// ─── FILTERING & SEARCH ───
const filteredBudgets = computed(() => {
  let list = props.budgets || []

  // Filter by status pill
  if (activeFilter.value === 'DANGER') {
    list = list.filter(b => calculateBudgetPct(b) >= 100)
  } else if (activeFilter.value === 'WARNING') {
    list = list.filter(b => {
      const pct = calculateBudgetPct(b)
      return pct >= 80 && pct < 100
    })
  } else if (activeFilter.value === 'SAFE') {
    list = list.filter(b => calculateBudgetPct(b) < 80)
  }

  // Search by category name
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(b => {
      const name = (b.category_name || '').toLowerCase()
      return name.includes(q)
    })
  }

  return list
})

function resetFilters() {
  searchQuery.value = ''
  activeFilter.value = 'ALL'
}

// ─── CARD STYLING & STATUS HELPERS ───
function getCardStatusClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'status-danger'
  if (pct >= 80) return 'status-warning'
  return 'status-safe'
}

function getGlowClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'glow-error'
  if (pct >= 80) return 'glow-warning'
  return 'glow-safe'
}

function getAvatarClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'avatar-error'
  if (pct >= 80) return 'avatar-warning'
  return 'avatar-safe'
}

function getBadgeClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'badge-danger'
  if (pct >= 80) return 'badge-warning'
  return 'badge-safe'
}

function getBudgetStatusIcon(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'local_fire_department'
  if (pct >= 80) return 'warning'
  return 'check_circle'
}

function getBudgetStatusLabel(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'TẨU HỎA NHẬP MA'
  if (pct >= 80) return 'CẢNH BÁO TÂM MA'
  return 'TÂM CẢNH AN ĐỊNH'
}

function getSpentTextClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'text-danger'
  if (pct >= 80) return 'text-gold'
  return 'text-jade'
}

function getDeltaLabel(b) {
  const spent = Number(b.spent || 0)
  const limit = Number(b.limit_amount || 0)
  if (spent > limit) {
    return `(Vượt ${props.formatVND(spent - limit)})`
  }
  return `(Còn ${props.formatVND(limit - spent)})`
}

function getProgressFillClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'fill-danger'
  if (pct >= 80) return 'fill-warning'
  return 'fill-safe'
}

function getAlertBoxClass(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'box-danger'
  if (pct >= 80) return 'box-warning'
  return 'box-safe'
}

function getAlertBoxIcon(b) {
  const pct = calculateBudgetPct(b)
  if (pct >= 100) return 'error'
  if (pct >= 80) return 'schedule'
  return 'verified'
}

function getAlertBoxMessage(b) {
  const pct = calculateBudgetPct(b)
  const spent = Number(b.spent || 0)
  const limit = Number(b.limit_amount || 0)

  if (pct >= 100) {
    const diff = spent - limit
    return `🔥 TẨU HỎA NHẬP MA! Đã vượt ngưỡng quy định ${props.formatVND(diff)}. Cần hạn chế chi tiêu danh mục này ngay lập tức.`
  }
  if (pct >= 80) {
    const remaining = limit - spent
    return `⚠️ CẢNH BÁO TÂM MA! Đã sử dụng ${pct.toFixed(1)}% hạn mức (còn ${props.formatVND(remaining)}). Cần lưu tâm tiết chế.`
  }
  return `✓ Tâm Cảnh An Định. Tiêu hao trong tầm kiểm soát, chân nguyên ngân khố vững vàng.`
}

// ─── FORM INTERACTIONS ───
function focusCreateForm() {
  if (createFormRef.value) {
    createFormRef.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
    const selectElem = createFormRef.value.querySelector('#budget-category-select')
    if (selectElem) {
      nextTick(() => selectElem.focus())
    }
  }
}

function handleSubmitCreate() {
  if (!props.budgetForm.category_id || !props.budgetForm.limit_amount) return
  // Ensure month_year is assigned from budgetMonth
  props.budgetForm.month_year = props.budgetMonth
  emit('create-budget')
}

function resetCreateForm() {
  props.budgetForm.category_id = null
  props.budgetForm.limit_amount = 0
  props.budgetForm.month_year = props.budgetMonth
}

// ─── KHÍ LINH ADVICE & DONUT GAUGE ───
const companionInsightText = computed(() => {
  const budgetsList = props.budgets || []
  if (!budgetsList.length) {
    return '"Chưa có giới cương nào được thiết lập trong tháng này. Đạo trưởng hãy sớm phân định hạn mức cho các linh mục để tránh tiêu hao bất ngờ."'
  }

  const dangerBudgets = budgetsList.filter(b => calculateBudgetPct(b) >= 100)
  if (dangerBudgets.length > 0) {
    const topDanger = dangerBudgets[0]
    const over = Number(topDanger.spent || 0) - Number(topDanger.limit_amount || 0)
    return `"Đạo trưởng hãy chú tâm mục ${topDanger.category_name} đã phát tác tâm ma vượt ${props.formatVND(over)}. Cần tiết chế ngay lập tức để bảo toàn chân nguyên tài chính!"`
  }

  const warningBudgets = budgetsList.filter(b => {
    const pct = calculateBudgetPct(b)
    return pct >= 80 && pct < 100
  })
  if (warningBudgets.length > 0) {
    const topWarning = warningBudgets[0]
    return `"Linh mục ${topWarning.category_name} đã đạt ${calculateBudgetPct(topWarning).toFixed(0)}% giới cương. Còn ${daysRemainingInMonth.value} ngày trong chu kỳ, đạo trưởng nên cân nhắc tiêu dùng có chừng mực."`
  }

  return '"Mọi linh mục chi tiêu đều đang trong tầm kiềm tỏa an định. Đạo hữu giữ vững kỷ luật chi tiêu sẽ tích lũy được phúc trạch thâm hậu!"'
})

const donutDashOffset = computed(() => {
  const pct = Math.min(100, overallSpentPct.value)
  return 100 - pct
})

const donutStrokeClass = computed(() => {
  if (overallSpentPct.value >= 100) return 'stroke-danger'
  if (overallSpentPct.value >= 80) return 'stroke-gold'
  return 'stroke-jade'
})
</script>

<style scoped>
/* ─── REALM ATMOSPHERE & TOKENS ─── */
.budgets-realm {
  position: relative;
  width: 100%;
  min-height: 100%;
  color: #dae2fd;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  padding-bottom: 2rem;
}

/* Ambient Spiritual Glow Orbs */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.orb-primary {
  top: -20px;
  right: 25%;
  width: 360px;
  height: 360px;
  background: rgba(125, 214, 204, 0.05);
}
.orb-secondary {
  top: 60px;
  left: 5%;
  width: 320px;
  height: 320px;
  background: rgba(68, 65, 115, 0.15);
}

/* Tabular Numerals */
.tabular-num {
  font-variant-numeric: tabular-nums;
}

/* Typography utilities */
.text-jade { color: #7dd6cc; }
.text-gold { color: #e3c370; }
.text-danger { color: #ffb4ab; }
.text-secondary { color: #c4c1fb; }
.text-on-surface-variant { color: #bdc9c6; }
.bg-jade { background-color: #7dd6cc; }
.bg-gold { background-color: #e3c370; }
.bg-danger { background-color: #ffb4ab; }

/* ─── 1. HEADER & ACTION BAR ─── */
.budgets-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 1024px) {
  .budgets-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.header-text-group {
  max-width: 42rem;
}

.header-badge-row {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: #171f33;
  border: 1px solid rgba(125, 214, 204, 0.2);
  margin-bottom: 0.5rem;
}

.status-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: #7dd6cc;
  box-shadow: 0 0 8px rgba(125, 214, 204, 0.8);
  animation: pulse-dot 2s infinite ease-in-out;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.badge-text {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #7dd6cc;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #dae2fd;
  margin: 0;
  line-height: 1.2;
}

@media (min-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
}

.page-subtitle {
  font-size: 0.875rem;
  color: #bdc9c6;
  margin: 0.35rem 0 0 0;
  line-height: 1.5;
}

.header-controls-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* Month Switcher */
.month-switcher-card {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  padding: 0.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.btn-month-nav {
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  background: transparent;
  border: none;
  color: #bdc9c6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-month-nav:hover {
  color: #7dd6cc;
  background: #222a3d;
}

.month-display-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0 0.5rem;
  cursor: pointer;
}

.month-icon {
  font-size: 1.125rem;
  color: #7dd6cc;
}

.month-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #dae2fd;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.hidden-month-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
}

.btn-month-today {
  padding: 0.25rem 0.6rem;
  border-radius: 0.375rem;
  background: rgba(125, 214, 204, 0.12);
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.3);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-month-today:hover {
  background: rgba(125, 214, 204, 0.22);
}

/* Primary Stitch Button */
.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.15rem;
  border-radius: 0.5rem;
  background: #7dd6cc;
  color: #003733;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.btn-stitch-primary:hover {
  background: #9af2e8;
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.5);
}

.btn-stitch-primary:active {
  transform: scale(0.98);
}

/* ─── 2. SUMMARY METRICS ROW (4 CARDS) ─── */
.budget-metrics-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .budget-metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .budget-metrics-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.budget-metric-card {
  position: relative;
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.budget-metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(125, 214, 204, 0.2);
}

.metric-card-glow {
  position: absolute;
  top: -1.5rem;
  right: -1.5rem;
  width: 6rem;
  height: 6rem;
  border-radius: 9999px;
  filter: blur(24px);
  pointer-events: none;
}

.glow-primary { background: rgba(125, 214, 204, 0.12); }
.glow-gold { background: rgba(227, 195, 112, 0.14); }
.glow-error { background: rgba(255, 180, 171, 0.15); }
.glow-secondary { background: rgba(196, 193, 251, 0.12); }

.metric-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.metric-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #bdc9c6;
}

.metric-icon-box {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #222a3d;
}

.icon-jade { color: #7dd6cc; }
.icon-gold { color: #e3c370; }
.icon-error { color: #ffb4ab; }
.icon-indigo { color: #c4c1fb; }

.icon-sm { font-size: 1.125rem; }
.icon-xs { font-size: 0.875rem; }

.metric-body-col {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.metric-value-text {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.metric-submeta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.775rem;
  color: #bdc9c6;
}

.ping-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  display: inline-block;
}

/* Health breakdown in metric 4 */
.health-breakdown-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.health-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.pill-danger { color: #ffb4ab; }
.pill-warning { color: #e3c370; }
.pill-safe { color: #7dd6cc; }

.health-gauge-track {
  width: 100%;
  height: 0.5rem;
  border-radius: 9999px;
  background: #2d3449;
  overflow: hidden;
  display: flex;
}

.health-gauge-segment {
  height: 100%;
  transition: width 0.4s ease;
}

/* ─── 3. MAIN BENTO GRID (8 COLS / 4 COLS) ─── */
.budgets-bento-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1.25rem;
}

@media (min-width: 1024px) {
  .budgets-bento-grid {
    grid-template-columns: repeat(12, minmax(0, 1fr));
  }
}

.bento-left-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

@media (min-width: 1024px) {
  .bento-left-col {
    grid-column: span 8 / span 8;
  }
}

.bento-right-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

@media (min-width: 1024px) {
  .bento-right-col {
    grid-column: span 4 / span 4;
  }
}

/* ─── TOOLBAR & FILTERS ─── */
.budget-toolbar-card {
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.toolbar-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.toolbar-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
}

.count-chip {
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: #222a3d;
  color: #bdc9c6;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-legend-group {
  display: none;
}

@media (min-width: 640px) {
  .status-legend-group {
    display: flex;
    align-items: center;
    gap: 0.875rem;
    font-size: 0.75rem;
  }
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.legend-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
}

.toolbar-actions-row {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .toolbar-actions-row {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.search-input-wrap {
  position: relative;
  flex: 1;
  max-width: 100%;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #bdc9c6;
  font-size: 1.125rem;
  pointer-events: none;
}

.stitch-search-input {
  width: 100%;
  height: 2.35rem;
  padding: 0 2rem 0 2.35rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #dae2fd;
  font-size: 0.875rem;
  box-sizing: border-box;
  transition: border-color 0.15s ease;
}

.stitch-search-input:focus {
  outline: none;
  border-color: #7dd6cc;
}

.search-clear-btn {
  position: absolute;
  right: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #bdc9c6;
  font-size: 0.875rem;
  cursor: pointer;
}

.filter-pills-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.filter-pill {
  padding: 0.35rem 0.65rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid transparent;
  color: #bdc9c6;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.filter-pill:hover {
  color: #dae2fd;
  background: #2d3449;
}

.filter-pill.active {
  background: #449f96;
  color: #00302c;
  font-weight: 600;
  border-color: rgba(125, 214, 204, 0.4);
  box-shadow: 0 0 10px rgba(68, 159, 150, 0.3);
}

.filter-pill.pill-error.active {
  background: #ffb4ab;
  color: #690005;
}

.filter-pill.pill-gold.active {
  background: #e3c370;
  color: #3d2e00;
}

.filter-pill.pill-jade.active {
  background: #7dd6cc;
  color: #003733;
}

/* ─── BUDGET CARDS GRID (1 OR 2 COLS) ─── */
.budget-cards-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 1rem;
}

@media (min-width: 640px) {
  .budget-cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.spiritual-budget-card {
  position: relative;
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.spiritual-budget-card:hover {
  transform: translateY(-2px);
}

.spiritual-budget-card.status-danger {
  border-color: rgba(255, 180, 171, 0.25);
}

.spiritual-budget-card.status-warning {
  border-color: rgba(227, 195, 112, 0.25);
}

.spiritual-budget-card.status-safe {
  border-color: rgba(125, 214, 204, 0.15);
}

.card-inner-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.1;
  transition: opacity 0.2s ease;
}

.spiritual-budget-card:hover .card-inner-glow {
  opacity: 0.18;
}

.glow-error {
  background: radial-gradient(circle at top left, #ffb4ab 0%, transparent 70%);
}

.glow-warning {
  background: radial-gradient(circle at top left, #e3c370 0%, transparent 70%);
}

.glow-safe {
  background: radial-gradient(circle at top left, #7dd6cc 0%, transparent 70%);
}

.card-content-wrap {
  position: relative;
  z-index: 1;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Card Top Row */
.card-top-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.category-meta-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.category-avatar-box {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
}

.avatar-error {
  background: rgba(147, 0, 10, 0.35);
  color: #ffb4ab;
  border: 1px solid rgba(255, 180, 171, 0.2);
}

.avatar-warning {
  background: rgba(198, 168, 88, 0.2);
  color: #e3c370;
  border: 1px solid rgba(227, 195, 112, 0.2);
}

.avatar-safe {
  background: rgba(68, 159, 150, 0.2);
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.2);
}

.category-text-col {
  display: flex;
  flex-direction: column;
}

.category-name {
  font-size: 1rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
  line-height: 1.3;
}

.category-limit-subtext {
  font-size: 0.775rem;
  color: #bdc9c6;
  margin-top: 0.15rem;
}

/* Status Badges */
.status-badge {
  padding: 0.25rem 0.55rem;
  border-radius: 0.375rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  text-transform: uppercase;
  white-space: nowrap;
}

.badge-icon {
  font-size: 0.8125rem;
}

.badge-danger {
  background: rgba(147, 0, 10, 0.6);
  color: #ffdad6;
  border: 1px solid rgba(255, 180, 171, 0.3);
}

.badge-warning {
  background: rgba(198, 168, 88, 0.25);
  color: #ffe08f;
  border: 1px solid rgba(227, 195, 112, 0.3);
}

.badge-safe {
  background: rgba(68, 159, 150, 0.25);
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.3);
}

/* Card Spending Section */
.card-spending-section {
  margin-bottom: 0.875rem;
}

.spending-figures-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 0.45rem;
}

.spent-amount {
  font-size: 1.15rem;
  font-weight: 700;
}

.spent-currency {
  font-size: 0.85rem;
  margin-left: 2px;
}

.spent-pct-wrap {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
  font-size: 0.8125rem;
}

.delta-text {
  font-size: 0.75rem;
  color: #bdc9c6;
}

.progress-track-wrapper {
  width: 100%;
  height: 0.65rem;
  border-radius: 9999px;
  background: #2d3449;
  overflow: hidden;
  padding: 1.5px;
}

.progress-fill-bar {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.fill-danger {
  background: #ffb4ab;
  box-shadow: 0 0 10px rgba(255, 180, 171, 0.5);
}

.fill-warning {
  background: linear-gradient(90deg, #c6a858 0%, #e3c370 100%);
  box-shadow: 0 0 10px rgba(227, 195, 112, 0.4);
}

.fill-safe {
  background: linear-gradient(90deg, #449f96 0%, #7dd6cc 100%);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.4);
}

/* Alert Box inside card */
.spiritual-alert-box {
  border-radius: 0.5rem;
  padding: 0.65rem 0.75rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.775rem;
  line-height: 1.45;
  margin-bottom: 1rem;
}

.alert-box-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.alert-box-text {
  margin: 0;
}

.box-danger {
  background: rgba(147, 0, 10, 0.2);
  border: 1px solid rgba(255, 180, 171, 0.2);
  color: #ffdad6;
}
.box-danger .alert-box-icon { color: #ffb4ab; }

.box-warning {
  background: #222a3d;
  border: 1px solid rgba(227, 195, 112, 0.2);
  color: #dae2fd;
}
.box-warning .alert-box-icon { color: #e3c370; }

.box-safe {
  background: #222a3d;
  border: 1px solid rgba(125, 214, 204, 0.15);
  color: #dae2fd;
}
.box-safe .alert-box-icon { color: #7dd6cc; }

/* Card Footer Actions */
.card-footer-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.5rem;
}

.btn-card-action {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #dae2fd;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-card-action:hover {
  background: #31394d;
  border-color: rgba(125, 214, 204, 0.3);
  color: #7dd6cc;
}

.btn-card-icon-danger {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #bdc9c6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-card-icon-danger:hover {
  background: #93000a;
  color: #ffdad6;
  border-color: #ffb4ab;
}

/* Empty State */
.budget-empty-state {
  background: #171f33;
  border: 1px dashed rgba(125, 214, 204, 0.2);
  border-radius: 0.75rem;
  padding: 3rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.empty-icon-box {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 9999px;
  background: rgba(125, 214, 204, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.empty-symbol {
  font-size: 2rem;
  color: #7dd6cc;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
}

.empty-desc {
  font-size: 0.85rem;
  color: #bdc9c6;
  max-width: 28rem;
  margin: 0;
  line-height: 1.5;
}

/* ─── 4. RIGHT COLUMN (FORMULATION & COMPANION) ─── */
.formulation-card {
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  position: relative;
  overflow: hidden;
}

.form-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1rem;
}

.form-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-icon-box {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background: #449f96;
  color: #00302c;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
  line-height: 1.2;
}

.form-card-subtitle {
  font-size: 0.75rem;
  color: #bdc9c6;
}

.period-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7dd6cc;
  background: rgba(125, 214, 204, 0.1);
  padding: 0.2rem 0.55rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(125, 214, 204, 0.2);
}

.budget-create-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #bdc9c6;
}

.field-required-hint {
  font-size: 0.6875rem;
  color: #7dd6cc;
}

.field-info-hint {
  font-size: 0.6875rem;
  color: #bdc9c6;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.stitch-select {
  width: 100%;
  height: 2.5rem;
  padding: 0 2rem 0 0.875rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #dae2fd;
  font-size: 0.875rem;
  appearance: none;
  cursor: pointer;
  box-sizing: border-box;
}

.stitch-select:focus {
  outline: none;
  border-color: #7dd6cc;
}

.select-chevron {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #bdc9c6;
  font-size: 1.125rem;
  pointer-events: none;
}

.input-with-icon-wrap {
  position: relative;
  width: 100%;
}

.input-prefix-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #bdc9c6;
  font-size: 1.125rem;
  pointer-events: none;
}

.stitch-input-prefixed {
  width: 100%;
  height: 2.5rem;
  padding: 0 0.875rem 0 2.35rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #dae2fd;
  font-size: 0.875rem;
  box-sizing: border-box;
}

.stitch-input-prefixed:focus {
  outline: none;
  border-color: #7dd6cc;
}

.readonly-input {
  background: rgba(34, 42, 61, 0.5);
  color: #bdc9c6;
  cursor: not-allowed;
}

.policy-note-card {
  padding: 0.65rem 0.75rem;
  border-radius: 0.5rem;
  background: rgba(6, 14, 32, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.75rem;
  line-height: 1.45;
  color: #bdc9c6;
}

.policy-bold {
  font-weight: 600;
}

.form-actions-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.25rem;
}

.btn-stitch-secondary {
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #dae2fd;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-stitch-secondary:hover {
  background: #31394d;
  color: #ffffff;
}

.btn-stitch-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 1.25rem;
  border-radius: 0.5rem;
  background: #7dd6cc;
  color: #003733;
  font-size: 0.8125rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 0 12px rgba(125, 214, 204, 0.3);
  transition: all 0.15s ease;
}

.btn-stitch-submit:hover:not(:disabled) {
  background: #9af2e8;
  transform: translateY(-1px);
}

.btn-stitch-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Khí Linh Wisdom Card */
.companion-wisdom-card {
  background: #171f33;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  position: relative;
  overflow: hidden;
}

.companion-header-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.companion-avatar-wrap {
  position: relative;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background: #449f96;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00302c;
  box-shadow: 0 0 14px rgba(68, 159, 150, 0.4);
  flex-shrink: 0;
}

.companion-live-dot {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 9px;
  height: 9px;
  border-radius: 9999px;
  background: #7dd6cc;
  border: 2px solid #171f33;
}

.companion-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
  line-height: 1.2;
}

.companion-role {
  font-size: 0.75rem;
  color: #7dd6cc;
}

.companion-quote-text {
  font-size: 0.8125rem;
  color: #bdc9c6;
  line-height: 1.5;
  margin: 0 0 1rem 0;
  font-style: italic;
}

/* Donut Micro-Chart Box */
.companion-donut-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: #222a3d;
  border-radius: 0.5rem;
}

.donut-chart-wrap {
  position: relative;
  width: 3rem;
  height: 3rem;
  flex-shrink: 0;
}

.donut-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.donut-track {
  fill: none;
  stroke: #2d3449;
  stroke-width: 3;
}

.donut-fill {
  fill: none;
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
}

.stroke-jade { stroke: #7dd6cc; }
.stroke-gold { stroke: #e3c370; }
.stroke-danger { stroke: #ffb4ab; }

.donut-center-pct {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  color: #dae2fd;
}

.donut-caption-col {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 0 0.75rem;
}

.donut-title {
  font-size: 0.8125rem;
  color: #dae2fd;
}

.donut-subtitle {
  font-size: 0.75rem;
  color: #bdc9c6;
}

.spark-icon {
  font-size: 1.25rem;
  color: #7dd6cc;
}
</style>
