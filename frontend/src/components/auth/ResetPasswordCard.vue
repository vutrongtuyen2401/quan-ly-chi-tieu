<template>
  <div class="auth-card-stitch">
    <!-- Top Step Accent Line -->
    <div class="card-accent-line" aria-hidden="true"></div>

    <!-- Step Indicator -->
    <div class="step-indicator-row">
      <span class="step-tag">Bước 2 / 2: Hoàn tất đổi mật khẩu</span>
    </div>

    <!-- Header Title & Subtitle -->
    <div class="card-header-block">
      <h2 class="card-title">Đặt lại mật khẩu</h2>
      <p class="card-subtitle">Thiết lập mật khẩu mới cùng mã đặt lại để hoàn tất khôi phục.</p>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMsg" class="auth-error-banner" role="alert">
      <span class="material-symbols-outlined error-icon">error</span>
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Reset Password Form -->
    <form class="auth-form-body" @submit.prevent="handleSubmit">
      <!-- Field 1: Email -->
      <div class="form-field-group">
        <label class="field-label" for="reset-email">Email</label>
        <div class="field-input-wrap">
          <span class="material-symbols-outlined input-icon-left" aria-hidden="true">mail</span>
          <input
            id="reset-email"
            v-model="form.email"
            type="email"
            class="stitch-auth-input with-left-icon"
            placeholder="daotruong@cankhon.tuien.vn"
            required
            :disabled="loading"
          />
        </div>
      </div>

      <!-- Field 2: Mã đặt lại mật khẩu -->
      <div class="form-field-group">
        <div class="field-label-row">
          <label class="field-label" for="reset-token">Mã đặt lại mật khẩu</label>
          <span class="field-subtext">Mã 6 ký tự nhận từ hệ thống</span>
        </div>
        <div class="field-input-wrap">
          <span class="material-symbols-outlined input-icon-left" aria-hidden="true">key</span>
          <input
            id="reset-token"
            v-model="form.token"
            type="text"
            class="stitch-auth-input with-left-icon font-mono uppercase"
            placeholder="Nhập mã 6 ký tự..."
            required
            :disabled="loading"
          />
        </div>
      </div>

      <!-- Field 3: Mật khẩu mới -->
      <div class="form-field-group">
        <label class="field-label" for="reset-new-password">Mật khẩu mới</label>
        <div class="field-input-wrap">
          <span class="material-symbols-outlined input-icon-left" aria-hidden="true">lock</span>
          <input
            id="reset-new-password"
            v-model="form.new_password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="new-password"
            minlength="4"
            class="stitch-auth-input with-left-icon with-toggle"
            placeholder="Tối thiểu 4 ký tự..."
            required
            :disabled="loading"
            @keyup.enter="handleSubmit"
          />
          <button
            type="button"
            class="password-toggle-btn"
            :aria-label="showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
            @click="showPassword = !showPassword"
          >
            <span class="material-symbols-outlined toggle-icon">
              {{ showPassword ? 'visibility_off' : 'visibility' }}
            </span>
          </button>
        </div>
      </div>

      <!-- Primary Submit Button -->
      <div class="submit-wrap">
        <button
          type="submit"
          class="btn-auth-submit"
          :disabled="loading || !form.token || !form.new_password"
        >
          <span v-if="loading" class="material-symbols-outlined spin-icon">progress_activity</span>
          <span v-if="loading">Đang cập nhật...</span>
          <span v-else>Đặt lại mật khẩu</span>
          <span v-if="!loading" class="material-symbols-outlined submit-arrow">verified</span>
        </button>
      </div>

      <!-- Bottom Link: Return to Login -->
      <div class="card-footer-switch">
        <button
          type="button"
          class="link-return-btn"
          @click="$emit('switch-mode', 'login')"
        >
          ← Quay lại đăng nhập
        </button>
      </div>
    </form>

    <!-- Security Notice -->
    <div class="security-notice-strip">
      <span>Mật khẩu mới sẽ làm tăng chỉ số Token Version và tự động vô hiệu hóa các phiên cũ trên thiết bị khác.</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  form: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  errorMsg: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['submit', 'switch-mode'])

