/** Quản trị: thống kê hệ thống, khóa tài khoản, phân quyền. */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { useSessionStore } from './session'

export const useAdminStore = defineStore('admin', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const session = useSessionStore()

  // Admin State
  const adminStats = ref({})
  const adminUsers = ref([])
  const adminFilter = ref({ search: '', role: '', status: '' })

  const filteredAdminUsers = computed(() => {
    return adminUsers.value.filter(u => {
      if (adminFilter.value.search) {
        const q = adminFilter.value.search.toLowerCase()
        const match = (u.full_name && u.full_name.toLowerCase().includes(q)) ||
                      (u.email && u.email.toLowerCase().includes(q))
        if (!match) return false
      }
      if (adminFilter.value.role && u.role !== adminFilter.value.role) return false
      if (adminFilter.value.status === 'active' && u.is_active !== 1) return false
      if (adminFilter.value.status === 'locked' && u.is_active !== 0) return false
      return true
    })
  })

  // ─── ADMIN MANAGEMENT (CHƯỞNG MÔN CÁC) ────
  async function loadAdminStats() {
    if (session.userRole !== 'admin') return
    try {
      const { data } = await api.get('/api/admin/stats')
      adminStats.value = data || {}
    } catch (err) {
      console.error('Lỗi tải thống kê admin:', err)
    }
  }

  async function loadAdminUsers() {
    if (session.userRole !== 'admin') return
    try {
      const { data } = await api.get('/api/admin/users')
      adminUsers.value = data || []
    } catch (err) {
      console.error('Lỗi tải danh sách người dùng:', err)
    }
  }

  async function toggleUserActive(u) {
    const action = u.is_active === 1 ? 'phong ấn (khóa)' : 'mở phong ấn cho'
    if (!confirm(`Đạo hữu có chắc chắn muốn ${action} tài khoản "${u.email}"?`)) return
    try {
      const { data } = await api.put(`/api/admin/users/${u.id}/toggle-active`)
      session.showToast(data.message || 'Thao tác thành công!')
      await loadAdminUsers()
      await loadAdminStats()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi cập nhật trạng thái người dùng!', 'error')
    }
  }

  async function changeUserRole(u, newRole) {
    const title = newRole === 'admin' ? 'thăng cấp Chưởng Môn' : 'giáng xuống Đệ Tử'
    if (!confirm(`Đạo hữu có chắc chắn muốn ${title} cho "${u.email}"?`)) return
    try {
      const { data } = await api.put(`/api/admin/users/${u.id}/role`, { role: newRole })
      session.showToast(data.message || 'Thao tác thành công!')
      await loadAdminUsers()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi thay đổi vai trò!', 'error')
    }
  }

  return {
    adminStats, adminUsers, adminFilter, filteredAdminUsers, loadAdminStats, loadAdminUsers, toggleUserActive,
    changeUserRole,
  }
})
