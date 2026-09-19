<template>
  <div class="debts-realm">
    <!-- Subtle Ambient Glow Orbs (Atmospheric Tier 0) -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & ACTION BAR ═══ -->
    <section class="debts-page-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">KHẾ ƯỚC MINH BẠCH • TÀI VẬN ĐẠO PHÁP</span>
        </div>
        <h1 class="page-title">Sổ Nợ &amp; Khế Ước (Debts &amp; Loans)</h1>
        <p class="page-subtitle">
          Ghi chép minh bạch các khoản nợ vay và cho vay giữa các đạo hữu, tự động theo dõi thời hạn hoàn tất khế ước.
        </p>
      </div>

      <div class="header-action-group">
        <!-- Toggle Mobile/Drawer Create Form Button -->
        <button
          type="button"
          class="btn-stitch-primary"
          @click="toggleAddForm"
          title="Tạo khế ước nợ mới"
        >
          <span class="material-symbols-outlined">{{ showMobileAddForm ? 'close' : 'add_circle' }}</span>
          <span>{{ showMobileAddForm ? 'Đóng Biểu Mẫu' : '+ Tạo Khế Ước Nợ Mới' }}</span>
        </button>
      </div>
    </section>

    <!-- ═══ SUMMARY STATS ROW (4 METRIC CARDS) ═══ -->
    <section class="debt-metrics-grid" aria-label="Thống kê tổng quan khế ước">
      <!-- Stat 1: Unsettled Borrow (Tôi Nợ) -->
      <div class="debt-metric-card card-borrow">
        <div class="metric-card-glow glow-error"></div>
        <div class="metric-header-row">
          <span class="metric-label">Tổng Vay Chưa Trả</span>
          <div class="metric-icon-box icon-error">
            <span class="material-symbols-outlined icon-sm">south_east</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-danger tabular-num font-bold">
            {{ formatVND(debtsSummary.total_borrow_unsettled || 0) }}
          </div>
          <div class="metric-submeta">
            <span class="ping-dot bg-danger"></span>
            <span>{{ unsettledBorrowCount }} khế ước cần thanh toán</span>
          </div>
        </div>
      </div>

      <!-- Stat 2: Unsettled Lend (Cho Vay) -->
      <div class="debt-metric-card card-lend">
        <div class="metric-card-glow glow-primary"></div>
        <div class="metric-header-row">
          <span class="metric-label">Tổng Cho Vay Chưa Thu</span>
          <div class="metric-icon-box icon-jade">
            <span class="material-symbols-outlined icon-sm">north_east</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-jade tabular-num font-bold">
            {{ formatVND(debtsSummary.total_lend_unsettled || 0) }}
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs text-jade">schedule</span>
            <span>{{ unsettledLendCount }} khế ước đang chờ thu hồi</span>
          </div>
        </div>
      </div>

      <!-- Stat 3: Net Balance (Hiệu Số Nợ Ròng) -->
      <div class="debt-metric-card card-net">
        <div class="metric-card-glow glow-gold"></div>
        <div class="metric-header-row">
          <span class="metric-label">Hiệu Số Nợ Ròng</span>
          <div class="metric-icon-box icon-gold">
            <span class="material-symbols-outlined icon-sm">balance</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div
            class="metric-value-text tabular-num font-bold"
            :class="netBalance >= 0 ? 'text-gold' : 'text-danger'"
          >
            {{ (netBalance > 0 ? '+' : '') + formatVND(netBalance) }}
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs" :class="netBalance >= 0 ? 'text-gold' : 'text-danger'">
              {{ netBalance >= 0 ? 'trending_up' : 'trending_down' }}
            </span>
            <span>{{ netBalance >= 0 ? 'Thặng dư phải thu' : 'Thâm hụt phải trả' }}</span>
          </div>
        </div>
      </div>

      <!-- Stat 4: Settled Total (Đã Tất Toán) -->
      <div class="debt-metric-card card-settled">
        <div class="metric-card-glow glow-secondary"></div>
        <div class="metric-header-row">
          <span class="metric-label">Đã Hoàn Tất Quyết Toán</span>
          <div class="metric-icon-box icon-indigo">
            <span class="material-symbols-outlined icon-sm">verified</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-secondary tabular-num font-bold">
            {{ formatVND((debtsSummary.total_borrow_settled || 0) + (debtsSummary.total_lend_settled || 0)) }}
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs text-secondary">task_alt</span>
            <span>{{ settledCount }} khế ước đã hoàn trả</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ MAIN BENTO CONTENT AREA (8 COLS / 4 COLS) ═══ -->
    <div class="debts-bento-grid">
      <!-- ─── LEFT COLUMN: FILTER & LEDGER TABLE (8 COLS) ─── -->
      <div class="bento-left-col">
        <!-- Filter & Search Bar -->
        <div class="debt-filter-card" aria-label="Bộ lọc khế ước">
          <div class="filter-top-row">
            <!-- Search Counterparty -->
            <div class="search-input-wrap">
              <span class="material-symbols-outlined search-icon">search</span>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Tìm theo tên đạo hữu, ghi chú khế ước..."
                class="stitch-search-input"
              />
            </div>

            <!-- Reset Filter Button -->
            <button
              type="button"
              class="btn-stitch-reset"
              @click="resetFilters"
              title="Đặt lại toàn bộ bộ lọc"
            >
              <span class="material-symbols-outlined icon-sm">restart_alt</span>
              <span>Đặt lại</span>
            </button>
          </div>

          <!-- Dual Filter Tabs Row -->
          <div class="filter-tabs-row">
            <!-- Type Tabs -->
            <div class="tab-pill-group">
              <button
                type="button"
                class="tab-pill-btn"
                :class="{ active: !debtFilter.type }"
                @click="setTypeFilter('')"
              >
                Tất cả khế ước
              </button>
              <button
                type="button"
                class="tab-pill-btn pill-borrow"
                :class="{ active: debtFilter.type === 'BORROW' }"
                @click="setTypeFilter('BORROW')"
              >
                🔴 Tôi Vay Nợ
              </button>
              <button
                type="button"
                class="tab-pill-btn pill-lend"
                :class="{ active: debtFilter.type === 'LEND' }"
                @click="setTypeFilter('LEND')"
              >
                🟢 Tôi Cho Vay
              </button>
            </div>

            <!-- Status Tabs -->
            <div class="tab-pill-group">
              <button
                type="button"
                class="tab-pill-btn"
                :class="{ active: debtFilter.is_settled === '' }"
                @click="setStatusFilter('')"
              >
                Tất cả
              </button>
              <button
                type="button"
                class="tab-pill-btn"
                :class="{ active: debtFilter.is_settled === 0 }"
                @click="setStatusFilter(0)"
              >
                ⏳ Chưa tất toán
              </button>
              <button
                type="button"
                class="tab-pill-btn"
                :class="{ active: debtFilter.is_settled === 1 }"
                @click="setStatusFilter(1)"
              >
                ✅ Đã tất toán
              </button>
            </div>
          </div>
        </div>

        <!-- Ledger Table Panel -->
        <div class="debt-ledger-card" aria-label="Bảng sổ cái khế ước">
          <div class="ledger-header-row">
            <div class="title-with-icon">
              <span class="material-symbols-outlined text-jade">assignment</span>
              <h2 class="ledger-card-title">Danh Sách Khế Ước Nợ Pháp</h2>
            </div>
            <span class="record-counter-tag tabular-num">
              {{ filteredDebts.length }} / {{ debts.length }} bản ghi
            </span>
          </div>

          <!-- Table Container -->
          <div class="table-responsive-wrap">
            <table class="stitch-debt-table">
              <thead>
                <tr>
                  <th scope="col" class="th-index">#</th>
                  <th scope="col" class="th-type">Loại Khế Ước</th>
                  <th scope="col" class="th-partner">Đạo Hữu / Đối Tác</th>
                  <th scope="col" class="th-amount text-right">Linh Thạch</th>
                  <th scope="col" class="th-due">Hạn Trả</th>
                  <th scope="col" class="th-wallet">Ví Liên Kết</th>
                  <th scope="col" class="th-status text-center">Trạng Thái</th>
                  <th scope="col" class="th-actions text-center">Thao Tác</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(debt, idx) in filteredDebts"
                  :key="debt.id"
                  class="debt-table-row"
                  :class="{ 'row-settled': debt.is_settled }"
                >
                  <!-- Index -->
                  <td class="td-index font-label-sm text-muted">
                    {{ idx + 1 }}
                  </td>

                  <!-- Type Badge -->
                  <td class="td-type whitespace-nowrap">
                    <span
                      class="type-pill"
                      :class="debt.debt_type === 'BORROW' ? 'pill-borrow' : 'pill-lend'"
                    >
                      <span class="material-symbols-outlined icon-xs">
                        {{ debt.debt_type === 'BORROW' ? 'call_received' : 'arrow_outward' }}
                      </span>
                      <span>{{ debt.debt_type === 'BORROW' ? 'VAY NỢ' : 'CHO VAY' }}</span>
                    </span>
                  </td>

                  <!-- Partner Info -->
                  <td class="td-partner">
                    <div class="partner-cell-wrap">
                      <div
                        class="partner-avatar"
                        :class="debt.debt_type === 'BORROW' ? 'avatar-borrow' : 'avatar-lend'"
                      >
                        {{ getInitials(debt.person_name) }}
                      </div>
                      <div class="partner-meta min-w-0">
                        <span class="partner-name truncate" :title="debt.person_name">
                          {{ debt.person_name }}
                        </span>
                        <span class="partner-note truncate" :title="debt.note || 'Không có ghi chú'">
                          {{ debt.note || 'Khế ước trực tiếp' }}
                        </span>
                      </div>
                    </div>
                  </td>

                  <!-- Amount -->
                  <td
                    class="td-amount text-right whitespace-nowrap font-currency-table font-bold"
                    :class="debt.debt_type === 'BORROW' ? 'text-danger' : 'text-jade'"
                  >
                    {{ debt.debt_type === 'BORROW' ? '-' : '+' }}{{ formatVND(debt.amount) }}
                  </td>

                  <!-- Due Date -->
                  <td class="td-due whitespace-nowrap">
                    <div class="due-cell-wrap" v-if="debt.due_date">
                      <span
                        class="due-date-text"
                        :class="{ 'text-muted line-through': debt.is_settled }"
                      >
                        {{ debt.due_date }}
                      </span>
                      <span
                        v-if="!debt.is_settled"
                        class="due-badge"
                        :class="getDebtStatusBadgeClass(debt)"
                      >
                        {{ getDebtStatusLabel(debt) }}
                      </span>
                    </div>
                    <span v-else class="text-muted font-body-sm">—</span>
                  </td>

                  <!-- Wallet -->
                  <td class="td-wallet whitespace-nowrap text-muted font-body-sm">
                    <div class="wallet-tag" v-if="debt.wallet_name">
                      <span class="material-symbols-outlined icon-xs text-secondary">
                        account_balance_wallet
                      </span>
                      <span class="truncate max-w-[120px]" :title="debt.wallet_name">
                        {{ debt.wallet_name }}
                      </span>
                    </div>
                    <span v-else class="text-muted">—</span>
                  </td>

                  <!-- Status -->
                  <td class="td-status text-center whitespace-nowrap">
                    <span
                      class="status-chip"
                      :class="debt.is_settled ? 'chip-settled' : 'chip-pending'"
                    >
                      <span class="status-dot" :class="debt.is_settled ? 'dot-settled' : 'dot-pending'"></span>
                      <span>{{ debt.is_settled ? 'Đã tất toán' : 'Chưa tất toán' }}</span>
                    </span>
                  </td>

                  <!-- Actions -->
                  <td class="td-actions text-center whitespace-nowrap">
                    <div class="action-btn-cluster">
                      <!-- Toggle Settle Button -->
                      <button
                        type="button"
                        class="btn-action-settle"
                        :class="getSettleButtonClass(debt)"
                        @click="$emit('toggle-settle-debt', debt)"
                        :title="debt.is_settled ? 'Hoàn tác chưa thanh toán' : (debt.debt_type === 'BORROW' ? 'Đã trả khoản này' : 'Đã thu khoản này')"
                      >
                        <span class="material-symbols-outlined icon-sm">
                          {{ debt.is_settled ? 'undo' : 'check' }}
                        </span>
                        <span class="settle-text">
                          {{ debt.is_settled ? 'Hoàn Tác' : (debt.debt_type === 'BORROW' ? 'Đã Trả' : 'Đã Thu') }}
                        </span>
                      </button>

                      <!-- Edit Button -->
                      <button
                        type="button"
                        class="btn-row-action btn-edit"
                        @click="$emit('open-edit-debt', debt)"
                        title="Chỉnh sửa khế ước"
                      >
                        <span class="material-symbols-outlined icon-sm">edit</span>
                      </button>

                      <!-- Delete Button -->
                      <button
                        type="button"
                        class="btn-row-action btn-delete"
                        @click="$emit('delete-debt', debt.id)"
                        title="Xóa khế ước khỏi sổ"
                      >
                        <span class="material-symbols-outlined icon-sm">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>

                <!-- Empty State -->
                <tr v-if="!filteredDebts.length">
                  <td colspan="8" class="td-empty">
                    <div class="empty-state-wrap">
                      <span class="material-symbols-outlined empty-icon">assignment_late</span>
                      <p>Sổ Nợ đang trống hoặc không có khoản nợ nào phù hợp với bộ lọc...</p>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ─── RIGHT COLUMN: QUICK ADD CONTRACT & GUIDANCE (4 COLS) ─── -->
      <div class="bento-right-col" ref="addFormAnchorRef">
        <!-- Quick Add Contract Box -->
        <div class="quick-add-card" aria-label="Tạo khế ước nợ mới">
          <div class="quick-add-header">
            <div class="title-with-icon">
              <span class="material-symbols-outlined text-jade">history_edu</span>
              <h3 class="quick-add-title">Tạo Khế Ước Mới</h3>
            </div>
            <span class="seal-badge">Ấn Ký</span>
          </div>

          <p class="quick-add-desc">
            Lập văn bản định ước tài chính giữa các tu giả, tính toán linh thạch chuẩn xác.
          </p>

          <form class="quick-add-form" @submit.prevent="$emit('create-debt')">
            <!-- Debt Type Selector -->
            <div class="form-field-group">
              <label class="field-label">Loại Khế Ước</label>
              <div class="type-segmented-control">
                <button
                  type="button"
                  class="segment-btn"
                  :class="{ active: debtForm.debt_type === 'LEND' }"
                  @click="debtForm.debt_type = 'LEND'"
                >
                  <span class="material-symbols-outlined icon-xs">call_made</span>
                  <span>Tôi Cho Vay</span>
                </button>
                <button
                  type="button"
                  class="segment-btn"
                  :class="{ active: debtForm.debt_type === 'BORROW' }"
                  @click="debtForm.debt_type = 'BORROW'"
                >
                  <span class="material-symbols-outlined icon-xs">call_received</span>
                  <span>Tôi Vay Nợ</span>
                </button>
              </div>
            </div>

            <!-- Partner Name -->
            <div class="form-field-group">
              <label class="field-label">Tên Đạo Hữu / Đối Tác</label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon">person</span>
                <input
                  v-model="debtForm.person_name"
                  type="text"
                  placeholder="Nhập tên đạo hữu..."
                  class="stitch-input-prefixed"
                  required
                />
              </div>
            </div>

            <!-- Amount -->
            <div class="form-field-group">
              <label class="field-label">Số Linh Thạch (VNĐ)</label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon text-jade">monetization_on</span>
                <input
                  v-model.number="debtForm.amount"
                  type="number"
                  placeholder="Ví dụ: 5.000.000"
                  min="1"
                  class="stitch-input-prefixed tabular-num"
                  required
                />
              </div>
            </div>

            <!-- Due Date -->
            <div class="form-field-group">
              <label class="field-label">Ngày Hẹn Trả (Tùy chọn)</label>
              <div class="input-with-icon-wrap">
                <span class="material-symbols-outlined input-prefix-icon">calendar_today</span>
                <input
                  v-model="debtForm.due_date"
                  type="date"
                  class="stitch-input-prefixed"
                />
              </div>
            </div>

            <!-- Linked Wallet -->
            <div class="form-field-group">
              <label class="field-label">Ví Nguồn Liên Kết (Tùy chọn)</label>
              <select v-model="debtForm.wallet_id" class="stitch-select">
                <option value="">— Không liên kết —</option>
                <option v-for="w in wallets" :key="'debt-form-w-' + w.id" :value="w.id">
                  {{ w.wallet_name }} ({{ formatVND(w.balance) }})
                </option>
              </select>
            </div>

            <!-- Note -->
            <div class="form-field-group">
              <label class="field-label">Ghi Chú Đạo Sự</label>
              <input
                v-model="debtForm.note"
                type="text"
                placeholder="Ghi chú pháp bảo thế chấp hoặc lý do..."
                class="stitch-input"
              />
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              class="btn-stitch-create-contract"
              :disabled="loading || !debtForm.person_name || !debtForm.amount"
            >
              <span class="material-symbols-outlined">draw</span>
              <span>{{ loading ? 'Đang khắc ấn...' : 'Khắc Ấn Khế Ước' }}</span>
            </button>
          </form>
        </div>

        <!-- Spiritual Guidance / Khí Linh Companion Card -->
        <div class="spiritual-guidance-card">
          <div class="guidance-icon-box">
            <span class="material-symbols-outlined text-secondary">auto_awesome</span>
          </div>
          <div class="guidance-text-wrap">
            <h4 class="guidance-title">Lời Khuyên Của Khí Linh</h4>
            <p class="guidance-desc">
              {{ guidanceMessage }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  debts: {
    type: Array,
    default: () => []
  },
  debtsSummary: {
    type: Object,
    default: () => ({
      total_borrow_unsettled: 0,
      total_lend_unsettled: 0,
      total_borrow_settled: 0,
      total_lend_settled: 0
    })
  },
  debtFilter: {
    type: Object,
    required: true
  },
  debtForm: {
    type: Object,
    required: true
  },
  wallets: {
    type: Array,
    default: () => []
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
  'create-debt',
  'delete-debt',
  'open-edit-debt',
  'toggle-settle-debt',
  'load-debts'
])

