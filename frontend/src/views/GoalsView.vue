<template>
  <!-- ═══════ TAB: SAVING GOALS (MỤC TIÊU TIẾT KIỆM) ═══════ -->
  <section class="tab-panel">
    <h2 class="section-title">🎯 Mục Tiêu Tích Lũy — Tụ Khí Linh Thạch</h2>

    <!-- Goals Summary Metrics -->
    <div class="metrics-grid">
      <div class="metric-card gold">
        <div class="metric-icon">🎯</div>
        <div class="metric-info">
          <span class="metric-label">Tổng Mục Tiêu</span>
          <span class="metric-value">{{ formatVND(goalsSummary.total_target) }}</span>
        </div>
      </div>
      <div class="metric-card jade">
        <div class="metric-icon">💎</div>
        <div class="metric-info">
          <span class="metric-label">Đã Tích Lũy</span>
          <span class="metric-value">{{ formatVND(goalsSummary.total_saved) }}</span>
        </div>
      </div>
      <div class="metric-card purple">
        <div class="metric-icon">📈</div>
        <div class="metric-info">
          <span class="metric-label">Tiến Độ Chung</span>
          <span class="metric-value">{{ goalsSummary.overall_percent }}%</span>
        </div>
      </div>
      <div class="metric-card crimson">
        <div class="metric-icon">🏆</div>
        <div class="metric-info">
          <span class="metric-label">Hoàn Thành</span>
          <span class="metric-value">{{ goalsSummary.completed_count }} / {{ goalsSummary.completed_count + goalsSummary.active_count }}</span>
        </div>
      </div>
    </div>

    <!-- Add Goal Form -->
    <div class="form-card">
      <h3 class="sub-title">➕ Khởi Tạo Mục Tiêu Tiết Kiệm Mới</h3>
      <div class="form-grid">
        <div class="input-group-xianxia">
          <label>Tên Mục Tiêu</label>
          <input v-model="goalForm.target_name" type="text" placeholder="VD: Tậu Phi Kiếm Mới (Laptop)" />
        </div>
        <div class="input-group-xianxia">
          <label>Số Tiền Đích (VNĐ)</label>
          <input v-model.number="goalForm.target_amount" type="number" placeholder="0" min="0" />
        </div>
        <div class="input-group-xianxia">
          <label>Số Tiền Ban Đầu (VNĐ)</label>
          <input v-model.number="goalForm.current_amount" type="number" placeholder="0" min="0" />
        </div>
        <div class="input-group-xianxia">
          <label>Thời Hạn Hoàn Thành (Tùy chọn)</label>
          <input v-model="goalForm.target_date" type="date" />
        </div>
        <div class="input-group-xianxia">
          <label>Biểu Tượng</label>
          <select v-model="goalForm.icon">
            <option value="🎯">🎯 Mục Tiêu</option>
            <option value="💻">💻 Thiết Bị</option>
            <option value="🚗">🚗 Phương Tiện</option>
            <option value="🏠">🏠 Nhà Cửa</option>
            <option value="✈️">✈️ Du Ngoạn</option>
            <option value="🛡️">🛡️ Quỹ Dự Phòng</option>
            <option value="🎓">🎓 Học Tập</option>
            <option value="🎁">🎁 Quà Tặng</option>
          </select>
        </div>
      </div>
      <button class="btn-jade" @click="createSavingGoal" :disabled="loading" style="margin-top: 16px;">
        {{ loading ? '⏳...' : '✨ Khởi Tạo Mục Tiêu' }}
      </button>
    </div>

    <!-- Goals Cards Grid -->
    <div class="table-header-flex" style="margin-top: 24px;">
      <h3 class="sub-title">🏆 Danh Sách Mục Tiêu ({{ savingGoals.length }})</h3>
    </div>

    <div class="goals-grid">
      <div v-for="goal in savingGoals" :key="goal.id" :class="['goal-card', { 'goal-completed': goal.is_completed }]">
        <div class="goal-header">
          <div class="goal-icon-name">
            <span class="goal-icon">{{ goal.icon }}</span>
            <div>
              <h4 class="goal-name">{{ goal.target_name }}</h4>
              <span v-if="goal.target_date" class="goal-date">
                📅 Hạn: {{ goal.target_date }}
                <span v-if="goal.days_left !== null" :class="goal.days_left < 0 ? 'text-crimson' : 'text-gold'">
                  ({{ goal.days_left < 0 ? `Quá hạn ${Math.abs(goal.days_left)} ngày` : `Còn ${goal.days_left} ngày` }})
                </span>
              </span>
            </div>
          </div>
          <span :class="['goal-badge', goal.is_completed ? 'completed' : 'in-progress']">
            {{ goal.is_completed ? '🎉 Đạt Mục Tiêu' : '⏳ Đang Tích Lũy' }}
          </span>
        </div>

        <!-- Progress Info -->
        <div class="goal-progress-wrap">
          <div class="goal-amounts">
            <span class="goal-current">{{ formatVND(goal.current_amount) }}</span>
            <span class="goal-target">/ {{ formatVND(goal.target_amount) }}</span>
          </div>
          <div class="goal-progress-bar">
            <div class="goal-progress-fill" :style="{ width: goal.percent + '%' }"></div>
          </div>
          <div class="goal-progress-labels">
            <span>Tiến độ: <strong>{{ goal.percent }}%</strong></span>
            <span v-if="!goal.is_completed">Còn thiếu: {{ formatVND(goal.remaining_amount) }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="goal-actions">
          <button class="btn-action-jade" @click="openDepositGoal(goal, 'deposit')" :disabled="goal.is_completed">
            ➕ Nạp Thêm
          </button>
          <button class="btn-action-gold" @click="openDepositGoal(goal, 'withdraw')" :disabled="goal.current_amount <= 0">
            ➖ Rút Bớt
          </button>
          <button class="btn-sm-edit" @click="openEditGoal(goal)" title="Sửa">✏️</button>
          <button class="btn-sm-danger" @click="deleteSavingGoal(goal.id)" title="Xóa">🗑️</button>
        </div>
      </div>
      <div v-if="!savingGoals.length" class="empty-state">Chưa có mục tiêu tiết kiệm nào. Hãy tạo mục tiêu đầu tiên!</div>
    </div>
  </section>

  <Teleport to="#modal-root" defer>
    <!-- EDIT SAVING GOAL MODAL -->
    <div v-if="showEditGoalModal" class="modal-backdrop" @click.self="showEditGoalModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Mục Tiêu Tiết Kiệm</h3>
          <button class="modal-close" @click="showEditGoalModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Tên Mục Tiêu</label>
              <input v-model="editGoalForm.target_name" type="text" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền Đích (VNĐ)</label>
              <input v-model.number="editGoalForm.target_amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền Đang Có (VNĐ)</label>
              <input v-model.number="editGoalForm.current_amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Thời Hạn</label>
              <input v-model="editGoalForm.target_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>Biểu Tượng</label>
              <select v-model="editGoalForm.icon">
                <option value="🎯">🎯 Mục Tiêu</option>
                <option value="💻">💻 Thiết Bị</option>
                <option value="🚗">🚗 Phương Tiện</option>
                <option value="🏠">🏠 Nhà Cửa</option>
                <option value="✈️">✈️ Du Ngoạn</option>
                <option value="🛡️">🛡️ Quỹ Dự Phòng</option>
                <option value="🎓">🎓 Học Tập</option>
                <option value="🎁">🎁 Quà Tặng</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Trạng Thái Hoàn Thành</label>
              <select v-model.number="editGoalForm.is_completed">
                <option :value="0">⏳ Đang Tích Lũy</option>
                <option :value="1">🎉 Đã Hoàn Thành</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditGoalModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateSavingGoal" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>

    <!-- DEPOSIT / WITHDRAW SAVING GOAL MODAL -->
    <div v-if="showDepositModal" class="modal-backdrop" @click.self="showDepositModal = false">
      <div class="modal-card" style="max-width: 480px;">
        <div class="modal-header">
          <h3 class="modal-title">{{ depositForm.action === 'deposit' ? '➕ Nạp Linh Thạch Tích Lũy' : '➖ Rút Linh Thạch Khỏi Mục Tiêu' }}</h3>
          <button class="modal-close" @click="showDepositModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="hint-text" style="margin-bottom: 16px;">Mục tiêu: <strong>{{ depositForm.goal_name }}</strong></p>
          <div class="input-group-xianxia">
            <label>Số Tiền {{ depositForm.action === 'deposit' ? 'Nạp (VNĐ)' : 'Rút (VNĐ)' }}</label>
            <input v-model.number="depositForm.amount" type="number" placeholder="0" min="0" />
          </div>
          <div class="input-group-xianxia">
            <label>{{ depositForm.action === 'deposit' ? 'Trừ Tiền Từ Ví (Tùy chọn)' : 'Cộng Tiền Vào Ví (Tùy chọn)' }}</label>
            <select v-model="depositForm.wallet_id">
              <option value="">— Không qua ví (tích lũy độc lập) —</option>
              <option v-for="w in wallets" :key="'dep-w-'+w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
            </select>
          </div>
          <div v-if="goalLogs.length" style="margin-top: 12px;">
            <label class="hint-text">📜 Lịch sử nạp / rút gần đây</label>
            <div class="table-scroll">
              <table class="xianxia-table">
                <tbody>
                  <tr v-for="log in goalLogs" :key="'gl-'+log.id">
                    <td>{{ log.created_at }}</td>
                    <td :class="log.action === 'DEPOSIT' ? 'amt-income' : 'amt-expense'">
                      {{ log.action === 'DEPOSIT' ? '+' : '-' }}{{ formatVND(log.amount) }}
                    </td>
                    <td>{{ log.wallet_name || 'Tích lũy độc lập' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDepositModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="submitDepositWithdrawGoal" :disabled="loading || !depositForm.amount">
            {{ loading ? '⏳...' : (depositForm.action === 'deposit' ? '✨ Xác Nhận Nạp' : '⚡ Xác Nhận Rút') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'GoalsView',
  setup() {
    return useAppBindings()
  },
}
</script>
