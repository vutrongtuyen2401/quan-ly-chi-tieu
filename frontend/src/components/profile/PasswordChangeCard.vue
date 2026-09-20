<template>
  <div class="password-change-card">
    <!-- Header & Badge -->
    <div class="card-header-row">
      <div class="card-title-group">
        <div class="key-icon-box">
          <span class="material-symbols-outlined text-[22px]" aria-hidden="true">vpn_key</span>
        </div>
        <div class="title-meta">
          <h2 class="card-title">Đổi Mật Khẩu Pháp Ấn (Master Password)</h2>
          <span class="card-subtitle">Cập nhật mật khóa đăng nhập thường nhật</span>
        </div>
      </div>

      <span class="version-chip">Phiên Bản 2.4.1</span>
    </div>

    <!-- Security Notice / Token Versioning -->
    <div class="security-notice-strip">
      <span class="material-symbols-outlined notice-icon" aria-hidden="true">info</span>
      <span class="notice-text">
        Đổi mật khẩu sẽ kích hoạt cơ chế <strong>Token Versioning</strong>, tự động vô hiệu hóa toàn bộ phiên đăng nhập cũ trên các bảo bối và thiết bị khác để đảm bảo an toàn.
      </span>
    </div>

    <!-- Form -->
    <form class="password-form" @submit.prevent="handleSubmit">
      <!-- Error banner if validation fails -->
      <div v-if="validationError" class="form-error-banner" role="alert">
        <span class="material-symbols-outlined text-[16px]">error</span>
        <span>{{ validationError }}</span>
      </div>

      <!-- Current Password -->
      <div class="form-field">
        <label class="field-label" for="current-pwd">Mật Khẩu Hiện Tại</label>
        <div class="input-container">
          <input
            id="current-pwd"
            v-model="currentPassword"
            :type="showCurPassword ? 'text' : 'password'"
            class="stitch-input"
            placeholder="Nhập mật khẩu đang sử dụng"
            required
            autocomplete="current-password"
          />
          <button
            type="button"
            class="toggle-vis-btn"
            :aria-label="showCurPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
            @click="showCurPassword = !showCurPassword"
          >
            <span class="material-symbols-outlined text-[18px]">
              {{ showCurPassword ? 'visibility_off' : 'visibility' }}
            </span>
          </button>
        </div>
      </div>

      <!-- New Password + Confirm in Grid -->
      <div class="password-grid">
        <div class="form-field">
          <label class="field-label" for="new-pwd">
            <span>Mật Khẩu Mới</span>
            <span class="field-hint">≥ 4 ký tự</span>
          </label>
          <div class="input-container">
            <input
              id="new-pwd"
              v-model="newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              class="stitch-input"
              placeholder="Mật khẩu pháp ấn mới"
              minlength="4"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="toggle-vis-btn"
              :aria-label="showNewPassword ? 'Ẩn mật khẩu mới' : 'Hiện mật khẩu mới'"
              @click="showNewPassword = !showNewPassword"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ showNewPassword ? 'visibility_off' : 'visibility' }}
              </span>
            </button>
          </div>
        </div>

        <div class="form-field">
          <label class="field-label" for="confirm-new-pwd">
            <span>Xác Nhận Mật Khẩu Mới</span>
          </label>
          <div class="input-container">
            <input
              id="confirm-new-pwd"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="stitch-input"
              placeholder="Nhập lại mật khẩu mới"
              minlength="4"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="toggle-vis-btn"
              :aria-label="showConfirmPassword ? 'Ẩn xác nhận mật khẩu' : 'Hiện xác nhận mật khẩu'"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ showConfirmPassword ? 'visibility_off' : 'visibility' }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Action Button -->
      <div class="form-submit-row">
        <button
          type="submit"
          class="btn-save-password"
          :disabled="loadingPassword || !isFormValid"
        >
          <span class="material-symbols-outlined text-[18px]" aria-hidden="true">lock_reset</span>
          <span>{{ loadingPassword ? 'Đang cập nhật...' : 'Cập Nhật Mật Khẩu Pháp Ấn' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'PasswordChangeCard',
  props: {
    loadingPassword: {
      type: Boolean,
      default: false
    }
  },
  emits: ['change-password'],
  setup(props, { emit }) {
    const currentPassword = ref('')
    const newPassword = ref('')
    const confirmPassword = ref('')
    const validationError = ref('')

    const showCurPassword = ref(false)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)

    const isFormValid = computed(() => {
      return (
        currentPassword.value.trim().length > 0 &&
        newPassword.value.length >= 4 &&
        confirmPassword.value.length >= 4
      )
    })

    function handleSubmit() {
      validationError.value = ''

      if (!currentPassword.value) {
        validationError.value = 'Vui lòng nhập mật khẩu hiện tại!'
        return
      }

      if (newPassword.value.length < 4) {
        validationError.value = 'Mật khẩu mới phải có tối thiểu 4 ký tự!'
        return
      }

      if (newPassword.value !== confirmPassword.value) {
        validationError.value = 'Mật khẩu xác nhận không trùng khớp!'
        return
      }

      emit('change-password', {
        current_password: currentPassword.value,
        new_password: newPassword.value
      })

      // Reset sensitive fields
      currentPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    }

    return {
      currentPassword,
      newPassword,
      confirmPassword,
      validationError,
      showCurPassword,
      showNewPassword,
      showConfirmPassword,
      isFormValid,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.password-change-card {
  position: relative;
  background: rgba(23, 31, 51, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 1rem);
  padding: var(--space-lg, 1.5rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md, 1rem);
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
}

.key-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(68, 65, 115, 0.3);
  color: var(--color-secondary, #c4c1fb);
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

.version-chip {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(45, 52, 73, 0.6);
  color: var(--color-on-surface-variant, #bdc9c6);
  white-space: nowrap;
}

/* Security Notice */
.security-notice-strip {
  display: flex;
  align-items: flex-start;
  gap: var(--space-xs, 0.25rem);
  padding: 0.5rem 0.75rem;
  background: rgba(6, 14, 32, 0.6);
  border: 1px solid rgba(125, 214, 204, 0.15);
  border-radius: var(--radius-md, 0.75rem);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 0.8125rem;
  line-height: 1.25rem;
}

.notice-icon {
  color: var(--color-primary, #7dd6cc);
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.notice-text strong {
  color: var(--color-primary, #7dd6cc);
}

/* Form Styles */
.password-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
}

.form-error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(147, 0, 10, 0.3);
  border: 1px solid rgba(255, 180, 171, 0.4);
  border-radius: var(--radius-md, 0.75rem);
  color: #ffb4ab;
  font-size: 13px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-on-surface, #dae2fd);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-hint {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.stitch-input {
  width: 100%;
  height: 40px;
  padding: 0 40px 0 12px;
  background: #060e20;
  color: var(--color-on-surface, #dae2fd);
  font-size: 14px;
  border-radius: var(--radius-md, 0.75rem);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.stitch-input:focus {
  outline: none;
  border-color: var(--color-secondary, #c4c1fb);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3), 0 0 0 2px rgba(196, 193, 251, 0.25);
}

.toggle-vis-btn {
  position: absolute;
  right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  border-radius: 4px;
  transition: color 0.2s;
}

.toggle-vis-btn:hover {
  color: var(--color-secondary, #c4c1fb);
}

.password-grid {
  display: grid;
  grid-cols: 1fr;
  gap: var(--space-md, 1rem);
}

@media (min-width: 768px) {
  .password-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.form-submit-row {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.25rem;
}

.btn-save-password {
  height: 40px;
  padding: 0 var(--space-lg, 1.5rem);
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(45, 52, 73, 0.8);
  border: 1px solid rgba(196, 193, 251, 0.3);
  color: var(--color-on-surface, #dae2fd);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 0.25rem);
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
}

.btn-save-password:hover:not(:disabled) {
  background: var(--color-secondary, #c4c1fb);
  color: #2d2a5b;
  box-shadow: 0 0 16px rgba(196, 193, 251, 0.4);
  transform: translateY(-1px);
}

.btn-save-password:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-save-password:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