// UI-only search state
const searchQuery = ref('')
const showMobileAddForm = ref(false)
const addFormAnchorRef = ref(null)

// Computed counts
const unsettledBorrowCount = computed(() => {
  return (props.debts || []).filter(d => d.debt_type === 'BORROW' && !d.is_settled).length
})

const unsettledLendCount = computed(() => {
  return (props.debts || []).filter(d => d.debt_type === 'LEND' && !d.is_settled).length
})

const settledCount = computed(() => {
  return (props.debts || []).filter(d => d.is_settled).length
})

const netBalance = computed(() => {
  const lend = Number(props.debtsSummary.total_lend_unsettled || 0)
  const borrow = Number(props.debtsSummary.total_borrow_unsettled || 0)
  return lend - borrow
})

// Search filtered list (local fast search while backend filters by type/status)
const filteredDebts = computed(() => {
  const list = props.debts || []
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return list
  return list.filter(d => {
    const nameMatch = d.person_name && d.person_name.toLowerCase().includes(q)
    const noteMatch = d.note && d.note.toLowerCase().includes(q)
    const walletMatch = d.wallet_name && d.wallet_name.toLowerCase().includes(q)
    return nameMatch || noteMatch || walletMatch
  })
})

// Dynamic guidance text based on overdue/unsettled state
const guidanceMessage = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  const overdueList = (props.debts || []).filter(d => !d.is_settled && d.due_date && d.due_date < today)
  if (overdueList.length > 0) {
    const first = overdueList[0]
    return `Khế ước với ${first.person_name} đã quá hạn. Đạo hữu nên chủ động đối soát thu chi để bảo đảm linh khí tài khố vẹn toàn.`
  }
  if (unsettledLendCount.value > 0) {
    return `Hiện có ${unsettledLendCount.value} khế ước cho vay đang trong kỳ hạn. Hãy định kỳ rà soát ngày đáo hạn để điều hòa dòng tiền.`
  }
  return 'Linh mạch nợ pháp đang ở trạng thái an định. Mọi khế ước đều được lưu vết minh bạch trong Càn Khôn Các.'
})

