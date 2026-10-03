/** Khí Linh AI (chat) và Linh Nhãn OCR hóa đơn. */
import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import router from '../router'
import { todayStr } from '../utils/format'
import { useCategoryStore } from './categories'
import { useSessionStore } from './session'
import { useTransactionStore } from './transactions'
import { useWalletStore } from './wallets'

export const useAiStore = defineStore('ai', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const categoryStore = useCategoryStore()
  const session = useSessionStore()
  const txnStore = useTransactionStore()
  const walletStore = useWalletStore()

  const chatMessages = ref([])
  const chatInput = ref('')
  const suggestedQuestions = ref([])

  // OCR
  const ocrFile = ref(null)
  const ocrPreview = ref(null)
  const ocrResult = ref(null)
  const ocrConfirmForm = ref({
    note: '',
    amount: 0,
    transaction_date: todayStr(),
    wallet_id: null,
    category_id: null,
    transaction_type: 'EXPENSE'
  })
  const chatLoading = ref(false)

  async function loadChatHistory() {
    try {
      const { data } = await api.get('/api/ai/chat-history')
      const rows = Array.isArray(data) ? [...data].reverse() : []
      chatMessages.value = rows.flatMap(r => [
        { role: 'user', text: r.prompt_question },
        { role: 'ai', text: r.ai_response }
      ])
    } catch {}
  }

  async function loadSuggestedQuestions() {
    try {
      const { data } = await api.get('/api/chat/suggested-questions')
      suggestedQuestions.value = data || []
    } catch {}
  }

  // ─── OCR ──────────────────────
  const OCR_MAX_BYTES = 8 * 1024 * 1024

  function setOCRFile(file) {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      session.showToast('Chỉ hỗ trợ file ảnh (JPG, PNG, WEBP...)!', 'error')
      return
    }
    if (file.size > OCR_MAX_BYTES) {
      session.showToast('Ảnh quá lớn (tối đa 8 MB)!', 'error')
      return
    }
    if (ocrPreview.value) URL.revokeObjectURL(ocrPreview.value)
    ocrFile.value = file
    ocrPreview.value = URL.createObjectURL(file)
    ocrResult.value = null
  }

  function handleOCRUpload(e) {
    setOCRFile(e.target.files[0])
    e.target.value = ''
  }

  function handleOCRDrop(e) {
    setOCRFile(e.dataTransfer.files[0])
  }

  async function scanInvoice() {
    if (!ocrFile.value) return
    session.loading = true
    try {
      const formData = new FormData()
      formData.append('file', ocrFile.value)
      const { data } = await api.post('/api/ai/scan-invoice', formData)
      ocrResult.value = data.data

      const defaultWallet = walletStore.wallets.length ? walletStore.wallets[0].id : null
      const defaultCat = categoryStore.expenseCategories.length ? categoryStore.expenseCategories[0].id : null
      ocrConfirmForm.value = {
        note: data.data.store_name || 'Chi tiêu từ hóa đơn',
        amount: data.data.total_amount || 0,
        transaction_date: data.data.date || todayStr(),
        wallet_id: defaultWallet,
        category_id: defaultCat,
        transaction_type: 'EXPENSE'
      }
      session.showToast('👁️ Linh Nhãn đã hoàn thành phân tích! Vui lòng kiểm tra và xác nhận.')
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi OCR!', 'error')
    }
    session.loading = false
  }

  async function confirmOCRTransaction() {
    if (!ocrConfirmForm.value.amount || ocrConfirmForm.value.amount <= 0) {
      session.showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
      return
    }
    if (!ocrConfirmForm.value.wallet_id || !ocrConfirmForm.value.category_id) {
      session.showToast('Vui lòng chọn Túi Càn Khôn và Danh Mục Chi!', 'error')
      return
    }
    session.loading = true
    try {
      await api.post('/api/transactions', ocrConfirmForm.value)
      session.showToast('⚡ Giao dịch từ hóa đơn đã được thêm vào lịch sử!')
      ocrResult.value = null
      ocrFile.value = null
      ocrPreview.value = null
      await txnStore.refreshAfterTxnChange(true)
      router.push({ name: 'transactions' })
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi lưu giao dịch!', 'error')
    }
    session.loading = false
  }

  // ─── AI CHAT ──────────────────
  async function sendChat() {
    if (!chatInput.value.trim() || chatLoading.value) return
    if (!Array.isArray(chatMessages.value)) {
      chatMessages.value = []
    }
    const msg = chatInput.value.trim()
    chatMessages.value.push({ role: 'user', text: msg })
    chatInput.value = ''

    chatLoading.value = true
    try {
      const { data } = await api.post('/api/ai/chat', { message: msg }, { timeout: 35000 })  // backend thử tối đa 3 mô hình × 10 giây
      if (!Array.isArray(chatMessages.value)) chatMessages.value = []
      chatMessages.value.push({ role: 'ai', text: data.response })
      loadSuggestedQuestions()
    } catch (err) {
      if (!Array.isArray(chatMessages.value)) chatMessages.value = []
      const errMsg = err.code === 'ECONNABORTED'
        ? '🔮 Tiên Trí phản hồi quá lâu do nghẽn mạng, vui lòng thử lại.'
        : (err.response?.data?.detail || 'Không thể kết nối với thần trí AI.')
      chatMessages.value.push({
        role: 'ai',
        text: '⚠️ ' + errMsg
      })
    } finally {
      chatLoading.value = false
    }
  }

  return {
    chatMessages, chatInput, suggestedQuestions, chatLoading, loadChatHistory, loadSuggestedQuestions,
    sendChat, ocrFile, ocrPreview, ocrResult, ocrConfirmForm, OCR_MAX_BYTES, setOCRFile, handleOCRUpload,
    handleOCRDrop, scanInvoice, confirmOCRTransaction,
  }
})
