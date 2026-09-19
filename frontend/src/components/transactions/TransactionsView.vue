<template>
  <div class="transactions-realm">
    <!-- Subtle Ambient Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & ACTION BAR ═══ -->
    <section class="txn-page-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">SỔ NHẬT KÝ NGÂN THẠCH</span>
        </div>
        <h1 class="page-title">Sổ Giao Dịch Càn Khôn</h1>
        <p class="page-subtitle">
          Theo dõi dòng tiền thu chi minh bạch, tự động kết toán chu kỳ pháp bảo và bảo lưu hoàn nguyên số dư.
        </p>
      </div>

      <div class="header-action-group">
        <!-- Toggle Recurring Tray Button -->
        <button
          type="button"
          class="btn-stitch-secondary"
          :class="{ active: showRecurringTray }"
          @click="showRecurringTray = !showRecurringTray"
          title="Xem danh sách giao dịch định kỳ"
        >
          <span class="material-symbols-outlined icon-tertiary">schedule</span>
          <span>Giao Dịch Định Kỳ</span>
          <span class="count-pill">{{ activeRecurringCount }} đang chạy</span>
        </button>

        <!-- Toggle Add Transaction Form Button -->
        <button
          type="button"
          class="btn-stitch-primary"
          @click="showAddForm = !showAddForm"
          title="Mở form thêm giao dịch mới"
        >
          <span class="material-symbols-outlined">{{ showAddForm ? 'close' : 'add' }}</span>
          <span>{{ showAddForm ? 'Đóng Biểu Mẫu' : 'Thêm Giao Dịch Mới' }}</span>
        </button>

        <!-- Export Dropdown / Action Buttons -->
        <div class="export-btn-group">
          <button
            type="button"
            class="btn-stitch-export btn-excel"
            @click="$emit('export-reports', 'excel')"
            title="Xuất báo cáo Excel"
          >
            <span class="material-symbols-outlined icon-sm">table_view</span>
            <span>Excel</span>
          </button>
          <button
            type="button"
            class="btn-stitch-export btn-csv"
            @click="$emit('export-reports', 'csv')"
            title="Xuất báo cáo CSV"
          >
            <span class="material-symbols-outlined icon-sm">description</span>
            <span>CSV</span>
          </button>
        </div>
      </div>
    </section>

    <!-- ═══ RECURRING TRANSACTIONS COLLAPSIBLE TRAY ═══ -->
    <transition name="tray-expand">
      <section v-if="showRecurringTray" class="recurring-tray-card" aria-label="Giao dịch định kỳ">
        <div class="tray-header">
          <div class="tray-title-group">
            <span class="material-symbols-outlined icon-jade">autorenew</span>
            <div>
              <h2 class="tray-title">Định Kỳ Pháp Trận (Tự Động Kết Toán)</h2>
              <p class="tray-desc">Lệnh chuyển dời linh thạch tự động được thi triển đúng ngày hẹn</p>
            </div>
          </div>
          <div class="tray-header-actions">
            <button
              type="button"
              class="btn-text-toggle"
              @click="showAddRecurringForm = !showAddRecurringForm"
            >
              <span class="material-symbols-outlined icon-xs">
                {{ showAddRecurringForm ? 'remove' : 'add' }}
              </span>
              <span>{{ showAddRecurringForm ? 'Ẩn Biểu Mẫu' : 'Thêm Định Kỳ' }}</span>
            </button>
            <button
              type="button"
              class="btn-icon-close"
              @click="showRecurringTray = false"
              title="Đóng khay định kỳ"
            >
              <span class="material-symbols-outlined">keyboard_arrow_up</span>
            </button>
          </div>
        </div>

        <!-- Add Recurring Form -->
        <div v-if="showAddRecurringForm" class="add-recurring-form-wrap">
          <div class="form-grid">
            <div class="input-col">
              <label class="input-label">Loại</label>
              <select v-model="recurringForm.transaction_type" class="stitch-select">
                <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
                <option value="INCOME">💎 Thu Hoạch (Thu)</option>
              </select>
            </div>
            <div class="input-col">
              <label class="input-label">Số Tiền (VNĐ)</label>
              <input
                v-model.number="recurringForm.amount"
                type="number"
                placeholder="0"
                min="0"
                class="stitch-input tabular-num"
              />
            </div>
            <div class="input-col">
              <label class="input-label">Túi Càn Khôn (Ví)</label>
              <select v-model="recurringForm.wallet_id" class="stitch-select">
                <option v-for="w in wallets" :key="'rec-w-' + w.id" :value="w.id">
                  {{ w.wallet_name }}
                </option>
              </select>
            </div>
            <div class="input-col">
              <label class="input-label">Danh Mục</label>
              <select v-model="recurringForm.category_id" class="stitch-select">
                <option
                  v-for="c in filteredRecurringCategories"
                  :key="'rec-c-' + c.id"
                  :value="c.id"
                >
                  {{ c.icon }} {{ c.category_name }}
                </option>
              </select>
            </div>
            <div class="input-col">
              <label class="input-label">Tần Suất</label>
              <select v-model="recurringForm.frequency" class="stitch-select">
                <option value="monthly">📅 Hàng Tháng</option>
                <option value="weekly">📆 Hàng Tuần</option>
              </select>
            </div>
            <div class="input-col">
              <label class="input-label">Kỳ Chạy Kế Tiếp</label>
              <input v-model="recurringForm.next_run_date" type="date" class="stitch-input" />
            </div>
            <div class="input-col col-span-full">
              <label class="input-label">Ghi Chú</label>
              <input
                v-model="recurringForm.note"
                type="text"
                placeholder="VD: Tiền trọ hàng tháng, Lương định kỳ..."
                class="stitch-input"
              />
            </div>
          </div>
          <button
            type="button"
            class="btn-stitch-primary mt-space-md"
            @click="$emit('create-recurring')"
            :disabled="loading"
          >
            <span class="material-symbols-outlined">auto_fix_high</span>
            <span>{{ loading ? 'Đang khởi tạo...' : 'Khởi Tạo Linh Trận Định Kỳ' }}</span>
          </button>
        </div>

        <!-- Recurring Items Grid -->
        <div class="recurring-grid" v-if="recurringList.length">
          <div
            v-for="rec in recurringList"
            :key="rec.id"
            class="recurring-item-card"
          >
            <div class="rec-left min-w-0">
              <div
                class="rec-icon-box shrink-0"
                :class="rec.transaction_type === 'INCOME' ? 'icon-income' : 'icon-expense'"
              >
                <span class="material-symbols-outlined">
                  {{ rec.transaction_type === 'INCOME' ? 'payments' : 'autorenew' }}
                </span>
              </div>
              <div class="rec-meta min-w-0">
                <span class="rec-note truncate" :title="rec.note || rec.category_name">
                  {{ rec.note || rec.category_name }}
                </span>
                <div class="rec-submeta">
                  <span
                    class="tabular-num font-semibold"
                    :class="rec.transaction_type === 'INCOME' ? 'text-income' : 'text-on-surface'"
                  >
                    {{ formatVND(rec.amount) }}
                  </span>
                  <span class="sep">•</span>
                  <span>{{ rec.frequency === 'weekly' ? 'Hàng Tuần' : 'Hàng Tháng' }}</span>
                  <span class="sep">•</span>
                  <span class="text-tertiary">Kế tiếp: {{ rec.next_run_date }}</span>
                </div>
              </div>
            </div>

            <div class="rec-actions shrink-0">
              <button
                type="button"
                class="btn-icon-action"
                :class="rec.is_active ? 'btn-active' : 'btn-paused'"
                @click="$emit('toggle-recurring', rec)"
                :title="rec.is_active ? 'Tạm dừng linh trận' : 'Kích hoạt linh trận'"
              >
                <span class="material-symbols-outlined icon-sm">
                  {{ rec.is_active ? 'pause' : 'play_arrow' }}
                </span>
              </button>
              <button
                type="button"
                class="btn-icon-action btn-edit"
                @click="$emit('edit-recurring', rec)"
                title="Chỉnh sửa pháp lệnh"
              >
                <span class="material-symbols-outlined icon-sm">edit</span>
              </button>
              <button
                type="button"
                class="btn-icon-action btn-delete"
                @click="$emit('delete-recurring', rec.id)"
                title="Giải trừ định kỳ"
              >
                <span class="material-symbols-outlined icon-sm">delete</span>
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-tray-state">
          <span class="material-symbols-outlined empty-icon">schedule</span>
          <p>Chưa có linh trận định kỳ nào được thiết lập...</p>
        </div>
      </section>
    </transition>

    <!-- ═══ QUICK TRANSACTION FORM (COLLAPSIBLE / TOGGLEABLE) ═══ -->
    <transition name="tray-expand">
      <section v-if="showAddForm" class="txn-form-card" aria-label="Ghi nhận giao dịch">
        <div class="form-header">
          <div class="title-with-icon">
            <span class="material-symbols-outlined text-jade">edit_note</span>
            <h2 class="form-title">Ghi Nhận Giao Dịch Linh Thạch</h2>
          </div>
          <button
            type="button"
            class="btn-icon-close"
            @click="showAddForm = false"
            title="Đóng biểu mẫu"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="form-grid">
          <div class="input-col">
            <label class="input-label">Loại Giao Dịch</label>
            <select v-model="txnForm.transaction_type" class="stitch-select">
              <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
              <option value="INCOME">💎 Thu Hoạch (Thu)</option>
            </select>
          </div>

          <div class="input-col">
            <label class="input-label">Số Linh Thạch (VNĐ)</label>
            <input
              v-model.number="txnForm.amount"
              type="number"
              placeholder="0"
              min="0"
              class="stitch-input tabular-num"
            />
          </div>

          <div class="input-col">
            <label class="input-label">Túi Càn Khôn (Ví)</label>
            <select v-model="txnForm.wallet_id" class="stitch-select">
              <option v-for="w in wallets" :key="'form-w-' + w.id" :value="w.id">
                {{ w.wallet_name }}
              </option>
            </select>
          </div>

          <div class="input-col">
            <label class="input-label">Danh Mục</label>
            <select v-model="txnForm.category_id" class="stitch-select">
              <option
                v-for="c in filteredCategories"
                :key="'form-c-' + c.id"
                :value="c.id"
              >
                {{ c.icon }} {{ c.category_name }}
              </option>
            </select>
          </div>

          <div class="input-col">
            <label class="input-label">Ngày Giao Dịch</label>
            <input v-model="txnForm.transaction_date" type="date" class="stitch-input" />
          </div>

          <div class="input-col">
            <label class="input-label">Ghi Chú</label>
            <input
              v-model="txnForm.note"
              type="text"
              placeholder="Mô tả giao dịch..."
              class="stitch-input"
            />
          </div>
        </div>

        <div class="form-footer">
          <button
            type="button"
            class="btn-stitch-primary"
            @click="$emit('create-transaction')"
            :disabled="loading"
          >
            <span class="material-symbols-outlined">bolt</span>
            <span>{{ loading ? 'Đang ghi nhận...' : 'Khắc Ghi Biến Động' }}</span>
          </button>
        </div>
      </section>
    </transition>

    <!-- ═══ FILTER & SEARCH BAR ═══ -->
    <section class="txn-filter-bar" aria-label="Bộ lọc giao dịch">
      <div class="filter-controls-row">
        <!-- Date Range Filter -->
        <div class="filter-date-group">
          <div class="filter-input-wrap">
            <span class="input-sublabel">Từ Ngày</span>
            <input
              v-model="txnFilter.start_date"
              type="date"
              class="stitch-input-sm"
              @change="$emit('filter-change')"
            />
          </div>
          <div class="filter-input-wrap">
            <span class="input-sublabel">Đến Ngày</span>
            <input
              v-model="txnFilter.end_date"
              type="date"
              class="stitch-input-sm"
              @change="$emit('filter-change')"
            />
          </div>
        </div>

        <!-- Type Dropdown -->
        <div class="filter-select-wrap">
          <select
            v-model="txnFilter.transaction_type"
            class="stitch-select-sm"
            @change="$emit('filter-change')"
          >
            <option value="">Tất cả loại</option>
            <option value="INCOME">💎 Khoản Thu (+)</option>
            <option value="EXPENSE">🔥 Khoản Chi (-)</option>
          </select>
        </div>

        <!-- Category Dropdown -->
        <div class="filter-select-wrap">
          <select
            v-model="txnFilter.category_id"
            class="stitch-select-sm"
            @change="$emit('filter-change')"
          >
            <option value="">Tất cả danh mục</option>
            <option v-for="c in categories" :key="'flt-c-' + c.id" :value="c.id">
              {{ c.icon }} {{ c.category_name }}
            </option>
          </select>
        </div>

        <!-- Wallet Dropdown -->
        <div class="filter-select-wrap">
          <select
            v-model="txnFilter.wallet_id"
            class="stitch-select-sm"
            @change="$emit('filter-change')"
          >
            <option value="">Tất cả túi (Ví)</option>
            <option v-for="w in wallets" :key="'flt-w-' + w.id" :value="w.id">
              {{ w.wallet_name }}
            </option>
          </select>
        </div>

        <!-- Search Keyword Input -->
        <div class="filter-search-wrap">
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="txnFilter.keyword"
            type="text"
            placeholder="Tìm theo ghi chú..."
            class="stitch-search-input"
            @input="$emit('filter-change')"
          />
        </div>

        <!-- Reset Button -->
        <button
          type="button"
          class="btn-stitch-reset"
          @click="$emit('reset-filter')"
          title="Đặt lại toàn bộ bộ lọc"
        >
          <span class="material-symbols-outlined icon-sm">filter_alt_off</span>
          <span class="reset-text">Làm Mới</span>
        </button>
      </div>

      <!-- Quick Ledger Meta Badges -->
      <div class="filter-meta-bar">
        <div class="meta-item">
          <span class="meta-label">Tổng hiển thị:</span>
          <span class="meta-badge-count">{{ txnPagination.totalCount }} giao dịch</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Thu trang này:</span>
          <strong class="text-income tabular-num">+{{ formatVND(pageTotals.income) }}</strong>
        </div>
        <div class="meta-item">
          <span class="meta-label">Chi trang này:</span>
          <strong class="text-expense tabular-num">-{{ formatVND(pageTotals.expense) }}</strong>
        </div>
        <div class="meta-item">
          <span class="meta-label">Thặng dư trang:</span>
          <strong
            class="tabular-num"
            :class="pageTotals.net >= 0 ? 'text-gold' : 'text-expense'"
          >
            {{ (pageTotals.net > 0 ? '+' : '') + formatVND(pageTotals.net) }}
          </strong>
        </div>
      </div>
    </section>

    <!-- ═══ TRANSACTION LEDGER TABLE ═══ -->
    <section class="txn-ledger-card" aria-label="Bảng sổ cái giao dịch">
      <div class="table-responsive-wrap">
        <table class="stitch-ledger-table">
          <thead>
            <tr>
              <th scope="col" class="th-index">#</th>
              <th scope="col" class="th-date">Ngày giao dịch</th>
              <th scope="col" class="th-desc">Mô tả &amp; Ghi chú</th>
              <th scope="col" class="th-cat">Danh mục</th>
              <th scope="col" class="th-wallet">Ví thanh toán</th>
              <th scope="col" class="th-type text-center">Loại</th>
              <th scope="col" class="th-amount text-right">Số tiền</th>
              <th scope="col" class="th-action text-center">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(txn, idx) in transactions"
              :key="txn.id"
              class="txn-table-row"
            >
              <!-- Index Column -->
              <td class="td-index font-label-sm text-muted">
                {{ (txnPagination.page - 1) * txnPagination.limit + idx + 1 }}
              </td>

              <!-- Date Column -->
              <td class="td-date font-label-md text-muted whitespace-nowrap">
                {{ txn.transaction_date }}
              </td>

              <!-- Description / Note Column -->
              <td class="td-desc">
                <div class="desc-cell-wrap">
                  <span class="desc-title text-on-surface font-title-sm">
                    {{ txn.note || txn.category_name }}
                  </span>
                  <span v-if="txn.note && txn.category_name" class="desc-sub text-muted font-body-sm">
                    {{ txn.category_name }}
                  </span>
                </div>
              </td>

              <!-- Category Column -->
              <td class="td-cat whitespace-nowrap">
                <span class="category-chip">
                  <span class="cat-icon">{{ txn.category_icon || '📦' }}</span>
                  <span class="cat-text">{{ txn.category_name }}</span>
                </span>
              </td>

              <!-- Wallet Column -->
              <td class="td-wallet whitespace-nowrap text-muted">
                <div class="wallet-cell">
                  <span class="material-symbols-outlined icon-xs text-secondary">
                    account_balance_wallet
                  </span>
                  <span>{{ txn.wallet_name }}</span>
                </div>
              </td>

              <!-- Type Column -->
              <td class="td-type text-center whitespace-nowrap">
                <span
                  class="type-badge"
                  :class="txn.transaction_type === 'INCOME' ? 'badge-income' : 'badge-expense'"
                >
                  {{ txn.transaction_type === 'INCOME' ? 'THU' : 'CHI' }}
                </span>
              </td>

              <!-- Amount Column -->
              <td
                class="td-amount text-right whitespace-nowrap font-currency-table"
                :class="txn.transaction_type === 'INCOME' ? 'text-income' : 'text-on-surface'"
              >
                {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
              </td>

              <!-- Action Column -->
              <td class="td-action text-center whitespace-nowrap">
                <button
                  type="button"
                  class="btn-row-delete"
                  @click="$emit('delete-transaction', txn.id)"
                  title="Xóa giao dịch & hoàn nguyên số dư"
                >
                  <span class="material-symbols-outlined icon-sm">delete</span>
                </button>
              </td>
            </tr>

            <!-- Empty Row -->
            <tr v-if="!transactions.length">
              <td colspan="8" class="td-empty">
                <div class="empty-state-wrap">
                  <span class="material-symbols-outlined empty-icon">receipt_long</span>
                  <p>Không tìm thấy biến động linh thạch nào phù hợp với bộ lọc...</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination & Summary Footer -->
      <div class="ledger-pagination-bar" v-if="totalPages > 1 || txnPagination.totalCount > 0">
        <div class="pagination-info">
          Hiển thị
          <strong class="text-on-surface">
            {{ (txnPagination.page - 1) * txnPagination.limit + 1 }} -
            {{ Math.min(txnPagination.page * txnPagination.limit, txnPagination.totalCount) }}
          </strong>
          trên tổng số
          <strong class="text-on-surface">{{ txnPagination.totalCount }}</strong>
          giao dịch
        </div>

        <div class="pagination-controls" v-if="totalPages > 1">
          <!-- Previous Page -->
          <button
            type="button"
            class="btn-page-nav"
            :disabled="txnPagination.page <= 1"
            @click="$emit('change-page', txnPagination.page - 1)"
            title="Trang trước"
          >
            <span class="material-symbols-outlined icon-sm">chevron_left</span>
          </button>

          <!-- Numeric Pages -->
          <button
            v-for="p in visiblePages"
            :key="'page-' + p"
            type="button"
            class="btn-page-num"
            :class="{ active: p === txnPagination.page }"
            @click="$emit('change-page', p)"
          >
            {{ p }}
          </button>

          <!-- Next Page -->
          <button
            type="button"
            class="btn-page-nav"
            :disabled="txnPagination.page >= totalPages"
            @click="$emit('change-page', txnPagination.page + 1)"
            title="Trang sau"
          >
            <span class="material-symbols-outlined icon-sm">chevron_right</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  wallets: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  transactions: {
    type: Array,
    default: () => []
  },
  recurringList: {
    type: Array,
    default: () => []
  },
  txnForm: {
    type: Object,
    required: true
  },
  recurringForm: {
    type: Object,
    required: true
  },
  txnFilter: {
    type: Object,
    required: true
  },
  txnPagination: {
    type: Object,
    default: () => ({ page: 1, limit: 20, totalCount: 0 })
  },
  totalPages: {
    type: Number,
    default: 1
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

defineEmits([
  'create-transaction',
  'delete-transaction',
  'create-recurring',
  'toggle-recurring',
  'delete-recurring',
  'edit-recurring',
  'change-page',
  'reset-filter',
  'filter-change',
  'export-reports'
])

// UI-only view toggles (do not affect backend or API)
const showRecurringTray = ref(false)
const showAddForm = ref(false)
const showAddRecurringForm = ref(false)

const activeRecurringCount = computed(() => {
  return (props.recurringList || []).filter(r => r.is_active).length
})

const filteredCategories = computed(() => {
  const t = props.txnForm.transaction_type
  return (props.categories || []).filter(c => c.category_type === t)
})

const filteredRecurringCategories = computed(() => {
  const t = props.recurringForm.transaction_type
  return (props.categories || []).filter(c => c.category_type === t)
})

// Current page totals for quick meta badges
const pageTotals = computed(() => {
  let income = 0
  let expense = 0
  for (const t of props.transactions || []) {
    if (t.transaction_type === 'INCOME') income += Number(t.amount || 0)
    else expense += Number(t.amount || 0)
  }
  return {
    income,
    expense,
    net: income - expense
  }
})

// Visible pages for clean pagination numbers (up to 5 pages)
const visiblePages = computed(() => {
  const total = Math.max(1, props.totalPages || 1)
  const current = (props.txnPagination && props.txnPagination.page) || 1
  if (total <= 5) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)
  if (end - start < 4) {
    start = Math.max(1, end - 4)
  }
  const pages = []
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC — TRANSACTIONS VIEW (STITCH CELESTIAL LEDGER)
   ═══════════════════════════════════════════════════════════════════════════ */

.transactions-realm {
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
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.orb-primary {
  top: -40px;
  right: 15%;
  width: 360px;
  height: 360px;
  background: rgba(125, 214, 204, 0.07);
}
.orb-secondary {
  top: 40%;
  left: -60px;
  width: 300px;
  height: 300px;
  background: rgba(196, 193, 251, 0.05);
}

/* ─── PAGE HEADER & ACTION BAR ─── */
.txn-page-header {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-md, 16px);
  padding-bottom: var(--space-xs, 4px);
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.8);
}

.badge-text {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary, #7dd6cc);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
  letter-spacing: -0.015em;
}

.page-subtitle {
  font-size: 13px;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 680px;
  margin: 0;
  line-height: 1.5;
}

.header-action-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 8px);
  flex-wrap: wrap;
}

