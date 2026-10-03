/**
 * Store Pinia chung của ứng dụng: state, gọi API và nghiệp vụ phía client.
 * (Chuyển nguyên văn từ setup() của App.vue cũ — template các view dùng trực tiếp qua useAppBindings().)
 */
import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { vi } from 'date-fns/locale'
import router from '../router'
import { toLocalDateStr, todayStr, toLocalMonthStr, escapeHtml, formatChatText, formatVND, budgetPct, walletTypeIcon } from '../utils/format'

export const useAppStore = defineStore('app', () => {
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
  const loadingTips = ref(false)
  const loadingProfile = ref(false)
  const loadingSoulLamp = ref(false)
  const errorMsg = ref('')
  const toast = ref(null)

  // Profile modal state
  const showProfileModal = ref(false)
  const profileForm = ref({ full_name: '' })
  const soulLampForm = ref({ current_password: '', new_soul_lamp: '' })

  // Edit Modals state
  const showEditWalletModal = ref(false)
  const editWalletForm = ref({ id: null, wallet_name: '', wallet_type: 'cash' })

  const showEditCatModal = ref(false)
  const editCatForm = ref({ id: null, category_name: '', icon: '📦' })

  const showEditBudgetModal = ref(false)
  const editBudgetForm = ref({ id: null, limit_amount: 0 })

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


  // Admin State
  const adminStats = ref({})
  const adminUsers = ref([])
  const adminFilter = ref({ search: '', role: '', status: '' })

  // Data
  const wallets = ref([])
  const categories = ref([])
  const transactions = ref([])
  const budgets = ref([])
  const summary = ref({ total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] })
  const budgetAlerts = ref([])
  const chatMessages = ref([])
  const chatInput = ref('')
  const suggestedQuestions = ref([])

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

  // New v3 data
  const trendData = ref({ trend: [] })
  const weeklyData = ref({ data: [] })
  const compareData = ref(null)
  const savingTips = ref(null)

  // Compare month defaults
  const now = new Date()
  const compareMonth2 = ref(toLocalMonthStr(now))
  const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
  const compareMonth1 = ref(toLocalMonthStr(prevMonth))

  const budgetMonth = ref(toLocalMonthStr(now))

  watch(budgetMonth, async (newVal) => {
    if (newVal) {
      await loadBudgets()
    }
  })

  const viLocale = vi

  const endNow = new Date()
  const start30Days = new Date(endNow)
  start30Days.setDate(endNow.getDate() - 30)
  const statsDateRange = ref([start30Days, endNow])
  
  const presetRanges = ref([
    { label: '7 ngày qua', value: () => { const e = new Date(); const s = new Date(e); s.setDate(e.getDate() - 7); return [s, e] } },
    { label: '30 ngày qua', value: () => { const e = new Date(); const s = new Date(e); s.setDate(e.getDate() - 30); return [s, e] } },
    { label: 'Tháng này', value: () => { const e = new Date(); const s = new Date(e.getFullYear(), e.getMonth(), 1); return [s, e] } },
    { label: 'Tháng trước', value: () => { const e = new Date(); const s = new Date(e.getFullYear(), e.getMonth() - 1, 1); const e2 = new Date(e.getFullYear(), e.getMonth(), 0); return [s, e2] } },
    { label: '3 tháng gần đây', value: () => { const e = new Date(); const s = new Date(e); s.setMonth(e.getMonth() - 3); return [s, e] } },
    { label: '6 tháng gần đây', value: () => { const e = new Date(); const s = new Date(e); s.setMonth(e.getMonth() - 6); return [s, e] } }
  ])

  function onStatsDateChange() {
    if (!statsDateRange.value || !statsDateRange.value[0] || !statsDateRange.value[1]) return
    
    let start = new Date(statsDateRange.value[0])
    let end = new Date(statsDateRange.value[1])
    
    if (end < start) {
      const tmp = start
      start = end
      end = tmp
      statsDateRange.value = [start, end]
    }
    
    let m = (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth() + 1
    if (m < 1) m = 1; if (m > 12) m = 12
    
    let w = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 7))
    if (w < 1) w = 1; if (w > 12) w = 12
    
    const yyyy = end.getFullYear()
    const mm = String(end.getMonth() + 1).padStart(2, '0')
    const my = `${yyyy}-${mm}`
    
    loadTrend(m)
    loadWeekly(w)
    loadSummary(my)
  }

  // Forms
  const txnForm = ref({
    transaction_type: 'EXPENSE', amount: 0, wallet_id: null,
    category_id: null, transaction_date: todayStr(), note: ''
  })
  const walletForm = ref({ wallet_name: '', balance: 0, wallet_type: 'cash' })
  const catForm = ref({ category_name: '', category_type: 'EXPENSE', icon: '📦' })
  const budgetForm = ref({
    category_id: null, limit_amount: 0,
    month_year: toLocalMonthStr(new Date())
  })
  const transferForm = ref({ from_wallet_id: null, to_wallet_id: null, amount: 0, note: '' })
  const walletTransfers = ref([])
  const goalLogs = ref([])

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

  const iconOptions = ['🍕','🛍️','🚗','💵','🎁','🏠','💊','📚','🎮','☕','🍜','🎬','🏋️','✈️','📱','👕','🎵','🐾','🔧','📦']

  // ─── AXIOS CONFIG ─────────────
  const api = axios.create({ baseURL: '' })
  api.interceptors.request.use(config => {
    if (token.value) config.headers.Authorization = `Bearer ${token.value}`
    return config
  })
  // Token hết hạn / tài khoản bị khóa → tự đăng xuất thay vì để các request thất bại âm thầm
  api.interceptors.response.use(
    response => response,
    error => {
      const isAuthCall = (error.config?.url || '').startsWith('/api/auth/')
      if (error.response?.status === 401 && !isAuthCall && isLoggedIn.value) {
        const reason = error.response.data?.detail || 'Phiên đăng nhập đã hết hạn.'
        doLogout()
        errorMsg.value = reason
        showToast(`🔒 ${reason}`, 'error')
      }
      return Promise.reject(error)
    }
  )

  // ─── COMPUTED ─────────────────
  const incomeCategories = computed(() => categories.value.filter(c => c.category_type === 'INCOME'))
  const expenseCategories = computed(() => categories.value.filter(c => c.category_type === 'EXPENSE'))
  const filteredCategories = computed(() =>
    categories.value.filter(c => c.category_type === txnForm.value.transaction_type)
  )
  const editTxnCategories = computed(() =>
    categories.value.filter(c => c.category_type === editTxnForm.value.transaction_type)
  )
  const maxCategoryExpense = computed(() => {
    if (!summary.value.expense_by_category?.length) return 1
    return Math.max(...summary.value.expense_by_category.map(c => c.total), 1)
  })
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(txnPagination.value.totalCount / txnPagination.value.limit))
  )

  // ─── CHART DATA COMPUTED ──────
  const dashboardDoughnutData = computed(() => ({
    labels: (summary.value.expense_by_category || []).map(c => `${c.icon} ${c.category_name}`),
    values: (summary.value.expense_by_category || []).map(c => c.total),
  }))

  const dashboardBarData = computed(() => ({
    labels: (trendData.value.trend || []).map(t => t.month),
    income: (trendData.value.trend || []).map(t => t.income),
    expense: (trendData.value.trend || []).map(t => t.expense),
  }))

  const trendBarData = computed(() => ({
    labels: (trendData.value.trend || []).map(t => t.month),
    income: (trendData.value.trend || []).map(t => t.income),
    expense: (trendData.value.trend || []).map(t => t.expense),
  }))

  const weeklyLineData = computed(() => ({
    labels: (weeklyData.value.data || []).map(w => w.week_start || w.week),
    expense: (weeklyData.value.data || []).map(w => w.expense),
    income: (weeklyData.value.data || []).map(w => w.income),
  }))

  // API trả đủ các tháng/tuần (kể cả kỳ bằng 0) → chỉ vẽ biểu đồ khi có ít nhất 1 kỳ phát sinh giao dịch
  const hasTrendData = computed(() => (trendData.value.trend || []).some(t => t.income || t.expense))
  const hasWeeklyData = computed(() => (weeklyData.value.data || []).some(w => w.income || w.expense))

  const statsDoughnutData = computed(() => ({
    labels: (summary.value.expense_by_category || []).map(c => `${c.icon} ${c.category_name}`),
    values: (summary.value.expense_by_category || []).map(c => c.total),
  }))

  const isUserAdmin = computed(() => {
    const r = (userRole.value || '').toString().toLowerCase().trim()
    return r === 'admin'
  })

  const displayTabs = computed(() => {
    return tabs.filter(t => !t.adminOnly || isUserAdmin.value)
  })

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

  // ─── THEME TOGGLE ─────────────
  function switchTheme() {
    currentTheme.value = currentTheme.value === 'modern' ? 'xianxia' : 'modern'
    localStorage.setItem('app_theme', currentTheme.value)
    document.body.setAttribute('data-theme', currentTheme.value)
  }

  // ─── HELPERS ──────────────────
  function resetAllState() {
    wallets.value = []
    categories.value = []
    transactions.value = []
    debts.value = []
    savingGoals.value = []
    adminUsers.value = []
    adminStats.value = {}
    recurringList.value = []
    walletTransfers.value = []
    goalLogs.value = []
    budgets.value = []
    summary.value = { total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] }
    budgetAlerts.value = []
    chatMessages.value = []
    chatInput.value = ''
    chatLoading.value = false
    trendData.value = { trend: [] }
    weeklyData.value = { data: [] }
    compareData.value = null
    savingTips.value = null
    ocrFile.value = null
    ocrPreview.value = null
    ocrResult.value = null
    ocrConfirmForm.value = {
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

  // ─── ADMIN MANAGEMENT (CHƯỞNG MÔN CÁC) ────
  async function loadAdminStats() {
    if (userRole.value !== 'admin') return
    try {
      const { data } = await api.get('/api/admin/stats')
      adminStats.value = data || {}
    } catch (err) {
      console.error('Lỗi tải thống kê admin:', err)
    }
  }

  async function loadAdminUsers() {
    if (userRole.value !== 'admin') return
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
      showToast(data.message || 'Thao tác thành công!')
      await loadAdminUsers()
      await loadAdminStats()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi cập nhật trạng thái người dùng!', 'error')
    }
  }

  async function changeUserRole(u, newRole) {
    const title = newRole === 'admin' ? 'thăng cấp Chưởng Môn' : 'giáng xuống Đệ Tử'
    if (!confirm(`Đạo hữu có chắc chắn muốn ${title} cho "${u.email}"?`)) return
    try {
      const { data } = await api.put(`/api/admin/users/${u.id}/role`, { role: newRole })
      showToast(data.message || 'Thao tác thành công!')
      await loadAdminUsers()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi thay đổi vai trò!', 'error')
    }
  }

  // ─── DATA LOADING ─────────────
  async function loadAllData() {
    await Promise.all([
      fetchUserProfile(),
      loadWallets(), loadCategories(), loadTransactions(true),
      loadDebts(), loadSavingGoals(),
      loadRecurring(), loadSummary(), loadBudgets(), checkBudgetAlerts(),
      loadTrend(), loadWeekly(), loadSuggestedQuestions(), loadChatHistory(),
      loadWalletTransfers(),
    ])
    if (userRole.value === 'admin') {
      loadAdminStats()
      loadAdminUsers()
    }
  }

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

  async function loadWalletTransfers() {
    try { walletTransfers.value = (await api.get('/api/wallets/transfers', { params: { limit: 10 } })).data || [] } catch {}
  }

  async function loadGoalLogs(goalId) {
    goalLogs.value = []
    try { goalLogs.value = (await api.get(`/api/saving-goals/${goalId}/logs`, { params: { limit: 5 } })).data || [] } catch {}
  }

  async function loadWallets() {
    try { wallets.value = (await api.get('/api/wallets')).data } catch {}
  }
  async function loadCategories() {
    try { categories.value = (await api.get('/api/categories')).data } catch {}
  }

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

  // Change 7: Export reports (CSV / Excel)
  // Tải file báo cáo CSV / Excel trong khoảng ngày (dùng chung cho tab Giao Dịch & Thống Kê)
  async function downloadReport(format, startDate, endDate) {
    try {
      showToast(`⏳ Đang kết xuất báo cáo ${format.toUpperCase()}...`)
      const params = { format }
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      const response = await api.get('/api/reports/export', {
        params,
        responseType: 'blob'
      })

      const blob = new Blob([response.data], {
        type: format === 'csv'
          ? 'text/csv;charset=utf-8;'
          : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `bao_cao_chi_tieu_${todayStr().replace(/-/g, '')}.${format === 'csv' ? 'csv' : 'xlsx'}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      showToast(`📥 Xuất báo cáo ${format.toUpperCase()} thành công!`)
    } catch (err) {
      showToast('Lỗi khi xuất file báo cáo!', 'error')
    }
  }

  function doExportReports(format = 'excel') {
    return downloadReport(format, txnFilter.value.start_date, txnFilter.value.end_date)
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
      showToast('Vui lòng nhập tên mục tiêu và số tiền đích hợp lệ!', 'error')
      return
    }
    loading.value = true
    try {
      const payload = {
        target_name: goalForm.value.target_name.trim(),
        target_amount: Number(goalForm.value.target_amount),
        current_amount: Number(goalForm.value.current_amount || 0),
        target_date: goalForm.value.target_date || '',
        icon: goalForm.value.icon || '🎯'
      }
      await api.post('/api/saving-goals', payload)
      showToast('🎯 Khởi tạo mục tiêu tiết kiệm thành công!')
      goalForm.value = { target_name: '', target_amount: null, current_amount: 0, target_date: '', icon: '🎯' }
      await loadSavingGoals()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi tạo mục tiêu!', 'error')
    } finally {
      loading.value = false
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
      showToast('Vui lòng nhập tên mục tiêu và số tiền đích hợp lệ!', 'error')
      return
    }
    loading.value = true
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
      showToast('✨ Đã cập nhật mục tiêu tiết kiệm!')
      showEditGoalModal.value = false
      await loadSavingGoals()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật mục tiêu!', 'error')
    } finally {
      loading.value = false
    }
  }

  function openDepositGoal(g, action = 'deposit') {
    depositForm.value = {
      goal_id: g.id,
      goal_name: g.target_name,
      amount: null,
      wallet_id: wallets.value.length ? wallets.value[0].id : '',
      action: action
    }
    showDepositModal.value = true
    loadGoalLogs(g.id)
  }

  async function submitDepositWithdrawGoal() {
    if (!depositForm.value.amount || depositForm.value.amount <= 0) {
      showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
      return
    }
    loading.value = true
    try {
      const payload = {
        amount: Number(depositForm.value.amount),
        wallet_id: depositForm.value.wallet_id ? Number(depositForm.value.wallet_id) : null
      }
      const endpoint = depositForm.value.action === 'deposit' ? 'deposit' : 'withdraw'
      const { data } = await api.post(`/api/saving-goals/${depositForm.value.goal_id}/${endpoint}`, payload)
      showToast(data.message || 'Thao tác thành công!')
      showDepositModal.value = false
      await loadSavingGoals()
      await loadWallets()
      await loadSummary()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi nạp/rút linh thạch!', 'error')
    } finally {
      loading.value = false
    }
  }

  async function deleteSavingGoal(id) {
    if (!confirm('Đạo hữu có chắc chắn muốn xóa mục tiêu này?')) return
    try {
      await api.delete(`/api/saving-goals/${id}`)
      showToast('🗑️ Đã xóa mục tiêu tiết kiệm!')
      await loadSavingGoals()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi xóa mục tiêu!', 'error')
    }
  }

  // Change 8: Recurring transactions
  async function loadRecurring() {
    try {
      recurringList.value = (await api.get('/api/recurring-transactions')).data
    } catch {}
  }

  async function createRecurring() {
    if (!recurringForm.value.amount || !recurringForm.value.wallet_id || !recurringForm.value.category_id) {
      showToast('Vui lòng chọn đầy đủ ví, danh mục và số tiền!', 'error')
      return
    }
    loading.value = true
    try {
      await api.post('/api/recurring-transactions', recurringForm.value)
      showToast('✨ Linh trận định kỳ đã được thiết lập!')
      recurringForm.value = {
        wallet_id: wallets.value.length ? wallets.value[0].id : null,
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
      showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch định kỳ!', 'error')
    }
    loading.value = false
  }

  async function toggleRecurring(rec) {
    try {
      const newStatus = rec.is_active ? 0 : 1
      await api.put(`/api/recurring-transactions/${rec.id}`, { is_active: newStatus })
      showToast(newStatus ? '✅ Đã kích hoạt linh trận!' : '⏸️ Đã tạm dừng linh trận!')
      await loadRecurring()
      if (newStatus) await refreshAfterTxnChange()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật linh trận!', 'error')
    }
  }

  async function deleteRecurring(id) {
    if (!confirm('Hủy bỏ linh trận định kỳ này?')) return
    try {
      await api.delete(`/api/recurring-transactions/${id}`)
      showToast('Linh trận đã bị hủy!')
      await loadRecurring()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi hủy linh trận!', 'error')
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
    loading.value = true
    try {
      await api.put(`/api/recurring-transactions/${editRecurringForm.value.id}`, editRecurringForm.value)
      showToast('✨ Linh trận định kỳ đã được cập nhật!')
      showEditRecurringModal.value = false
      await loadRecurring()
      await refreshAfterTxnChange()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật linh trận!', 'error')
    }
    loading.value = false
  }

  function openEditBudget(b) {
    editBudgetForm.value = { id: b.id, limit_amount: b.limit_amount }
    showEditBudgetModal.value = true
  }

  async function updateBudget() {
    if (!editBudgetForm.value.limit_amount) return showToast('Vui lòng nhập số tiền!', 'error')
    loading.value = true
    try {
      await api.put(`/api/budgets/${editBudgetForm.value.id}`, { limit_amount: editBudgetForm.value.limit_amount })
      showToast('Đã cập nhật hạn mức!')
      showEditBudgetModal.value = false
      await loadBudgets()
      await checkBudgetAlerts()
    } catch (err) {
      showToast('Lỗi cập nhật!', 'error')
    }
    loading.value = false
  }

  function doExport(format) {
    const range = statsDateRange.value
    if (range && range[0] && range[1]) {
      return downloadReport(format, toLocalDateStr(range[0]), toLocalDateStr(range[1]))
    }
    return downloadReport(format)
  }

  // Change 3: Edit Wallet & Category
  function openEditWallet(w) {
    editWalletForm.value = { id: w.id, wallet_name: w.wallet_name, wallet_type: w.wallet_type }
    showEditWalletModal.value = true
  }

  async function updateWallet() {
    if (!editWalletForm.value.wallet_name.trim()) {
      showToast('Tên ví không được để trống!', 'error')
      return
    }
    loading.value = true
    try {
      await api.put(`/api/wallets/${editWalletForm.value.id}`, {
        wallet_name: editWalletForm.value.wallet_name,
        wallet_type: editWalletForm.value.wallet_type
      })
      showToast('✨ Túi Càn Khôn đã được cập nhật!')
      showEditWalletModal.value = false
      await loadWallets()
      await loadSummary()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật ví!', 'error')
    }
    loading.value = false
  }

  function openEditCategory(c) {
    editCatForm.value = { id: c.id, category_name: c.category_name, icon: c.icon }
    showEditCatModal.value = true
  }

  async function updateCategory() {
    if (!editCatForm.value.category_name.trim()) {
      showToast('Tên danh mục không được để trống!', 'error')
      return
    }
    loading.value = true
    try {
      await api.put(`/api/categories/${editCatForm.value.id}`, {
        category_name: editCatForm.value.category_name,
        icon: editCatForm.value.icon
      })
      showToast('✨ Danh mục đã được cập nhật!')
      showEditCatModal.value = false
      await loadCategories()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật danh mục!', 'error')
    }
    loading.value = false
  }

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
      showToast('Vui lòng nhập đối tác và số tiền hợp lệ!', 'error')
      return
    }
    loading.value = true
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
      showToast('📜 Đã ghi nhận khoản nợ thành công!')
      debtForm.value = { debt_type: 'BORROW', person_name: '', amount: null, due_date: '', wallet_id: '', note: '' }
      await loadDebts()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi ghi sổ nợ!', 'error')
    } finally {
      loading.value = false
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
      showToast('Vui lòng nhập đối tác và số tiền hợp lệ!', 'error')
      return
    }
    loading.value = true
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
      showToast('✨ Đã cập nhật khoản nợ!')
      showEditDebtModal.value = false
      await loadDebts()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật khoản nợ!', 'error')
    } finally {
      loading.value = false
    }
  }

  async function toggleSettleDebt(d) {
    try {
      const { data } = await api.post(`/api/debts/${d.id}/settle`)
      showToast(data.message || 'Đã cập nhật trạng thái tất toán!')
      await loadDebts()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi tất toán khoản nợ!', 'error')
    }
  }

  async function deleteDebt(id) {
    if (!confirm('Đạo hữu có chắc chắn muốn xóa khoản nợ này khỏi sổ?')) return
    try {
      await api.delete(`/api/debts/${id}`)
      showToast('🗑️ Đã xóa khoản nợ khỏi sổ!')
      await loadDebts()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi xóa khoản nợ!', 'error')
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

  async function loadSummary(monthYear = null) {
    let url = '/api/reports/summary'
    if (monthYear) url += `?month_year=${monthYear}`
    try { summary.value = (await api.get(url)).data } catch {}
  }
  async function loadBudgets() {
    try { budgets.value = (await api.get(`/api/budgets?month_year=${budgetMonth.value}`)).data } catch {}
  }
  async function checkBudgetAlerts() {
    try { budgetAlerts.value = (await api.post('/api/ai/check-budget')).data.alerts } catch {}
  }
  async function loadTrend(months = 6) {
    try { trendData.value = (await api.get(`/api/reports/trend?months=${months}`)).data } catch {}
  }
  async function loadWeekly(weeks = 4) {
    try { weeklyData.value = (await api.get(`/api/reports/weekly?weeks=${weeks}`)).data } catch {}
  }
  async function loadCompare() {
    if (!compareMonth1.value || !compareMonth2.value) return
    try {
      compareData.value = (await api.get(`/api/reports/compare?month1=${compareMonth1.value}&month2=${compareMonth2.value}`)).data
    } catch {}
  }
  async function loadSavingTips() {
    loadingTips.value = true
    try {
      savingTips.value = (await api.post('/api/ai/saving-tips')).data
      showToast('🔮 Khai Thị Tiết Kiệm đã đến!')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Không thể nhận khai thị (cần API key Gemini)', 'error')
    }
    loadingTips.value = false
  }

  // ─── CRUD ─────────────────────
  async function createTransaction() {
    if (!txnForm.value.amount || !txnForm.value.wallet_id || !txnForm.value.category_id) {
      showToast('Vui lòng điền đầy đủ thông tin!', 'error')
      return
    }
    loading.value = true
    try {
      await api.post('/api/transactions', txnForm.value)
      showToast('⚡ Giao dịch Linh Thạch đã ghi nhận!')
      txnForm.value = {
        transaction_type: 'EXPENSE', amount: 0, wallet_id: txnForm.value.wallet_id,
        category_id: null, transaction_date: todayStr(), note: ''
      }
      await refreshAfterTxnChange(true)
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch!', 'error')
    }
    loading.value = false
  }

  // Tải lại những dữ liệu phụ thuộc vào giao dịch (số dư ví, tổng quan, hạn mức, biểu đồ)
  async function refreshAfterTxnChange(resetPage = false) {
    await Promise.all([
      loadTransactions(resetPage), loadWallets(), loadSummary(),
      loadBudgets(), checkBudgetAlerts(), loadTrend(), loadWeekly(),
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
      showToast('Vui lòng điền đầy đủ thông tin hợp lệ!', 'error')
      return
    }
    loading.value = true
    try {
      await api.put(`/api/transactions/${f.id}`, {
        transaction_type: f.transaction_type,
        amount: Number(f.amount),
        wallet_id: f.wallet_id,
        category_id: f.category_id,
        transaction_date: f.transaction_date,
        note: f.note || ''
      })
      showToast('✨ Giao dịch đã được cập nhật!')
      showEditTxnModal.value = false
      await refreshAfterTxnChange()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi cập nhật giao dịch!', 'error')
    }
    loading.value = false
  }

  async function deleteTransaction(id) {
    if (!confirm('Xóa giao dịch này?')) return
    try {
      await api.delete(`/api/transactions/${id}`)
      showToast('Giao dịch đã xóa!')
      await refreshAfterTxnChange()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi xóa giao dịch!', 'error')
    }
  }

  async function createWallet() {
    if (!walletForm.value.wallet_name) {
      showToast('Vui lòng nhập tên ví!', 'error')
      return
    }
    loading.value = true
    try {
      await api.post('/api/wallets', walletForm.value)
      showToast('✨ Túi Càn Khôn mới đã khai mở!')
      walletForm.value = { wallet_name: '', balance: 0, wallet_type: 'cash' }
      await loadWallets()
      await loadSummary()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi tạo ví!', 'error')
    }
    loading.value = false
  }

  async function deleteWallet(id) {
    if (!confirm('Xóa ví này? (Chỉ xóa được ví chưa có giao dịch nào.)')) return
    try {
      await api.delete(`/api/wallets/${id}`)
      showToast('Ví đã xóa!')
      await Promise.all([loadWallets(), loadSummary(), loadDebts()])
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi xóa ví!', 'error')
    }
  }

  async function doTransfer() {
    if (!transferForm.value.from_wallet_id || !transferForm.value.to_wallet_id || !transferForm.value.amount) {
      showToast('Vui lòng điền đầy đủ thông tin chuyển tiền!', 'error')
      return
    }
    loading.value = true
    try {
      const { data } = await api.post('/api/wallets/transfer', transferForm.value)
      showToast(`⚡ ${data.message}`)
      transferForm.value = { from_wallet_id: null, to_wallet_id: null, amount: 0, note: '' }
      await Promise.all([loadWallets(), loadSummary(), loadWalletTransfers()])
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi chuyển tiền!', 'error')
    }
    loading.value = false
  }

  async function createCategory() {
    if (!catForm.value.category_name) {
      showToast('Vui lòng nhập tên danh mục!', 'error')
      return
    }
    loading.value = true
    try {
      await api.post('/api/categories', catForm.value)
      showToast('✨ Danh mục mới đã khai mở!')
      catForm.value = { category_name: '', category_type: 'EXPENSE', icon: '📦' }
      await loadCategories()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi!', 'error')
    }
    loading.value = false
  }

  async function deleteCategory(id) {
    if (!confirm('Xóa danh mục này?')) return
    try {
      await api.delete(`/api/categories/${id}`)
      showToast('Danh mục đã xóa!')
      await Promise.all([loadCategories(), loadBudgets(), checkBudgetAlerts()])
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi xóa danh mục!', 'error')
    }
  }

  async function createBudget() {
    if (!budgetForm.value.category_id || !budgetForm.value.limit_amount) {
      showToast('Vui lòng điền đầy đủ!', 'error')
      return
    }
    loading.value = true
    try {
      await api.post('/api/budgets', budgetForm.value)
      showToast('🎯 Hạn mức tu luyện đã thiết lập!')
      await loadBudgets()
      await checkBudgetAlerts()
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi!', 'error')
    }
    loading.value = false
  }

  async function deleteBudget(id) {
    if (!confirm('Xóa hạn mức này?')) return
    try {
      await api.delete(`/api/budgets/${id}`)
      showToast('Hạn mức đã xóa!')
      await Promise.all([loadBudgets(), checkBudgetAlerts()])
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi khi xóa hạn mức!', 'error')
    }
  }

  // ─── OCR ──────────────────────
  const OCR_MAX_BYTES = 8 * 1024 * 1024

  function setOCRFile(file) {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      showToast('Chỉ hỗ trợ file ảnh (JPG, PNG, WEBP...)!', 'error')
      return
    }
    if (file.size > OCR_MAX_BYTES) {
      showToast('Ảnh quá lớn (tối đa 8 MB)!', 'error')
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
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', ocrFile.value)
      const { data } = await api.post('/api/ai/scan-invoice', formData)
      ocrResult.value = data.data

      const defaultWallet = wallets.value.length ? wallets.value[0].id : null
      const defaultCat = expenseCategories.value.length ? expenseCategories.value[0].id : null
      ocrConfirmForm.value = {
        note: data.data.store_name || 'Chi tiêu từ hóa đơn',
        amount: data.data.total_amount || 0,
        transaction_date: data.data.date || todayStr(),
        wallet_id: defaultWallet,
        category_id: defaultCat,
        transaction_type: 'EXPENSE'
      }
      showToast('👁️ Linh Nhãn đã hoàn thành phân tích! Vui lòng kiểm tra và xác nhận.')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi OCR!', 'error')
    }
    loading.value = false
  }

  async function confirmOCRTransaction() {
    if (!ocrConfirmForm.value.amount || ocrConfirmForm.value.amount <= 0) {
      showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
      return
    }
    if (!ocrConfirmForm.value.wallet_id || !ocrConfirmForm.value.category_id) {
      showToast('Vui lòng chọn Túi Càn Khôn và Danh Mục Chi!', 'error')
      return
    }
    loading.value = true
    try {
      await api.post('/api/transactions', ocrConfirmForm.value)
      showToast('⚡ Giao dịch từ hóa đơn đã được thêm vào lịch sử!')
      ocrResult.value = null
      ocrFile.value = null
      ocrPreview.value = null
      await refreshAfterTxnChange(true)
      router.push({ name: 'transactions' })
    } catch (err) {
      showToast(err.response?.data?.detail || 'Lỗi lưu giao dịch!', 'error')
    }
    loading.value = false
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
    userEmail, loading, loadingTips, loadingProfile, loadingSoulLamp, errorMsg, toast, showProfileModal,
    profileForm, soulLampForm, showEditWalletModal, editWalletForm, showEditCatModal, editCatForm,
    showEditBudgetModal, editBudgetForm, showEditTxnModal, editTxnForm, showEditRecurringModal,
    editRecurringForm, userRole, currentUserId, tabs, adminStats, adminUsers, adminFilter, wallets,
    categories, transactions, budgets, summary, budgetAlerts, chatMessages, chatInput, suggestedQuestions,
    debts, debtsSummary, debtFilter, debtForm, showEditDebtModal, editDebtForm, savingGoals, goalsSummary,
    goalForm, showEditGoalModal, editGoalForm, showDepositModal, depositForm, showRecurringSection,
    recurringList, recurringForm, txnFilter, txnPagination, trendData, weeklyData, compareData, savingTips,
    compareMonth2, compareMonth1, budgetMonth, viLocale, statsDateRange, presetRanges, onStatsDateChange,
    txnForm, walletForm, catForm, budgetForm, transferForm, walletTransfers, goalLogs, ocrFile, ocrPreview,
    ocrResult, ocrConfirmForm, chatLoading, iconOptions, incomeCategories, expenseCategories,
    filteredCategories, editTxnCategories, maxCategoryExpense, totalPages, dashboardDoughnutData,
    dashboardBarData, trendBarData, weeklyLineData, hasTrendData, hasWeeklyData, statsDoughnutData,
    isUserAdmin, displayTabs, filteredAdminUsers, switchTheme, resetAllState, showToast, doLogin, doRegister,
    openForgotPassword, doForgotPassword, doResetPassword, doLogout, openProfileModal, saveProfile,
    saveSoulLamp, fetchUserProfile, loadAdminStats, loadAdminUsers, toggleUserActive, changeUserRole,
    loadAllData, loadChatHistory, loadSuggestedQuestions, loadWalletTransfers, loadGoalLogs, loadWallets,
    loadCategories, loadTransactions, changeTxnPage, resetTxnFilter, downloadReport, doExportReports,
    loadSavingGoals, createSavingGoal, openEditGoal, updateSavingGoal, openDepositGoal,
    submitDepositWithdrawGoal, deleteSavingGoal, loadRecurring, createRecurring, toggleRecurring,
    deleteRecurring, openEditRecurring, updateRecurring, openEditBudget, updateBudget, doExport,
    openEditWallet, updateWallet, openEditCategory, updateCategory, loadDebts, createDebt, openEditDebt,
    updateDebt, toggleSettleDebt, deleteDebt, getDebtStatus, loadSummary, loadBudgets, checkBudgetAlerts,
    loadTrend, loadWeekly, loadCompare, loadSavingTips, createTransaction, refreshAfterTxnChange, openEditTxn,
    updateTransaction, deleteTransaction, createWallet, deleteWallet, doTransfer, createCategory,
    deleteCategory, createBudget, deleteBudget, OCR_MAX_BYTES, setOCRFile, handleOCRUpload, handleOCRDrop,
    scanInvoice, confirmOCRTransaction, sendChat, switchTab, restoreSession, toLocalDateStr, todayStr,
    toLocalMonthStr, escapeHtml, formatChatText, formatVND, budgetPct, walletTypeIcon,
  }
})
