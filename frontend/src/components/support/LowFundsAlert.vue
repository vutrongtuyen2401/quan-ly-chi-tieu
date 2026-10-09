<template>
  <div
    v-if="isVisible"
    class="low-funds-alert-strip"
    :class="alertClass"
    role="region"
    aria-live="polite"
    aria-labelledby="low-funds-title"
  >
    <!-- Background Glow Effect -->
    <div class="alert-strip-glow" aria-hidden="true"></div>

    <!-- ═══ HEADER ROW: Icon + Titles + Summary + Dismiss Button ═══ -->
    <div class="alert-header-row">
      <div class="alert-title-wrap">
        <div class="alert-icon-box" aria-hidden="true">
          <span class="material-symbols-outlined text-[24px]">
            {{ isCritical ? 'warning' : 'info' }}
          </span>
        </div>
        <div class="alert-titles">
          <div class="title-with-badge">
            <h2 id="low-funds-title" class="alert-main-title">Linh Thạch Sắp Cạn</h2>
            <span class="level-badge" :class="isCritical ? 'badge-critical' : 'badge-warning'">
              {{ isCritical ? 'Linh thạch cạn kiệt' : 'Linh thạch hao hụt' }}
            </span>
          </div>
          <p class="alert-summary-line">
            Còn <strong class="text-amount">{{ displayTotalBalance }}</strong>
            <template v-if="status.runway_days != null">
              · đủ khoảng <strong>{{ status.runway_days }} ngày</strong>
            </template>
            · còn <strong>{{ status.days_left }} ngày</strong> tới {{ displayAllowanceDate }}
            · nên xin thêm khoảng <strong class="text-suggested">{{ displaySuggestedAmount }}</strong>
          </p>
        </div>
      </div>

      <!-- Actions: Đã nhận tiền + Để sau -->
      <div class="alert-header-actions">
        <!-- Nút phụ: Đã nhận tiền → Ghi khoản thu -->
        <button
          type="button"
          class="btn-record-income"
          title="Đã nhận tiền hỗ trợ từ người thân, mở sổ ghi khoản thu"
          @click="$emit('record-income')"
        >
          <span class="material-symbols-outlined text-[18px]">payments</span>
          <span class="record-income-label">Đã nhận tiền → Ghi khoản thu</span>
        </button>

        <!-- Action: Để Sau (Snooze) -->
        <button
          type="button"
          class="btn-dismiss"
          title="Để sau (ẩn cảnh báo tới hết hôm nay)"
          aria-label="Để sau"
          @click="$emit('dismiss')"
        >
          <span class="material-symbols-outlined text-[18px]">alarm_off</span>
          <span class="dismiss-label">Để sau</span>
        </button>
      </div>
    </div>

    <!-- ═══ REASONS SECTION ═══ -->
    <div v-if="status.reasons && status.reasons.length > 0" class="alert-reasons-wrap">
      <div class="reasons-label">
        <span class="material-symbols-outlined text-[15px]">analytics</span>
        <span>Nguyên nhân và phân tích số liệu:</span>
      </div>
      <ul class="reasons-list">
        <li v-for="(reason, idx) in status.reasons" :key="idx" class="reason-item">
          <span class="reason-bullet" aria-hidden="true">•</span>
          <span>{{ reason }}</span>
        </li>
      </ul>
    </div>

    <!-- ═══ CONTACTS SECTION: Danh Bạ Hộ Đạo Gợi Ý ═══ -->
    <div class="alert-contacts-section">
      <div class="contacts-section-header">
        <div class="section-title-wrap">
          <span class="material-symbols-outlined text-[18px]">ring_volume</span>
          <span class="contacts-section-title">Người thân hỗ trợ (Danh Bạ Hộ Đạo):</span>
        </div>
        <button
          type="button"
          class="btn-manage-contacts"
          @click="$emit('open-contacts')"
        >
          <span class="material-symbols-outlined text-[16px]">edit_note</span>
          <span>Quản lý danh bạ</span>
        </button>
      </div>

      <!-- TRƯỜNG HỢP A: Đã có người thân trong danh bạ -->
      <div v-if="status.contacts && status.contacts.length > 0" class="contacts-table-wrap">
        <div
          v-for="contact in status.contacts"
          :key="contact.id"
          class="contact-item-row"
        >
          <!-- Cột thông tin người thân -->
          <div class="contact-identity">
            <span class="contact-name">{{ contact.contact_name }}</span>
            <span class="contact-rel-badge">{{ contact.relationship_label || 'Người thân' }}</span>
            <span class="contact-phone">{{ formatPhoneDisplay(contact.phone) }}</span>
            <span v-if="contact.note" class="contact-note" :title="contact.note">
              ({{ contact.note }})
            </span>
          </div>

          <!-- Cột nút tương tác nhanh: Gọi, Nhắn tin, Sao chép -->
          <div class="contact-actions">
            <!-- Nút Gọi Điện (tel:) -->
            <a
              :href="'tel:' + contact.phone"
              class="btn-call"
              title="Gọi ngay"
              :aria-label="'Gọi cho ' + contact.contact_name"
            >
              <span class="material-symbols-outlined text-[18px]">call</span>
              <span>Gọi</span>
            </a>

            <!-- Nút Nhắn Tin (sms: kèm nội dung soạn sẵn) -->
            <a
              :href="'sms:' + contact.phone + (contact.message ? '?body=' + encodeURIComponent(contact.message) : '')"
              class="btn-sms"
              title="Gửi tin nhắn soạn sẵn"
              :aria-label="'Nhắn tin cho ' + contact.contact_name"
            >
              <span class="material-symbols-outlined text-[18px]">chat</span>
              <span>Nhắn tin</span>
            </a>

            <!-- Nút Sao Chép SĐT -->
            <button
              type="button"
              class="btn-copy"
              :title="'Sao chép số: ' + contact.phone"
              @click="copyText(contact.phone, 'phone_' + contact.id)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ copiedState['phone_' + contact.id] ? 'done' : 'content_copy' }}
              </span>
              <span>{{ copiedState['phone_' + contact.id] ? 'Đã chép số' : 'Sao chép số' }}</span>
            </button>

            <!-- Nút Sao Chép Lời Nhắn -->
            <button
              v-if="contact.message"
              type="button"
              class="btn-copy-msg"
              title="Sao chép nội dung lời nhắn xin hỗ trợ"
              @click="copyText(contact.message, 'msg_' + contact.id)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ copiedState['msg_' + contact.id] ? 'done' : 'assignment' }}
              </span>
              <span>{{ copiedState['msg_' + contact.id] ? 'Đã chép lời nhắn' : 'Sao chép lời nhắn' }}</span>
            </button>

            <!-- Toggle xem trước tin nhắn -->
            <button
              v-if="contact.message"
              type="button"
              class="btn-preview-toggle"
              :title="expandedMsgs[contact.id] ? 'Thu gọn lời nhắn' : 'Xem trước lời nhắn'"
              @click="toggleMessagePreview(contact.id)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ expandedMsgs[contact.id] ? 'expand_less' : 'visibility' }}
              </span>
            </button>
          </div>

          <!-- Lời nhắn soạn sẵn mở rộng (preview) -->
          <div v-if="expandedMsgs[contact.id]" class="message-preview-bubble">
            <div class="bubble-header">
              <span class="material-symbols-outlined text-[15px]">sms</span>
              <span>Lời nhắn soạn sẵn:</span>
            </div>
            <p class="bubble-body">{{ contact.message }}</p>
          </div>
        </div>
      </div>

      <!-- TRƯỜNG HỢP B: Chưa có người thân nào trong danh bạ -->
      <div v-else class="contacts-empty-banner">
        <div class="empty-icon-box">
          <span class="material-symbols-outlined text-[20px]">person_off</span>
        </div>
        <div class="empty-meta">
          <p class="empty-title">Bạn chưa lưu số người thân nào trong Danh Bạ Hộ Đạo</p>
          <p class="empty-desc">
            Hãy thêm số của phụ huynh hoặc người thân để được hỗ trợ gọi hoặc gửi tin nhắn xin thêm linh thạch khi cần.
          </p>
        </div>
        <button
          type="button"
          class="btn-add-contact-now"
          @click="$emit('open-contacts')"
        >
          <span class="material-symbols-outlined text-[18px]">person_add</span>
          <span>Thêm Người Thân Ngay</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  status: {
    type: Object,
    default: null,
  },
  formatVND: {
    type: Function,
    default: null,
  },
})

