/** Phiên đăng nhập, hồ sơ người dùng, giao diện (theme, toast, loading) và điều phối tải / xóa dữ liệu. */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import router from '../router'
import { todayStr } from '../utils/format'
import { useAdminStore } from './admin'
import { useAiStore } from './ai'
import { useBudgetStore } from './budgets'
import { useCategoryStore } from './categories'
import { useDebtStore } from './debts'
import { useGoalStore } from './goals'
import { useReportStore } from './reports'
import { useTransactionStore } from './transactions'
import { useWalletStore } from './wallets'

export const useSessionStore = defineStore('session', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const adminStore = useAdminStore()
  const aiStore = useAiStore()
  const budgetStore = useBudgetStore()
  const categoryStore = useCategoryStore()
  const debtStore = useDebtStore()
  const goalStore = useGoalStore()
  const reportStore = useReportStore()
  const txnStore = useTransactionStore()
  const walletStore = useWalletStore()

  // ─── STATE ────────────────────
  const isLoggedIn = ref(false)
  const authMode = ref('login')
  const authForm = ref({ email: '', password: '', full_name: '', soul_lamp: '' })
  const currentTheme = ref(localStorage.getItem('app_theme') || 'xianxia')
  const forgotForm = ref({ email: '', soul_lamp: '' })
  const resetForm = ref({ email: '', token: '', new_password: '' })
  const devResetToken = ref('')
  const token = ref('')
  const userName = ref('Ký Chủ')
  const userEmail = ref('')
  const loading = ref(false)
  const loadingProfile = ref(false)
  const loadingSoulLamp = ref(false)
  const errorMsg = ref('')
  const toast = ref(null)

  // Profile modal state
  const showProfileModal = ref(false)
  const profileForm = ref({ full_name: '' })
  const soulLampForm = ref({ current_password: '', new_soul_lamp: '' })

  const userRole = ref(localStorage.getItem('xianxia_role') || 'user')
  const currentUserId = ref(parseInt(localStorage.getItem('xianxia_uid')) || null)

  const tabs = [
    { id: 'dashboard',    icon: '📊', label: 'Tổng Quan' },
    { id: 'transactions', icon: '💸', label: 'Giao Dịch' },
    { id: 'debts',        icon: '📜', label: 'Sổ Nợ' },
    { id: 'goals',        icon: '🎯', label: 'Mục Tiêu' },
    { id: 'wallets',      icon: '💳', label: 'Túi Càn Khôn' },
    { id: 'categories',   icon: '🏷️', label: 'Danh Mục' },
    { id: 'ocr',          icon: '🧾', label: 'Linh Nhãn OCR' },
    { id: 'budgets',      icon: '🎯', label: 'Hạn Mức' },
    { id: 'stats',        icon: '📈', label: 'Thống Kê' },
    { id: 'chat',         icon: '💬', label: 'Khí Linh AI' },
    { id: 'admin',        icon: '🛡️', label: 'Phân Quyền', adminOnly: true },
  ]

  const isUserAdmin = computed(() => {
    const r = (userRole.value || '').toString().toLowerCase().trim()
    return r === 'admin'
  })

  const displayTabs = computed(() => {
    return tabs.filter(t => !t.adminOnly || isUserAdmin.value)
  })

  // ─── THEME TOGGLE ─────────────
  function switchTheme() {
    currentTheme.value = currentTheme.value === 'modern' ? 'xianxia' : 'modern'
    localStorage.setItem('app_theme', currentTheme.value)
    document.body.setAttribute('data-theme', currentTheme.value)
  }

  // ─── HELPERS ──────────────────
  function resetAllState() {
    walletStore.wallets = []
    categoryStore.categories = []
    txnStore.transactions = []
    debtStore.debts = []
    goalStore.savingGoals = []
    adminStore.adminUsers = []
    adminStore.adminStats = {}
    txnStore.recurringList = []
    walletStore.walletTransfers = []
    goalStore.goalLogs = []
    budgetStore.budgets = []
    reportStore.summary = { total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] }
    budgetStore.budgetAlerts = []
    aiStore.chatMessages = []
    aiStore.chatInput = ''
    aiStore.chatLoading = false
    reportStore.trendData = { trend: [] }
    reportStore.weeklyData = { data: [] }
    reportStore.compareData = null
    reportStore.savingTips = null
    aiStore.ocrFile = null
    aiStore.ocrPreview = null
    aiStore.ocrResult = null
    aiStore.ocrConfirmForm = {
      note: '',
      amount: 0,
      transaction_date: todayStr(),
      wallet_id: null,
      category_id: null,
      transaction_type: 'EXPENSE'
    }
    errorMsg.value = ''
    toast.value = null
  }

  function showToast(message, type = 'success') {
    toast.value = { message, type }
    setTimeout(() => { toast.value = null }, 3500)
  }

  // ─── AUTH ─────────────────────
  async function doLogin() {
    loading.value = true
    errorMsg.value = ''
    resetAllState()
    try {
      const { data } = await api.post('/api/auth/login', {
        email: authForm.value.email,
        password: authForm.value.password
      })
      token.value = data.token
      userName.value = data.full_name || 'Ký Chủ'
      userEmail.value = data.email
      userRole.value = data.role || 'user'
      currentUserId.value = data.user_id
      isLoggedIn.value = true
      localStorage.setItem('xianxia_token', data.token)
      localStorage.setItem('xianxia_user', userName.value)
      localStorage.setItem('xianxia_email', data.email)
      localStorage.setItem('xianxia_role', userRole.value)
      localStorage.setItem('xianxia_uid', data.user_id)
      await loadAllData()
    } catch (err) {
      errorMsg.value = err.response?.data?.detail || 'Lỗi đăng nhập!'
    }
    loading.value = false
  }

  async function doRegister() {
    if (!authForm.value.password || authForm.value.password.length < 6) {
      errorMsg.value = 'Mật khẩu phải có ít nhất 6 ký tự.'
      return
    }
    if (!authForm.value.soul_lamp || authForm.value.soul_lamp.trim().length < 3) {
      errorMsg.value = 'Bản Mệnh Hồn Đăng không được để trống và phải có ít nhất 3 ký tự.'
      return
    }
    loading.value = true
    errorMsg.value = ''
    resetAllState()
    try {
      const regForm = {
        ...authForm.value,
        full_name: authForm.value.full_name.trim() || 'Ký Chủ',
        soul_lamp: authForm.value.soul_lamp.trim()
      }
      const { data } = await api.post('/api/auth/register', regForm)
      token.value = data.token
      userName.value = data.full_name || 'Ký Chủ'
      userEmail.value = data.email
      userRole.value = data.role || 'user'
      currentUserId.value = data.user_id
      isLoggedIn.value = true
      localStorage.setItem('xianxia_token', data.token)
      localStorage.setItem('xianxia_user', userName.value)
      localStorage.setItem('xianxia_email', data.email)
      localStorage.setItem('xianxia_role', userRole.value)
      localStorage.setItem('xianxia_uid', data.user_id)
      await loadAllData()
    } catch (err) {
      errorMsg.value = err.response?.data?.detail || 'Lỗi đăng ký!'
    }
    loading.value = false
  }

  function openForgotPassword() {
    forgotForm.value.email = authForm.value.email || ''
    forgotForm.value.soul_lamp = ''
    devResetToken.value = ''
    authMode.value = 'forgot'
    errorMsg.value = ''
  }

  async function doForgotPassword() {
    if (!forgotForm.value.email || !forgotForm.value.soul_lamp) {
      errorMsg.value = 'Vui lòng nhập đầy đủ Email và Bản Mệnh Hồn Đăng!'
      return
    }
    loading.value = true
    errorMsg.value = ''
    try {
      const { data } = await api.post('/api/auth/forgot-password', {
        email: forgotForm.value.email,
        soul_lamp: forgotForm.value.soul_lamp.trim()
      })
      // Production: mã được gửi qua email, response không chứa reset_token
      devResetToken.value = data.reset_token || ''
      resetForm.value.email = forgotForm.value.email
      resetForm.value.token = data.reset_token || ''
      resetForm.value.new_password = ''
      authMode.value = 'reset'
      showToast(data.email_sent ? '📧 Mã xác thực đã được gửi tới email của bạn!' : '🔑 Đã tạo mã xác thực khôi phục!')
    } catch (err) {
      errorMsg.value = err.response?.data?.detail || 'Thông tin xác thực không chính xác, vui lòng kiểm tra lại'
    }
    loading.value = false
  }

  async function doResetPassword() {
    if (!resetForm.value.token || !resetForm.value.new_password) {
      errorMsg.value = 'Vui lòng nhập đầy đủ mã xác thực và mật khẩu mới!'
      return
    }
    if (resetForm.value.new_password.length < 6) {
      errorMsg.value = 'Mật khẩu mới phải có ít nhất 6 ký tự.'
      return
    }
    loading.value = true
    errorMsg.value = ''
    try {
      await api.post('/api/auth/reset-password', resetForm.value)
      showToast('✨ Mật khẩu đã được đặt lại thành công! Hãy đăng nhập.')
      authForm.value.email = resetForm.value.email
      authForm.value.password = ''
      authMode.value = 'login'
      devResetToken.value = ''
    } catch (err) {
      errorMsg.value = err.response?.data?.detail || 'Lỗi đặt lại mật khẩu!'
    }
    loading.value = false
  }

  function doLogout() {
    isLoggedIn.value = false
    token.value = ''
    userName.value = 'Ký Chủ'
    userEmail.value = ''
    userRole.value = 'user'
    currentUserId.value = null
    localStorage.removeItem('xianxia_token')
    localStorage.removeItem('xianxia_user')
    localStorage.removeItem('xianxia_email')
    localStorage.removeItem('xianxia_role')
    localStorage.removeItem('xianxia_uid')
    authForm.value = { email: '', password: '', full_name: '', soul_lamp: '' }
    forgotForm.value = { email: '', soul_lamp: '' }
    resetAllState()
    router.replace({ name: 'dashboard' })
  }

  // ─── USER PROFILE MANAGEMENT ──
  function openProfileModal() {
    profileForm.value.full_name = userName.value
    soulLampForm.value = { current_password: '', new_soul_lamp: '' }
    showProfileModal.value = true
  }

  async function saveProfile() {
    const newName = profileForm.value.full_name.trim()
    if (!newName) {
      showToast('Vui lòng nhập đạo hiệu!', 'error')
      return
    }
    loadingProfile.value = true
    try {
      await api.put('/api/user/profile', { full_name: newName })
      userName.value = newName
      localStorage.setItem('xianxia_user', newName)
      showToast('✨ Đạo hiệu đã được cập nhật!')
      showProfileModal.value = false
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật tên!', 'error')
    }
    loadingProfile.value = false
  }

  async function saveSoulLamp() {
    if (!soulLampForm.value.current_password) {
      showToast('Vui lòng nhập khẩu quyết (mật khẩu) hiện tại!', 'error')
      return
    }
    if (!soulLampForm.value.new_soul_lamp || soulLampForm.value.new_soul_lamp.trim().length < 3) {
      showToast('Bản Mệnh Hồn Đăng mới phải có ít nhất 3 ký tự!', 'error')
      return
    }
    loadingSoulLamp.value = true
    try {
      const { data } = await api.put('/api/user/soul-lamp', {
        current_password: soulLampForm.value.current_password,
        new_soul_lamp: soulLampForm.value.new_soul_lamp.trim()
      })
      showToast(data.message || '✨ Đã cập nhật Bản Mệnh Hồn Đăng thành công!')
      soulLampForm.value = { current_password: '', new_soul_lamp: '' }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi cập nhật Bản Mệnh Hồn Đăng!', 'error')
    }
    loadingSoulLamp.value = false
  }

  async function fetchUserProfile() {
    try {
      const { data } = await api.get('/api/user/profile')
      if (data && data.full_name) {
        userName.value = data.full_name
        userEmail.value = data.email
        userRole.value = data.role || 'user'
        currentUserId.value = data.id
        localStorage.setItem('xianxia_user', data.full_name)
        localStorage.setItem('xianxia_email', data.email)
        localStorage.setItem('xianxia_role', userRole.value)
        localStorage.setItem('xianxia_uid', data.id)
      }
    } catch {}
  }

  // ─── DATA LOADING ─────────────
  async function loadAllData() {
    await Promise.all([
      fetchUserProfile(),
      walletStore.loadWallets(), categoryStore.loadCategories(), txnStore.loadTransactions(true),
      debtStore.loadDebts(), goalStore.loadSavingGoals(),
      txnStore.loadRecurring(), reportStore.loadSummary(), budgetStore.loadBudgets(), budgetStore.checkBudgetAlerts(),
      reportStore.loadTrend(), reportStore.loadWeekly(), aiStore.loadSuggestedQuestions(), aiStore.loadChatHistory(),
      walletStore.loadWalletTransfers(),
    ])
    if (userRole.value === 'admin') {
      adminStore.loadAdminStats()
      adminStore.loadAdminUsers()
    }
  }

  // ─── TAB SWITCH (điều hướng qua vue-router; tác vụ riêng từng tab nằm trong onMounted của view) ───
  function switchTab(tabId) {
    router.push({ name: tabId })
  }

  // ─── INIT ─────────────────────
  // Khôi phục phiên đăng nhập đã lưu (gọi một lần khi App mount)
  function restoreSession() {
    const savedToken = localStorage.getItem('xianxia_token')
    const savedUser = localStorage.getItem('xianxia_user')
    const savedEmail = localStorage.getItem('xianxia_email')
    const savedRole = localStorage.getItem('xianxia_role')
    const savedUid = localStorage.getItem('xianxia_uid')
    if (savedRole) userRole.value = savedRole
    if (savedUid) currentUserId.value = parseInt(savedUid)
    if (savedToken) {
      token.value = savedToken
      userName.value = (savedUser && savedUser !== 'Đạo Hữu Admin') ? savedUser : 'Ký Chủ'
      userEmail.value = savedEmail || 'admin@gmail.com'
      isLoggedIn.value = true
      loadAllData()
    }
  }

  return {
    isLoggedIn, authMode, authForm, currentTheme, forgotForm, resetForm, devResetToken, token, userName,
    userEmail, loading, loadingProfile, loadingSoulLamp, errorMsg, toast, showProfileModal, profileForm,
    soulLampForm, userRole, currentUserId, tabs, isUserAdmin, displayTabs, switchTheme, showToast, doLogin,
    doRegister, openForgotPassword, doForgotPassword, doResetPassword, doLogout, openProfileModal,
    saveProfile, saveSoulLamp, fetchUserProfile, switchTab, restoreSession, resetAllState, loadAllData,
  }
})
