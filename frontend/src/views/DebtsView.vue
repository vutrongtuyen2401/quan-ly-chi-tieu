<template>
  <!-- ═══════ TAB: DEBTS (SỔ NỢ / VAY MƯỢN) ═══════ -->
  <section class="tab-panel">
    <h2 class="section-title">📜 Sổ Ghi Nợ — Vay Mượn Linh Thạch</h2>

    <!-- Debt Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card crimson">
        <div class="metric-icon">🔴</div>
        <div class="metric-info">
          <span class="metric-label">Tôi Nợ (Cần Trả)</span>
          <span class="metric-value">{{ formatVND(debtsSummary.total_borrow_unsettled) }}</span>
        </div>
      </div>
      <div class="metric-card jade">
        <div class="metric-icon">🟢</div>
        <div class="metric-info">
          <span class="metric-label">Cho Vay (Cần Thu)</span>
          <span class="metric-value">{{ formatVND(debtsSummary.total_lend_unsettled) }}</span>
        </div>
      </div>
      <div class="metric-card gold">
        <div class="metric-icon">⚖️</div>
        <div class="metric-info">
          <span class="metric-label">Hiệu Số Nợ Ròng</span>
          <span class="metric-value" :class="debtsSummary.total_lend_unsettled - debtsSummary.total_borrow_unsettled >= 0 ? 'positive' : 'negative'">
            {{ formatVND(debtsSummary.total_lend_unsettled - debtsSummary.total_borrow_unsettled) }}
          </span>
        </div>
      </div>
      <div class="metric-card purple">
        <div class="metric-icon">✅</div>
        <div class="metric-info">
          <span class="metric-label">Đã Tất Toán</span>
          <span class="metric-value">{{ formatVND(debtsSummary.total_borrow_settled + debtsSummary.total_lend_settled) }}</span>
        </div>
      </div>
    </div>

    <!-- Add Debt Form -->
    <div class="form-card">
      <h3 class="sub-title">➕ Ghi Nhận Khoản Nợ / Cho Vay Mới</h3>
      <div class="form-grid">
        <div class="input-group-xianxia">
          <label>Loại Khoản Nợ</label>
          <select v-model="debtForm.debt_type">
            <option value="BORROW">🔴 Tôi Vay Nợ (Cần trả người khác)</option>
            <option value="LEND">🟢 Tôi Cho Vay (Người khác nợ tôi)</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Đối Tác / Người Vay-Mượn</label>
          <input v-model="debtForm.person_name" type="text" placeholder="VD: Đạo hữu Tiêu Viêm" />
        </div>
        <div class="input-group-xianxia">
          <label>Số Linh Thạch (VNĐ)</label>
          <input v-model.number="debtForm.amount" type="number" placeholder="0" min="0" />
        </div>
        <div class="input-group-xianxia">
          <label>Ngày Đến Hạn (Tùy chọn)</label>
          <input v-model="debtForm.due_date" type="date" />
        </div>
        <div class="input-group-xianxia">
          <label>Liên Kết Túi Càn Khôn (Tùy chọn)</label>
          <select v-model="debtForm.wallet_id">
            <option value="">— Không liên kết —</option>
            <option v-for="w in wallets" :key="'debt-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Ghi Chú / Lý Do</label>
          <input v-model="debtForm.note" type="text" placeholder="VD: Mượn mua đan dược..." />
        </div>
      </div>
      <button class="btn-jade" @click="createDebt" :disabled="loading" style="margin-top: 16px;">
        {{ loading ? '⏳...' : '✨ Ghi Vào Sổ Nợ' }}
      </button>
    </div>

    <!-- Filter & Search Debts -->
    <div class="form-card filter-card" style="margin-top: 24px;">
      <div class="filter-card-header">
        <h3 class="sub-title">🔍 Lọc Sổ Nợ</h3>
      </div>
      <div class="form-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
        <div class="input-group-xianxia">
          <label>Loại Khoản Nợ</label>
          <select v-model="debtFilter.type" @change="loadDebts">
            <option value="">Tất Cả Loại Nợ</option>
            <option value="BORROW">🔴 Tôi Vay Nợ (Cần Trả)</option>
            <option value="LEND">🟢 Tôi Cho Vay (Cần Thu)</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Trạng Thái Tất Toán</label>
          <select v-model="debtFilter.is_settled" @change="loadDebts">
            <option value="">Tất Cả Trạng Thái</option>
            <option :value="0">⏳ Chưa Tất Toán</option>
            <option :value="1">✅ Đã Tất Toán</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Debts Table -->
    <div class="table-header-flex" style="margin-top: 24px;">
      <h3 class="sub-title">📜 Danh Sách Khoản Nợ ({{ debts.length }})</h3>
    </div>

    <div class="table-scroll">
      <table class="xianxia-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Phân Loại</th>
            <th>Đối Tác</th>
            <th>Số Tiền</th>
            <th>Hạn Trả</th>
            <th>Ví Liên Kết</th>
            <th>Ghi Chú</th>
            <th>Trạng Thái</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(debt, idx) in debts" :key="debt.id" :class="{ 'row-settled': debt.is_settled }">
            <td>{{ idx + 1 }}</td>
            <td>
              <span :class="['badge-debt-type', debt.debt_type === 'BORROW' ? 'borrow' : 'lend']">
                {{ debt.debt_type === 'BORROW' ? '🔴 Vay Nợ' : '🟢 Cho Vay' }}
              </span>
            </td>
            <td class="person-cell"><strong>{{ debt.person_name }}</strong></td>
            <td :class="debt.debt_type === 'BORROW' ? 'amt-expense' : 'amt-income'">
              {{ formatVND(debt.amount) }}
            </td>
            <td>
              <span v-if="debt.due_date">{{ debt.due_date }}</span>
              <span v-else class="text-dim">—</span>
            </td>
            <td>{{ debt.wallet_name || '—' }}</td>
            <td>{{ debt.note || '—' }}</td>
            <td>
              <span :class="['debt-status-tag', getDebtStatus(debt).class]">
                {{ getDebtStatus(debt).icon }} {{ getDebtStatus(debt).label }}
              </span>
            </td>
            <td>
              <div class="row-actions">
                <button class="btn-sm-settle" @click="toggleSettleDebt(debt)" :title="debt.is_settled ? 'Hoàn tác chưa trả' : 'Tất toán'">
                  {{ debt.is_settled ? '↩️' : '✅' }}
                </button>
                <button class="btn-sm-edit" @click="openEditDebt(debt)" title="Sửa">✏️</button>
                <button class="btn-sm-danger" @click="deleteDebt(debt.id)" title="Xóa">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="!debts.length">
            <td colspan="9" class="empty-row">Sổ Nợ đang trống hoặc không có khoản nợ phù hợp bộ lọc...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <Teleport to="#modal-root" defer>
    <!-- EDIT DEBT MODAL -->
    <div v-if="showEditDebtModal" class="modal-backdrop" @click.self="showEditDebtModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Khoản Nợ</h3>
          <button class="modal-close" @click="showEditDebtModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Loại Khoản Nợ</label>
              <select v-model="editDebtForm.debt_type">
                <option value="BORROW">🔴 Tôi Vay Nợ (Cần trả)</option>
                <option value="LEND">🟢 Tôi Cho Vay (Cần thu)</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Đối Tác</label>
              <input v-model="editDebtForm.person_name" type="text" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền (VNĐ)</label>
              <input v-model.number="editDebtForm.amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Ngày Đến Hạn</label>
              <input v-model="editDebtForm.due_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>Ví Liên Kết</label>
              <select v-model="editDebtForm.wallet_id">
                <option value="">— Không liên kết —</option>
                <option v-for="w in wallets" :key="'ed-debt-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Trạng Thái</label>
              <select v-model.number="editDebtForm.is_settled">
                <option :value="0">⏳ Chưa Tất Toán</option>
                <option :value="1">✅ Đã Tất Toán</option>
              </select>
            </div>
            <div class="input-group-xianxia" style="grid-column: 1 / -1;">
              <label>Ghi Chú</label>
              <input v-model="editDebtForm.note" type="text" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditDebtModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateDebt" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Lưu Thay Đổi' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'DebtsView',
  setup() {
    return useAppBindings()
  },
}
</script>
