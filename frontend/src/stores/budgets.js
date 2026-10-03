/** Hạn mức chi tiêu theo tháng và cảnh báo vượt hạn mức. */
import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { toLocalMonthStr } from '../utils/format'
import { useSessionStore } from './session'

export const useBudgetStore = defineStore('budgets', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const session = useSessionStore()

  const showEditBudgetModal = ref(false)
  const editBudgetForm = ref({ id: null, limit_amount: 0 })
  const budgets = ref([])
  const budgetAlerts = ref([])

  const budgetMonth = ref(toLocalMonthStr(new Date()))

  watch(budgetMonth, async (newVal) => {
    if (newVal) {
      await loadBudgets()
    }
  })
  const budgetForm = ref({
    category_id: null, limit_amount: 0,
    month_year: toLocalMonthStr(new Date())
  })

  function openEditBudget(b) {
    editBudgetForm.value = { id: b.id, limit_amount: b.limit_amount }
    showEditBudgetModal.value = true
  }

  async function updateBudget() {
    if (!editBudgetForm.value.limit_amount) return session.showToast('Vui lòng nhập số tiền!', 'error')
    session.loading = true
    try {
      await api.put(`/api/budgets/${editBudgetForm.value.id}`, { limit_amount: editBudgetForm.value.limit_amount })
      session.showToast('Đã cập nhật hạn mức!')
      showEditBudgetModal.value = false
      await loadBudgets()
      await checkBudgetAlerts()
    } catch (err) {
      session.showToast('Lỗi cập nhật!', 'error')
    }
    session.loading = false
  }
  async function loadBudgets() {
    try { budgets.value = (await api.get(`/api/budgets?month_year=${budgetMonth.value}`)).data } catch {}
  }
  async function checkBudgetAlerts() {
    try { budgetAlerts.value = (await api.post('/api/ai/check-budget')).data.alerts } catch {}
  }

  async function createBudget() {
    if (!budgetForm.value.category_id || !budgetForm.value.limit_amount) {
      session.showToast('Vui lòng điền đầy đủ!', 'error')
      return
    }
    session.loading = true
    try {
      await api.post('/api/budgets', budgetForm.value)
      session.showToast('🎯 Hạn mức tu luyện đã thiết lập!')
      await loadBudgets()
      await checkBudgetAlerts()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi!', 'error')
    }
    session.loading = false
  }

  async function deleteBudget(id) {
    if (!confirm('Xóa hạn mức này?')) return
    try {
      await api.delete(`/api/budgets/${id}`)
      session.showToast('Hạn mức đã xóa!')
      await Promise.all([loadBudgets(), checkBudgetAlerts()])
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi xóa hạn mức!', 'error')
    }
  }

  return {
    showEditBudgetModal, editBudgetForm, budgets, budgetAlerts, budgetMonth, budgetForm, openEditBudget,
    updateBudget, loadBudgets, checkBudgetAlerts, createBudget, deleteBudget,
  }
})
