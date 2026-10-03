/** Tổng quan, biểu đồ, so sánh tháng, gợi ý tiết kiệm AI và xuất báo cáo. */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { vi } from 'date-fns/locale'
import api from '../api'
import { toLocalDateStr, todayStr, toLocalMonthStr } from '../utils/format'
import { useSessionStore } from './session'
import { useTransactionStore } from './transactions'

export const useReportStore = defineStore('reports', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const session = useSessionStore()
  const txnStore = useTransactionStore()

  const loadingTips = ref(false)
  const summary = ref({ total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] })

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
  const maxCategoryExpense = computed(() => {
    if (!summary.value.expense_by_category?.length) return 1
    return Math.max(...summary.value.expense_by_category.map(c => c.total), 1)
  })

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

  // Change 7: Export reports (CSV / Excel)
  // Tải file báo cáo CSV / Excel trong khoảng ngày (dùng chung cho tab Giao Dịch & Thống Kê)
  async function downloadReport(format, startDate, endDate) {
    try {
      session.showToast(`⏳ Đang kết xuất báo cáo ${format.toUpperCase()}...`)
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
      session.showToast(`📥 Xuất báo cáo ${format.toUpperCase()} thành công!`)
    } catch (err) {
      session.showToast('Lỗi khi xuất file báo cáo!', 'error')
    }
  }

  function doExportReports(format = 'excel') {
    return downloadReport(format, txnStore.txnFilter.start_date, txnStore.txnFilter.end_date)
  }

  function doExport(format) {
    const range = statsDateRange.value
    if (range && range[0] && range[1]) {
      return downloadReport(format, toLocalDateStr(range[0]), toLocalDateStr(range[1]))
    }
    return downloadReport(format)
  }

  async function loadSummary(monthYear = null) {
    let url = '/api/reports/summary'
    if (monthYear) url += `?month_year=${monthYear}`
    try { summary.value = (await api.get(url)).data } catch {}
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
      session.showToast('🔮 Khai Thị Tiết Kiệm đã đến!')
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Không thể nhận khai thị (cần API key Gemini)', 'error')
    }
    loadingTips.value = false
  }

  return {
    summary, trendData, weeklyData, compareData, savingTips, loadingTips, compareMonth2, compareMonth1,
    viLocale, statsDateRange, presetRanges, onStatsDateChange, maxCategoryExpense, dashboardDoughnutData,
    dashboardBarData, trendBarData, weeklyLineData, hasTrendData, hasWeeklyData, statsDoughnutData,
    loadSummary, loadTrend, loadWeekly, loadCompare, loadSavingTips, doExport, downloadReport,
    doExportReports,
  }
})