defineEmits(['open-contacts', 'dismiss', 'record-income'])

// ═══ VISIBILITY COMPUTED ═══
const isVisible = computed(() => {
  if (!props.status) return false
  if (!props.status.enabled) return false
  if (props.status.level !== 'WARNING' && props.status.level !== 'CRITICAL') return false
  return true
})

const isCritical = computed(() => {
  return props.status?.level === 'CRITICAL'
})

const alertClass = computed(() => {
  return isCritical.value ? 'alert-critical' : 'alert-warning'
})

// ═══ FORMATTING HELPERS ═══
function formatMoney(amount) {
  if (props.formatVND && typeof props.formatVND === 'function') {
    return props.formatVND(amount)
  }
  const val = Number(amount) || 0
  return val.toLocaleString('vi-VN') + ' ₫'
}

const displayTotalBalance = computed(() => {
  return formatMoney(props.status?.total_balance ?? 0)
})

const displaySuggestedAmount = computed(() => {
  return formatMoney(props.status?.suggested_amount ?? 0)
})

const displayAllowanceDate = computed(() => {
  const dateStr = props.status?.next_allowance_date
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}`
  }
  return dateStr
})

function formatPhoneDisplay(raw) {
  if (!raw) return ''
  const str = String(raw).trim()
  if (str.length === 10 && str.startsWith('0')) {
    return `${str.slice(0, 4)} ${str.slice(4, 7)} ${str.slice(7)}`
  }
  return str
}

// ═══ CLIPBOARD & PREVIEW INTERACTION ═══
const copiedState = ref({})
const expandedMsgs = ref({})

async function copyText(text, key) {
  if (!text) return
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      // Fallback cho trình duyệt cũ
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.focus()
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    copiedState.value[key] = true
    setTimeout(() => {
      copiedState.value[key] = false
    }, 2000)
  } catch (err) {
    console.warn('Không thể sao chép văn bản:', err)
  }
}

function toggleMessagePreview(contactId) {
  expandedMsgs.value[contactId] = !expandedMsgs.value[contactId]
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   LOW FUNDS ALERT STRIP — THIẾT KẾ ĐƠN DẢI, KHÔNG CARD LỒNG CARD
   ═══════════════════════════════════════════════════════════════════════════ */
.low-funds-alert-strip {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg, 16px);
  margin-bottom: 1.5rem;
  padding: 1.25rem 1.5rem;
  transition: all 0.25s ease;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.alert-strip-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  opacity: 0.12;
  z-index: 0;
}

/* ─── VARIANT: WARNING (Linh Thạch Hao Hụt - Vàng) ─── */
.alert-warning {
  background: linear-gradient(
    135deg,
    rgba(34, 42, 61, 0.95) 0%,
    rgba(23, 31, 51, 0.98) 100%
  );
  border: 1px solid rgba(227, 195, 112, 0.35);
  border-left: 5px solid var(--color-tertiary, #e3c370);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 16px rgba(227, 195, 112, 0.12);
}

.alert-warning .alert-icon-box {
  background: rgba(227, 195, 112, 0.15);
  color: var(--color-tertiary, #e3c370);
  border: 1px solid rgba(227, 195, 112, 0.4);
}

.alert-warning .badge-warning {
  background: rgba(227, 195, 112, 0.15);
  color: var(--color-tertiary-fixed, #ffe08f);
  border: 1px solid rgba(227, 195, 112, 0.4);
}

.alert-warning .text-suggested {
  color: var(--color-tertiary, #e3c370);
}

/* ─── VARIANT: CRITICAL (Linh Thạch Cạn Kiệt - Đỏ) ─── */
.alert-critical {
  background: linear-gradient(
    135deg,
    rgba(45, 26, 32, 0.95) 0%,
    rgba(23, 31, 51, 0.98) 100%
  );
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-left: 5px solid var(--color-error-tribulation, #ef4444);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), 0 0 20px rgba(239, 68, 68, 0.16);
}

.alert-critical .alert-icon-box {
  background: rgba(239, 68, 68, 0.18);
  color: #ff8577;
  border: 1px solid rgba(239, 68, 68, 0.45);
}

.alert-critical .badge-critical {
  background: rgba(239, 68, 68, 0.18);
  color: #ffdad6;
  border: 1px solid rgba(239, 68, 68, 0.45);
}

.alert-critical .text-suggested {
  color: #ff8577;
}

/* ═══ HEADER ROW ═══ */
.alert-header-row {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.alert-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  flex: 1;
}

.alert-icon-box {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md, 12px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-titles {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.alert-main-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
  line-height: 1.3;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.alert-summary-line {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  line-height: 1.5;
}

.alert-summary-line strong {
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.alert-summary-line .text-amount {
  color: var(--color-on-surface, #ffffff);
}

/* Header Action Group */
.alert-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex-shrink: 0;
}

/* Nút phụ: Đã nhận tiền → Ghi khoản thu */
.btn-record-income {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 44px;
  padding: 0.5rem 0.875rem;
  background: rgba(4, 108, 70, 0.22);
  border: 1px solid rgba(79, 168, 160, 0.45);
  border-radius: var(--radius-md, 12px);
  color: #5ed6ca;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-record-income:hover {
  background: rgba(4, 108, 70, 0.4);
  border-color: #6ed0c5;
  color: #a7f3ec;
  transform: translateY(-1px);
}

/* Nút Để Sau (Dismiss) */
.btn-dismiss {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 44px;
  padding: 0.5rem 0.875rem;
  background: rgba(45, 52, 73, 0.6);
  border: 1px solid rgba(136, 147, 145, 0.3);
  border-radius: var(--radius-md, 12px);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-dismiss:hover {
  background: rgba(45, 52, 73, 0.95);
  color: var(--color-on-surface, #dae2fd);
  border-color: var(--color-outline, #889391);
}

/* ═══ REASONS SECTION ═══ */
.alert-reasons-wrap {
  position: relative;
  z-index: 1;
  margin-top: 0.875rem;
  padding: 0.75rem 1rem;
  background: rgba(11, 19, 38, 0.55);
  border-radius: var(--radius-md, 10px);
  border: 1px solid rgba(62, 73, 71, 0.35);
}

.reasons-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-outline, #889391);
  margin-bottom: 0.35rem;
}

.reasons-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.reason-item {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  font-size: 0.84rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  line-height: 1.45;
}

.reason-bullet {
  color: var(--color-outline, #889391);
  font-weight: bold;
}

/* ═══ CONTACTS SECTION ═══ */
.alert-contacts-section {
  position: relative;
  z-index: 1;
  margin-top: 1rem;
  padding-top: 0.875rem;
  border-top: 1px dashed rgba(62, 73, 71, 0.45);
}

.contacts-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--color-primary, #7dd6cc);
}

.contacts-section-title {
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.btn-manage-contacts {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.65rem;
  background: transparent;
  border: 1px solid rgba(125, 214, 204, 0.3);
  border-radius: var(--radius-sm, 8px);
  color: var(--color-primary, #7dd6cc);
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-manage-contacts:hover {
  background: rgba(125, 214, 204, 0.12);
  border-color: var(--color-primary, #7dd6cc);
}

/* Contacts Table Wrap */
.contacts-table-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.contact-item-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(11, 19, 38, 0.6);
  border: 1px solid rgba(62, 73, 71, 0.35);
  border-radius: var(--radius-md, 10px);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.contact-item-row:hover {
  background: rgba(11, 19, 38, 0.85);
  border-color: rgba(125, 214, 204, 0.3);
}

@media (min-width: 768px) {
  .contact-item-row {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.contact-identity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.contact-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.contact-rel-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: rgba(196, 193, 251, 0.15);
  color: var(--color-secondary-fixed, #e3dfff);
  border: 1px solid rgba(196, 193, 251, 0.3);
}

.contact-phone {
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--color-primary, #7dd6cc);
  font-weight: 500;
}

.contact-note {
  font-size: 0.78rem;
  color: var(--color-outline, #889391);
  font-style: italic;
}

.contact-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

/* Action Buttons (≥ 44px height tap target friendly) */
.btn-call,
.btn-sms,
.btn-copy,
.btn-copy-msg,
.btn-preview-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-height: 44px;
  padding: 0.45rem 0.75rem;
  border-radius: var(--radius-sm, 8px);
  font-size: 0.82rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  border: none;
}

/* Call Button */
.btn-call {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.45);
}

.btn-call:hover {
  background: rgba(16, 185, 129, 0.32);
  color: #6ee7b7;
  border-color: #10b981;
}

/* SMS Button */
.btn-sms {
  background: rgba(68, 159, 150, 0.2);
  color: var(--color-primary, #7dd6cc);
  border: 1px solid rgba(125, 214, 204, 0.4);
}

.btn-sms:hover {
  background: rgba(68, 159, 150, 0.35);
  color: #a7f3d0;
  border-color: var(--color-primary, #7dd6cc);
}

/* Copy Buttons */
.btn-copy,
.btn-copy-msg {
  background: rgba(45, 52, 73, 0.6);
  color: var(--color-on-surface-variant, #bdc9c6);
  border: 1px solid rgba(136, 147, 145, 0.25);
}

.btn-copy:hover,
.btn-copy-msg:hover {
  background: rgba(45, 52, 73, 0.95);
  color: var(--color-on-surface, #dae2fd);
  border-color: var(--color-outline, #889391);
}

.btn-preview-toggle {
  min-width: 44px;
  padding: 0.45rem;
  background: rgba(45, 52, 73, 0.4);
  color: var(--color-outline, #889391);
  border: 1px solid rgba(136, 147, 145, 0.2);
}

.btn-preview-toggle:hover {
  color: var(--color-on-surface, #dae2fd);
  background: rgba(45, 52, 73, 0.8);
}

/* Message Preview Bubble */
.message-preview-bubble {
  width: 100%;
  margin-top: 0.35rem;
  padding: 0.65rem 0.85rem;
  background: rgba(6, 14, 32, 0.7);
  border-radius: var(--radius-sm, 8px);
  border-left: 3px solid var(--color-primary, #7dd6cc);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
}

.bubble-body {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-on-surface, #dae2fd);
  line-height: 1.45;
  font-style: italic;
}

/* Empty Contacts Banner */
.contacts-empty-banner {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.875rem 1rem;
  background: rgba(11, 19, 38, 0.55);
  border: 1px dashed rgba(136, 147, 145, 0.3);
  border-radius: var(--radius-md, 10px);
  flex-wrap: wrap;
}

.empty-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(136, 147, 145, 0.12);
  color: var(--color-outline, #889391);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.empty-meta {
  flex: 1;
  min-width: 220px;
}

.empty-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.empty-desc {
  margin: 0.15rem 0 0 0;
  font-size: 0.8rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  line-height: 1.4;
}

.btn-add-contact-now {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 44px;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, var(--color-primary-core, #2b8a82), var(--color-primary, #7dd6cc));
  color: #00201d;
  border: none;
  border-radius: var(--radius-md, 10px);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(125, 214, 204, 0.25);
  flex-shrink: 0;
}

.btn-add-contact-now:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

/* Mobile Adjustments */
@media (max-width: 640px) {
  .low-funds-alert-strip {
    padding: 1rem;
  }
  .alert-header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  .record-income-label {
    font-size: 0.8rem;
  }
  .dismiss-label {
    display: none;
  }
  .btn-dismiss {
    min-width: 44px;
    padding: 0.5rem;
    justify-content: center;
  }
  .contact-actions {
    width: 100%;
    justify-content: flex-start;
  }
  .btn-add-contact-now {
    width: 100%;
    justify-content: center;
  }
}
</style>
