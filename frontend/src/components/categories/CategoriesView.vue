<template>
  <div class="categories-realm">
    <!-- Spatial Atmosphere Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & TOP CONTROLS ═══ -->
    <section class="categories-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">CÀN KHÔN BÁCH KHOA ẤN • QUẢN LÝ PHÂN LOẠI</span>
        </div>
        <h1 class="page-title">Danh Mục Thu Chi (Categories)</h1>
        <p class="page-subtitle">
          Phân định ranh giới các luồng linh thạch nạp xuất, giúp tâm pháp tài chính luôn rành mạch, chuẩn xác và không bị hỗn loạn.
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="btn-stitch-primary"
          @click="focusCreateForm"
          title="Tạo danh mục phân loại mới"
        >
          <span class="material-symbols-outlined">add_circle</span>
          <span>+ Khai Mở Danh Mục Mới</span>
        </button>
      </div>
    </section>

    <!-- ═══ SUMMARY METRICS ROW (3 CARDS) ═══ -->
    <section class="categories-metrics-grid" aria-label="Thống kê tổng quan danh mục">
      <!-- Metric 1: Expense Categories -->
      <div class="category-metric-card card-expense">
        <div class="metric-glow glow-error"></div>
        <div class="metric-header-row">
          <span class="metric-label">Linh Thạch Xuất Quán</span>
          <div class="metric-icon-box icon-expense">
            <span class="material-symbols-outlined icon-sm">north_east</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-danger tabular-num font-bold">
            {{ expenseList.length }} Danh Mục
          </div>
          <div class="metric-submeta">
            <span class="ping-dot bg-danger"></span>
            <span>Khoản chi tiêu • Tổn hao chân nguyên</span>
          </div>
        </div>
      </div>

      <!-- Metric 2: Income Categories -->
      <div class="category-metric-card card-income">
        <div class="metric-glow glow-jade"></div>
        <div class="metric-header-row">
          <span class="metric-label">Linh Thạch Nhập Động</span>
          <div class="metric-icon-box icon-income">
            <span class="material-symbols-outlined icon-sm">south_west</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-jade tabular-num font-bold">
            {{ incomeList.length }} Danh Mục
          </div>
          <div class="metric-submeta">
            <span class="ping-dot bg-jade"></span>
            <span>Khoản thu hoạch • Tích tụ ngân khố</span>
          </div>
        </div>
      </div>

      <!-- Metric 3: Total Categories -->
      <div class="category-metric-card card-total">
        <div class="metric-glow glow-gold"></div>
        <div class="metric-header-row">
          <span class="metric-label">Tổng Thể Phân Loại</span>
          <div class="metric-icon-box icon-total">
            <span class="material-symbols-outlined icon-sm">account_tree</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-gold tabular-num font-bold">
            {{ allCategories.length }} Linh Mục
          </div>
          <div class="metric-submeta">
            <span class="ping-dot bg-gold"></span>
            <span>Toàn bộ ấn ký phân loại hoạt động</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ FILTER & SEARCH TOOLBAR ═══ -->
    <section class="categories-toolbar-card">
      <div class="toolbar-search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm danh mục theo tên linh mục..."
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

      <div class="toolbar-filter-pills">
        <button
          type="button"
          class="filter-pill"
          :class="{ active: activeFilter === 'ALL' }"
          @click="activeFilter = 'ALL'"
        >
          Tất cả ({{ allCategories.length }})
        </button>
        <button
          type="button"
          class="filter-pill pill-expense"
          :class="{ active: activeFilter === 'EXPENSE' }"
          @click="activeFilter = 'EXPENSE'"
        >
          🔥 Chi Tiêu ({{ expenseList.length }})
        </button>
        <button
          type="button"
          class="filter-pill pill-income"
          :class="{ active: activeFilter === 'INCOME' }"
          @click="activeFilter = 'INCOME'"
        >
          💎 Thu Nhập ({{ incomeList.length }})
        </button>
      </div>
    </section>

    <!-- ═══ MAIN BENTO WORKSPACE (8 COLS / 4 COLS) ═══ -->
    <div class="categories-bento-grid">
      <!-- ─── LEFT COLUMN: CATEGORIES LEDGER LIST (8 COLS) ─── -->
      <div class="bento-left-col">
        <!-- Section A: Expense Categories (Visible if filter is ALL or EXPENSE) -->
        <div
          v-if="activeFilter === 'ALL' || activeFilter === 'EXPENSE'"
          class="category-panel-card"
        >
          <div class="panel-header-row">
            <div class="panel-title-group">
              <span class="status-dot bg-danger"></span>
              <h2 class="panel-title">Danh Mục Chi Tiêu</h2>
              <span class="count-badge badge-expense">{{ filteredExpenses.length }} mục</span>
            </div>
            <span class="panel-tag tag-expense">Linh Thạch Tổn Hao</span>
          </div>

          <div v-if="filteredExpenses.length" class="category-items-list">
            <div
              v-for="c in filteredExpenses"
              :key="'exp-' + c.id"
              class="category-item-card item-expense"
            >
              <div class="item-left-group">
                <div class="item-avatar-box avatar-expense">
                  <span class="category-icon">{{ c.icon || '📦' }}</span>
                </div>
                <div class="item-text-col">
                  <div class="item-title-row">
                    <span class="category-name font-semibold">{{ c.category_name }}</span>
                    <span class="category-type-pill pill-exp-mini">Chi</span>
                  </div>
                  <span class="category-meta-subtext">Mã định danh linh mục: #{{ c.id }}</span>
                </div>
              </div>

              <div class="item-actions-group">
                <button
                  type="button"
                  class="btn-item-action btn-edit"
                  @click="$emit('open-edit-category', c)"
                  title="Chỉnh sửa danh mục này"
                >
                  <span class="material-symbols-outlined icon-xs">tune</span>
                  <span>Sửa</span>
                </button>
                <button
                  type="button"
                  class="btn-item-action btn-delete"
                  @click="$emit('delete-category', c.id)"
                  title="Xóa danh mục này"
                >
                  <span class="material-symbols-outlined icon-xs">delete</span>
                  <span>Xóa</span>
                </button>
              </div>
            </div>
          </div>

          <div v-else class="category-empty-box">
            <span class="material-symbols-outlined empty-icon">production_quantity_limits</span>
            <p class="empty-text">
              {{ searchQuery ? 'Không tìm thấy danh mục chi tiêu phù hợp từ khóa.' : 'Chưa có danh mục chi tiêu nào được khai mở.' }}
            </p>
          </div>
        </div>

        <!-- Section B: Income Categories (Visible if filter is ALL or INCOME) -->
        <div
          v-if="activeFilter === 'ALL' || activeFilter === 'INCOME'"
          class="category-panel-card"
        >
          <div class="panel-header-row">
            <div class="panel-title-group">
              <span class="status-dot bg-jade"></span>
              <h2 class="panel-title">Danh Mục Thu Nhập</h2>
              <span class="count-badge badge-income">{{ filteredIncomes.length }} mục</span>
            </div>
            <span class="panel-tag tag-income">Linh Thạch Tích Tụ</span>
          </div>

          <div v-if="filteredIncomes.length" class="category-items-list">
            <div
              v-for="c in filteredIncomes"
              :key="'inc-' + c.id"
              class="category-item-card item-income"
            >
              <div class="item-left-group">
                <div class="item-avatar-box avatar-income">
                  <span class="category-icon">{{ c.icon || '💰' }}</span>
                </div>
                <div class="item-text-col">
                  <div class="item-title-row">
                    <span class="category-name font-semibold">{{ c.category_name }}</span>
                    <span class="category-type-pill pill-inc-mini">Thu</span>
                  </div>
                  <span class="category-meta-subtext">Mã định danh linh mục: #{{ c.id }}</span>
                </div>
              </div>

              <div class="item-actions-group">
                <button
                  type="button"
                  class="btn-item-action btn-edit"
                  @click="$emit('open-edit-category', c)"
                  title="Chỉnh sửa danh mục này"
                >
                  <span class="material-symbols-outlined icon-xs">tune</span>
                  <span>Sửa</span>
                </button>
                <button
                  type="button"
                  class="btn-item-action btn-delete"
                  @click="$emit('delete-category', c.id)"
                  title="Xóa danh mục này"
                >
                  <span class="material-symbols-outlined icon-xs">delete</span>
                  <span>Xóa</span>
                </button>
              </div>
            </div>
          </div>

          <div v-else class="category-empty-box">
            <span class="material-symbols-outlined empty-icon">savings</span>
            <p class="empty-text">
              {{ searchQuery ? 'Không tìm thấy danh mục thu nhập phù hợp từ khóa.' : 'Chưa có danh mục thu nhập nào được khai mở.' }}
            </p>
          </div>
        </div>
      </div>

      <!-- ─── RIGHT COLUMN: QUICK CREATION & WISDOM (4 COLS) ─── -->
      <div class="bento-right-col">
        <!-- Quick Category Creation Card -->
        <div class="formulation-card" ref="createFormRef" id="category-create-card">
          <div class="form-header-row">
            <div class="form-title-group">
              <div class="form-icon-box">
                <span class="material-symbols-outlined">bookmark_add</span>
              </div>
              <div>
                <h3 class="form-card-title">Khai Mở Danh Mục Mới</h3>
                <span class="form-card-subtitle">Thiết lập ấn ký phân loại thu chi</span>
              </div>
            </div>
          </div>

          <form class="category-create-form" @submit.prevent="handleSubmit">
            <!-- Field 1: Category Name -->
            <div class="form-field-group">
              <label class="field-label" for="category-name-input">
                <span>Tên Danh Mục</span>
                <span class="field-required-hint">Bắt buộc</span>
              </label>
              <div class="input-wrap">
                <input
                  id="category-name-input"
                  v-model="catForm.category_name"
                  type="text"
                  placeholder="Ví dụ: Đan Dược, Phi Hành, Y Tế..."
                  class="stitch-input"
                  required
                />
              </div>
            </div>

            <!-- Field 2: Category Type Toggle -->
            <div class="form-field-group">
              <label class="field-label">
                <span>Loại Danh Mục</span>
                <span class="field-info-hint">Hướng luân chuyển</span>
              </label>
              <div class="type-toggle-grid">
                <button
                  type="button"
                  class="type-toggle-btn"
                  :class="{ active: catForm.category_type === 'EXPENSE' }"
                  @click="catForm.category_type = 'EXPENSE'"
                >
                  <span class="material-symbols-outlined icon-sm">north_east</span>
                  <span>Tiêu Hao (Chi)</span>
                </button>
                <button
                  type="button"
                  class="type-toggle-btn btn-inc"
                  :class="{ active: catForm.category_type === 'INCOME' }"
                  @click="catForm.category_type = 'INCOME'"
                >
                  <span class="material-symbols-outlined icon-sm">south_west</span>
                  <span>Thu Hoạch (Thu)</span>
                </button>
              </div>
            </div>

            <!-- Field 3: Icon Emoji Selector -->
            <div class="form-field-group">
              <div class="icon-label-row">
                <label class="field-label">Biểu Tượng Linh Ấn</label>
                <span class="selected-icon-badge">Đang chọn: {{ catForm.icon || '📦' }}</span>
              </div>
              <div class="emoji-grid-picker">
                <button
                  v-for="ic in availableIcons"
                  :key="'icon-' + ic"
                  type="button"
                  class="emoji-select-btn"
                  :class="{ selected: catForm.icon === ic }"
                  @click="catForm.icon = ic"
                  :title="'Chọn biểu tượng ' + ic"
                >
                  {{ ic }}
                </button>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="form-actions-row">
              <button
                type="button"
                class="btn-stitch-secondary"
                @click="resetForm"
                title="Đặt lại thông tin nhập"
              >
                Làm Lại
              </button>

              <button
                type="submit"
                class="btn-stitch-submit"
                :disabled="loading || !catForm.category_name || !catForm.category_name.trim()"
              >
                <span class="material-symbols-outlined icon-sm">auto_awesome</span>
                <span>{{ loading ? 'Đang khai mở...' : 'Khai Mở Danh Mục' }}</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Khí Linh System Flow & Architecture Insight Box -->
        <div class="companion-wisdom-card">
          <div class="companion-header-row">
            <div class="companion-avatar-wrap">
              <span class="material-symbols-outlined avatar-icon">hub</span>
              <span class="companion-live-dot"></span>
            </div>
            <div>
              <h4 class="companion-title">Cơ Cấu Luân Chuyển Linh Thạch</h4>
              <span class="companion-role">Ngũ Hành Phân Bổ Danh Mục</span>
            </div>
          </div>

          <p class="companion-quote-text">
            {{ companionAdviceText }}
          </p>

          <!-- Distribution Ratio Gauge -->
          <div class="category-distribution-box">
            <div class="distribution-labels-row">
              <span class="dist-label text-danger">Chi: {{ expensePct }}%</span>
              <span class="dist-label text-jade">Thu: {{ incomePct }}%</span>
            </div>
            <div class="distribution-track">
              <div
                class="dist-fill bg-danger"
                :style="{ width: expensePct + '%' }"
                title="Tỷ lệ danh mục chi tiêu"
              ></div>
              <div
                class="dist-fill bg-jade"
                :style="{ width: incomePct + '%' }"
                title="Tỷ lệ danh mục thu nhập"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  incomeCategories: {
    type: Array,
    default: () => []
  },
  expenseCategories: {
    type: Array,
    default: () => []
  },
  catForm: {
    type: Object,
    required: true
  },
  iconOptions: {
    type: Array,
    default: () => ['🍕','🛍️','🚗','💵','🎁','🏠','💊','📚','🎮','☕','🍜','🎬','🏋️','✈️','📱','👕','🎵','🐾','🔧','📦']
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'create-category',
  'delete-category',
  'open-edit-category'
])

