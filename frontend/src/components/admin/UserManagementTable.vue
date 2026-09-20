<template>
  <section class="table-workspace-section">
    <!-- Filter and Query Ribbon -->
    <div class="filter-ribbon-card">
      <!-- Search Input -->
      <div class="search-input-wrap">
        <span class="material-symbols-outlined search-icon" aria-hidden="true">search</span>
        <input
          v-model="searchQuery"
          type="text"
          class="stitch-search-input"
          placeholder="Tìm kiếm theo tên đạo hiệu, thư điện tử..."
        />
        <button
          v-if="searchQuery"
          type="button"
          class="clear-search-btn"
          aria-label="Xóa tìm kiếm"
          @click="searchQuery = ''"
        >
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>

      <!-- Filter Controls Group -->
      <div class="filter-controls-group">
        <!-- Role Filter -->
        <div class="custom-select-wrap">
          <select v-model="roleFilter" class="stitch-select" aria-label="Lọc theo vai trò">
            <option value="all">Tất cả vai trò</option>
            <option value="admin">Quản Trị Viên (Admin)</option>
            <option value="user">Đạo Hữu (User)</option>
          </select>
          <span class="material-symbols-outlined select-arrow" aria-hidden="true">expand_more</span>
        </div>

        <!-- Status Filter -->
        <div class="custom-select-wrap">
          <select v-model="statusFilter" class="stitch-select" aria-label="Lọc theo trạng thái">
            <option value="all">Tất cả trạng thái</option>
            <option value="active">Đang Hoạt Động</option>
            <option value="locked">Bị Phong Ấn</option>
          </select>
          <span class="material-symbols-outlined select-arrow" aria-hidden="true">expand_more</span>
        </div>

        <!-- Reset Button -->
        <button
          type="button"
          class="btn-filter-action"
          title="Đặt lại bộ lọc"
          @click="resetFilters"
        >
          <span class="material-symbols-outlined text-[16px]" aria-hidden="true">restart_alt</span>
          <span>Đặt Lại</span>
        </button>

        <!-- Refresh Button -->
        <button
          type="button"
          class="btn-filter-action primary"
          :disabled="loading"
          title="Làm mới danh sách tu sĩ"
          @click="$emit('refresh')"
        >
          <span class="material-symbols-outlined text-[16px]" :class="{ 'spin-icon': loading }" aria-hidden="true">
            refresh
          </span>
          <span>Làm Mới</span>
        </button>
      </div>
    </div>

    <!-- Data Table Container -->
    <div class="table-card-container">
      <div class="table-scroll-wrapper">
        <table class="stitch-admin-table" role="table">
          <thead>
            <tr class="table-head-row">
              <th scope="col" class="th-user">Tu Sĩ / Đạo Hữu</th>
              <th scope="col" class="th-email">Thư Điện Tử</th>
              <th scope="col" class="th-role">Vai Trò Hệ Thống</th>
              <th scope="col" class="th-status">Trạng Thái</th>
              <th scope="col" class="th-id">Mã / Ngày Tạo</th>
              <th scope="col" class="th-actions text-right">Thao Tác Bảo Mật</th>
            </tr>
          </thead>
          <tbody class="table-body">
            <tr
              v-for="u in paginatedUsers"
              :key="u.id"
              class="table-data-row"
              :class="{ 'row-locked': u.is_active === 0, 'row-current': u.id === currentUserId }"
            >
              <!-- Column 1: User & Avatar -->
              <td class="td-user">
                <div class="user-meta-cell">
                  <div class="avatar-circle" :class="u.role === 'admin' ? 'admin' : 'user'">
                    {{ getUserInitials(u) }}
                  </div>
                  <div class="name-sub-col">
                    <span class="cell-user-name">
                      {{ u.full_name || 'Đạo Hữu' }}
                      <span v-if="u.id === currentUserId" class="self-tag">Hiện Tại</span>
                    </span>
                    <span class="cell-sub-date font-mono">
                      Khởi tạo: {{ formatDate(u.created_at) }}
                    </span>
                  </div>
                </div>
              </td>

              <!-- Column 2: Email -->
              <td class="td-email font-mono">
                <span class="email-text" :title="u.email">{{ u.email }}</span>
              </td>

              <!-- Column 3: Role -->
              <td class="td-role">
                <span v-if="u.role === 'admin'" class="role-pill admin">
                  <span class="material-symbols-outlined text-[13px]" aria-hidden="true">shield_person</span>
                  <span>Admin</span>
                </span>
                <span v-else class="role-pill user">
                  <span class="material-symbols-outlined text-[13px]" aria-hidden="true">person</span>
                  <span>User</span>
                </span>
              </td>

              <!-- Column 4: Status -->
              <td class="td-status">
                <span v-if="u.is_active === 1" class="status-pill active">
                  <span class="status-dot green animate-pulse" aria-hidden="true"></span>
                  <span>Đang Hoạt Động</span>
                </span>
                <span v-else class="status-pill locked">
                  <span class="status-dot red" aria-hidden="true"></span>
                  <span>Bị Phong Ấn</span>
                </span>
              </td>

              <!-- Column 5: ID -->
              <td class="td-id font-mono">
                <span class="id-badge">#{{ u.id }}</span>
              </td>

              <!-- Column 6: Actions -->
              <td class="td-actions text-right">
                <!-- If current logged-in user: self-protection note -->
                <span v-if="u.id === currentUserId" class="self-protect-note">
                  Tự bảo vệ: Không thể tự phong ấn / hạ quyền
                </span>

                <!-- Action buttons for other users -->
                <div v-else class="actions-group">
                  <!-- Toggle Lock Button -->
                  <button
                    type="button"
                    class="btn-action-lock"
                    :class="u.is_active === 1 ? 'danger' : 'unlock'"
                    :title="u.is_active === 1 ? 'Phong ấn tài khoản' : 'Mở phong ấn tài khoản'"
                    @click="$emit('toggle-active', u)"
                  >
                    {{ u.is_active === 1 ? 'Khóa Tài Khoản' : 'Mở Khóa' }}
                  </button>

                  <!-- Change Role Button -->
                  <button
                    v-if="u.role === 'user'"
                    type="button"
                    class="btn-action-role promote"
                    title="Thăng cấp Quản Trị Viên"
                    @click="$emit('open-role-modal', { user: u, targetRole: 'admin' })"
                  >
                    Nâng Lên Admin
                  </button>
                  <button
                    v-else
                    type="button"
                    class="btn-action-role demote"
                    title="Hạ xuống Đạo Hữu"
                    @click="$emit('open-role-modal', { user: u, targetRole: 'user' })"
                  >
                    Hạ Xuống User
                  </button>
                </div>
              </td>
            </tr>

            <!-- Empty Row -->
            <tr v-if="!filteredUsers.length" class="empty-data-row">
              <td colspan="6" class="empty-cell">
                <div class="empty-state-box">
                  <span class="material-symbols-outlined empty-icon" aria-hidden="true">group_off</span>
                  <span class="empty-text">Không tìm thấy tu sĩ nào phù hợp với bộ lọc...</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Pagination Footer -->
      <div class="table-pagination-footer">
        <span class="pagination-info">
          Hiển thị {{ paginatedUsers.length }} trên tổng số {{ filteredUsers.length }} tu sĩ môn quy
        </span>

        <div v-if="totalPages > 1" class="pagination-controls">
          <button
            type="button"
            class="btn-page-nav"
            :disabled="currentPage <= 1"
            aria-label="Trang trước"
            @click="currentPage--"
          >
            <span class="material-symbols-outlined text-[16px]">chevron_left</span>
          </button>
          <span class="page-current-indicator">
            Trang {{ currentPage }} / {{ totalPages }}
          </span>
          <button
            type="button"
            class="btn-page-nav"
            :disabled="currentPage >= totalPages"
            aria-label="Trang kế tiếp"
            @click="currentPage++"
          >
            <span class="material-symbols-outlined text-[16px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'UserManagementTable',
  props: {
    users: {
      type: Array,
      default: () => []
    },
    currentUserId: {
      type: Number,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-active', 'open-role-modal', 'refresh'],
  setup(props) {
    const searchQuery = ref('')
    const roleFilter = ref('all')
    const statusFilter = ref('all')
    const currentPage = ref(1)
    const pageSize = ref(10)

    const filteredUsers = computed(() => {
      const list = props.users || []
      const query = searchQuery.value.trim().toLowerCase()
      const role = roleFilter.value
      const status = statusFilter.value

      return list.filter(u => {
        if (query) {
          const name = (u.full_name || '').toLowerCase()
          const email = (u.email || '').toLowerCase()
          if (!name.includes(query) && !email.includes(query)) {
            return false
          }
        }
        if (role !== 'all' && u.role !== role) {
          return false
        }
        if (status === 'active' && u.is_active !== 1) {
          return false
        }
        if (status === 'locked' && u.is_active !== 0) {
          return false
        }
        return true
      })
    })

    const totalPages = computed(() => {
      const len = filteredUsers.value.length
      return Math.max(1, Math.ceil(len / pageSize.value))
    })

    const paginatedUsers = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return filteredUsers.value.slice(start, start + pageSize.value)
    })

    // Reset page on filter changes
    watch([searchQuery, roleFilter, statusFilter], () => {
      currentPage.value = 1
    })

    function resetFilters() {
      searchQuery.value = ''
      roleFilter.value = 'all'
      statusFilter.value = 'all'
      currentPage.value = 1
    }

    function getUserInitials(u) {
      const name = (u.full_name || u.email || 'ĐH').trim()
      const words = name.split(/\s+/)
      if (words.length >= 2) {
        return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase()
      }
      return name.slice(0, 2).toUpperCase()
    }

    function formatDate(dateStr) {
      if (!dateStr) return '01/01/2024'
      return dateStr.slice(0, 10)
    }

    return {
      searchQuery,
      roleFilter,
      statusFilter,
      currentPage,
      pageSize,
      filteredUsers,
      totalPages,
      paginatedUsers,
      resetFilters,
      getUserInitials,
      formatDate
    }
  }
}
</script>