/* ─── ACTION BUTTONS (STITCH PRESETS) ─── */
.btn-stitch-primary {
  display: inline-flex;
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
  box-shadow: 0 2px 12px rgba(125, 214, 204, 0.3);
  transition: all 0.2s ease;
}
.btn-stitch-primary:hover:not(:disabled) {
  background: var(--color-primary-container, #449f96);
  color: #ffffff;
  transform: translateY(-1px);
}
.btn-stitch-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-stitch-secondary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-high, #222a3d);
  color: var(--color-on-surface, #dae2fd);
  font-size: 13px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-stitch-secondary:hover {
  background: var(--color-surface-bright, #31394d);
  border-color: rgba(227, 195, 112, 0.3);
}
.btn-stitch-secondary.active {
  border-color: var(--color-tertiary, #e3c370);
  background: rgba(227, 195, 112, 0.12);
}

.count-pill {
  padding: 2px 7px;
  border-radius: 9999px;
  background: rgba(227, 195, 112, 0.18);
  color: var(--color-tertiary, #e3c370);
  font-size: 11px;
  font-weight: 600;
}

.export-btn-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-stitch-export {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: var(--radius-DEFAULT, 8px);
  font-size: 12.5px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-excel {
  background: rgba(125, 214, 204, 0.1);
  color: var(--color-primary, #7dd6cc);
  border-color: rgba(125, 214, 204, 0.2);
}
.btn-excel:hover {
  background: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
}
.btn-csv {
  background: var(--color-surface-container, #171f33);
  color: var(--color-on-surface-variant, #bdc9c6);
}
.btn-csv:hover {
  background: var(--color-surface-container-high, #222a3d);
  color: var(--color-on-surface, #dae2fd);
}

/* ─── RECURRING COLLAPSIBLE TRAY ─── */
.recurring-tray-card {
  position: relative;
  z-index: 1;
  padding: var(--space-md, 16px);
  border-radius: var(--radius-xl, 16px);
  background: var(--color-surface-container, #171f33);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(14px);
}

.tray-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: var(--space-md, 16px);
}

.tray-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tray-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.tray-desc {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 2px 0 0 0;
}

.tray-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-text-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: var(--color-primary, #7dd6cc);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-DEFAULT, 8px);
  transition: all 0.2s ease;
}
.btn-text-toggle:hover {
  background: rgba(125, 214, 204, 0.1);
}

.btn-icon-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-icon-close:hover {
  background: var(--color-surface-container-high, #222a3d);
  color: var(--color-on-surface, #dae2fd);
}

.recurring-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md, 16px);
}

.recurring-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}
.recurring-item-card:hover {
  background: var(--color-surface-bright, #31394d);
}

.rec-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rec-icon-box {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-DEFAULT, 8px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-income {
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
}
.icon-expense {
  background: rgba(196, 193, 251, 0.15);
  color: var(--color-secondary, #c4c1fb);
}

.rec-meta {
  display: flex;
  flex-direction: column;
}

.rec-note {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.rec-submeta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: 2px;
  flex-wrap: wrap;
}

.rec-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-icon-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container, #171f33);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-icon-action:hover {
  background: var(--color-surface-bright, #31394d);
}
.btn-active:hover { color: var(--color-primary, #7dd6cc); }
.btn-paused:hover { color: var(--color-tertiary, #e3c370); }
.btn-edit:hover { color: var(--color-primary, #7dd6cc); }
.btn-delete:hover { color: var(--color-error, #ffb4ab); }

.add-recurring-form-wrap {
  padding: 14px;
  margin-bottom: 16px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.empty-tray-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 13px;
  gap: 6px;
}

/* ─── QUICK TRANSACTION FORM ─── */
.txn-form-card {
  position: relative;
  z-index: 1;
  padding: var(--space-lg, 24px);
  border-radius: var(--radius-xl, 16px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(14px);
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md, 16px);
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md, 16px);
}

.col-span-full {
  grid-column: 1 / -1;
}

.input-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label {
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.stitch-input, .stitch-select {
  width: 100%;
  height: 42px;
  padding: 8px 12px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 13.5px;
  font-family: var(--font-body);
  outline: none;
  transition: all 0.2s ease;
}
.stitch-input:focus, .stitch-select:focus {
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 0 2px rgba(125, 214, 204, 0.2);
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-md, 16px);
  padding-top: var(--space-sm, 8px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* ─── FILTER & SEARCH BAR ─── */
.txn-filter-bar {
  position: relative;
  z-index: 1;
  padding: var(--space-md, 16px);
  border-radius: var(--radius-xl, 16px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.filter-controls-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 8px);
  flex-wrap: wrap;
}

.filter-date-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-input-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.input-sublabel {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.stitch-input-sm, .stitch-select-sm {
  height: 36px;
  padding: 6px 10px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 12.5px;
  font-family: var(--font-body);
  outline: none;
  transition: all 0.2s ease;
}
.stitch-input-sm:focus, .stitch-select-sm:focus {
  border-color: var(--color-primary, #7dd6cc);
}

.filter-select-wrap {
  min-width: 140px;
}

.filter-search-wrap {
  position: relative;
  flex: 1;
  min-width: 180px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: var(--color-on-surface-variant, #bdc9c6);
  pointer-events: none;
}

.stitch-search-input {
  width: 100%;
  height: 36px;
  padding: 6px 12px 6px 34px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 12.5px;
  font-family: var(--font-body);
  outline: none;
  transition: all 0.2s ease;
}
.stitch-search-input:focus {
  border-color: var(--color-primary, #7dd6cc);
}

.btn-stitch-reset {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 36px;
  padding: 0 12px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container, #171f33);
  color: var(--color-on-surface-variant, #bdc9c6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-stitch-reset:hover {
  background: var(--color-surface-container-high, #222a3d);
  color: var(--color-on-surface, #dae2fd);
}

/* Filter Meta Badges */
.filter-meta-bar {
  display: flex;
  align-items: center;
  gap: var(--space-md, 16px);
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-label {
  color: var(--color-on-surface-variant, #bdc9c6);
}

.meta-badge-count {
  padding: 1px 8px;
  border-radius: 9999px;
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-primary, #7dd6cc);
  font-weight: 600;
}

/* ─── TRANSACTION LEDGER TABLE ─── */
.txn-ledger-card {
  position: relative;
  z-index: 1;
  border-radius: var(--radius-xl, 16px);
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.table-responsive-wrap {
  width: 100%;
  overflow-x: auto;
}

.stitch-ledger-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.stitch-ledger-table thead tr {
  background: var(--color-surface-container-high, #222a3d);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.stitch-ledger-table th {
  padding: 12px 16px;
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-on-surface-variant, #bdc9c6);
  white-space: nowrap;
}

.stitch-ledger-table td {
  padding: 14px 16px;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.txn-table-row {
  transition: background 0.15s ease;
}
.txn-table-row:hover {
  background: var(--color-surface-container, #171f33);
}

.td-index { width: 44px; text-align: center; }
.th-index { text-align: center; }

.desc-cell-wrap {
  display: flex;
  flex-direction: column;
}

.desc-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.desc-sub {
  font-size: 11.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: 2px;
}

.category-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-on-surface, #dae2fd);
  font-size: 12px;
}

.wallet-cell {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm, 4px);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.badge-income {
  background: rgba(125, 214, 204, 0.2);
  color: var(--color-primary, #7dd6cc);
}
.badge-expense {
  background: var(--color-surface-container-highest, #2d3449);
  color: var(--color-on-surface-variant, #bdc9c6);
}

.btn-row-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-row-delete:hover {
  background: rgba(255, 180, 171, 0.15);
  color: var(--color-error, #ffb4ab);
}

.td-empty {
  padding: 48px 16px;
  text-align: center;
}

.empty-state-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 13px;
}

/* ─── PAGINATION BAR ─── */
.ledger-pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-surface-container, #171f33);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 12.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
  flex-wrap: wrap;
  gap: var(--space-sm, 8px);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-page-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--color-on-surface, #dae2fd);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-page-nav:hover:not(:disabled) {
  background: var(--color-surface-bright, #31394d);
}
.btn-page-nav:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--color-on-surface, #dae2fd);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-page-num:hover:not(.active) {
  background: var(--color-surface-bright, #31394d);
}
.btn-page-num.active {
  background: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  font-weight: 700;
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.3);
}

/* ─── TRANSITIONS ─── */
.tray-expand-enter-active, .tray-expand-leave-active {
  transition: all 0.25s ease-out;
  max-height: 800px;
  overflow: hidden;
}
.tray-expand-enter-from, .tray-expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-8px);
}

/* ─── UTILITIES ─── */
.text-income { color: var(--color-primary, #7dd6cc); }
.text-expense { color: var(--color-error, #ffb4ab); }
.text-gold { color: var(--color-tertiary, #e3c370); }
.text-muted { color: var(--color-on-surface-variant, #bdc9c6); }
.text-on-surface { color: var(--color-on-surface, #dae2fd); }
.icon-jade { color: var(--color-primary, #7dd6cc); }
.icon-tertiary { color: var(--color-tertiary, #e3c370); }
.icon-sm { font-size: 16px; }
.icon-xs { font-size: 14px; }
.sep { opacity: 0.4; }
.truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.whitespace-nowrap { white-space: nowrap; }

/* ─── RESPONSIVE BREAKPOINTS ─── */
@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .recurring-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .filter-controls-row {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-date-group {
    width: 100%;
    flex-direction: column;
  }
  .filter-select-wrap, .filter-search-wrap {
    width: 100%;
  }
  .btn-stitch-reset {
    width: 100%;
    justify-content: center;
  }
  .filter-meta-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .header-action-group {
    width: 100%;
  }
  .btn-stitch-primary, .btn-stitch-secondary {
    flex: 1;
    justify-content: center;
  }
}
</style>