// UI-only state
const searchQuery = ref('')
const activeFilter = ref('ALL') // 'ALL' | 'EXPENSE' | 'INCOME'
const createFormRef = ref(null)

// Fallback list of icons if empty
const defaultIcons = ['🍕','🛍️','🚗','💵','🎁','🏠','💊','📚','🎮','☕','🍜','🎬','🏋️','✈️','📱','👕','🎵','🐾','🔧','📦']
const availableIcons = computed(() => {
  return props.iconOptions && props.iconOptions.length ? props.iconOptions : defaultIcons
})

// Safe list computed
const allCategories = computed(() => props.categories || [])

const incomeList = computed(() => {
  if (props.incomeCategories && props.incomeCategories.length) {
    return props.incomeCategories
  }
  return allCategories.value.filter(c => c.category_type === 'INCOME')
})

const expenseList = computed(() => {
  if (props.expenseCategories && props.expenseCategories.length) {
    return props.expenseCategories
  }
  return allCategories.value.filter(c => c.category_type === 'EXPENSE')
})

// Search-filtered lists
const filteredExpenses = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return expenseList.value
  return expenseList.value.filter(c => (c.category_name || '').toLowerCase().includes(q))
})

const filteredIncomes = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return incomeList.value
  return incomeList.value.filter(c => (c.category_name || '').toLowerCase().includes(q))
})

