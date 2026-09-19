<template>
  <div class="saving-goals-realm">
    <!-- Ambient Celestial Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & ACTION BAR ═══ -->
    <section class="goals-page-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">TU VI TÍCH LŨY • TRÚC CƠ TRÌ</span>
        </div>
        <h1 class="page-title">Mục Tiêu Tích Lũy (Saving Goals)</h1>
        <p class="page-subtitle">
          Định hướng tu vi tài chính, gom góp linh thạch cho các pháp bảo, cơ duyên và đan dược thượng thừa.
        </p>
      </div>

      <div class="header-action-group">
        <button
          type="button"
          class="btn-stitch-primary"
          @click="toggleCreateForm"
          title="Khởi tạo mục tiêu tích lũy mới"
        >
          <span class="material-symbols-outlined">{{ showCreateSection ? 'close' : 'add_circle' }}</span>
          <span>{{ showCreateSection ? 'Đóng Biểu Mẫu' : '+ Khởi Tạo Mục Tiêu' }}</span>
        </button>
      </div>
    </section>

    <!-- ═══ SUMMARY STATS ROW (4 METRIC CARDS) ═══ -->
    <section class="goals-metrics-grid" aria-label="Thống kê tổng quan mục tiêu tích lũy">
      <!-- Stat 1: Total Saved -->
      <div class="goal-metric-card card-saved">
        <div class="metric-card-glow glow-jade"></div>
        <div class="metric-header-row">
          <span class="metric-label">Tổng Linh Thạch Đã Tích</span>
          <div class="metric-icon-box icon-jade">
            <span class="material-symbols-outlined icon-sm">account_balance_wallet</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-jade tabular-num font-bold">
            {{ formatVND(goalsSummary.total_saved || 0) }}
          </div>
          <div class="metric-submeta">
            <span class="text-dim">Mục tiêu: {{ formatVND(goalsSummary.total_target || 0) }}</span>
          </div>
          <!-- Mini overall progress bar -->
          <div class="mini-progress-bar-wrap">
            <div
              class="mini-progress-fill bg-jade"
              :style="{ width: Math.min(100, Math.max(0, goalsSummary.overall_percent || 0)) + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Stat 2: Active Goals -->
      <div class="goal-metric-card card-active">
        <div class="metric-card-glow glow-secondary"></div>
        <div class="metric-header-row">
          <span class="metric-label">Đang Thực Hiện</span>
          <div class="metric-icon-box icon-secondary">
            <span class="material-symbols-outlined icon-sm">hourglass_top</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-secondary tabular-num font-bold">
            {{ goalsSummary.active_count || 0 }} <span class="unit-text">Mục Tiêu</span>
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs text-secondary">bolt</span>
            <span>Dòng chân khí tích tụ ổn định</span>
          </div>
        </div>
      </div>

      <!-- Stat 3: Completed Goals -->
      <div class="goal-metric-card card-completed">
        <div class="metric-card-glow glow-gold"></div>
        <div class="metric-header-row">
          <span class="metric-label">Mục Tiêu Viên Mãn</span>
          <div class="metric-icon-box icon-gold">
            <span class="material-symbols-outlined icon-sm">workspace_premium</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-gold tabular-num font-bold">
            {{ goalsSummary.completed_count || 0 }} <span class="unit-text">Hoàn Tất</span>
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs text-gold">check_circle</span>
            <span>Linh thạch kết tinh viên mãn</span>
          </div>
        </div>
      </div>

      <!-- Stat 4: Remaining Needed -->
      <div class="goal-metric-card card-remaining">
        <div class="metric-card-glow glow-cyan"></div>
        <div class="metric-header-row">
          <span class="metric-label">Linh Thạch Cần Thêm</span>
          <div class="metric-icon-box icon-cyan">
            <span class="material-symbols-outlined icon-sm">trending_up</span>
          </div>
        </div>
        <div class="metric-body-col">
          <div class="metric-value-text text-cyan tabular-num font-bold">
            {{ formatVND(remainingNeeded) }}
          </div>
          <div class="metric-submeta">
            <span class="material-symbols-outlined icon-xs text-cyan">donut_large</span>
            <span>Tiến độ đại đạo: {{ goalsSummary.overall_percent || 0 }}%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ CREATE GOAL FORM SECTION (COLLAPSIBLE / DRAWER) ═══ -->
    <transition name="expand">
      <section v-if="showCreateSection" ref="createFormRef" class="create-goal-section" aria-label="Biểu mẫu khởi tạo mục tiêu mới">
        <div class="create-goal-card">
          <div class="create-card-header">
            <div class="create-title-box">
              <span class="material-symbols-outlined text-jade icon-md">flag</span>
              <h3 class="create-title">Khởi Tạo Mục Tiêu Tiết Kiệm Mới</h3>
            </div>
            <button type="button" class="btn-icon-close" @click="showCreateSection = false" title="Đóng">✕</button>
          </div>

          <form class="create-goal-form" @submit.prevent="handleSubmitCreate">
            <div class="create-form-grid">
              <!-- Goal Name -->
              <div class="form-field-group">
                <label class="field-label">Tên Mục Tiêu / Pháp Bảo <span class="text-danger">*</span></label>
                <div class="input-with-icon-wrap">
                  <span class="material-symbols-outlined input-prefix-icon">military_tech</span>
                  <input
                    v-model="goalForm.target_name"
                    type="text"
                    placeholder="VD: Tậu Phi Kiếm Mới (Laptop), Quỹ Phòng Thân..."
                    class="stitch-input-prefixed"
                    required
                  />
                </div>
              </div>

              <!-- Target Amount -->
              <div class="form-field-group">
                <label class="field-label">Số Tiền Đích (VNĐ) <span class="text-danger">*</span></label>
                <div class="input-with-icon-wrap">
                  <span class="material-symbols-outlined input-prefix-icon text-jade">monetization_on</span>
                  <input
                    v-model.number="goalForm.target_amount"
                    type="number"
                    placeholder="Ví dụ: 30.000.000"
                    min="1"
                    class="stitch-input-prefixed tabular-num"
                    required
                  />
                </div>
              </div>

              <!-- Initial Saved Amount -->
              <div class="form-field-group">
                <label class="field-label">Số Tiền Ban Đầu (VNĐ)</label>
                <div class="input-with-icon-wrap">
                  <span class="material-symbols-outlined input-prefix-icon">savings</span>
                  <input
                    v-model.number="goalForm.current_amount"
                    type="number"
                    placeholder="0"
                    min="0"
                    class="stitch-input-prefixed tabular-num"
                  />
                </div>
              </div>

              <!-- Target Date -->
              <div class="form-field-group">
                <label class="field-label">Thời Hạn Hoàn Thành (Tùy chọn)</label>
                <div class="input-with-icon-wrap">
                  <span class="material-symbols-outlined input-prefix-icon">calendar_today</span>
                  <input
                    v-model="goalForm.target_date"
                    type="date"
                    class="stitch-input-prefixed"
                  />
                </div>
              </div>

              <!-- Icon Selector -->
              <div class="form-field-group">
                <label class="field-label">Biểu Tượng Tâm Pháp</label>
                <select v-model="goalForm.icon" class="stitch-select">
                  <option value="🎯">🎯 Mục Tiêu Chung</option>
                  <option value="💻">💻 Thiết Bị Công Nghệ</option>
                  <option value="🚗">🚗 Phương Tiện Đi Lại</option>
                  <option value="🏠">🏠 An Cư Lạc Nghiệp</option>
                  <option value="✈️">✈️ Du Ngoạn Tứ Phương</option>
                  <option value="🛡️">🛡️ Quỹ Dự Phòng Hộ Thân</option>
                  <option value="🎓">🎓 Tu Học Công Pháp</option>
                  <option value="🎁">🎁 Báo Ân Quà Cáp</option>
                  <option value="🗡️">🗡️ Phi Kiếm Pháp Khí</option>
                  <option value="💊">💊 Đan Dược Đột Phá</option>
                </select>
              </div>
            </div>

            <!-- Submit Button Row -->
            <div class="create-actions-row">
              <button
                type="submit"
                class="btn-stitch-create"
                :disabled="loading || !goalForm.target_name || !goalForm.target_amount || goalForm.target_amount <= 0"
              >
                <span class="material-symbols-outlined">add_task</span>
                <span>{{ loading ? 'Đang khởi tạo...' : '✨ Khởi Tạo Mục Tiêu' }}</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </transition>

    <!-- ═══ FILTER & SEARCH TOOLBAR ═══ -->
    <section class="goals-toolbar-section">
      <div class="toolbar-search-wrap">
        <span class="material-symbols-outlined search-icon">search</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm mục tiêu theo tên..."
          class="toolbar-search-input"
        />
        <button
          v-if="searchQuery"
          type="button"
          class="btn-clear-search"
          @click="searchQuery = ''"
          title="Xóa tìm kiếm"
        >
          ✕
        </button>
      </div>

      <div class="toolbar-controls-group">
        <!-- Status Filter Tabs -->
        <div class="filter-segmented-control" role="tablist">
          <button
            type="button"
            class="filter-pill"
            :class="{ active: activeStatusFilter === 'all' }"
            @click="activeStatusFilter = 'all'"
          >
            Tất Cả ({{ savingGoals.length }})
          </button>
          <button
            type="button"
            class="filter-pill"
            :class="{ active: activeStatusFilter === 'active' }"
            @click="activeStatusFilter = 'active'"
          >
            Đang Tích Tụ ({{ goalsSummary.active_count || 0 }})
          </button>
          <button
            type="button"
            class="filter-pill"
            :class="{ active: activeStatusFilter === 'completed' }"
            @click="activeStatusFilter = 'completed'"
          >
            Viên Mãn ({{ goalsSummary.completed_count || 0 }})
          </button>
        </div>

        <!-- Sort Select -->
        <div class="sort-select-wrap">
          <span class="material-symbols-outlined sort-icon">sort</span>
          <select v-model="sortBy" class="sort-select">
            <option value="default">Mặc định</option>
            <option value="deadline">Kỳ hạn gần nhất</option>
            <option value="progress">Tiến độ cao nhất</option>
            <option value="amount">Số tiền lớn nhất</option>
            <option value="name">Tên A-Z</option>
          </select>
        </div>
      </div>
    </section>

    <!-- ═══ GOALS GRID (2-COL DESKTOP) ═══ -->
    <section class="goals-grid-section" aria-label="Danh sách mục tiêu tích lũy">
      <div v-if="filteredAndSortedGoals.length" class="goals-cards-grid">
        <article
          v-for="goal in filteredAndSortedGoals"
          :key="goal.id"
          class="goal-card-item"
          :class="{ 'card-is-completed': goal.is_completed }"
        >
          <!-- Accent Corner Gradient Backdrop -->
          <div class="card-ambient-corner" :class="goal.is_completed ? 'corner-gold' : 'corner-jade'"></div>

          <!-- Card Top: Icon, Titles & Action Buttons -->
          <div class="goal-card-top">
            <div class="goal-info-cluster">
              <div class="goal-avatar-box">
                <span class="goal-emoji-icon">{{ goal.icon || '🎯' }}</span>
              </div>
              <div class="goal-text-col">
                <div class="goal-status-badge-row">
                  <span
                    class="goal-status-chip"
                    :class="goal.is_completed ? 'chip-completed' : 'chip-active'"
                  >
                    <span class="chip-dot"></span>
                    <span>{{ goal.is_completed ? '🎉 Đạt Mục Tiêu' : '⏳ Đang Tích Lũy' }}</span>
                  </span>
                  <span v-if="goal.target_date" class="goal-date-badge" :class="getDateBadgeClass(goal)">
                    <span class="material-symbols-outlined icon-xs">event</span>
                    <span>{{ getDateLabel(goal) }}</span>
                  </span>
                </div>
                <h3 class="goal-card-name" :title="goal.target_name">{{ goal.target_name }}</h3>
              </div>
            </div>

            <!-- Card Header Action Icons (Edit & Delete) -->
            <div class="card-icon-actions">
              <button
                type="button"
                class="btn-icon-action btn-edit-goal"
                @click="$emit('open-edit-goal', goal)"
                title="Chỉnh sửa mục tiêu"
              >
                <span class="material-symbols-outlined icon-sm">edit</span>
              </button>
              <button
                type="button"
                class="btn-icon-action btn-delete-goal"
                @click="$emit('delete-goal', goal.id)"
                title="Xóa mục tiêu"
              >
                <span class="material-symbols-outlined icon-sm">delete</span>
              </button>
            </div>
          </div>

          <!-- Financial Figures Ledger (3-column box) -->
          <div class="goal-ledger-box">
            <div class="ledger-col">
              <span class="ledger-label">Đã Gom Góp</span>
              <span class="ledger-value text-jade tabular-num font-bold">{{ formatVND(goal.current_amount) }}</span>
            </div>
            <div class="ledger-col border-center">
              <span class="ledger-label">Mục Tiêu Đích</span>
              <span class="ledger-value text-main tabular-num font-bold">{{ formatVND(goal.target_amount) }}</span>
            </div>
            <div class="ledger-col text-right">
              <span class="ledger-label">{{ goal.is_completed ? 'Dư Linh Thạch' : 'Còn Thiếu' }}</span>
              <span
                class="ledger-value tabular-num font-bold"
                :class="goal.is_completed ? 'text-gold' : 'text-amber'"
              >
                {{ formatVND(goal.remaining_amount) }}
              </span>
            </div>
          </div>

          <!-- Progress Bar Section -->
          <div class="goal-progress-section">
            <div class="progress-meta-row">
              <span class="progress-label">Tiến Độ Đại Đạo</span>
              <span class="progress-percent font-bold" :class="goal.is_completed ? 'text-gold' : 'text-jade'">
                {{ goal.percent }}%
              </span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :class="goal.is_completed ? 'fill-gold' : 'fill-jade'"
                :style="{ width: Math.min(100, Math.max(0, goal.percent)) + '%' }"
              ></div>
            </div>
          </div>

          <!-- Card Footer Quick Actions (Deposit & Withdraw) -->
          <div class="goal-card-footer">
            <div class="footer-tip">
              <span class="pulse-dot-sm" :class="goal.is_completed ? 'bg-gold' : 'bg-jade'"></span>
              <span class="tip-text">{{ getGoalAdvice(goal) }}</span>
            </div>
            <div class="footer-btn-group">
              <button
                type="button"
                class="btn-card-action btn-deposit"
                :disabled="goal.is_completed"
                @click="$emit('open-deposit-goal', goal, 'deposit')"
                title="Nạp thêm linh thạch vào mục tiêu"
              >
                <span class="material-symbols-outlined icon-sm">input</span>
                <span>Nạp Thêm</span>
              </button>
              <button
                type="button"
                class="btn-card-action btn-withdraw"
                :disabled="goal.current_amount <= 0"
                @click="$emit('open-deposit-goal', goal, 'withdraw')"
                title="Rút linh thạch khỏi mục tiêu"
              >
                <span class="material-symbols-outlined icon-sm">output</span>
                <span>Rút</span>
              </button>
            </div>
          </div>
        </article>
      </div>

      <!-- Empty State -->
      <div v-else class="goals-empty-state">
        <div class="empty-icon-wrap">
          <span class="material-symbols-outlined empty-symbol">flag_circle</span>
        </div>
        <h3 class="empty-title">
          {{ searchQuery || activeStatusFilter !== 'all' ? 'Không Tìm Thấy Mục Tiêu Phù Hợp' : 'Chưa Có Mục Tiêu Tích Lũy Nào' }}
        </h3>
        <p class="empty-desc">
          {{ searchQuery || activeStatusFilter !== 'all' 
            ? 'Đạo hữu vui lòng kiểm tra lại từ khóa tìm kiếm hoặc điều chỉnh bộ lọc phân loại.' 
            : 'Hãy khởi tạo mục tiêu đầu tiên để gom góp linh thạch tu luyện, tậu pháp bảo thượng thừa!' }}
        </p>
        <button
          v-if="!searchQuery && activeStatusFilter === 'all'"
          type="button"
          class="btn-stitch-primary"
          @click="toggleCreateForm"
        >
          <span class="material-symbols-outlined">add_circle</span>
          <span>Khởi Tạo Mục Tiêu Đầu Tiên</span>
        </button>
        <button
          v-else
          type="button"
          class="btn-stitch-outline"
          @click="resetFilters"
        >
          <span>Khôi Phục Bộ Lọc</span>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  savingGoals: {
    type: Array,
    default: () => []
  },
  goalsSummary: {
    type: Object,
    default: () => ({
      total_target: 0,
      total_saved: 0,
      completed_count: 0,
      active_count: 0,
      overall_percent: 0
    })
  },
  goalForm: {
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
  'create-goal',
  'open-edit-goal',
  'open-deposit-goal',
  'delete-goal',
  'load-goals'
])

