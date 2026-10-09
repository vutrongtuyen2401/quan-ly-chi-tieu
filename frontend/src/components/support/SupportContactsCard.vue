<template>
  <div class="support-contacts-card">
    <div class="card-ambient-glow" aria-hidden="true"></div>

    <!-- ═══ HEADER ROW ═══ -->
    <div class="card-header-row">
      <div class="card-title-group">
        <div class="support-icon-box">
          <span class="material-symbols-outlined text-[22px]" aria-hidden="true">contact_phone</span>
        </div>
        <div class="title-meta">
          <h2 class="card-title">Danh Bạ Hộ Đạo (Truyền Âm Cầu Viện)</h2>
          <span class="card-subtitle">Người thân có thể hỗ trợ khi linh thạch sắp cạn</span>
        </div>
      </div>

      <div class="header-action-wrap">
        <span class="count-badge">
          {{ contacts.length }}/10 Người
        </span>
        <button
          v-if="contacts.length < 10 && !showAddForm"
          type="button"
          class="btn-add-contact"
          @click="openAddForm"
        >
          <span class="material-symbols-outlined text-[18px]">person_add</span>
          <span>Thêm Người Thân</span>
        </button>
      </div>
    </div>

    <!-- Description -->
    <p class="card-description">
      Lưu số điện thoại của phụ huynh hoặc người thân hỗ trợ. Khi linh thạch chạm đáy hoặc không đủ tới ngày nhận tiền tiếp theo, hệ thống sẽ gợi ý liên lạc xin viện trợ kịp thời.
    </p>

    <!-- ═══ ADD / EDIT CONTACT FORM ═══ -->
    <div v-if="showAddForm" class="contact-form-panel">
      <div class="form-panel-header">
        <span class="form-panel-title">
          <span class="material-symbols-outlined text-[18px]">
            {{ editingId ? 'edit' : 'person_add' }}
          </span>
          <span>{{ editingId ? 'Chỉnh Sửa Người Thân' : 'Thêm Người Thân Mới' }}</span>
        </span>
        <button type="button" class="btn-close-form" @click="cancelForm">✕</button>
      </div>

      <div v-if="formError" class="form-error-banner" role="alert">
        <span class="material-symbols-outlined text-[16px]">error</span>
        <span>{{ formError }}</span>
      </div>

      <form class="contact-inner-form" @submit.prevent="handleSubmitContact">
        <div class="form-row-grid">
          <!-- Tên người thân -->
          <div class="form-field">
            <label class="field-label" for="contact-name">
              <span>Họ Tên / Xưng Hô</span>
              <span class="field-required">*</span>
            </label>
            <input
              id="contact-name"
              v-model="contactForm.contact_name"
              type="text"
              class="stitch-input"
              placeholder="Ví dụ: Mẹ Yêu, Bố, Anh Cả..."
              maxlength="50"
              required
            />
          </div>

          <!-- Mối quan hệ -->
          <div class="form-field">
            <label class="field-label" for="contact-relationship">
              <span>Mối Quan Hệ</span>
              <span class="field-required">*</span>
            </label>
            <select
              id="contact-relationship"
              v-model="contactForm.relationship"
              class="stitch-input select-dark"
              required
            >
              <option v-for="opt in relationshipOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-row-grid">
          <!-- Số điện thoại -->
          <div class="form-field">
            <label class="field-label" for="contact-phone">
              <span>Số Điện Thoại</span>
              <span class="field-required">*</span>
            </label>
            <input
              id="contact-phone"
              v-model="contactForm.phone"
              type="tel"
              inputmode="tel"
              class="stitch-input font-mono"
              placeholder="Ví dụ: 0912 345 678 hoặc +849..."
              required
            />
          </div>

          <!-- Độ ưu tiên -->
          <div class="form-field">
            <label class="field-label" for="contact-priority">
              <span>Độ Ưu Tiên</span>
              <span class="field-hint">(Số nhỏ hiện trước: 1, 2, 3...)</span>
            </label>
            <input
              id="contact-priority"
              v-model.number="contactForm.priority"
              type="number"
              class="stitch-input"
              min="1"
              max="99"
            />
          </div>
        </div>

        <!-- Ghi chú -->
        <div class="form-field">
          <label class="field-label" for="contact-note">
            <span>Ghi Chú Nhắc Nhở</span>
            <span class="field-hint">(Tối đa 200 ký tự)</span>
          </label>
          <input
            id="contact-note"
            v-model="contactForm.note"
            type="text"
            class="stitch-input"
            placeholder="Ví dụ: Thường rảnh sau 19h tối..."
            maxlength="200"
          />
        </div>

        <!-- Form Actions -->
        <div class="form-actions-row">
          <button type="button" class="btn-cancel" @click="cancelForm">
            Hủy Bỏ
          </button>
          <button type="submit" class="btn-submit-contact" :disabled="loading">
            <span class="material-symbols-outlined text-[18px]">
              {{ editingId ? 'check_circle' : 'save' }}
            </span>
            <span>{{ editingId ? 'Lưu Thay Đổi' : 'Xác Nhận Thêm' }}</span>
          </button>
        </div>
      </form>
    </div>

    <!-- ═══ CONTACT LIST (ROW-BASED, NO NESTED CARDS) ═══ -->
    <div class="contacts-list-container">
      <div v-if="contacts.length === 0" class="contacts-empty-state">
        <span class="material-symbols-outlined empty-icon">contact_support</span>
        <p class="empty-text">
          Chưa có người thân nào. Thêm số bố mẹ hoặc người thân để được gợi ý gọi khi sắp hết tiền.
        </p>
        <button
          v-if="!showAddForm"
          type="button"
          class="btn-add-contact-empty"
          @click="openAddForm"
        >
          <span class="material-symbols-outlined text-[18px]">person_add</span>
          <span>+ Thêm Người Thân Ngay</span>
        </button>
      </div>

      <div v-else class="contacts-rows-wrapper">
        <div
          v-for="c in sortedContacts"
          :key="c.id"
          class="contact-row-item"
          :class="{ 'row-inactive': !c.is_active }"
        >
          <!-- Left: Relationship badge & Priority -->
          <div class="row-left-meta">
            <span class="priority-badge" :title="'Độ ưu tiên: ' + c.priority">
              #{{ c.priority }}
            </span>
            <span class="relation-pill" :class="getRelationClass(c.relationship)">
              <span class="material-symbols-outlined relation-icon">
                {{ getRelationIcon(c.relationship) }}
              </span>
              <span>{{ getRelationLabel(c.relationship) }}</span>
            </span>
          </div>

          <!-- Middle: Name, Phone & Note -->
          <div class="row-info-col">
            <div class="row-name-line">
              <span class="contact-name-text">{{ c.contact_name }}</span>
              <span class="contact-phone-text font-mono">{{ formatDisplayPhone(c.phone) }}</span>
            </div>
            <div v-if="c.note" class="contact-note-line">
              <span class="material-symbols-outlined text-[14px]">info</span>
              <span>{{ c.note }}</span>
            </div>
          </div>

          <!-- Right: Actions & Toggle Switch -->
          <div class="row-actions-group">
            <!-- Toggle active switch -->
            <label class="switch-toggle" :title="c.is_active ? 'Đang bật cảnh báo' : 'Đang tạm tắt'">
              <input
                type="checkbox"
                :checked="Boolean(c.is_active)"
                @change="handleToggleActive(c)"
              />
              <span class="slider-round"></span>
            </label>

            <!-- Edit button -->
            <button
              type="button"
              class="btn-row-action btn-edit"
              title="Chỉnh sửa thông tin"
              @click="openEditForm(c)"
            >
              <span class="material-symbols-outlined text-[18px]">edit</span>
            </button>

            <!-- Delete button -->
            <button
              type="button"
              class="btn-row-action btn-delete"
              title="Xóa người thân"
              @click="handleDeleteContact(c)"
            >
              <span class="material-symbols-outlined text-[18px]">delete</span>
            </button>
          </div>
        </div>

        <div v-if="contacts.length >= 10" class="max-contacts-notice">
          <span class="material-symbols-outlined text-[16px]">info</span>
          <span>Đã đạt tối đa 10 người thân trong Danh Bạ Hộ Đạo.</span>
        </div>
      </div>
    </div>

    <!-- ═══ SETTINGS ACCORDION / PANEL ═══ -->
    <div class="support-settings-section">
      <button
        type="button"
        class="settings-toggle-bar"
        @click="showSettingsPanel = !showSettingsPanel"
      >
        <div class="toggle-bar-left">
          <span class="material-symbols-outlined text-[20px] text-primary">tune</span>
          <span class="settings-bar-title">Cài Đặt Cảnh Báo Linh Thạch Sắp Cạn</span>
        </div>
        <span class="material-symbols-outlined chevron-icon" :class="{ 'chevron-rotated': showSettingsPanel }">
          expand_more
        </span>
      </button>

      <div v-if="showSettingsPanel" class="settings-body-panel">
        <form @submit.prevent="handleSaveSettings">
          <!-- Bật / Tắt chức năng cảnh báo -->
          <div class="settings-field-row">
            <div class="field-meta">
              <span class="setting-title">Kích Hoạt Cảnh Báo Sắp Cạn</span>
              <span class="setting-desc">Tự động hiện banner hỗ trợ ở Tổng Quan khi có dấu hiệu thiếu hụt</span>
            </div>
            <label class="switch-toggle">
              <input type="checkbox" v-model="localSettings.enabled" />
              <span class="slider-round"></span>
            </label>
          </div>

          <!-- Ngưỡng số dư cảnh báo -->
          <div class="settings-form-grid">
            <div class="form-field">
              <label class="field-label" for="setting-threshold">
                <span>Ngưỡng Cảnh Báo Số Dư (₫)</span>
                <span class="field-hint">Mặc định: 500.000 ₫</span>
              </label>
              <div class="input-with-currency">
                <input
                  id="setting-threshold"
                  v-model.number="localSettings.low_balance_threshold"
                  type="number"
                  class="stitch-input font-mono"
                  min="0"
                  max="1000000000"
                  step="50000"
                  required
                />
                <span class="currency-tag">VNĐ</span>
              </div>
              <div class="threshold-preview" v-if="formatVND">
                Tương đương: <strong class="text-primary">{{ formatVND(localSettings.low_balance_threshold || 0) }}</strong>
              </div>
            </div>

            <!-- Ngày nhận tiền chu cấp hằng tháng -->
            <div class="form-field">
              <label class="field-label" for="setting-allowance-day">
                <span>Ngày Nhận Tiền Hằng Tháng</span>
                <span class="field-hint">(Từ ngày 1 đến 28)</span>
              </label>
              <div class="select-wrapper">
                <select
                  id="setting-allowance-day"
                  v-model.number="localSettings.allowance_day"
                  class="stitch-input select-dark"
                  required
                >
                  <option v-for="day in 28" :key="day" :value="day">
                    Ngày {{ day }} {{ day === 1 ? '(Đầu tháng)' : day === 15 ? '(Giữa tháng)' : '' }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- Mẫu tin nhắn soạn sẵn -->
          <div class="form-field">
            <div class="template-label-row">
              <label class="field-label" for="setting-template">
                <span>Mẫu Lời Nhắn Soạn Sẵn (SMS)</span>
              </label>
              <button
                type="button"
                class="btn-reset-template"
                @click="resetMessageTemplate"
                title="Sử dụng mẫu mặc định của tông môn"
              >
                <span class="material-symbols-outlined text-[14px]">restart_alt</span>
                <span>Dùng Mẫu Mặc Định</span>
              </button>
            </div>
            <textarea
              id="setting-template"
              v-model="localSettings.message_template"
              class="stitch-input template-textarea"
              rows="3"
              maxlength="500"
              :placeholder="defaultTemplateHint"
            ></textarea>
            <div class="template-placeholders-hint">
              <span>Các biến số có thể dùng:</span>
              <code class="code-tag">{xung_ho}</code>
              <code class="code-tag">{so_du}</code>
              <code class="code-tag">{so_ngay}</code>
              <code class="code-tag">{so_tien}</code>
            </div>
          </div>

          <!-- Save Settings Action -->
          <div class="settings-actions-row">
            <button type="submit" class="btn-save-settings" :disabled="loading">
              <span class="material-symbols-outlined text-[18px]">tune</span>
              <span>Lưu Cài Đặt Cảnh Báo</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'SupportContactsCard',
  props: {
    contacts: {
      type: Array,
      default: () => []
    },
    settings: {
      type: Object,
      default: () => ({
        enabled: true,
        low_balance_threshold: 500000,
        allowance_day: 1,
        message_template: ''
      })
    },
    loading: {
      type: Boolean,
      default: false
    },
    formatVND: {
      type: Function,
      default: (val) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0)
    }
  },
  emits: [
    'create-contact',
    'update-contact',
    'delete-contact',
    'toggle-contact',
    'save-settings'
  ],
  setup(props, { emit }) {
    const showAddForm = ref(false)
    const editingId = ref(null)
    const formError = ref('')
    const showSettingsPanel = ref(false)

    // Form data with all fields initialized
    const contactForm = ref({
      contact_name: '',
      relationship: 'MOTHER',
      phone: '',
      priority: 1,
      note: ''
    })

    // Local clone of settings to avoid direct prop mutation
    const localSettings = ref({
      enabled: props.settings?.enabled ?? true,
      low_balance_threshold: props.settings?.low_balance_threshold ?? 500000,
      allowance_day: props.settings?.allowance_day ?? 1,
      message_template: props.settings?.message_template ?? ''
    })

    watch(
      () => props.settings,
      (newVal) => {
        if (newVal) {
          localSettings.value = {
            enabled: newVal.enabled ?? true,
            low_balance_threshold: newVal.low_balance_threshold ?? 500000,
            allowance_day: newVal.allowance_day ?? 1,
            message_template: newVal.message_template ?? ''
          }
        }
      },
      { deep: true }
    )

    const relationshipOptions = [
      { value: 'MOTHER', label: 'Mẹ', icon: 'favorite' },
      { value: 'FATHER', label: 'Bố', icon: 'shield' },
      { value: 'SIBLING', label: 'Anh/Chị/Em', icon: 'groups' },
      { value: 'RELATIVE', label: 'Họ hàng', icon: 'diversity_3' },
      { value: 'FRIEND', label: 'Bạn bè', icon: 'handshake' },
      { value: 'OTHER', label: 'Khác', icon: 'person' }
    ]

    const defaultTemplateHint =
      '{xung_ho} ơi, tháng này con chi tiêu hơi quá tay, hiện chỉ còn {so_du}, mà còn {so_ngay} ngày nữa mới tới ngày nhận tiền. {xung_ho} cho con xin thêm khoảng {so_tien} được không ạ? Con cảm ơn {xung_ho} ạ!'

    const sortedContacts = computed(() => {
      return [...props.contacts].sort((a, b) => {
        if (a.priority !== b.priority) {
          return (a.priority || 1) - (b.priority || 1)
        }
        return (a.id || 0) - (b.id || 0)
      })
    })

    function getRelationLabel(rel) {
      const found = relationshipOptions.find((r) => r.value === rel)
      return found ? found.label : 'Người thân'
    }

    function getRelationIcon(rel) {
      const found = relationshipOptions.find((r) => r.value === rel)
      return found ? found.icon : 'person'
    }

    function getRelationClass(rel) {
      switch (rel) {
        case 'MOTHER':
        case 'FATHER':
          return 'pill-primary'
        case 'SIBLING':
          return 'pill-secondary'
        case 'RELATIVE':
          return 'pill-tertiary'
        case 'FRIEND':
          return 'pill-cyan'
        default:
          return 'pill-muted'
      }
    }

    function formatDisplayPhone(rawPhone) {
      if (!rawPhone) return ''
      const cleaned = String(rawPhone).replace(/\D/g, '')
      if (cleaned.length === 10) {
        return cleaned.replace(/(\d{4})(\d{3})(\d{3})/, '$1 $2 $3')
      }
      return rawPhone
    }

    function validatePhone(phone) {
      const sanitized = String(phone).replace(/[\s.\-()]/g, '')
      const regex = /^(0|\+84|84)(3|5|7|8|9)\d{8}$/
      return regex.test(sanitized)
    }

    function openAddForm() {
      editingId.value = null
      formError.value = ''
      contactForm.value = {
        contact_name: '',
        relationship: 'MOTHER',
        phone: '',
        priority: props.contacts.length + 1,
        note: ''
      }
      showAddForm.value = true
    }

    function openEditForm(contact) {
      editingId.value = contact.id
      formError.value = ''
      contactForm.value = {
        contact_name: contact.contact_name || '',
        relationship: contact.relationship || 'OTHER',
        phone: contact.phone || '',
        priority: contact.priority || 1,
        note: contact.note || ''
      }
      showAddForm.value = true
    }

    function cancelForm() {
      showAddForm.value = false
      editingId.value = null
      formError.value = ''
    }

    function handleSubmitContact() {
      formError.value = ''
      const name = contactForm.value.contact_name.trim()
      const phone = contactForm.value.phone.trim()

      if (!name) {
        formError.value = 'Vui lòng nhập họ tên hoặc xưng hô người thân.'
        return
      }

      if (!phone) {
        formError.value = 'Vui lòng nhập số điện thoại.'
        return
      }

      if (!validatePhone(phone)) {
        formError.value = 'Số điện thoại không hợp lệ! Vui lòng nhập số di động Việt Nam (10 số, đầu 03/05/07/08/09).'
        return
      }

      const payload = {
        contact_name: name,
        relationship: contactForm.value.relationship,
        phone: phone,
        priority: Number(contactForm.value.priority) || 1,
        note: (contactForm.value.note || '').trim()
      }

      if (editingId.value) {
        emit('update-contact', { id: editingId.value, ...payload })
      } else {
        emit('create-contact', payload)
      }

      showAddForm.value = false
      editingId.value = null
    }

    function handleToggleActive(contact) {
      const newActive = contact.is_active ? 0 : 1
      emit('toggle-contact', { id: contact.id, is_active: newActive })
    }

    function handleDeleteContact(contact) {
      if (window.confirm(`Đạo trưởng có chắc chắn muốn xóa "${contact.contact_name}" khỏi Danh Bạ Hộ Đạo?`)) {
        emit('delete-contact', contact.id)
      }
    }

    function resetMessageTemplate() {
      localSettings.value.message_template = ''
    }

    function handleSaveSettings() {
      emit('save-settings', {
        enabled: Boolean(localSettings.value.enabled),
        low_balance_threshold: Math.max(0, Number(localSettings.value.low_balance_threshold) || 0),
        allowance_day: Math.min(28, Math.max(1, Number(localSettings.value.allowance_day) || 1)),
        message_template: (localSettings.value.message_template || '').trim()
      })
    }

    return {
      showAddForm,
      editingId,
      formError,
      showSettingsPanel,
      contactForm,
      localSettings,
      relationshipOptions,
      defaultTemplateHint,
      sortedContacts,
      getRelationLabel,
      getRelationIcon,
      getRelationClass,
      formatDisplayPhone,
      openAddForm,
      openEditForm,
      cancelForm,
      handleSubmitContact,
      handleToggleActive,
      handleDeleteContact,
      resetMessageTemplate,
      handleSaveSettings
    }
  }
}
</script>

