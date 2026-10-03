/** Mục tiêu tiết kiệm (nạp / rút, lịch sử). */
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { useReportStore } from './reports'
import { useSessionStore } from './session'
import { useWalletStore } from './wallets'

export const useGoalStore = defineStore('goals', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const reportStore = useReportStore()
  const session = useSessionStore()
  const walletStore = useWalletStore()

  // Saving Goals State
  const savingGoals = ref([])
  const goalsSummary = ref({
    total_target: 0,
    total_saved: 0,
    completed_count: 0,
    active_count: 0,
    overall_percent: 0
  })
  const goalForm = ref({
    target_name: '',
    target_amount: null,
    current_amount: 0,
    target_date: '',
    icon: '🎯'
  })
  const showEditGoalModal = ref(false)
  const editGoalForm = ref({
    id: null,
    target_name: '',
    target_amount: 0,
    current_amount: 0,
    target_date: '',
    icon: '🎯',
    is_completed: 0
  })
  const showDepositModal = ref(false)
  const depositForm = ref({
    goal_id: null,
    goal_name: '',
    amount: null,
    wallet_id: '',
    action: 'deposit'
  })
  const goalLogs = ref([])

  async function loadGoalLogs(goalId) {
    goalLogs.value = []
    try { goalLogs.value = (await api.get(`/api/saving-goals/${goalId}/logs`, { params: { limit: 5 } })).data || [] } catch {}
  }

  // ─── SAVING GOALS (MỤC TIÊU TIẾT KIỆM) ────
  async function loadSavingGoals() {
    try {
      const { data } = await api.get('/api/saving-goals')
      if (data) {
        savingGoals.value = data.goals || []
        goalsSummary.value = data.summary || {
          total_target: 0,
          total_saved: 0,
          completed_count: 0,
          active_count: 0,
          overall_percent: 0
        }
      }
    } catch (err) {
      console.error('Lỗi tải mục tiêu tiết kiệm:', err)
    }
  }

  async function createSavingGoal() {
    if (!goalForm.value.target_name.trim() || !goalForm.value.target_amount || goalForm.value.target_amount <= 0) {
      session.showToast('Vui lòng nhập tên mục tiêu và số tiền đích hợp lệ!', 'error')
      return
    }
    session.loading = true
    try {
      const payload = {
        target_name: goalForm.value.target_name.trim(),
        target_amount: Number(goalForm.value.target_amount),
        current_amount: Number(goalForm.value.current_amount || 0),
        target_date: goalForm.value.target_date || '',
        icon: goalForm.value.icon || '🎯'
      }
      await api.post('/api/saving-goals', payload)
      session.showToast('🎯 Khởi tạo mục tiêu tiết kiệm thành công!')
      goalForm.value = { target_name: '', target_amount: null, current_amount: 0, target_date: '', icon: '🎯' }
      await loadSavingGoals()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi tạo mục tiêu!', 'error')
    } finally {
      session.loading = false
    }
  }

  function openEditGoal(g) {
    editGoalForm.value = {
      id: g.id,
      target_name: g.target_name,
      target_amount: g.target_amount,
      current_amount: g.current_amount,
      target_date: g.target_date || '',
      icon: g.icon || '🎯',
      is_completed: g.is_completed
    }
    showEditGoalModal.value = true
  }

  async function updateSavingGoal() {
    if (!editGoalForm.value.target_name.trim() || !editGoalForm.value.target_amount || editGoalForm.value.target_amount <= 0) {
      session.showToast('Vui lòng nhập tên mục tiêu và số tiền đích hợp lệ!', 'error')
      return
    }
    session.loading = true
    try {
      const payload = {
        target_name: editGoalForm.value.target_name.trim(),
        target_amount: Number(editGoalForm.value.target_amount),
        current_amount: Number(editGoalForm.value.current_amount || 0),
        target_date: editGoalForm.value.target_date || '',
        icon: editGoalForm.value.icon || '🎯',
        is_completed: Number(editGoalForm.value.is_completed)
      }
      await api.put(`/api/saving-goals/${editGoalForm.value.id}`, payload)
      session.showToast('✨ Đã cập nhật mục tiêu tiết kiệm!')
      showEditGoalModal.value = false
      await loadSavingGoals()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật mục tiêu!', 'error')
    } finally {
      session.loading = false
    }
  }

  function openDepositGoal(g, action = 'deposit') {
    depositForm.value = {
      goal_id: g.id,
      goal_name: g.target_name,
      amount: null,
      wallet_id: walletStore.wallets.length ? walletStore.wallets[0].id : '',
      action: action
    }
    showDepositModal.value = true
    loadGoalLogs(g.id)
  }

  async function submitDepositWithdrawGoal() {
    if (!depositForm.value.amount || depositForm.value.amount <= 0) {
      session.showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
      return
    }
    session.loading = true
    try {
      const payload = {
        amount: Number(depositForm.value.amount),
        wallet_id: depositForm.value.wallet_id ? Number(depositForm.value.wallet_id) : null
      }
      const endpoint = depositForm.value.action === 'deposit' ? 'deposit' : 'withdraw'
      const { data } = await api.post(`/api/saving-goals/${depositForm.value.goal_id}/${endpoint}`, payload)
      session.showToast(data.message || 'Thao tác thành công!')
      showDepositModal.value = false
      await loadSavingGoals()
      await walletStore.loadWallets()
      await reportStore.loadSummary()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi nạp/rút linh thạch!', 'error')
    } finally {
      session.loading = false
    }
  }

  async function deleteSavingGoal(id) {
    if (!confirm('Đạo hữu có chắc chắn muốn xóa mục tiêu này?')) return
    try {
      await api.delete(`/api/saving-goals/${id}`)
      session.showToast('🗑️ Đã xóa mục tiêu tiết kiệm!')
      await loadSavingGoals()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi xóa mục tiêu!', 'error')
    }
  }

  return {
    savingGoals, goalsSummary, goalForm, showEditGoalModal, editGoalForm, showDepositModal, depositForm,
    goalLogs, loadGoalLogs, loadSavingGoals, createSavingGoal, openEditGoal, updateSavingGoal,
    openDepositGoal, submitDepositWithdrawGoal, deleteSavingGoal,
  }
})
