/** Giao dịch, bộ lọc / phân trang và giao dịch định kỳ. */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { todayStr } from '../utils/format'
import { useBudgetStore } from './budgets'
import { useCategoryStore } from './categories'
import { useReportStore } from './reports'
import { useSessionStore } from './session'
import { useWalletStore } from './wallets'

export const useTransactionStore = defineStore('transactions', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const budgetStore = useBudgetStore()
  const categoryStore = useCategoryStore()
  const reportStore = useReportStore()
  const session = useSessionStore()
  const walletStore = useWalletStore()

  const showEditTxnModal = ref(false)
  const editTxnForm = ref({
    id: null, transaction_type: 'EXPENSE', amount: 0, wallet_id: null,
    category_id: null, transaction_date: '', note: ''
  })

  const showEditRecurringModal = ref(false)
  const editRecurringForm = ref({
    id: null, wallet_id: null, category_id: null, amount: 0,
    transaction_type: 'EXPENSE', frequency: 'monthly', next_run_date: '', note: '', is_active: 1
  })
  const transactions = ref([])

  // Recurring Transactions Data
  const showRecurringSection = ref(false)
  const recurringList = ref([])
  const recurringForm = ref({
    wallet_id: null, category_id: null, amount: 0,
    transaction_type: 'EXPENSE', frequency: 'monthly',
    next_run_date: todayStr(), note: ''
  })

  // Transactions Filter & Pagination
  const txnFilter = ref({
    start_date: '', end_date: '', category_id: '',
    wallet_id: '', transaction_type: '', keyword: ''
  })
  const txnPagination = ref({
    page: 1,
    limit: 15,
    totalCount: 0
  })

  // Forms
  const txnForm = ref({
    transaction_type: 'EXPENSE', amount: 0, wallet_id: null,
    category_id: null, transaction_date: todayStr(), note: ''
  })
  const filteredCategories = computed(() =>
    categoryStore.categories.filter(c => c.category_type === txnForm.value.transaction_type)
  )
  const editTxnCategories = computed(() =>
    categoryStore.categories.filter(c => c.category_type === editTxnForm.value.transaction_type)
  )
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(txnPagination.value.totalCount / txnPagination.value.limit))
  )

  // Change 4: loadTransactions with filter and pagination
  async function loadTransactions(resetPage = false) {
    if (resetPage) txnPagination.value.page = 1
    const offset = (txnPagination.value.page - 1) * txnPagination.value.limit
    const params = {
      limit: txnPagination.value.limit,
      offset: offset,
    }
    if (txnFilter.value.start_date) params.start_date = txnFilter.value.start_date
    if (txnFilter.value.end_date) params.end_date = txnFilter.value.end_date
    if (txnFilter.value.category_id) params.category_id = txnFilter.value.category_id
    if (txnFilter.value.wallet_id) params.wallet_id = txnFilter.value.wallet_id
    if (txnFilter.value.transaction_type) params.transaction_type = txnFilter.value.transaction_type
    if (txnFilter.value.keyword) params.keyword = txnFilter.value.keyword

    try {
      const { data } = await api.get('/api/transactions', { params })
      if (data && data.data) {
        transactions.value = data.data
        txnPagination.value.totalCount = data.total_count || 0
      } else if (Array.isArray(data)) {
        transactions.value = data
        txnPagination.value.totalCount = data.length
      }
    } catch {}
  }

  function changeTxnPage(newPage) {
    if (newPage >= 1 && newPage <= totalPages.value) {
      txnPagination.value.page = newPage
      loadTransactions(false)
    }
  }

  function resetTxnFilter() {
    txnFilter.value = {
      start_date: '', end_date: '', category_id: '',
      wallet_id: '', transaction_type: '', keyword: ''
    }
    loadTransactions(true)
  }

  // Change 8: Recurring transactions
  async function loadRecurring() {
    try {
      recurringList.value = (await api.get('/api/recurring-transactions')).data
    } catch {}
  }

  async function createRecurring() {
    if (!recurringForm.value.amount || !recurringForm.value.wallet_id || !recurringForm.value.category_id) {
      session.showToast('Vui lòng chọn đầy đủ ví, danh mục và số tiền!', 'error')
      return
    }
    session.loading = true
    try {
      await api.post('/api/recurring-transactions', recurringForm.value)
      session.showToast('✨ Linh trận định kỳ đã được thiết lập!')
      recurringForm.value = {
        wallet_id: walletStore.wallets.length ? walletStore.wallets[0].id : null,
        category_id: null,
        amount: 0,
        transaction_type: 'EXPENSE',
        frequency: 'monthly',
        next_run_date: todayStr(),
        note: ''
      }
      await loadRecurring()
      await refreshAfterTxnChange()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch định kỳ!', 'error')
    }
    session.loading = false
  }

  async function toggleRecurring(rec) {
    try {
      const newStatus = rec.is_active ? 0 : 1
      await api.put(`/api/recurring-transactions/${rec.id}`, { is_active: newStatus })
      session.showToast(newStatus ? '✅ Đã kích hoạt linh trận!' : '⏸️ Đã tạm dừng linh trận!')
      await loadRecurring()
      if (newStatus) await refreshAfterTxnChange()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật linh trận!', 'error')
    }
  }

  async function deleteRecurring(id) {
    if (!confirm('Hủy bỏ linh trận định kỳ này?')) return
    try {
      await api.delete(`/api/recurring-transactions/${id}`)
      session.showToast('Linh trận đã bị hủy!')
      await loadRecurring()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi hủy linh trận!', 'error')
    }
  }

  function openEditRecurring(rec) {
    editRecurringForm.value = {
      id: rec.id,
      wallet_id: rec.wallet_id,
      category_id: rec.category_id,
      amount: rec.amount,
      transaction_type: rec.transaction_type,
      frequency: rec.frequency,
      next_run_date: rec.next_run_date,
      note: rec.note || '',
      is_active: rec.is_active
    }
    showEditRecurringModal.value = true
  }

  async function updateRecurring() {
    session.loading = true
    try {
      await api.put(`/api/recurring-transactions/${editRecurringForm.value.id}`, editRecurringForm.value)
      session.showToast('✨ Linh trận định kỳ đã được cập nhật!')
      showEditRecurringModal.value = false
      await loadRecurring()
      await refreshAfterTxnChange()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật linh trận!', 'error')
    }
    session.loading = false
  }

  // ─── CRUD ─────────────────────
  async function createTransaction() {
    if (!txnForm.value.amount || !txnForm.value.wallet_id || !txnForm.value.category_id) {
      session.showToast('Vui lòng điền đầy đủ thông tin!', 'error')
      return
    }
    session.loading = true
    try {
      await api.post('/api/transactions', txnForm.value)
      session.showToast('⚡ Giao dịch Linh Thạch đã ghi nhận!')
      txnForm.value = {
        transaction_type: 'EXPENSE', amount: 0, wallet_id: txnForm.value.wallet_id,
        category_id: null, transaction_date: todayStr(), note: ''
      }
      await refreshAfterTxnChange(true)
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch!', 'error')
    }
    session.loading = false
  }

  // Tải lại những dữ liệu phụ thuộc vào giao dịch (số dư ví, tổng quan, hạn mức, biểu đồ)
  async function refreshAfterTxnChange(resetPage = false) {
    await Promise.all([
      loadTransactions(resetPage), walletStore.loadWallets(), reportStore.loadSummary(),
      budgetStore.loadBudgets(), budgetStore.checkBudgetAlerts(), reportStore.loadTrend(), reportStore.loadWeekly(),
    ])
  }

  function openEditTxn(txn) {
    editTxnForm.value = {
      id: txn.id,
      transaction_type: txn.transaction_type,
      amount: txn.amount,
      wallet_id: txn.wallet_id,
      category_id: txn.category_id,
      transaction_date: txn.transaction_date,
      note: txn.note || ''
    }
    showEditTxnModal.value = true
  }

  async function updateTransaction() {
    const f = editTxnForm.value
    if (!f.amount || f.amount <= 0 || !f.wallet_id || !f.category_id || !f.transaction_date) {
      session.showToast('Vui lòng điền đầy đủ thông tin hợp lệ!', 'error')
      return
    }
    session.loading = true
    try {
      await api.put(`/api/transactions/${f.id}`, {
        transaction_type: f.transaction_type,
        amount: Number(f.amount),
        wallet_id: f.wallet_id,
        category_id: f.category_id,
        transaction_date: f.transaction_date,
        note: f.note || ''
      })
      session.showToast('✨ Giao dịch đã được cập nhật!')
      showEditTxnModal.value = false
      await refreshAfterTxnChange()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật giao dịch!', 'error')
    }
    session.loading = false
  }

  async function deleteTransaction(id) {
    if (!confirm('Xóa giao dịch này?')) return
    try {
      await api.delete(`/api/transactions/${id}`)
      session.showToast('Giao dịch đã xóa!')
      await refreshAfterTxnChange()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi xóa giao dịch!', 'error')
    }
  }

  return {
    showEditTxnModal, editTxnForm, showEditRecurringModal, editRecurringForm, transactions,
    showRecurringSection, recurringList, recurringForm, txnFilter, txnPagination, txnForm, filteredCategories,
    editTxnCategories, totalPages, loadTransactions, changeTxnPage, resetTxnFilter, loadRecurring,
    createRecurring, toggleRecurring, deleteRecurring, openEditRecurring, updateRecurring, createTransaction,
    refreshAfterTxnChange, openEditTxn, updateTransaction, deleteTransaction,
  }
})
