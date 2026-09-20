<template>
  <div class="auth-card-stitch">
    <!-- Card Title & Subtitle -->
    <div class="card-header-block">
      <h2 class="card-title">Đăng nhập</h2>
      <p class="card-subtitle">Chào mừng trở lại động phủ tài chính.</p>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMsg" class="auth-error-banner" role="alert">
      <span class="material-symbols-outlined error-icon">error</span>
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Login Form -->
    <form class="auth-form-body" @submit.prevent="handleSubmit">
      <!-- Email Input -->
      <div class="form-field-group">
        <label class="field-label" for="login-email">Email</label>
        <div class="field-input-wrap">
          <input
            id="login-email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            class="stitch-auth-input"
            placeholder="daotruong@cankhon.tuien.vn"
            required
            :disabled="loading"
            @keyup.enter="handleSubmit"
          />
          <span class="material-symbols-outlined input-icon-right" aria-hidden="true">mail</span>
        </div>
      </div>

      <!-- Password Input -->
      <div class="form-field-group">
        <label class="field-label" for="login-password">Mật khẩu</label>
        <div class="field-input-wrap">
          <input
            id="login-password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            class="stitch-auth-input with-toggle"
            placeholder="••••••••"
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

      <!-- Quick Action: Forgot Password -->
      <div class="form-action-row">
        <button
          type="button"
          class="link-forgot-btn"
          @click="$emit('switch-mode', 'forgot')"
        >
          Quên mật khẩu?
        </button>
      </div>

      <!-- Primary Submit Button -->
      <div class="submit-wrap">
        <button
          type="submit"
          class="btn-auth-submit"
          :disabled="loading || !form.email || !form.password"
        >
          <span v-if="loading" class="material-symbols-outlined spin-icon">progress_activity</span>
          <span v-if="loading">Đang xác thực...</span>
          <span v-else>Đăng nhập</span>
          <span v-if="!loading" class="material-symbols-outlined submit-arrow">arrow_forward</span>
        </button>
      </div>
    </form>

    <!-- Bottom Switch Link: Register -->
    <div class="card-footer-switch">
      <span class="switch-text">Chưa có tài khoản?</span>
      <button
        type="button"
        class="switch-action-btn"
        @click="$emit('switch-mode', 'register')"
      >
        Tạo tài khoản
      </button>
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

/* ─── CARD HEADER ─── */
.card-header-block {
  margin-bottom: 1.5rem;
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
  gap: 1rem;
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  text-align: left;
}

.field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #cbd5e1;
  letter-spacing: 0.02em;
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
  padding: 0 2.5rem 0 0.875rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.2s ease;
  outline: none;
  box-sizing: border-box;
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

.input-icon-right {
  position: absolute;
  right: 0.875rem;
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

/* ─── QUICK ACTIONS ─── */
.form-action-row {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.125rem;
}

.link-forgot-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.775rem;
  cursor: pointer;
  padding: 2px 4px;
  transition: color 0.2s ease;
}

.link-forgot-btn:hover {
  color: #7dd6cc;
  text-decoration: underline;
}

/* ─── SUBMIT BUTTON ─── */
.submit-wrap {
  padding-top: 0.5rem;
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
  margin-top: 1.5rem;
  padding-top: 1rem;
  text-align: center;
  font-size: 0.875rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.switch-text {
  color: #94a3b8;
}

.switch-action-btn {
  background: transparent;
  border: none;
  color: #dae2fd;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}

.switch-action-btn:hover {
  color: #7dd6cc;
  text-decoration: underline;
}
</style>
