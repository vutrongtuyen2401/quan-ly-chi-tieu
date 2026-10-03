<template>
  <!-- ═══════ TAB 2: TRANSACTIONS ═══════ -->
  <section class="tab-panel">
    <div class="section-header-flex">
      <h2 class="section-title">💸 Tàng Kinh Giao Dịch</h2>
      <div class="action-btn-group">
        <button class="btn-action-gold" @click="showRecurringSection = !showRecurringSection">
          🔄 {{ showRecurringSection ? 'Ẩn Định Kỳ' : 'Linh Trận Định Kỳ' }} ({{ recurringList.length }})
        </button>
        <button class="btn-action-jade" @click="doExportReports('excel')">
          📥 Xuất Excel
        </button>
        <button class="btn-action-secondary" @click="doExportReports('csv')">
          📄 Xuất CSV
        </button>
      </div>
    </div>

    <!-- RECURRING TRANSACTIONS SECTION -->
    <div v-if="showRecurringSection" class="recurring-box">
      <div class="recurring-header">
        <h3 class="sub-title">🔄 Linh Trận Định Kỳ (Tự Động Sinh Giao Dịch)</h3>
        <p class="hint-text">Thiết lập chi tiêu / thu nhập tự động định kỳ (hàng tuần hoặc hàng tháng)</p>
      </div>

      <!-- Add Recurring Form -->
      <div class="form-grid recurring-form-grid">
        <div class="input-group-xianxia">
          <label>Loại</label>
          <select v-model="recurringForm.transaction_type">
            <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
            <option value="INCOME">💎 Thu Hoạch (Thu)</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Số Tiền (VNĐ)</label>
          <input v-model.number="recurringForm.amount" type="number" placeholder="0" min="0" />
        </div>
        <div class="input-group-xianxia">
          <label>Túi Càn Khôn</label>
          <select v-model="recurringForm.wallet_id">
            <option v-for="w in wallets" :key="'rec-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Danh Mục</label>
          <select v-model="recurringForm.category_id">
            <option v-for="c in categories.filter(cat => cat.category_type === recurringForm.transaction_type)" :key="'rec-c-'+c.id" :value="c.id">
              {{ c.icon }} {{ c.category_name }}
            </option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Tần Suất</label>
          <select v-model="recurringForm.frequency">
            <option value="monthly">📅 Hàng Tháng</option>
            <option value="weekly">📆 Hàng Tuần</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Ngày Chạy Kế Tiếp</label>
          <input v-model="recurringForm.next_run_date" type="date" />
        </div>
        <div class="input-group-xianxia" style="grid-column: 1 / -1;">
          <label>Ghi Chú</label>
          <input v-model="recurringForm.note" type="text" placeholder="VD: Tiền trọ hàng tháng, Lương định kỳ..." />
        </div>
      </div>
      <button class="btn-jade" @click="createRecurring" :disabled="loading" style="margin-top: 14px;">
        {{ loading ? '⏳...' : '✨ Khởi Tạo Linh Trận Định Kỳ' }}
      </button>

      <!-- Recurring List Table -->
      <div class="table-scroll" style="margin-top: 20px;">
        <table class="xianxia-table">
          <thead>
            <tr>
              <th>Loại</th>
              <th>Danh Mục</th>
              <th>Số Tiền</th>
              <th>Ví</th>
              <th>Tần Suất</th>
              <th>Kỳ Kế Tiếp</th>
              <th>Trạng Thái</th>
              <th>Thao Tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rec in recurringList" :key="rec.id">
              <td>
                <span :class="rec.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                  {{ rec.transaction_type === 'INCOME' ? '💎 Thu' : '🔥 Chi' }}
                </span>
              </td>
              <td><span class="cat-badge">{{ rec.category_icon }} {{ rec.category_name }}</span></td>
              <td :class="rec.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                {{ formatVND(rec.amount) }}
              </td>
              <td>{{ rec.wallet_name }}</td>
              <td>{{ rec.frequency === 'weekly' ? 'Hàng Tuần' : 'Hàng Tháng' }}</td>
              <td><strong>{{ rec.next_run_date }}</strong></td>
              <td>
                <button :class="rec.is_active ? 'btn-status-active' : 'btn-status-inactive'" @click="toggleRecurring(rec)">
                  {{ rec.is_active ? '✅ Đang chạy' : '⏸️ Tạm dừng' }}
                </button>
              </td>
              <td>
                <div class="action-cell">
                  <button class="btn-sm-edit" @click="openEditRecurring(rec)" title="Sửa">✏️</button>
                  <button class="btn-sm-danger" @click="deleteRecurring(rec.id)" title="Xóa">🗑️</button>
                </div>
              </td>
            </tr>
            <tr v-if="!recurringList.length">
              <td colspan="8" class="empty-row">Chưa có giao dịch định kỳ nào...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Transaction Form -->
    <div class="form-card">
      <h3 class="sub-title">✍️ Ghi Nhận Giao Dịch Linh Thạch</h3>
      <div class="form-grid">
        <div class="input-group-xianxia">
          <label>Loại Giao Dịch</label>
          <select v-model="txnForm.transaction_type">
            <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
            <option value="INCOME">💎 Thu Hoạch (Thu)</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Số Linh Thạch (VNĐ)</label>
          <input v-model.number="txnForm.amount" type="number" placeholder="0" min="0" />
        </div>
        <div class="input-group-xianxia">
          <label>Túi Càn Khôn (Ví)</label>
          <select v-model="txnForm.wallet_id">
            <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Danh Mục</label>
          <select v-model="txnForm.category_id">
            <option v-for="c in filteredCategories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Ngày Giao Dịch</label>
          <input v-model="txnForm.transaction_date" type="date" />
        </div>
        <div class="input-group-xianxia">
          <label>Ghi Chú</label>
          <input v-model="txnForm.note" type="text" placeholder="Mô tả giao dịch..." />
        </div>
      </div>
      <button class="btn-jade" @click="createTransaction" :disabled="loading" style="margin-top: 16px;">
        {{ loading ? '⏳...' : '⚡ Ghi Nhận Giao Dịch' }}
      </button>
    </div>

    <!-- FILTER & SEARCH BAR -->
    <div class="filter-card">
      <div class="filter-header">
        <h3 class="filter-title">🔍 Bộ Lọc & Tìm Kiếm Giao Dịch</h3>
        <button class="btn-link" @click="resetTxnFilter">🔄 Đặt lại bộ lọc</button>
      </div>
      <div class="filter-grid">
        <div class="input-group-xianxia">
          <label>Từ Ngày</label>
          <input v-model="txnFilter.start_date" type="date" @change="loadTransactions(true)" />
        </div>
        <div class="input-group-xianxia">
          <label>Đến Ngày</label>
          <input v-model="txnFilter.end_date" type="date" @change="loadTransactions(true)" />
        </div>
        <div class="input-group-xianxia">
          <label>Danh Mục</label>
          <select v-model="txnFilter.category_id" @change="loadTransactions(true)">
            <option value="">— Tất cả danh mục —</option>
            <option v-for="c in categories" :key="'flt-c-'+c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Túi Càn Khôn</label>
          <select v-model="txnFilter.wallet_id" @change="loadTransactions(true)">
            <option value="">— Tất cả ví —</option>
            <option v-for="w in wallets" :key="'flt-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Loại</label>
          <select v-model="txnFilter.transaction_type" @change="loadTransactions(true)">
            <option value="">— Tất cả loại —</option>
            <option value="EXPENSE">🔥 Tiêu Hao</option>
            <option value="INCOME">💎 Thu Hoạch</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Từ Khóa Ghi Chú</label>
          <input v-model="txnFilter.keyword" type="text" placeholder="Tìm theo ghi chú..." @input="loadTransactions(true)" />
        </div>
      </div>
    </div>

    <!-- Transactions Table -->
    <div class="table-header-flex" style="margin-top: 24px;">
      <h3 class="sub-title">📜 Lịch Sử Giao Dịch ({{ txnPagination.totalCount }})</h3>
      <div class="pagination-controls" v-if="totalPages > 1">
        <button class="btn-page" :disabled="txnPagination.page <= 1" @click="changeTxnPage(txnPagination.page - 1)">« Trước</button>
        <span class="page-info">Trang {{ txnPagination.page }} / {{ totalPages }}</span>
        <button class="btn-page" :disabled="txnPagination.page >= totalPages" @click="changeTxnPage(txnPagination.page + 1)">Sau »</button>
      </div>
    </div>

    <div class="table-scroll">
      <table class="xianxia-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Ngày</th>
            <th>Danh Mục</th>
            <th>Ghi Chú</th>
            <th>Ví</th>
            <th>Số Tiền</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(txn, idx) in transactions" :key="txn.id">
            <td>{{ (txnPagination.page - 1) * txnPagination.limit + idx + 1 }}</td>
            <td>{{ txn.transaction_date }}</td>
            <td><span class="cat-badge">{{ txn.category_icon }} {{ txn.category_name }}</span></td>
            <td>{{ txn.note || '—' }}</td>
            <td>{{ txn.wallet_name }}</td>
            <td :class="txn.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
              {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
            </td>
            <td>
              <div class="action-cell">
                <button class="btn-sm-edit" @click="openEditTxn(txn)" title="Sửa">✏️</button>
                <button class="btn-sm-danger" @click="deleteTransaction(txn.id)" title="Xóa">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="!transactions.length">
            <td colspan="7" class="empty-row">Không tìm thấy giao dịch nào phù hợp...</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bottom Pagination -->
    <div class="pagination-footer" v-if="totalPages > 1">
      <button class="btn-page" :disabled="txnPagination.page <= 1" @click="changeTxnPage(txnPagination.page - 1)">« Trang Trước</button>
      <span class="page-info">Trang {{ txnPagination.page }} / {{ totalPages }} (Tổng {{ txnPagination.totalCount }} giao dịch)</span>
      <button class="btn-page" :disabled="txnPagination.page >= totalPages" @click="changeTxnPage(txnPagination.page + 1)">Trang Sau »</button>
    </div>
  </section>

  <Teleport to="#modal-root" defer>
    <!-- EDIT TRANSACTION MODAL -->
    <div v-if="showEditTxnModal" class="modal-backdrop" @click.self="showEditTxnModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Sửa Giao Dịch Linh Thạch</h3>
          <button class="modal-close" @click="showEditTxnModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Loại Giao Dịch</label>
              <select v-model="editTxnForm.transaction_type" @change="editTxnForm.category_id = null">
                <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
                <option value="INCOME">💎 Thu Hoạch (Thu)</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Số Linh Thạch (VNĐ)</label>
              <input v-model.number="editTxnForm.amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Túi Càn Khôn (Ví)</label>
              <select v-model="editTxnForm.wallet_id">
                <option v-for="w in wallets" :key="'ed-txn-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Danh Mục</label>
              <select v-model="editTxnForm.category_id">
                <option v-for="c in editTxnCategories" :key="'ed-txn-c-'+c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Ngày Giao Dịch</label>
              <input v-model="editTxnForm.transaction_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>Ghi Chú</label>
              <input v-model="editTxnForm.note" type="text" placeholder="Mô tả giao dịch..." />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditTxnModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateTransaction" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Cập Nhật Giao Dịch' }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT RECURRING MODAL -->
    <div v-if="showEditRecurringModal" class="modal-backdrop" @click.self="showEditRecurringModal = false">
      <div class="modal-card" style="max-width: 520px;">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Sửa Linh Trận Định Kỳ</h3>
          <button class="modal-close" @click="showEditRecurringModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Loại</label>
              <select v-model="editRecurringForm.transaction_type">
                <option value="EXPENSE">🔥 Tiêu Hao</option>
                <option value="INCOME">💎 Thu Hoạch</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền (VNĐ)</label>
              <input v-model.number="editRecurringForm.amount" type="number" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Túi Càn Khôn</label>
              <select v-model="editRecurringForm.wallet_id">
                <option v-for="w in wallets" :key="'ed-rec-w-'+w.id" :value="w.id">{{ w.wallet_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Danh Mục</label>
              <select v-model="editRecurringForm.category_id">
                <option v-for="c in categories.filter(cat => cat.category_type === editRecurringForm.transaction_type)" :key="'ed-rec-c-'+c.id" :value="c.id">
                  {{ c.icon }} {{ c.category_name }}
                </option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Tần Suất</label>
              <select v-model="editRecurringForm.frequency">
                <option value="monthly">📅 Hàng Tháng</option>
                <option value="weekly">📆 Hàng Tuần</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Ngày Chạy Kế Tiếp</label>
              <input v-model="editRecurringForm.next_run_date" type="date" />
            </div>
            <div class="input-group-xianxia" style="grid-column: 1 / -1;">
              <label>Ghi Chú</label>
              <input v-model="editRecurringForm.note" type="text" />
            </div>
            <div class="input-group-xianxia" style="grid-column: 1 / -1;">
              <label>Trạng Thái</label>
              <select v-model.number="editRecurringForm.is_active">
                <option :value="1">✅ Đang Kích Hoạt</option>
                <option :value="0">⏸️ Tạm Dừng</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditRecurringModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateRecurring" :disabled="loading">
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
  name: 'TransactionsView',
  setup() {
    return useAppBindings()
  },
}
</script>