// Filter actions
function setTypeFilter(type) {
  props.debtFilter.type = type
  emit('load-debts')
}

function setStatusFilter(status) {
  props.debtFilter.is_settled = status
  emit('load-debts')
}

function resetFilters() {
  searchQuery.value = ''
  props.debtFilter.type = ''
  props.debtFilter.is_settled = ''
  emit('load-debts')
}

function toggleAddForm() {
  showMobileAddForm.value = !showMobileAddForm.value
  nextTick(() => {
    if (addFormAnchorRef.value?.scrollIntoView) {
      addFormAnchorRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

// Helpers
function getInitials(name) {
  if (!name) return 'ĐH'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

function getDebtStatusLabel(debt) {
  if (debt.is_settled) return 'Đã Tất Toán'
  if (!debt.due_date) return 'Chưa Đặt Hạn'
  const today = new Date().toISOString().split('T')[0]
  if (debt.due_date < today) {
    const diffTime = Math.abs(new Date(today) - new Date(debt.due_date))
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return `Quá hạn ${diffDays} ngày`
  } else if (debt.due_date === today) {
    return 'Hôm nay đến hạn'
  } else {
    const diffTime = new Date(debt.due_date) - new Date(today)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return `Còn ${diffDays} ngày`
  }
}

function getDebtStatusBadgeClass(debt) {
  if (debt.is_settled) return 'badge-settled'
  if (!debt.due_date) return 'badge-neutral'
  const today = new Date().toISOString().split('T')[0]
  if (debt.due_date < today) return 'badge-overdue'
  if (debt.due_date === today) return 'badge-today'
  return 'badge-pending'
}

function getSettleButtonClass(debt) {
  if (debt.is_settled) return 'settle-undo'
  if (debt.debt_type === 'BORROW') return 'settle-borrow'
  return 'settle-lend'
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC — DEBTS VIEW (STITCH CELESTIAL LEDGER)
   ═══════════════════════════════════════════════════════════════════════════ */

.debts-realm {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 24px);
  width: 100%;
}

/* ─── AMBIENT GLOW ORBS ─── */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
}

.orb-primary {
  top: -60px;
  right: 15%;
  width: 440px;
  height: 260px;
  background: rgba(125, 214, 204, 0.08);
}

.orb-secondary {
  top: 360px;
  left: -80px;
  width: 380px;
  height: 300px;
  background: rgba(196, 193, 251, 0.06);
}

/* ─── HEADER & ACTION BAR ─── */
.debts-page-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-md, 16px);
}

@media (min-width: 1024px) {
  .debts-page-header {
    flex-direction: row;
    align-items: flex-end;
  }
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 6px);
}

.header-badge-row {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs, 8px);
}