// Ratio calculations for distribution box
const totalCategoryCount = computed(() => allCategories.value.length)
const expensePct = computed(() => {
  if (!totalCategoryCount.value) return 50
  return Math.round((expenseList.value.length / totalCategoryCount.value) * 100)
})
const incomePct = computed(() => {
  if (!totalCategoryCount.value) return 50
  return 100 - expensePct.value
})

const companionAdviceText = computed(() => {
  if (!totalCategoryCount.value) {
    return '"Đạo trưởng chưa thiết lập danh mục nào. Hãy khai mở các linh mục chi tiêu và thu hoạch đầu tiên để khởi động đồ hình tài chính."'
  }
  if (expenseList.value.length >= 8) {
    return '"Hệ thống ghi nhận cơ cấu chi tiêu rất chi tiết. Hãy duy trì định mức theo từng linh mục để giữ tâm cảnh an định, không bị phân tâm."'
  }
  return '"Các linh mục phân loại giúp Khí Linh định vị chính xác mọi dòng chảy linh thạch, ngăn ngừa thất thoát chân nguyên."'
})

function focusCreateForm() {
  if (createFormRef.value) {
    createFormRef.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
    const input = createFormRef.value.querySelector('#category-name-input')
    if (input) {
      nextTick(() => input.focus())
    }
  }
}