// UI-only reactive states
const showCreateSection = ref(false)
const createFormRef = ref(null)
const searchQuery = ref('')
const activeStatusFilter = ref('all') // 'all' | 'active' | 'completed'
const sortBy = ref('default') // 'default' | 'deadline' | 'progress' | 'amount' | 'name'

// Computed metrics
const remainingNeeded = computed(() => {
  const target = Number(props.goalsSummary.total_target || 0)
  const saved = Number(props.goalsSummary.total_saved || 0)
  return Math.max(0, target - saved)
})

// Filtered and Sorted Goals List
const filteredAndSortedGoals = computed(() => {
  let list = [...(props.savingGoals || [])]

  // Filter by status
  if (activeStatusFilter.value === 'active') {
    list = list.filter(g => !g.is_completed)
  } else if (activeStatusFilter.value === 'completed') {
    list = list.filter(g => g.is_completed)
  }

  // Filter by search query
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(g => g.target_name && g.target_name.toLowerCase().includes(q))
  }

  // Sort
  if (sortBy.value === 'deadline') {
    list.sort((a, b) => {
      if (!a.target_date) return 1
      if (!b.target_date) return -1
      return new Date(a.target_date) - new Date(b.target_date)
    })
  } else if (sortBy.value === 'progress') {
    list.sort((a, b) => (b.percent || 0) - (a.percent || 0))
  } else if (sortBy.value === 'amount') {
    list.sort((a, b) => (b.target_amount || 0) - (a.target_amount || 0))
  } else if (sortBy.value === 'name') {
    list.sort((a, b) => (a.target_name || '').localeCompare(b.target_name || ''))
  }

  return list
})