.status-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: var(--primary, #7dd6cc);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.8);
  animation: pulse-glow 2s infinite ease-in-out;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.badge-text {
  font-family: var(--font-label-sm, 'Inter', sans-serif);
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--primary, #7dd6cc);
  text-transform: uppercase;
}

.page-title {
  font-family: var(--font-headline-lg, 'Inter', sans-serif);
  font-size: clamp(24px, 3vw, 32px);
  font-weight: 700;
  color: var(--on-surface, #dae2fd);
  letter-spacing: -0.02em;
  line-height: 1.25;
  margin: 0;
}

.page-subtitle {
  font-family: var(--font-body-md, 'Inter', sans-serif);
  font-size: var(--text-body-md, 14px);
  color: var(--on-surface-variant, #bdc9c6);
  max-width: 680px;
  line-height: 1.5;
  margin: 0;
}

.header-action-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 10px);
}

.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs, 8px);
  padding: 10px 18px;
  background: var(--primary, #7dd6cc);
  color: var(--on-primary, #003733);
  font-family: var(--font-label-lg, 'Inter', sans-serif);
  font-size: var(--text-label-lg, 14px);
  font-weight: 600;
  border-radius: var(--radius-xl, 12px);
  border: 1px solid rgba(125, 214, 204, 0.4);
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.3);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-stitch-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 24px rgba(125, 214, 204, 0.45);
  background: var(--primary-container, #449f96);
  color: var(--on-primary-container, #00302c);
}

.btn-stitch-primary:active {
  transform: translateY(0);
}

/* ─── SUMMARY STATS ROW (4 METRIC CARDS) ─── */
.debt-metrics-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-md, 18px);
}

