/** Sổ nợ / cho vay. */
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { todayStr } from '../utils/format'
import { useSessionStore } from './session'

export const useDebtStore = defineStore('debts', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const session = useSessionStore()

  // Debts State
  const debts = ref([])
  const debtsSummary = ref({
    total_borrow_unsettled: 0,
    total_lend_unsettled: 0,
    total_borrow_settled: 0,
    total_lend_settled: 0
  })
  const debtFilter = ref({ type: '', is_settled: '' })
  const debtForm = ref({
    debt_type: 'BORROW',
    person_name: '',
    amount: null,
    due_date: '',
    wallet_id: '',
    note: ''
  })
  const showEditDebtModal = ref(false)
  const editDebtForm = ref({
    id: null,
    debt_type: 'BORROW',
    person_name: '',
    amount: 0,
    due_date: '',
    wallet_id: '',
    note: '',
    is_settled: 0
  })

  // ─── DEBTS (SỔ NỢ / VAY MƯỢN) ────
  async function loadDebts() {
    try {
      const params = {}
      if (debtFilter.value.type) params.debt_type = debtFilter.value.type
      if (debtFilter.value.is_settled !== '') params.is_settled = debtFilter.value.is_settled
      const { data } = await api.get('/api/debts', { params })
      if (data) {
        debts.value = data.debts || []
        debtsSummary.value = data.summary || {
          total_borrow_unsettled: 0,
          total_lend_unsettled: 0,
          total_borrow_settled: 0,
          total_lend_settled: 0
        }
      }
    } catch (err) {
      console.error('Lỗi tải sổ nợ:', err)
    }
  }

  async function createDebt() {
    if (!debtForm.value.person_name || !debtForm.value.amount || debtForm.value.amount <= 0) {
      session.showToast('Vui lòng nhập đối tác và số tiền hợp lệ!', 'error')
      return
    }
    session.loading = true
    try {
      const payload = {
        debt_type: debtForm.value.debt_type,
        person_name: debtForm.value.person_name.trim(),
        amount: Number(debtForm.value.amount),
        due_date: debtForm.value.due_date || '',
        wallet_id: debtForm.value.wallet_id ? Number(debtForm.value.wallet_id) : null,
        note: debtForm.value.note || ''
      }
      await api.post('/api/debts', payload)
      session.showToast('📜 Đã ghi nhận khoản nợ thành công!')
      debtForm.value = { debt_type: 'BORROW', person_name: '', amount: null, due_date: '', wallet_id: '', note: '' }
      await loadDebts()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi ghi sổ nợ!', 'error')
    } finally {
      session.loading = false
    }
  }

  function openEditDebt(d) {
    editDebtForm.value = {
      id: d.id,
      debt_type: d.debt_type,
      person_name: d.person_name,
      amount: d.amount,
      due_date: d.due_date || '',
      wallet_id: d.wallet_id || '',
      note: d.note || '',
      is_settled: d.is_settled
    }
    showEditDebtModal.value = true
  }

  async function updateDebt() {
    if (!editDebtForm.value.person_name || !editDebtForm.value.amount || editDebtForm.value.amount <= 0) {
      session.showToast('Vui lòng nhập đối tác và số tiền hợp lệ!', 'error')
      return
    }
    session.loading = true
    try {
      const payload = {
        debt_type: editDebtForm.value.debt_type,
        person_name: editDebtForm.value.person_name.trim(),
        amount: Number(editDebtForm.value.amount),
        due_date: editDebtForm.value.due_date || '',
        wallet_id: editDebtForm.value.wallet_id ? Number(editDebtForm.value.wallet_id) : null,
        note: editDebtForm.value.note || '',
        is_settled: Number(editDebtForm.value.is_settled)
      }
      await api.put(`/api/debts/${editDebtForm.value.id}`, payload)
      session.showToast('✨ Đã cập nhật khoản nợ!')
      showEditDebtModal.value = false
      await loadDebts()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật khoản nợ!', 'error')
    } finally {
      session.loading = false
    }
  }

  async function toggleSettleDebt(d) {
    try {
      const { data } = await api.post(`/api/debts/${d.id}/settle`)
      session.showToast(data.message || 'Đã cập nhật trạng thái tất toán!')
      await loadDebts()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi tất toán khoản nợ!', 'error')
    }
  }

  async function deleteDebt(id) {
    if (!confirm('Đạo hữu có chắc chắn muốn xóa khoản nợ này khỏi sổ?')) return
    try {
      await api.delete(`/api/debts/${id}`)
      session.showToast('🗑️ Đã xóa khoản nợ khỏi sổ!')
      await loadDebts()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi xóa khoản nợ!', 'error')
    }
  }

  function getDebtStatus(debt) {
    if (debt.is_settled) return { label: 'Đã Tất Toán', class: 'badge-settled', icon: '✅' }
    if (!debt.due_date) return { label: 'Chưa Đặt Hạn', class: 'badge-no-due', icon: '⏳' }
    const today = todayStr()
    if (debt.due_date < today) {
      const diffTime = Math.abs(new Date(today) - new Date(debt.due_date))
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return { label: `Quá Hạn ${diffDays} Ngày`, class: 'badge-overdue', icon: '⚠️' }
    } else if (debt.due_date === today) {
      return { label: 'Hôm Nay Đến Hạn', class: 'badge-due-today', icon: '⚡' }
    } else {
      const diffTime = new Date(debt.due_date) - new Date(today)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return { label: `Còn ${diffDays} Ngày`, class: 'badge-pending', icon: '⏳' }
    }
  }

  return {
    debts, debtsSummary, debtFilter, debtForm, showEditDebtModal, editDebtForm, loadDebts, createDebt,
    openEditDebt, updateDebt, toggleSettleDebt, deleteDebt, getDebtStatus,
  }
})