const showPassword = ref(false)

function handleSubmit() {
  if (props.loading) return
  emit('submit')
}
</script>

<style scoped>
.auth-card-stitch {
  position: relative;
  width: 100%;
  background: rgba(19, 27, 46, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(43, 138, 130, 0.1);
  padding: 1.75rem 1.5rem;
  box-sizing: border-box;
  animation: fadeIn 0.4s ease-out;
  overflow: hidden;
}

@media (min-width: 640px) {
  .auth-card-stitch {
    padding: 2rem 2rem;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-accent-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(43, 138, 130, 0.6), transparent);
}

/* ─── STEP INDICATOR ─── */
.step-indicator-row {
  margin-bottom: 0.5rem;
  text-align: left;
}

.step-tag {
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #7dd6cc;
}

/* ─── CARD HEADER ─── */
.card-header-block {
  margin-bottom: 1.25rem;
  text-align: left;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
  margin: 0;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0.25rem 0 0 0;
}

/* ─── ERROR BANNER ─── */
.auth-error-banner {
  margin-bottom: 1.25rem;
  padding: 0.75rem 1rem;
  background: rgba(147, 0, 10, 0.25);
  border: 1px solid rgba(255, 180, 171, 0.35);
  border-radius: 0.75rem;
  color: #ffb4ab;
  font-size: 0.825rem;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: fadeIn 0.3s ease-out;
}

.error-icon {
  font-size: 18px;
  color: #ffb4ab;
  flex-shrink: 0;
}

/* ─── FORM ─── */
.auth-form-body {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  text-align: left;
}

.field-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #cbd5e1;
  letter-spacing: 0.02em;
}

.field-subtext {
  font-size: 0.6875rem;
  color: #94a3b8;
}

.field-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.stitch-auth-input {
  width: 100%;
  height: 44px;
  background: #060e20;
  color: #ffffff;
  font-size: 0.875rem;
  border-radius: 0.75rem;
  padding: 0 0.875rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.2s ease;
  outline: none;
  box-sizing: border-box;
}

.stitch-auth-input.with-left-icon {
  padding-left: 2.5rem;
}

.stitch-auth-input.with-toggle {
  padding-right: 2.75rem;
}

.stitch-auth-input:focus {
  border-color: #2b8a82;
  box-shadow: 0 0 0 2px rgba(43, 138, 130, 0.3);
}

.stitch-auth-input::placeholder {
  color: #64748b;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.uppercase {
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.input-icon-left {
  position: absolute;
  left: 0.875rem;
  color: #64748b;
  font-size: 18px;
  pointer-events: none;
}

.password-toggle-btn {
  position: absolute;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 4px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.password-toggle-btn:hover {
  color: #ffffff;
}

.toggle-icon {
  font-size: 19px;
}

/* ─── SUBMIT BUTTON ─── */
.submit-wrap {
  padding-top: 0.25rem;
}

.btn-auth-submit {
  width: 100%;
  height: 46px;
  border-radius: 0.75rem;
  background: #2b8a82;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(43, 138, 130, 0.25);
}

.btn-auth-submit:hover:not(:disabled) {
  background: #236e68;
  box-shadow: 0 6px 20px rgba(43, 138, 130, 0.35);
  transform: translateY(-1px);
}

.btn-auth-submit:active:not(:disabled) {
  transform: scale(0.99);
}

.btn-auth-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-arrow {
  font-size: 18px;
}

.spin-icon {
  font-size: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ─── CARD FOOTER SWITCH ─── */
.card-footer-switch {
  padding-top: 0.5rem;
  text-align: center;
}

.link-return-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.8125rem;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s ease;
}

.link-return-btn:hover {
  color: #ffffff;
  text-decoration: underline;
}

/* ─── SECURITY NOTICE ─── */
.security-notice-strip {
  margin-top: 1rem;
  padding-top: 0.875rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.725rem;
  color: #94a3b8;
  line-height: 1.4;
  text-align: center;
}
</style>