// Toggle create form with auto-scroll
function toggleCreateForm() {
  showCreateSection.value = !showCreateSection.value
  if (showCreateSection.value) {
    nextTick(() => {
      if (createFormRef.value?.scrollIntoView) {
        createFormRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
  }
}

function handleSubmitCreate() {
  emit('create-goal')
}

function resetFilters() {
  searchQuery.value = ''
  activeStatusFilter.value = 'all'
  sortBy.value = 'default'
}

// Helpers for dates and advice
function getDateLabel(goal) {
  if (!goal.target_date) return ''
  if (goal.days_left === null || goal.days_left === undefined) {
    return goal.target_date
  }
  if (goal.days_left < 0) {
    return `Quá hạn ${Math.abs(goal.days_left)} ngày`
  } else if (goal.days_left === 0) {
    return 'Hôm nay đến hạn'
  } else {
    return `Còn ${goal.days_left} ngày`
  }
}

function getDateBadgeClass(goal) {
  if (goal.is_completed) return 'date-completed'
  if (goal.days_left === null || goal.days_left === undefined) return 'date-neutral'
  if (goal.days_left < 0) return 'date-overdue'
  if (goal.days_left <= 7) return 'date-warning'
  return 'date-normal'
}

function getGoalAdvice(goal) {
  if (goal.is_completed) {
    return 'Đại thành viên mãn! Linh thạch đã hội tụ đủ.'
  }
  if (goal.days_left !== null && goal.days_left > 0 && goal.remaining_amount > 0) {
    const dailyNeed = Math.ceil(goal.remaining_amount / goal.days_left)
    return `Khuyên nạp: ~${props.formatVND(dailyNeed)} / ngày`
  }
  return 'Tiếp tục gom góp linh thạch để sớm đạt mục tiêu.'
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   SAVING GOALS REALM (STITCH CELESTIAL TREASURY)
   ═══════════════════════════════════════════════════════════════════════════ */

.saving-goals-realm {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 24px);
  width: 100%;
}

/* Ambient Glow Orbs */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
}

.orb-primary {
  top: -60px;
  right: 12%;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.08) 0%, transparent 70%);
}