function handleSubmit() {
  if (!props.catForm.category_name || !props.catForm.category_name.trim()) return
  emit('create-category')
}

function resetForm() {
  props.catForm.category_name = ''
  props.catForm.category_type = 'EXPENSE'
  props.catForm.icon = '📦'
}
</script>

<style scoped>
/* ─── REALM ATMOSPHERE & TOKENS ─── */
.categories-realm {
  position: relative;
  width: 100%;
  min-height: 100%;
  color: #dae2fd;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  padding-bottom: 2.5rem;
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
  right: 20%;
  width: 360px;
  height: 360px;
  background: rgba(125, 214, 204, 0.05);
}
.orb-secondary {
  top: 80px;
  left: 5%;
  width: 320px;
  height: 320px;
  background: rgba(68, 65, 115, 0.15);
}

/* Tabular Numerals */
.tabular-num {
  font-variant-numeric: tabular-nums;
}

/* Typography & Colors */
.text-jade { color: #7dd6cc; }
.text-gold { color: #e3c370; }
.text-danger { color: #ffb4ab; }
.bg-danger { background-color: #ffb4ab; }
.bg-jade { background-color: #7dd6cc; }
.bg-gold { background-color: #e3c370; }

/* ─── HEADER SECTION ─── */
.categories-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-top: 0.5rem;
  padding-bottom: 1.5rem;
}
@media (min-width: 768px) {
  .categories-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.header-text-group {
  max-width: 44rem;
}

.header-badge-row {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: rgba(125, 214, 204, 0.08);
  border: 1px solid rgba(125, 214, 204, 0.2);
  margin-bottom: 0.75rem;
}

.status-pulse-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: #7dd6cc;
  box-shadow: 0 0 8px #7dd6cc;
}

.badge-text {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: #7dd6cc;
}

.page-title {
  font-size: 1.875rem;
  line-height: 2.25rem;
  font-weight: 700;
  color: #dae2fd;
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #a3aed0;
  margin: 0;
}

.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #7dd6cc;
  color: #003733;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.65rem 1.25rem;
  border-radius: 0.625rem;
  border: none;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.28);
  transition: all 0.2s ease;
  white-space: nowrap;
}
.btn-stitch-primary:hover {
  background: #9af2e8;
  box-shadow: 0 0 24px rgba(125, 214, 204, 0.45);
  transform: translateY(-1px);
}

/* ─── SUMMARY METRICS (3 CARDS) ─── */
.categories-metrics-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
@media (min-width: 640px) {
  .categories-metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.category-metric-card {
  position: relative;
  overflow: hidden;
  background: rgba(23, 31, 51, 0.72);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, border-color 0.2s ease;
}
.category-metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.16);
}

.metric-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  border-radius: 9999px;
  filter: blur(40px);
  pointer-events: none;
  opacity: 0.15;
}
.glow-error { background: #ffb4ab; }
.glow-jade { background: #7dd6cc; }
.glow-gold { background: #e3c370; }

.metric-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.metric-label {
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #a3aed0;
}

.metric-icon-box {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-expense {
  background: rgba(255, 180, 171, 0.12);
  color: #ffb4ab;
}
.icon-income {
  background: rgba(125, 214, 204, 0.12);
  color: #7dd6cc;
}
.icon-total {
  background: rgba(227, 195, 112, 0.12);
  color: #e3c370;
}

.metric-value-text {
  font-size: 1.5rem;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.metric-submeta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #a3aed0;
}

.ping-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 9999px;
}

/* ─── TOOLBAR (SEARCH & FILTER) ─── */
.categories-toolbar-card {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: rgba(23, 31, 51, 0.65);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.875rem;
  padding: 0.875rem 1.25rem;
  margin-bottom: 1.5rem;
}
@media (min-width: 768px) {
  .categories-toolbar-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.toolbar-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 28rem;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  color: #a3aed0;
  font-size: 1.15rem;
  pointer-events: none;
}

.stitch-search-input {
  width: 100%;
  height: 2.35rem;
  padding: 0 2rem 0 2.5rem;
  background: rgba(11, 19, 38, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.5rem;
  color: #dae2fd;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
}
.stitch-search-input:focus {
  border-color: #7dd6cc;
  background: rgba(11, 19, 38, 0.95);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.25);
}

.search-clear-btn {
  position: absolute;
  right: 0.65rem;
  background: transparent;
  border: none;
  color: #a3aed0;
  cursor: pointer;
  font-size: 0.85rem;
}

.toolbar-filter-pills {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-pill {
  padding: 0.35rem 0.85rem;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #a3aed0;
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-pill:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #dae2fd;
}
.filter-pill.active {
  background: rgba(125, 214, 204, 0.18);
  border-color: #7dd6cc;
  color: #7dd6cc;
  font-weight: 600;
}
.filter-pill.pill-expense.active {
  background: rgba(255, 180, 171, 0.18);
  border-color: #ffb4ab;
  color: #ffb4ab;
}
.filter-pill.pill-income.active {
  background: rgba(125, 214, 204, 0.18);
  border-color: #7dd6cc;
  color: #7dd6cc;
}

/* ─── BENTO GRID (8 COLS / 4 COLS) ─── */
.categories-bento-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 1024px) {
  .categories-bento-grid {
    grid-template-columns: 8fr 4fr;
  }
}

.bento-left-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.bento-right-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ─── CATEGORY PANEL CARD ─── */
.category-panel-card {
  background: rgba(23, 31, 51, 0.72);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.panel-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 1rem;
}

.panel-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
}

.count-badge {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.08);
  color: #a3aed0;
}
.badge-expense {
  background: rgba(255, 180, 171, 0.12);
  color: #ffb4ab;
}
.badge-income {
  background: rgba(125, 214, 204, 0.12);
  color: #7dd6cc;
}

.panel-tag {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 0.375rem;
  font-weight: 500;
}
.tag-expense {
  background: rgba(255, 180, 171, 0.1);
  color: #ffb4ab;
}
.tag-income {
  background: rgba(125, 214, 204, 0.1);
  color: #7dd6cc;
}

/* Category Items List */
.category-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.category-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: rgba(11, 19, 38, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}
.category-item-card:hover {
  background: rgba(11, 19, 38, 0.85);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateX(2px);
}

.item-left-group {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  min-width: 0;
}

.item-avatar-box {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.avatar-expense {
  background: rgba(255, 180, 171, 0.08);
}
.avatar-income {
  background: rgba(125, 214, 204, 0.08);
}

.item-text-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-name {
  font-size: 0.95rem;
  color: #dae2fd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-type-pill {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
  text-transform: uppercase;
}
.pill-exp-mini {
  background: rgba(255, 180, 171, 0.15);
  color: #ffb4ab;
}
.pill-inc-mini {
  background: rgba(125, 214, 204, 0.15);
  color: #7dd6cc;
}

.category-meta-subtext {
  font-size: 0.75rem;
  color: #889391;
  margin-top: 0.15rem;
}

.item-actions-group {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-shrink: 0;
}

.btn-item-action {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.65rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.icon-xs {
  font-size: 0.95rem;
}

.btn-edit {
  background: rgba(125, 214, 204, 0.08);
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.2);
}
.btn-edit:hover {
  background: rgba(125, 214, 204, 0.2);
  color: #9af2e8;
}

.btn-delete {
  background: rgba(255, 180, 171, 0.08);
  color: #ffb4ab;
  border: 1px solid rgba(255, 180, 171, 0.2);
}
.btn-delete:hover {
  background: rgba(255, 180, 171, 0.2);
  color: #ffdad6;
}

.category-empty-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  color: #889391;
  text-align: center;
}
.empty-icon {
  font-size: 2.25rem;
  margin-bottom: 0.5rem;
  opacity: 0.6;
}
.empty-text {
  font-size: 0.85rem;
  margin: 0;
}

/* ─── FORMULATION / CREATION CARD ─── */
.formulation-card {
  background: rgba(23, 31, 51, 0.78);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(125, 214, 204, 0.18);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.form-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 1.25rem;
}

.form-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-icon-box {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background: rgba(125, 214, 204, 0.12);
  color: #7dd6cc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
}

.form-card-subtitle {
  font-size: 0.75rem;
  color: #a3aed0;
}

.category-create-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8rem;
  font-weight: 500;
  color: #dae2fd;
}

.field-required-hint {
  font-size: 0.7rem;
  color: #ffb4ab;
}

.field-info-hint {
  font-size: 0.7rem;
  color: #a3aed0;
}

.stitch-input {
  width: 100%;
  height: 2.5rem;
  padding: 0 0.875rem;
  background: rgba(11, 19, 38, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.5rem;
  color: #dae2fd;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
}
.stitch-input:focus {
  border-color: #7dd6cc;
  background: rgba(11, 19, 38, 0.95);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.25);
}

/* Type Toggle Grid */
.type-toggle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  background: rgba(11, 19, 38, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  padding: 0.25rem;
}

.type-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.5rem 0.25rem;
  border-radius: 0.375rem;
  border: none;
  background: transparent;
  color: #a3aed0;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.type-toggle-btn:hover {
  color: #dae2fd;
}
.type-toggle-btn.active {
  background: rgba(255, 180, 171, 0.2);
  color: #ffb4ab;
  font-weight: 600;
  box-shadow: 0 0 8px rgba(255, 180, 171, 0.2);
}
.type-toggle-btn.btn-inc.active {
  background: rgba(125, 214, 204, 0.2);
  color: #7dd6cc;
  font-weight: 600;
  box-shadow: 0 0 8px rgba(125, 214, 204, 0.2);
}

