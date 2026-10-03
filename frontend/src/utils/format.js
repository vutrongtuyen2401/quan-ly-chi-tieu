/** Hàm định dạng / tiện ích thuần — dùng chung cho store và các view. */

// Ngày theo giờ địa phương (toISOString() trả về giờ UTC → trước 7h sáng ở VN sẽ lệch sang hôm qua)
export function toLocalDateStr(d) {
  const date = d instanceof Date ? d : new Date(d)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

export function todayStr() {
  return toLocalDateStr(new Date())
}

export function toLocalMonthStr(d) {
  return toLocalDateStr(d).slice(0, 7)
}

export function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

export function formatChatText(text) {
  if (!text) return ''
  // Escape trước khi chuyển markdown → HTML để chặn XSS qua v-html
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>')
}

export function formatVND(val) {
  if (val === undefined || val === null) return '0 ₫'
  return Number(val).toLocaleString('vi-VN') + ' ₫'
}

export function budgetPct(b) {
  return b.limit_amount > 0 ? (b.spent / b.limit_amount * 100) : 0
}

export function walletTypeIcon(type) {
  return type === 'cash' ? '💵' : type === 'bank' ? '🏦' : '📱'
}