.orb-secondary {
  top: 300px;
  left: 5%;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(196, 193, 251, 0.06) 0%, transparent 70%);
}

/* ─── PAGE HEADER & ACTION BAR ─── */
.goals-page-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 16px);
}

@media (min-width: 768px) {
  .goals-page-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.header-badge-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.status-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.8);
  animation: pulse-glow 2s infinite ease-in-out;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.badge-text {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-primary, #7dd6cc);
}

.page-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
  letter-spacing: -0.02em;
}

@media (min-width: 768px) {
  .page-title {
    font-size: 32px;
  }
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 640px;
  line-height: 1.5;
}

/* Stitch Primary Button */
.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  font-size: 14px;
  font-weight: 700;
  border: none;
  border-radius: var(--radius-lg, 12px);
  cursor: pointer;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.btn-stitch-primary:hover {
  background-color: var(--color-primary-fixed, #9af2e8);
  transform: translateY(-2px);
  box-shadow: 0 0 25px rgba(125, 214, 204, 0.5);
}

.btn-stitch-primary:active {
  transform: translateY(0);
}

.btn-stitch-outline {
  padding: 8px 18px;
  background: transparent;
  color: var(--color-primary, #7dd6cc);
  border: 1px solid rgba(125, 214, 204, 0.4);
  border-radius: var(--radius-lg, 12px);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-outline:hover {
  background: rgba(125, 214, 204, 0.1);
  border-color: var(--color-primary, #7dd6cc);
}

/* ─── 4 METRICS GRID ─── */
.goals-metrics-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md, 16px);
}

@media (min-width: 640px) {
  .goals-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .goals-metrics-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.goal-metric-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-md, 16px) var(--space-lg, 20px);
  background: rgba(23, 31, 51, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-xl, 16px);
  overflow: hidden;
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.goal-metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
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
  opacity: 0.35;
  transition: opacity 0.3s ease;
}

.goal-metric-card:hover .metric-card-glow {
  opacity: 0.6;
}

.glow-jade { background: var(--color-primary, #7dd6cc); }
.glow-secondary { background: var(--color-secondary, #c4c1fb); }
.glow-gold { background: var(--color-tertiary, #e3c370); }
.glow-cyan { background: #38bdf8; }

.metric-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.metric-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.metric-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md, 8px);
}

.icon-jade {
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
}

.icon-secondary {
  background: rgba(196, 193, 251, 0.15);
  color: var(--color-secondary, #c4c1fb);
}

.icon-gold {
  background: rgba(227, 195, 112, 0.15);
  color: var(--color-tertiary, #e3c370);
}

.icon-cyan {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
}

.metric-body-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-value-text {
  font-size: 22px;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.unit-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.metric-submeta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.mini-progress-bar-wrap {
  width: 100%;
  height: 4px;
  background: rgba(6, 14, 32, 0.7);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 4px;
}

.mini-progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.5s ease;
}

/* ─── CREATE GOAL SECTION ─── */
.create-goal-section {
  position: relative;
  z-index: 1;
}

.create-goal-card {
  background: rgba(23, 31, 51, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(125, 214, 204, 0.25);
  border-radius: var(--radius-xl, 16px);
  padding: var(--space-lg, 24px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
}

.create-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.create-title-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.create-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
}

.btn-icon-close {
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 16px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: var(--radius-md, 8px);
  transition: background 0.2s ease;
}

.btn-icon-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-on-surface, #dae2fd);
}

.create-form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md, 16px);
}

@media (min-width: 640px) {
  .create-form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .create-form-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-on-surface-variant, #bdc9c6);
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
  color: var(--color-on-surface-variant, #bdc9c6);
  pointer-events: none;
}

.stitch-input-prefixed {
  width: 100%;
  padding: 10px 12px 10px 38px;
  background: rgba(6, 14, 32, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg, 10px);
  color: var(--color-on-surface, #dae2fd);
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.stitch-input-prefixed:focus {
  outline: none;
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 0 2px rgba(125, 214, 204, 0.2);
}

.stitch-select {
  width: 100%;
  padding: 10px 12px;
  background: rgba(6, 14, 32, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg, 10px);
  color: var(--color-on-surface, #dae2fd);
  font-size: 14px;
  cursor: pointer;
}

.stitch-select:focus {
  outline: none;
  border-color: var(--color-primary, #7dd6cc);
}

.create-actions-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-stitch-create {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 24px;
  background: linear-gradient(135deg, var(--color-primary, #7dd6cc) 0%, var(--color-primary-container, #449f96) 100%);
  color: var(--color-on-primary, #003733);
  font-size: 14px;
  font-weight: 700;
  border: none;
  border-radius: var(--radius-lg, 10px);
  cursor: pointer;
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.35);
  transition: all 0.2s ease;
}

.btn-stitch-create:hover:not(:disabled) {
  box-shadow: 0 0 22px rgba(125, 214, 204, 0.55);
  transform: translateY(-1px);
}

.btn-stitch-create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── TOOLBAR SECTION ─── */
.goals-toolbar-section {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 16px);
  padding: 14px 18px;
  background: rgba(23, 31, 51, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-xl, 14px);
}

@media (min-width: 768px) {
  .goals-toolbar-section {
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
  max-width: 380px;
}

.search-icon {
  position: absolute;
  left: 12px;
  font-size: 18px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.toolbar-search-input {
  width: 100%;
  padding: 8px 36px 8px 36px;
  background: rgba(6, 14, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 10px);
  color: var(--color-on-surface, #dae2fd);
  font-size: 13px;
}

.toolbar-search-input:focus {
  outline: none;
  border-color: var(--color-primary, #7dd6cc);
}

.btn-clear-search {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 14px;
  cursor: pointer;
}

.toolbar-controls-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-segmented-control {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(6, 14, 32, 0.8);
  padding: 4px;
  border-radius: var(--radius-lg, 10px);
}

.filter-pill {
  padding: 6px 14px;
  border-radius: var(--radius-md, 8px);
  border: none;
  background: transparent;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-pill.active {
  background: rgba(125, 214, 204, 0.2);
  color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.25);
}

.sort-select-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(6, 14, 32, 0.8);
  padding: 2px 10px;
  border-radius: var(--radius-lg, 10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.sort-icon {
  font-size: 16px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.sort-select {
  background: transparent;
  border: none;
  color: var(--color-on-surface, #dae2fd);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 4px;
}

.sort-select:focus {
  outline: none;
}

/* ─── GOALS GRID (2-COL) ─── */
.goals-grid-section {
  position: relative;
  z-index: 1;
}

.goals-cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg, 20px);
}

@media (min-width: 1024px) {
  .goals-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.goal-card-item {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-lg, 22px);
  background: rgba(23, 31, 51, 0.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 16px);
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.goal-card-item:hover {
  transform: translateY(-2px);
  border-color: rgba(125, 214, 204, 0.3);
  box-shadow: 0 12px 36px rgba(125, 214, 204, 0.15);
}

.goal-card-item.card-is-completed {
  border-color: rgba(227, 195, 112, 0.25);
}

.goal-card-item.card-is-completed:hover {
  border-color: rgba(227, 195, 112, 0.45);
  box-shadow: 0 12px 36px rgba(227, 195, 112, 0.15);
}

.card-ambient-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 130px;
  height: 130px;
  border-bottom-left-radius: 9999px;
  pointer-events: none;
  opacity: 0.15;
  transition: opacity 0.3s ease;
}

.goal-card-item:hover .card-ambient-corner {
  opacity: 0.3;
}

.corner-jade {
  background: radial-gradient(circle, var(--color-primary, #7dd6cc) 0%, transparent 70%);
}

.corner-gold {
  background: radial-gradient(circle, var(--color-tertiary, #e3c370) 0%, transparent 70%);
}

/* Card Top Row */
.goal-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.goal-info-cluster {
  display: flex;
  align-items: center;
  gap: 14px;
}

.goal-avatar-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  background: rgba(34, 42, 61, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg, 12px);
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4);
}

.goal-emoji-icon {
  font-size: 26px;
}

.goal-text-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.goal-status-badge-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.goal-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 700;
}

.chip-active {
  background: rgba(125, 214, 204, 0.12);
  color: var(--color-primary, #7dd6cc);
}

.chip-completed {
  background: rgba(227, 195, 112, 0.15);
  color: var(--color-tertiary, #e3c370);
}

.chip-dot {
  width: 5px;
  height: 5px;
  border-radius: 9999px;
  background-color: currentColor;
}

.goal-date-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 500;
}

.date-normal {
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-on-surface-variant, #bdc9c6);
}

.date-warning {
  background: rgba(227, 195, 112, 0.15);
  color: var(--color-tertiary, #e3c370);
}

.date-overdue {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.date-completed {
  background: rgba(125, 214, 204, 0.1);
  color: var(--color-primary, #7dd6cc);
}

.goal-card-name {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
  line-height: 1.3;
  transition: color 0.2s ease;
}

.goal-card-item:hover .goal-card-name {
  color: var(--color-primary, #7dd6cc);
}

.card-icon-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-icon-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md, 8px);
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit-goal:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--color-primary, #7dd6cc);
}

.btn-delete-goal:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Financial Ledger Box */
.goal-ledger-box {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px 14px;
  background: rgba(6, 14, 32, 0.6);
  border-radius: var(--radius-lg, 12px);
  border: 1px solid rgba(255, 255, 255, 0.04);
  margin-bottom: 16px;
}

.ledger-col {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.border-center {
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0 10px;
}

.ledger-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-on-surface-variant, #bdc9c6);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.ledger-value {
  font-size: 14px;
  letter-spacing: -0.01em;
}

/* Progress Bar */
.goal-progress-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.progress-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.progress-label {
  color: var(--color-on-surface-variant, #bdc9c6);
}

.progress-track {
  width: 100%;
  height: 8px;
  background: rgba(6, 14, 32, 0.8);
  border-radius: 9999px;
  overflow: hidden;
  padding: 1px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.5);
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fill-jade {
  background: linear-gradient(90deg, #2b8a82 0%, #7dd6cc 100%);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.5);
}

.fill-gold {
  background: linear-gradient(90deg, #c6a858 0%, #e3c370 100%);
  box-shadow: 0 0 10px rgba(227, 195, 112, 0.5);
}

/* Card Footer */
.goal-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.footer-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.pulse-dot-sm {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
}

.tip-text {
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.footer-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-card-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-md, 8px);
  font-size: 13px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-deposit {
  background-color: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  box-shadow: 0 0 12px rgba(125, 214, 204, 0.3);
}

.btn-deposit:hover:not(:disabled) {
  background-color: var(--color-primary-fixed, #9af2e8);
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.5);
  transform: translateY(-1px);
}

.btn-deposit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-withdraw {
  background: rgba(34, 42, 61, 0.8);
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-withdraw:hover:not(:disabled) {
  background: rgba(49, 57, 77, 0.9);
  color: var(--color-on-surface, #dae2fd);
}

.btn-withdraw:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ─── EMPTY STATE ─── */
.goals-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 60px 24px;
  background: rgba(23, 31, 51, 0.5);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xl, 16px);
}

.empty-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 9999px;
  background: rgba(125, 214, 204, 0.1);
  margin-bottom: 16px;
}

.empty-symbol {
  font-size: 32px;
  color: var(--color-primary, #7dd6cc);
}

.empty-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
}

.empty-desc {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 460px;
  line-height: 1.5;
}

/* Helper utility text classes */
.text-jade { color: var(--color-primary, #7dd6cc); }
.text-gold { color: var(--color-tertiary, #e3c370); }
.text-secondary { color: var(--color-secondary, #c4c1fb); }
.text-cyan { color: #38bdf8; }
.text-amber { color: #fbbf24; }
.text-danger { color: var(--color-error, #ffb4ab); }
.text-main { color: var(--color-on-surface, #dae2fd); }
.text-dim { color: var(--color-on-surface-variant, #bdc9c6); }

.bg-jade { background-color: var(--color-primary, #7dd6cc); }
.bg-gold { background-color: var(--color-tertiary, #e3c370); }

.tabular-num { font-variant-numeric: tabular-nums; }
.font-bold { font-weight: 700; }

.icon-xs { font-size: 14px; }
.icon-sm { font-size: 18px; }
.icon-md { font-size: 22px; }

/* Transitions */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease-out;
  max-height: 500px;
  opacity: 1;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
}
</style>