<style scoped>
.table-workspace-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
}

/* ─── FILTER RIBBON CARD ─── */
.filter-ribbon-card {
  padding: var(--space-md, 1rem);
  background: rgba(19, 27, 46, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 1rem);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
}

@media (min-width: 768px) {
  .filter-ribbon-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.search-input-wrap {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 18px;
  pointer-events: none;
}

.stitch-search-input {
  width: 100%;
  height: 40px;
  padding: 0 36px 0 38px;
  background: #222a3d;
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md, 0.75rem);
  font-size: 14px;
  transition: all 0.2s ease;
}

.stitch-search-input:focus {
  outline: none;
  background: #31394d;
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 0 2px rgba(125, 214, 204, 0.2);
}

.clear-search-btn {
  position: absolute;
  right: 8px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  border-radius: 4px;
}

.clear-search-btn:hover {
  color: #ffb4ab;
}

.filter-controls-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
}

.custom-select-wrap {
  position: relative;
  min-width: 160px;
  flex: 1;
}

@media (min-width: 768px) {
  .custom-select-wrap {
    flex: none;
  }
}

.stitch-select {
  width: 100%;
  height: 40px;
  padding: 0 32px 0 12px;
  background: #222a3d;
  color: var(--color-on-surface, #dae2fd);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md, 0.75rem);
  font-size: 13px;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stitch-select:focus {
  outline: none;
  background: #31394d;
  border-color: var(--color-primary, #7dd6cc);
}

.select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 18px;
  pointer-events: none;
}

.btn-filter-action {
  height: 40px;
  padding: 0 var(--space-md, 1rem);
  border-radius: var(--radius-md, 0.75rem);
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.btn-filter-action:hover:not(:disabled) {
  background: #31394d;
  color: var(--color-on-surface, #dae2fd);
}

.btn-filter-action.primary {
  color: var(--color-primary, #7dd6cc);
  border-color: rgba(125, 214, 204, 0.25);
}

.btn-filter-action.primary:hover:not(:disabled) {
  background: rgba(125, 214, 204, 0.15);
  color: #9af2e8;
}

.btn-filter-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── DATA TABLE CARD ─── */
.table-card-container {
  background: rgba(19, 27, 46, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 1rem);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

.table-scroll-wrapper {
  overflow-x: auto;
  width: 100%;
}

.stitch-admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.table-head-row {
  background: rgba(34, 42, 61, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.table-head-row th {
  padding: 0.85rem 1.25rem;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-on-surface-variant, #bdc9c6);
  white-space: nowrap;
}

.table-data-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s ease;
}

.table-data-row:hover {
  background: rgba(23, 31, 51, 0.6);
}

.table-data-row.row-locked {
  background: rgba(147, 0, 10, 0.06);
}

.table-data-row.row-current {
  background: rgba(125, 214, 204, 0.04);
}

.table-data-row td {
  padding: 0.85rem 1.25rem;
  font-size: 13px;
  color: var(--color-on-surface, #dae2fd);
  vertical-align: middle;
}

/* User & Avatar Cell */
.user-meta-cell {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.avatar-circle.admin {
  background: var(--color-primary, #7dd6cc);
  color: #003733;
}

.avatar-circle.user {
  background: #222a3d;
  color: var(--color-primary, #7dd6cc);
}

.name-sub-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.cell-user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.self-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(125, 214, 204, 0.2);
  color: var(--color-primary, #7dd6cc);
  font-weight: 600;
}

.cell-sub-date {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  white-space: nowrap;
}

/* Email Cell */
.email-text {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

/* Role Pill */
.role-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.role-pill.admin {
  background: rgba(68, 65, 115, 0.6);
  color: var(--color-secondary, #c4c1fb);
  border: 1px solid rgba(196, 193, 251, 0.25);
}

.role-pill.user {
  background: rgba(34, 42, 61, 0.8);
  color: var(--color-primary, #7dd6cc);
  border: 1px solid rgba(125, 214, 204, 0.15);
}

/* Status Pill */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.status-pill.active {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.status-pill.locked {
  background: rgba(239, 68, 68, 0.12);
  color: var(--color-error, #ffb4ab);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
}

.status-dot.green {
  background-color: #10b981;
}

.status-dot.red {
  background-color: var(--color-error, #ffb4ab);
}

/* ID Badge */
.id-badge {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

/* Actions Group */
.text-right {
  text-align: right;
}

.self-protect-note {
  font-size: 11px;
  color: rgba(189, 201, 198, 0.6);
  font-style: italic;
  white-space: nowrap;
}

.actions-group {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-xs, 0.25rem);
  white-space: nowrap;
}

.btn-action-lock {
  padding: 4px 10px;
  border-radius: var(--radius-sm, 0.25rem);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-action-lock.danger {
  background: rgba(239, 68, 68, 0.12);
  color: var(--color-error, #ffb4ab);
  border-color: rgba(239, 68, 68, 0.25);
}

.btn-action-lock.danger:hover {
  background: rgba(239, 68, 68, 0.25);
  color: #ffdad6;
}

.btn-action-lock.unlock {
  background: rgba(34, 42, 61, 0.8);
  color: var(--color-on-surface, #dae2fd);
  border-color: rgba(255, 255, 255, 0.1);
}

.btn-action-lock.unlock:hover {
  background: #31394d;
  color: #fff;
}

.btn-action-role {
  padding: 4px 10px;
  border-radius: var(--radius-sm, 0.25rem);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-action-role.promote {
  background: rgba(68, 65, 115, 0.5);
  color: var(--color-secondary, #c4c1fb);
  border-color: rgba(196, 193, 251, 0.2);
}

.btn-action-role.promote:hover {
  background: rgba(68, 65, 115, 0.8);
  color: #fff;
}

.btn-action-role.demote {
  background: rgba(34, 42, 61, 0.8);
  color: var(--color-on-surface-variant, #bdc9c6);
  border-color: rgba(255, 255, 255, 0.1);
}

.btn-action-role.demote:hover {
  background: #31394d;
  color: var(--color-on-surface, #dae2fd);
}

/* Empty State */
.empty-data-row td {
  padding: 3rem 1.5rem;
}

.empty-state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 0.25rem);
  color: var(--color-on-surface-variant, #bdc9c6);
}

.empty-icon {
  font-size: 36px;
  opacity: 0.5;
}

.empty-text {
  font-size: 13px;
}

/* Pagination Footer */
.table-pagination-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm, 0.5rem);
  padding: var(--space-sm, 0.5rem) var(--space-lg, 1.5rem);
  background: rgba(23, 31, 51, 0.9);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

@media (min-width: 640px) {
  .table-pagination-footer {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.pagination-info {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 0.25rem);
}

.btn-page-nav {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm, 0.25rem);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #222a3d;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-page-nav:hover:not(:disabled) {
  background: #31394d;
  color: var(--color-on-surface, #dae2fd);
}

.btn-page-nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-current-indicator {
  padding: 4px 10px;
  border-radius: var(--radius-sm, 0.25rem);
  background: #222a3d;
  color: var(--color-primary, #7dd6cc);
  font-size: 12px;
  font-weight: 600;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
