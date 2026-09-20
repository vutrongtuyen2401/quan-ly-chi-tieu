<template>
  <div class="soul-lamp-card">
    <div class="flame-aura-glow" aria-hidden="true"></div>

    <!-- Header & Badge -->
    <div class="card-header-row">
      <div class="card-title-group">
        <div class="fire-icon-box">
          <span class="material-symbols-outlined text-[22px]" aria-hidden="true">local_fire_department</span>
        </div>
        <div class="title-meta">
          <h2 class="card-title">Bản Mệnh Hồn Đăng (Cấp Bảo Mật Tối Cao)</h2>
          <span class="card-subtitle">Pháp ấn phòng vệ linh hồn vĩnh cửu</span>
        </div>
      </div>

      <span class="burning-chip">
        <span class="chip-ping" aria-hidden="true"></span>
        <span>Đang Cháy Sáng</span>
      </span>
    </div>

    <!-- Description -->
    <p class="card-description">
      Hồn Đăng là ấn chứng phong ấn tối cao dùng để phục hồi tài khoản khi lạc mất thần thức hoặc quên mật khẩu. Khẩu quyết được bảo vệ bằng thuật toán băm Bcrypt an toàn.
    </p>

    <!-- Verified Status Strip -->
    <div class="status-strip">
      <div class="strip-left">
        <span class="material-symbols-outlined strip-icon" aria-hidden="true">shield_lock</span>
        <span>Đã Thiết Lập &amp; Khắc Sâu Vào Hồn Đăng (Đã Xác Thực)</span>
      </div>
      <span class="strip-hash font-mono">Ấn chú: •••••••••••••</span>
    </div>

    <!-- Form -->
    <form class="soul-lamp-form" @submit.prevent="handleSubmit">
      <!-- Error banner if validation fails -->
      <div v-if="validationError" class="form-error-banner" role="alert">
        <span class="material-symbols-outlined text-[16px]">error</span>
        <span>{{ validationError }}</span>
      </div>

      <!-- Current Password -->
      <div class="form-field">
        <label class="field-label" for="lamp-cur-pwd">Mật Khẩu Hiện Tại</label>
        <div class="input-container">
          <input
            id="lamp-cur-pwd"
            v-model="currentPassword"
            :type="showCurPassword ? 'text' : 'password'"
            class="stitch-input"
            placeholder="Nhập mật khẩu hiện tại để khai mở Hồn Đăng"
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

      <!-- New Phrase + Confirm in Grid -->
      <div class="phrase-grid">
        <div class="form-field">
          <label class="field-label" for="lamp-phrase">
            <span>Khẩu Quyết Hồn Đăng Mới</span>
            <span class="field-hint">Tối thiểu 3 ký tự</span>
          </label>
          <div class="input-container">
            <input
              id="lamp-phrase"
              v-model="newSoulLamp"
              :type="showNewPhrase ? 'text' : 'password'"
              class="stitch-input font-mono"
              placeholder="Ví dụ: VanKiemQuyTong99"
              minlength="3"
              required
            />
            <button
              type="button"
              class="toggle-vis-btn"
              :aria-label="showNewPhrase ? 'Ẩn khẩu quyết' : 'Hiện khẩu quyết'"
              @click="showNewPhrase = !showNewPhrase"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ showNewPhrase ? 'visibility_off' : 'visibility' }}
              </span>
            </button>
          </div>
        </div>

        <div class="form-field">
          <label class="field-label" for="lamp-phrase-confirm">
            <span>Nhập Lại Khẩu Quyết</span>
          </label>
          <div class="input-container">
            <input
              id="lamp-phrase-confirm"
              v-model="confirmSoulLamp"
              :type="showConfirmPhrase ? 'text' : 'password'"
              class="stitch-input font-mono"
              placeholder="Nhập lại khẩu quyết chính xác"
              minlength="3"
              required
            />
            <button
              type="button"
              class="toggle-vis-btn"
              :aria-label="showConfirmPhrase ? 'Ẩn khẩu quyết xác nhận' : 'Hiện khẩu quyết xác nhận'"
              @click="showConfirmPhrase = !showConfirmPhrase"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ showConfirmPhrase ? 'visibility_off' : 'visibility' }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Action Button -->
      <div class="form-submit-row">
        <button
          type="submit"
          class="btn-save-soul-lamp"
          :disabled="loadingSoulLamp || !isFormValid"
        >
          <span class="material-symbols-outlined text-[18px]" aria-hidden="true">wb_sunny</span>
          <span>{{ loadingSoulLamp ? 'Đang khắc ghi...' : 'Khắc Ghi Hồn Đăng Mới' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'SoulLampCard',
  props: {
    loadingSoulLamp: {
      type: Boolean,
      default: false
    }
  },
  emits: ['save-soul-lamp'],
  setup(props, { emit }) {
    const currentPassword = ref('')
    const newSoulLamp = ref('')
    const confirmSoulLamp = ref('')
    const validationError = ref('')

    const showCurPassword = ref(false)
    const showNewPhrase = ref(false)
    const showConfirmPhrase = ref(false)

    const isFormValid = computed(() => {
      return (
        currentPassword.value.trim().length > 0 &&
        newSoulLamp.value.trim().length >= 3 &&
        confirmSoulLamp.value.trim().length >= 3
      )
    })

    function handleSubmit() {
      validationError.value = ''

      if (!currentPassword.value) {
        validationError.value = 'Vui lòng nhập mật khẩu hiện tại!'
        return
      }

      const trimmedPhrase = newSoulLamp.value.trim()
      if (trimmedPhrase.length < 3) {
        validationError.value = 'Khẩu quyết Hồn Đăng mới phải có tối thiểu 3 ký tự!'
        return
      }

      if (trimmedPhrase !== confirmSoulLamp.value.trim()) {
        validationError.value = 'Khẩu quyết xác nhận không trùng khớp!'
        return
      }

      emit('save-soul-lamp', {
        current_password: currentPassword.value,
        new_soul_lamp: trimmedPhrase
      })

      // Reset sensitive fields
      currentPassword.value = ''
      newSoulLamp.value = ''
      confirmSoulLamp.value = ''
    }

    return {
      currentPassword,
      newSoulLamp,
      confirmSoulLamp,
      validationError,
      showCurPassword,
      showNewPhrase,
      showConfirmPhrase,
      isFormValid,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.soul-lamp-card {
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
  overflow: hidden;
}

.flame-aura-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 10rem;
  height: 10rem;
  background: radial-gradient(circle at top right, rgba(227, 195, 112, 0.15) 0%, transparent 70%);
  pointer-events: none;
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

.fire-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(198, 168, 88, 0.2);
  color: var(--color-tertiary, #e3c370);
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

.burning-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 9999px;
  background: rgba(198, 168, 88, 0.2);
  color: var(--color-tertiary, #e3c370);
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.chip-ping {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background-color: var(--color-tertiary, #e3c370);
  animation: pulse-lamp 1.8s infinite ease-in-out;
}

@keyframes pulse-lamp {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.3; transform: scale(1.4); }
}

.card-description {
  font-size: 0.875rem;
  line-height: 1.35rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

/* Status Strip */
.status-strip {
  padding: 0.5rem 0.75rem;
  background: rgba(6, 14, 32, 0.8);
  border: 1px solid rgba(227, 195, 112, 0.2);
  border-radius: var(--radius-md, 0.75rem);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

@media (min-width: 640px) {
  .status-strip {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.strip-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-tertiary, #e3c370);
}

.strip-icon {
  font-size: 16px;
}

.strip-hash {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

/* Form Styles */
.soul-lamp-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
  padding-top: 0.25rem;
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
  border-color: var(--color-tertiary, #e3c370);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3), 0 0 0 2px rgba(227, 195, 112, 0.25);
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
  color: var(--color-tertiary, #e3c370);
}

.phrase-grid {
  display: grid;
  grid-cols: 1fr;
  gap: var(--space-md, 1rem);
}

@media (min-width: 768px) {
  .phrase-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.form-submit-row {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.25rem;
}

.btn-save-soul-lamp {
  height: 40px;
  padding: 0 var(--space-lg, 1.5rem);
  border-radius: var(--radius-md, 0.75rem);
  background: var(--color-tertiary, #e3c370);
  color: #3d2e00;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 0.25rem);
  border: none;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(227, 195, 112, 0.3);
  transition: all 0.2s ease;
}

.btn-save-soul-lamp:hover:not(:disabled) {
  background: #ffe08f;
  box-shadow: 0 0 22px rgba(227, 195, 112, 0.45);
  transform: translateY(-1px);
}

.btn-save-soul-lamp:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-save-soul-lamp:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
