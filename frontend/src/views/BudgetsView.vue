<template>
  <!-- ═══════ TAB 6: BUDGETS ═══════ -->
  <section class="tab-panel">
    <div class="tab-header" style="display:flex; justify-content: space-between; align-items:center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
      <h2 class="section-title" style="margin:0;">🎯 Hạn Mức Tu Luyện — Ngân Sách</h2>
      <div class="input-group-xianxia" style="width: auto; margin-bottom: 0;">
        <input type="month" v-model="budgetMonth" style="padding: 6px 12px;" />
      </div>
    </div>

    <div class="form-card">
      <h3 class="sub-title">➕ Thiết Lập Hạn Mức</h3>
      <div class="form-grid">
        <div class="input-group-xianxia">
          <label>Danh Mục Chi</label>
          <select v-model="budgetForm.category_id">
            <option v-for="c in expenseCategories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Hạn Mức (VNĐ)</label>
          <input v-model.number="budgetForm.limit_amount" type="number" placeholder="0" />
        </div>
        <div class="input-group-xianxia">
          <label>Tháng</label>
          <input v-model="budgetForm.month_year" type="month" />
        </div>
      </div>
      <button class="btn-jade" @click="createBudget" :disabled="loading" style="margin-top: 16px;">
        {{ loading ? '⏳...' : '🎯 Thiết Lập Hạn Mức' }}
      </button>
    </div>

    <div class="budget-list">
      <div v-for="b in budgets" :key="b.id" class="budget-card">
        <div class="budget-header">
          <span>{{ b.category_icon }} {{ b.category_name }}</span>
          <div class="card-action-btns">
            <button class="btn-sm-edit" @click="openEditBudget(b)" title="Sửa hạn mức">✏️</button>
            <button class="btn-sm-danger" @click="deleteBudget(b.id)" title="Xóa hạn mức">✕</button>
          </div>
        </div>
        <div style="font-size: 0.85rem; color: #a3a3a3; margin-bottom: 8px;">Áp dụng: Tháng {{ b.month_year }}</div>
        <div class="budget-amounts">
          <span>Đã chi: <strong>{{ formatVND(b.spent) }}</strong></span>
          <span>Hạn mức: <strong>{{ formatVND(b.limit_amount) }}</strong></span>
        </div>
        <div class="progress-track">
          <div class="progress-fill"
               :class="budgetPct(b) >= 100 ? 'danger' : budgetPct(b) >= 80 ? 'warning' : 'safe'"
               :style="{ width: Math.min(100, budgetPct(b)) + '%' }">
          </div>
        </div>
        <span class="budget-pct" :class="budgetPct(b) >= 100 ? 'pct-danger' : budgetPct(b) >= 80 ? 'pct-warning' : 'pct-safe'">
          {{ budgetPct(b).toFixed(1) }}%
          <span v-if="budgetPct(b) >= 100"> — 🔥 TẨU HỎA NHẬP MA!</span>
          <span v-else-if="budgetPct(b) >= 80"> — ⚠️ Cảnh Báo Tâm Ma</span>
        </span>
      </div>
      <div v-if="!budgets.length" class="empty-state">Chưa thiết lập hạn mức tu luyện nào...</div>
    </div>
  </section>

  <Teleport to="#modal-root" defer>
    <!-- EDIT BUDGET MODAL -->
    <div v-if="showEditBudgetModal" class="modal-backdrop" @click.self="showEditBudgetModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Hạn Mức</h3>
          <button class="modal-close" @click="showEditBudgetModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>Hạn Mức Mới (VNĐ)</label>
            <input v-model.number="editBudgetForm.limit_amount" type="number" min="0" placeholder="0" @keyup.enter="updateBudget" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditBudgetModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateBudget" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Cập Nhật Hạn Mức' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'BudgetsView',
  setup() {
    const store = useAppStore()
    onMounted(() => store.loadBudgets())
    return useAppBindings()
  },
}
</script>