/* Emoji Grid Picker */
.icon-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.selected-icon-badge {
  font-size: 0.75rem;
  color: #7dd6cc;
}

.emoji-grid-picker {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.375rem;
  background: rgba(11, 19, 38, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  padding: 0.5rem;
  max-height: 140px;
  overflow-y: auto;
}
.emoji-select-btn {
  font-size: 1.2rem;
  padding: 0.35rem;
  border-radius: 0.375rem;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}
.emoji-select-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.15);
}
.emoji-select-btn.selected {
  background: rgba(125, 214, 204, 0.2);
  border-color: #7dd6cc;
  box-shadow: 0 0 8px rgba(125, 214, 204, 0.3);
}

/* Form Actions */
.form-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-stitch-secondary {
  padding: 0.6rem 1rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #a3aed0;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-stitch-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #dae2fd;
}

.btn-stitch-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.6rem 1.25rem;
  border-radius: 0.5rem;
  background: #7dd6cc;
  color: #003733;
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 0 12px rgba(125, 214, 204, 0.25);
  flex: 1;
  justify-content: center;
}
.btn-stitch-submit:hover:not(:disabled) {
  background: #9af2e8;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.45);
}
.btn-stitch-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── KHÍ LINH SYSTEM FLOW CARD ─── */
.companion-wisdom-card {
  background: rgba(23, 31, 51, 0.72);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.companion-header-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.875rem;
}

.companion-avatar-wrap {
  position: relative;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background: rgba(196, 193, 251, 0.12);
  color: #c4c1fb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.companion-live-dot {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: #7dd6cc;
  border: 1.5px solid #0b1326;
}

.companion-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #dae2fd;
  margin: 0;
}

.companion-role {
  font-size: 0.75rem;
  color: #a3aed0;
}

.companion-quote-text {
  font-size: 0.85rem;
  line-height: 1.5;
  color: #dae2fd;
  font-style: italic;
  margin: 0 0 1rem 0;
}

/* Distribution Gauge */
.category-distribution-box {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.distribution-labels-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-weight: 600;
}

.distribution-track {
  width: 100%;
  height: 0.5rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
  display: flex;
}

.dist-fill {
  height: 100%;
  transition: width 0.3s ease;
}
</style>