<style scoped>
.support-contacts-card {
  position: relative;
  background: var(--color-surface-container-low, #131b2e);
  border: 1px solid var(--tier-1-border, rgba(255, 255, 255, 0.08));
  border-radius: var(--radius-lg, 1rem);
  padding: var(--space-lg, 1.5rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

.card-ambient-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 12rem;
  height: 12rem;
  background: radial-gradient(circle at top right, rgba(125, 214, 204, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md, 1rem);
  flex-wrap: wrap;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
}

.support-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
}

.title-meta {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.card-subtitle {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.header-action-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 11.5px;
  font-weight: 600;
}

.btn-add-contact {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  font-size: 12.5px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(125, 214, 204, 0.25);
}

.btn-add-contact:hover {
  background: #9af2e8;
  transform: translateY(-1px);
}

.card-description {
  font-size: 0.875rem;
  line-height: 1.35rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

/* ─── CONTACT FORM PANEL ─── */
.contact-form-panel {
  background: rgba(6, 14, 32, 0.85);
  border: 1px solid rgba(125, 214, 204, 0.25);
  border-radius: var(--radius-md, 0.75rem);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.form-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
}

.btn-close-form {
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.btn-close-form:hover {
  color: #ffffff;
}

.contact-inner-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 640px) {
  .form-row-grid {
    grid-template-columns: 1fr;
  }
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field-required {
  color: var(--color-error, #ffb4ab);
}

.field-hint {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-weight: normal;
  text-transform: none;
}

.stitch-input {
  width: 100%;
  padding: 8px 12px;
  background: rgba(19, 27, 46, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-DEFAULT, 8px);
  color: var(--color-on-surface, #dae2fd);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stitch-input:focus {
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 0 2px rgba(125, 214, 204, 0.2);
}

.select-dark {
  appearance: auto;
  cursor: pointer;
}

.form-error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(147, 0, 10, 0.25);
  border: 1px solid var(--color-error, #ffb4ab);
  border-radius: var(--radius-DEFAULT, 8px);
  color: var(--color-error, #ffb4ab);
  font-size: 12px;
}

.form-actions-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 4px;
}

.btn-cancel {
  padding: 8px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.btn-submit-contact {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  font-size: 12.5px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-submit-contact:hover {
  background: #9af2e8;
}

/* ─── CONTACTS LIST (ROW-BASED) ─── */
.contacts-list-container {
  display: flex;
  flex-direction: column;
}

.contacts-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 24px 16px;
  background: rgba(6, 14, 32, 0.4);
  border: 1px dashed rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-md, 0.75rem);
  gap: 10px;
}

.empty-icon {
  font-size: 36px;
  color: var(--color-primary, #7dd6cc);
  opacity: 0.7;
}

.empty-text {
  font-size: 13px;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 360px;
  line-height: 1.4;
  margin: 0;
}

.btn-add-contact-empty {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: rgba(125, 214, 204, 0.15);
  border: 1px solid rgba(125, 214, 204, 0.3);
  color: var(--color-primary, #7dd6cc);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add-contact-empty:hover {
  background: rgba(125, 214, 204, 0.25);
}

.contacts-rows-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-row-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(6, 14, 32, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-md, 0.75rem);
  transition: all 0.2s ease;
}

.contact-row-item:hover {
  background: rgba(15, 24, 48, 0.85);
  border-color: rgba(125, 214, 204, 0.2);
}

.row-inactive {
  opacity: 0.55;
  background: rgba(6, 14, 32, 0.3);
}

.row-left-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.priority-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-tertiary, #e3c370);
  background: rgba(227, 195, 112, 0.12);
  padding: 2px 6px;
  border-radius: 4px;
}

.relation-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.relation-icon {
  font-size: 13px;
}

.pill-primary {
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
  border: 1px solid rgba(125, 214, 204, 0.3);
}

.pill-secondary {
  background: rgba(196, 193, 251, 0.15);
  color: var(--color-secondary, #c4c1fb);
  border: 1px solid rgba(196, 193, 251, 0.3);
}

.pill-tertiary {
  background: rgba(227, 195, 112, 0.15);
  color: var(--color-tertiary, #e3c370);
  border: 1px solid rgba(227, 195, 112, 0.3);
}

.pill-cyan {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.pill-muted {
  background: rgba(255, 255, 255, 0.08);
  color: #bdc9c6;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.row-info-col {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex-grow: 1;
  min-width: 0;
}

.row-name-line {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.contact-name-text {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.contact-phone-text {
  font-size: 12.5px;
  color: var(--color-primary, #7dd6cc);
}

.contact-note-line {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.row-actions-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-row-action {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--color-on-surface-variant, #bdc9c6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-row-action.btn-edit:hover {
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
  border-color: rgba(125, 214, 204, 0.3);
}

.btn-row-action.btn-delete:hover {
  background: rgba(255, 180, 171, 0.15);
  color: var(--color-error, #ffb4ab);
  border-color: rgba(255, 180, 171, 0.3);
}

.max-contacts-notice {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 6px;
  margin-top: 4px;
}

/* ─── SWITCH TOGGLE ─── */
.switch-toggle {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
  flex-shrink: 0;
  cursor: pointer;
}

.switch-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider-round {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.15);
  transition: 0.3s;
  border-radius: 20px;
}

.slider-round:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: #ffffff;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider-round {
  background-color: var(--color-primary, #7dd6cc);
}

input:checked + .slider-round:before {
  transform: translateX(16px);
  background-color: #003733;
}

/* ─── SETTINGS SECTION ─── */
.support-settings-section {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(6, 14, 32, 0.5);
  overflow: hidden;
}

.settings-toggle-bar {
  width: 100%;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-on-surface, #dae2fd);
  transition: background 0.2s;
}

.settings-toggle-bar:hover {
  background: rgba(255, 255, 255, 0.04);
}

.toggle-bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-bar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.chevron-icon {
  font-size: 20px;
  color: var(--color-on-surface-variant, #bdc9c6);
  transition: transform 0.2s ease;
}

.chevron-rotated {
  transform: rotate(180deg);
}

.settings-body-panel {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: rgba(6, 14, 32, 0.7);
}

.settings-field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.field-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.setting-desc {
  font-size: 11.5px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.settings-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 10px;
}

@media (max-width: 640px) {
  .settings-form-grid {
    grid-template-columns: 1fr;
  }
}

.input-with-currency {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-currency input {
  padding-right: 48px;
}

.currency-tag {
  position: absolute;
  right: 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
  pointer-events: none;
}

.threshold-preview {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: 2px;
}

.template-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.btn-reset-template {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: var(--color-tertiary, #e3c370);
  font-size: 11px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-reset-template:hover {
  background: rgba(227, 195, 112, 0.12);
}

.template-textarea {
  resize: vertical;
  min-height: 68px;
  font-size: 12.5px;
  line-height: 1.4;
}

.template-placeholders-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin-top: 4px;
}

.code-tag {
  font-family: monospace;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.08);
  padding: 1px 5px;
  border-radius: 4px;
  color: var(--color-secondary, #c4c1fb);
}

.settings-actions-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.btn-save-settings {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-DEFAULT, 8px);
  background: var(--color-primary, #7dd6cc);
  color: var(--color-on-primary, #003733);
  font-size: 12.5px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-save-settings:hover {
  background: #9af2e8;
}

@media (max-width: 640px) {
  .contact-row-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .row-actions-group {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