.debt-metric-card {
  position: relative;
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-xl, 14px);
  padding: var(--space-lg, 20px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-sm, 12px);
  overflow: hidden;
  transition: all 0.25s ease;
}

.debt-metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
}

.metric-card-glow {
  position: absolute;
  top: -24px;
  right: -24px;
  width: 90px;
  height: 90px;
  border-radius: 9999px;
  filter: blur(28px);
  pointer-events: none;
  opacity: 0.25;
}

.glow-error { background: #ffb4ab; }
.glow-primary { background: var(--primary, #7dd6cc); }
.glow-gold { background: var(--tertiary, #e3c370); }
.glow-secondary { background: var(--secondary, #c4c1fb); }

.metric-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-label {
  font-size: var(--text-label-md, 13px);
  color: var(--on-surface-variant, #bdc9c6);
  font-weight: 500;
}

.metric-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-error {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.icon-jade {
  background: rgba(125, 214, 204, 0.15);
  color: var(--primary, #7dd6cc);
}

.icon-gold {
  background: rgba(227, 195, 112, 0.15);
  color: var(--tertiary, #e3c370);
}

.icon-indigo {
  background: rgba(196, 193, 251, 0.15);
  color: var(--secondary, #c4c1fb);
}

.metric-body-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-value-text {
  font-size: 24px;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.metric-submeta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
}

.ping-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  flex-shrink: 0;
}

.bg-danger {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.8);
}

/* ─── BENTO GRID LAYOUT ─── */
.debts-bento-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg, 24px);
  align-items: start;
}

@media (min-width: 1024px) {
  .debts-bento-grid {
    grid-template-columns: 8fr 4fr;
  }
}

.bento-left-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 18px);
}

.bento-right-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 18px);
}

/* ─── FILTER & SEARCH BAR ─── */
.debt-filter-card {
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-xl, 14px);
  padding: var(--space-md, 16px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm, 12px);
}

.filter-top-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs, 10px);
}

.search-input-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: var(--on-surface-variant, #bdc9c6);
  pointer-events: none;
}

.stitch-search-input {
  width: 100%;
  height: 40px;
  padding-left: 38px;
  padding-right: 14px;
  background: var(--surface-container, #171f33);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 10px);
  color: var(--on-surface, #dae2fd);
  font-size: var(--text-body-md, 14px);
  font-family: inherit;
  transition: all 0.2s ease;
}

.stitch-search-input:focus {
  outline: none;
  border-color: var(--primary, #7dd6cc);
  background: var(--surface-container-high, #222a3d);
}

.btn-stitch-reset {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-lg, 10px);
  background: var(--surface-container, #171f33);
  color: var(--on-surface-variant, #bdc9c6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: var(--text-label-md, 13px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-reset:hover {
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface, #dae2fd);
}

.filter-tabs-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xs, 10px);
  padding-top: 4px;
}

.tab-pill-group {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--surface-container, #171f33);
  padding: 3px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.tab-pill-btn {
  padding: 5px 12px;
  border-radius: 6px;
  font-size: var(--text-label-sm, 12px);
  font-weight: 500;
  color: var(--on-surface-variant, #bdc9c6);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-pill-btn:hover {
  color: var(--on-surface, #dae2fd);
}

.tab-pill-btn.active {
  background: var(--surface-container-high, #222a3d);
  color: var(--primary, #7dd6cc);
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.tab-pill-btn.pill-borrow.active {
  color: #ef4444;
}

.tab-pill-btn.pill-lend.active {
  color: var(--primary, #7dd6cc);
}

/* ─── DEBT LEDGER TABLE CARD ─── */
.debt-ledger-card {
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ledger-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md, 16px) var(--space-lg, 20px);
  background: var(--surface-container, #171f33);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 8px);
}

.ledger-card-title {
  font-size: var(--text-title-md, 16px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.record-counter-tag {
  font-size: var(--text-label-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--surface-container-high, #222a3d);
}

.table-responsive-wrap {
  width: 100%;
  overflow-x: auto;
}

.stitch-debt-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.stitch-debt-table thead tr {
  background: rgba(34, 42, 61, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.stitch-debt-table th {
  padding: 12px 14px;
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
  color: var(--on-surface-variant, #bdc9c6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stitch-debt-table td {
  padding: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  vertical-align: middle;
}

.debt-table-row {
  transition: background 0.15s ease;
}

.debt-table-row:hover {
  background: rgba(34, 42, 61, 0.45);
}

.debt-table-row.row-settled {
  opacity: 0.72;
}

/* Type Pill */
.type-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
}

.pill-borrow {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.pill-lend {
  background: rgba(125, 214, 204, 0.15);
  color: var(--primary, #7dd6cc);
}

/* Partner Cell */
.partner-cell-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.partner-avatar {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.avatar-borrow {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.avatar-lend {
  background: rgba(125, 214, 204, 0.2);
  color: var(--primary, #7dd6cc);
}

.partner-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.partner-name {
  font-size: var(--text-title-sm, 14px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
}

.partner-note {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  max-width: 180px;
}

/* Due Date Cell */
.due-cell-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.due-date-text {
  font-size: var(--text-body-md, 13px);
  color: var(--on-surface, #dae2fd);
}

.due-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  max-width: fit-content;
}

.badge-overdue {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  animation: pulse-glow 2s infinite;
}

.badge-today {
  background: rgba(227, 195, 112, 0.2);
  color: var(--tertiary, #e3c370);
}

.badge-pending {
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface-variant, #bdc9c6);
}

.badge-neutral {
  background: var(--surface-container, #171f33);
  color: var(--on-surface-variant, #bdc9c6);
}

/* Wallet Tag */
.wallet-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Status Chip */
.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 500;
}

.chip-pending {
  background: var(--surface-container-highest, #2d3449);
  color: var(--on-surface-variant, #bdc9c6);
}

.chip-settled {
  background: rgba(125, 214, 204, 0.15);
  color: var(--primary, #7dd6cc);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
}

.dot-pending { background: #e3c370; }
.dot-settled { background: #7dd6cc; }

/* Action Buttons */
.action-btn-cluster {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-action-settle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 28px;
  padding: 0 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.settle-lend {
  background: rgba(125, 214, 204, 0.18);
  color: var(--primary, #7dd6cc);
}

.settle-lend:hover {
  background: var(--primary, #7dd6cc);
  color: var(--on-primary, #003733);
}

.settle-borrow {
  background: rgba(239, 68, 68, 0.18);
  color: #ef4444;
}

.settle-borrow:hover {
  background: #ef4444;
  color: #ffffff;
}

.settle-undo {
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface-variant, #bdc9c6);
}

.settle-undo:hover {
  background: var(--surface-bright, #31394d);
  color: var(--on-surface, #dae2fd);
}

.btn-row-action {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-container, #171f33);
  color: var(--on-surface-variant, #bdc9c6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-row-action:hover {
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface, #dae2fd);
}

.btn-row-action.btn-delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
}

/* Empty Table */
.td-empty {
  padding: 48px 16px !important;
  text-align: center;
}

.empty-state-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--on-surface-variant, #bdc9c6);
}

.empty-icon {
  font-size: 32px;
  opacity: 0.6;
}

/* ─── QUICK ADD CONTRACT (RIGHT 4 COLS) ─── */
.quick-add-card {
  position: relative;
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 14px);
  padding: var(--space-lg, 22px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.quick-add-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  border-radius: 9999px;
  background: rgba(125, 214, 204, 0.08);
  filter: blur(28px);
  pointer-events: none;
}

.quick-add-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.quick-add-title {
  font-size: var(--text-title-md, 16px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.seal-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--primary, #7dd6cc);
  background: var(--surface-container, #171f33);
  padding: 2px 8px;
  border-radius: 9999px;
  border: 1px solid rgba(125, 214, 204, 0.3);
}

.quick-add-desc {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  line-height: 1.4;
  margin-bottom: var(--space-md, 16px);
}

.quick-add-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm, 12px);
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-label {
  font-size: var(--text-label-sm, 12px);
  font-weight: 500;
  color: var(--on-surface-variant, #bdc9c6);
}

/* Type Segmented Control */
.type-segmented-control {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  background: var(--surface-container, #171f33);
  padding: 4px;
  border-radius: var(--radius-lg, 10px);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.segment-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 4px;
  border-radius: 7px;
  background: transparent;
  color: var(--on-surface-variant, #bdc9c6);
  font-size: var(--text-label-md, 13px);
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.segment-btn:hover {
  color: var(--on-surface, #dae2fd);
}

.segment-btn.active {
  background: var(--primary-container, #449f96);
  color: var(--on-primary-container, #00302c);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(68, 159, 150, 0.3);
}

.input-with-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-prefix-icon {
  position: absolute;
  left: 12px;
  font-size: 18px;
  color: var(--on-surface-variant, #bdc9c6);
  pointer-events: none;
}

.stitch-input-prefixed {
  width: 100%;
  height: 42px;
  padding-left: 38px;
  padding-right: 12px;
  background: var(--surface-container, #171f33);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 10px);
  color: var(--on-surface, #dae2fd);
  font-size: var(--text-body-md, 13px);
  font-family: inherit;
  transition: all 0.2s ease;
}

.stitch-input-prefixed:focus {
  outline: none;
  border-color: var(--primary, #7dd6cc);
  background: var(--surface-container-high, #222a3d);
}

.stitch-input,
.stitch-select {
  width: 100%;
  height: 42px;
  padding: 0 12px;
  background: var(--surface-container, #171f33);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 10px);
  color: var(--on-surface, #dae2fd);
  font-size: var(--text-body-md, 13px);
  font-family: inherit;
  transition: all 0.2s ease;
}

.stitch-input:focus,
.stitch-select:focus {
  outline: none;
  border-color: var(--primary, #7dd6cc);
  background: var(--surface-container-high, #222a3d);
}

.btn-stitch-create-contract {
  margin-top: 4px;
  width: 100%;
  height: 44px;
  border-radius: var(--radius-lg, 10px);
  background: var(--primary, #7dd6cc);
  color: var(--on-primary, #003733);
  font-family: var(--font-label-lg, 'Inter', sans-serif);
  font-size: var(--text-label-lg, 14px);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid rgba(125, 214, 204, 0.4);
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.25);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-create-contract:hover:not(:disabled) {
  background: var(--primary-container, #449f96);
  color: var(--on-primary-container, #00302c);
  transform: translateY(-1px);
}

.btn-stitch-create-contract:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

/* ─── SPIRITUAL GUIDANCE CARD ─── */
.spiritual-guidance-card {
  background: rgba(196, 193, 251, 0.08);
  border: 1px solid rgba(196, 193, 251, 0.15);
  border-radius: var(--radius-xl, 14px);
  padding: var(--space-md, 16px);
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm, 12px);
}

.guidance-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(196, 193, 251, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.guidance-text-wrap {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.guidance-title {
  font-size: var(--text-title-sm, 13px);
  font-weight: 600;
  color: var(--secondary, #c4c1fb);
  margin: 0;
}

.guidance-desc {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  line-height: 1.45;
  margin: 0;
}

/* ─── UTILITIES ─── */
.text-jade { color: var(--primary, #7dd6cc); }
.text-secondary { color: var(--secondary, #c4c1fb); }
.text-gold { color: var(--tertiary, #e3c370); }
.text-danger { color: #ef4444; }
.text-muted { color: var(--on-surface-variant, #bdc9c6); }
.tabular-num { font-variant-numeric: tabular-nums; }
.font-bold { font-weight: 700; }
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.whitespace-nowrap { white-space: nowrap; }
.icon-xs { font-size: 14px !important; }
.icon-sm { font-size: 18px !important; }
.line-through { text-decoration: line-through; }
</style>
