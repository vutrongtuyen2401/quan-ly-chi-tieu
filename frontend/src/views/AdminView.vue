<template>
  <!-- ═══════ TAB: ADMIN & ROLE MANAGEMENT (PHÂN QUYỀN & QUẢN TRỊ) ═══════ -->
  <section v-if="isUserAdmin" class="tab-panel">
    <h2 class="section-title">🛡️ Phân Quyền & Quản Trị Hệ Thống</h2>

    <!-- Admin System Metrics -->
    <div class="metrics-grid">
      <div class="metric-card jade">
        <div class="metric-icon">👥</div>
        <div class="metric-info">
          <span class="metric-label">Tổng Đạo Hữu</span>
          <span class="metric-value">{{ adminStats.total_users || 0 }}</span>
          <span class="metric-sub">🟢 {{ adminStats.active_users || 0 }} hoạt động | 🔴 {{ adminStats.locked_users || 0 }} khóa</span>
        </div>
      </div>
      <div class="metric-card gold">
        <div class="metric-icon">💳</div>
        <div class="metric-info">
          <span class="metric-label">Túi Càn Khôn</span>
          <span class="metric-value">{{ adminStats.total_wallets || 0 }}</span>
          <span class="metric-sub">Số dư: {{ formatVND(adminStats.total_balance || 0) }}</span>
        </div>
      </div>
      <div class="metric-card purple">
        <div class="metric-icon">💸</div>
        <div class="metric-info">
          <span class="metric-label">Tổng Giao Dịch</span>
          <span class="metric-value">{{ adminStats.total_transactions || 0 }}</span>
          <span class="metric-sub">Dòng tiền: {{ formatVND(adminStats.total_system_cashflow || 0) }}</span>
        </div>
      </div>
      <div class="metric-card crimson">
        <div class="metric-icon">📜</div>
        <div class="metric-info">
          <span class="metric-label">Sổ Nợ & Mục Tiêu</span>
          <span class="metric-value">{{ adminStats.total_debts || 0 }} / {{ adminStats.total_goals || 0 }}</span>
          <span class="metric-sub">Nợ / Mục tiêu</span>
        </div>
      </div>
    </div>

    <!-- User Management Table Filter & Search -->
    <div class="filter-card" style="margin-top: 24px;">
      <div class="filter-grid">
        <div class="input-group-xianxia">
          <label>🔍 Tìm Kiếm Đạo Hữu</label>
          <input v-model="adminFilter.search" type="text" placeholder="Tên hoặc Email..." />
        </div>
        <div class="input-group-xianxia">
          <label>Vai Trò</label>
          <select v-model="adminFilter.role">
            <option value="">— Tất Cả —</option>
            <option value="admin">🛡️ Chưởng Môn (Admin)</option>
            <option value="user">🧙 Đệ Tử (User)</option>
          </select>
        </div>
        <div class="input-group-xianxia">
          <label>Trạng Thái</label>
          <select v-model="adminFilter.status">
            <option value="">— Tất Cả —</option>
            <option value="active">🟢 Đang Hoạt Động</option>
            <option value="locked">🔴 Đã Bị Khóa</option>
          </select>
        </div>
        <div class="input-group-xianxia" style="display: flex; align-items: flex-end;">
          <button class="btn-secondary" @click="loadAdminUsers" :disabled="loading" style="width: 100%;">
            🔄 Làm Mới
          </button>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="table-header-flex" style="margin-top: 20px;">
      <h3 class="sub-title">👥 Danh Sách Đạo Hữu Trong Tông Môn ({{ filteredAdminUsers.length }})</h3>
    </div>

    <div class="table-scroll">
      <table class="xianxia-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Đạo Hiệu / Họ Tên</th>
            <th>Email</th>
            <th>Vai Trò</th>
            <th>Túi Càn Khôn</th>
            <th>Tổng Số Dư</th>
            <th>Số Giao Dịch</th>
            <th>Trạng Thái</th>
            <th>Ngày Gia Nhập</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filteredAdminUsers" :key="u.id" :class="{ 'row-locked': u.is_active === 0 }">
            <td>#{{ u.id }}</td>
            <td><strong>{{ u.full_name }}</strong></td>
            <td>{{ u.email }}</td>
            <td>
              <span :class="['role-badge', u.role === 'admin' ? 'admin' : 'user']">
                {{ u.role === 'admin' ? '🛡️ Chưởng Môn' : '🧙 Đệ Tử' }}
              </span>
            </td>
            <td>{{ u.wallet_count }} ví</td>
            <td>{{ formatVND(u.total_balance) }}</td>
            <td>{{ u.txn_count }} GD</td>
            <td>
              <span :class="['status-badge', u.is_active === 1 ? 'active' : 'locked']">
                {{ u.is_active === 1 ? '🟢 Bình Thường' : '🔴 Bị Phong Ấn' }}
              </span>
            </td>
            <td>{{ (u.created_at || '').slice(0, 10) }}</td>
            <td>
              <div class="actions-cell">
                <button v-if="u.id !== currentUserId"
                        :class="u.is_active === 1 ? 'btn-sm-danger' : 'btn-sm-edit'"
                        @click="toggleUserActive(u)"
                        :title="u.is_active === 1 ? 'Phong ấn tài khoản' : 'Mở phong ấn'">
                  {{ u.is_active === 1 ? '🔒 Khóa' : '🔓 Mở' }}
                </button>
                <button v-if="u.id !== currentUserId"
                        class="btn-sm-secondary"
                        @click="changeUserRole(u, u.role === 'admin' ? 'user' : 'admin')"
                        :title="u.role === 'admin' ? 'Giáng xuống Đệ Tử' : 'Thăng cấp Chưởng Môn'">
                  {{ u.role === 'admin' ? '⬇️ Giáng' : '⬆️ Thăng' }}
                </button>
                <span v-else class="text-dim">(Chính bạn)</span>
              </div>
            </td>
          </tr>
          <tr v-if="!filteredAdminUsers.length">
            <td colspan="10" class="empty-row">Không tìm thấy đệ tử nào...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'AdminView',
  setup() {
    return useAppBindings()
  },
}
</script>
