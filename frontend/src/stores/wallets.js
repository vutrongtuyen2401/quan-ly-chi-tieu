/** Ví (Túi Càn Khôn) và chuyển tiền giữa các ví. */
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { useDebtStore } from './debts'
import { useReportStore } from './reports'
import { useSessionStore } from './session'

export const useWalletStore = defineStore('wallets', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const debtStore = useDebtStore()
  const reportStore = useReportStore()
  const session = useSessionStore()

  // Edit Modals state
  const showEditWalletModal = ref(false)
  const editWalletForm = ref({ id: null, wallet_name: '', wallet_type: 'cash' })

  // Data
  const wallets = ref([])
  const walletForm = ref({ wallet_name: '', balance: 0, wallet_type: 'cash' })
  const transferForm = ref({ from_wallet_id: null, to_wallet_id: null, amount: 0, note: '' })
  const walletTransfers = ref([])

  async function loadWalletTransfers() {
    try { walletTransfers.value = (await api.get('/api/wallets/transfers', { params: { limit: 10 } })).data || [] } catch {}
  }

  async function loadWallets() {
    try { wallets.value = (await api.get('/api/wallets')).data } catch {}
  }

  // Change 3: Edit Wallet & Category
  function openEditWallet(w) {
    editWalletForm.value = { id: w.id, wallet_name: w.wallet_name, wallet_type: w.wallet_type }
    showEditWalletModal.value = true
  }

  async function updateWallet() {
    if (!editWalletForm.value.wallet_name.trim()) {
      session.showToast('Tên ví không được để trống!', 'error')
      return
    }
    session.loading = true
    try {
      await api.put(`/api/wallets/${editWalletForm.value.id}`, {
        wallet_name: editWalletForm.value.wallet_name,
        wallet_type: editWalletForm.value.wallet_type
      })
      session.showToast('✨ Túi Càn Khôn đã được cập nhật!')
      showEditWalletModal.value = false
      await loadWallets()
      await reportStore.loadSummary()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật ví!', 'error')
    }
    session.loading = false
  }

  async function createWallet() {
    if (!walletForm.value.wallet_name) {
      session.showToast('Vui lòng nhập tên ví!', 'error')
      return
    }
    session.loading = true
    try {
      await api.post('/api/wallets', walletForm.value)
      session.showToast('✨ Túi Càn Khôn mới đã khai mở!')
      walletForm.value = { wallet_name: '', balance: 0, wallet_type: 'cash' }
      await loadWallets()
      await reportStore.loadSummary()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi tạo ví!', 'error')
    }
    session.loading = false
  }

  async function deleteWallet(id) {
    if (!confirm('Xóa ví này? (Chỉ xóa được ví chưa có giao dịch nào.)')) return
    try {
      await api.delete(`/api/wallets/${id}`)
      session.showToast('Ví đã xóa!')
      await Promise.all([loadWallets(), reportStore.loadSummary(), debtStore.loadDebts()])
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi xóa ví!', 'error')
    }
  }

  async function doTransfer() {
    if (!transferForm.value.from_wallet_id || !transferForm.value.to_wallet_id || !transferForm.value.amount) {
      session.showToast('Vui lòng điền đầy đủ thông tin chuyển tiền!', 'error')
      return
    }
    session.loading = true
    try {
      const { data } = await api.post('/api/wallets/transfer', transferForm.value)
      session.showToast(`⚡ ${data.message}`)
      transferForm.value = { from_wallet_id: null, to_wallet_id: null, amount: 0, note: '' }
      await Promise.all([loadWallets(), reportStore.loadSummary(), loadWalletTransfers()])
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi chuyển tiền!', 'error')
    }
    session.loading = false
  }

  return {
    showEditWalletModal, editWalletForm, wallets, walletForm, transferForm, walletTransfers,
    loadWalletTransfers, loadWallets, openEditWallet, updateWallet, createWallet, deleteWallet, doTransfer,
  }
})
