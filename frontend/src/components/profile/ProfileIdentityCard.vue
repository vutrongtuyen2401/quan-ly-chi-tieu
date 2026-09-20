<template>
  <div class="identity-column">
    <!-- MASTER IDENTITY CARD -->
    <div class="identity-card">
      <div class="aura-glow" aria-hidden="true"></div>

      <!-- Avatar & Basic Info -->
      <div class="user-hero-row">
        <div class="avatar-wrapper">
          <div class="avatar-ring">
            <img
              v-if="!imgError"
              class="avatar-img"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuB3DFU11GifrA_qI6yn6x2-uCdjPIJKisPB3j6sKLSgQ4tO37DDcrW8YCLSaSImUgoJpkATa9_fGc1CcQ-iWBVKBNT1j2GeoyZHFHK-qJzTp_teCzNVJb4EvzleNdlS2aVa1FhIhLWJLiNOSdZIhA1WGbVhEctj8NMdh9xiLUcJXWMaBad5TBqgqtpUy8JNZzWQWX6bSeqvbcZFMPR-N-vuSYHprDhLZSDIJi055BwapN61uBjhHfh7NQ"
              alt="Chân dung Đạo Trưởng"
              @error="imgError = true"
            />
            <div v-else class="avatar-fallback">
              {{ avatarInitial }}
            </div>
          </div>

          <span class="spirit-status-orb" title="Trạng Thái Thần Thức">
            <span class="ping-ring" aria-hidden="true"></span>
            <span class="core-dot" aria-hidden="true"></span>
          </span>
        </div>

        <div class="user-meta-info">
          <div class="tag-badges">
            <span class="role-badge" :class="userRole === 'admin' ? 'admin' : 'user'">
              {{ userRole === 'admin' ? 'Trưởng Lão Tông Môn' : 'Đệ Tử Tông Môn' }}
            </span>
            <span class="cultivation-badge">Đang Tu Luyện</span>
          </div>
          <h2 class="user-display-name" :title="userName || 'Đạo Hữu'">
            {{ userName || 'Đạo Hữu' }}
          </h2>
          <span class="user-email-text" :title="userEmail">
            {{ userEmail || 'daohuu@cankhon.tuien.vn' }}
          </span>
        </div>
      </div>

      <!-- Cultivation / Financial Realm -->
      <div class="realm-stats-box">
        <div class="realm-row">
          <span class="realm-label">Cảnh Giới Tài Chính</span>
          <span class="realm-grade">
            <span class="material-symbols-outlined realm-star" aria-hidden="true">stars</span>
            {{ cultivationRealm }}
          </span>
        </div>

        <div class="balance-row">
          <span class="balance-label">Tích Lũy Ngân Các:</span>
          <span class="balance-value">{{ formatAmount(totalBalance) }}</span>
        </div>

        <div class="progress-track" role="progressbar" :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>

        <span class="progress-hint">{{ progressPercent }}% tiến độ đột phá Kim Đan Sơ Kỳ</span>
      </div>

      <!-- Update Name Form -->
      <form class="profile-form" @submit.prevent="handleSubmit">
        <div class="form-field">
          <label class="field-label" for="dao-hieu-input">
            <span>Đạo Hiệu / Tên Hiển Thị</span>
            <span class="field-sub-badge">Công khai tông môn</span>
          </label>
          <div class="input-container">
            <span class="material-symbols-outlined input-icon" aria-hidden="true">badge</span>
            <input
              id="dao-hieu-input"
              v-model="localName"
              type="text"
              class="stitch-input"
              placeholder="Nhập đạo hiệu mới..."
              required
              maxlength="50"
            />
          </div>
        </div>

        <div class="form-field">
          <label class="field-label">
            <span>Thư Điện Tử (Email Tông Môn)</span>
            <span class="field-locked-badge">
              <span class="material-symbols-outlined text-[13px]" aria-hidden="true">lock</span>
              Đã Khóa Định Danh
            </span>
          </label>
          <div class="input-container">
            <span class="material-symbols-outlined input-icon" aria-hidden="true">mail</span>
            <input
              type="email"
              class="stitch-input locked-input"
              :value="userEmail"
              readonly
              tabindex="-1"
              aria-label="Email tài khoản đã khóa cố định"
            />
          </div>
        </div>

        <div class="form-field">
          <label class="field-label">Động Phủ Quản Thác</label>
          <div class="managed-cave-box">
            <div class="cave-info">
              <span class="material-symbols-outlined cave-icon" aria-hidden="true">temple_buddhist</span>
              <span class="cave-name">Vạn Hạc Động Phủ • Phân Khu Nhị</span>
            </div>
            <span class="cave-role-tag">{{ userRole === 'admin' ? 'Chủ trì' : 'Đệ Tử' }}</span>
          </div>
        </div>

        <div class="form-submit-row">
          <button
            type="submit"
            class="btn-save-profile"
            :disabled="loadingProfile || !localName.trim() || localName.trim() === userName"
          >
            <span class="material-symbols-outlined btn-icon" aria-hidden="true">save</span>
            <span>{{ loadingProfile ? 'Đang cập nhật...' : 'Cập Nhật Đạo Hiệu' }}</span>
          </button>
        </div>
      </form>
    </div>

    <!-- PRIVILEGES CARD -->
    <div class="privileges-card">
      <div class="privilege-icon-wrap">
        <span class="material-symbols-outlined privilege-icon" aria-hidden="true">workspace_premium</span>
      </div>
      <div class="privilege-content">
        <span class="privilege-title">
          {{ userRole === 'admin' ? 'Đặc Quyền Chưởng Môn' : 'Đặc Quyền Đệ Tử Nhập Môn' }}
        </span>
        <span class="privilege-desc">
          Miễn phí quản lý Càn Khôn Các, thần thức phân bổ tối đa không giới hạn linh thạch.
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'ProfileIdentityCard',
  props: {
    userName: {
      type: String,
      default: ''
    },
    userEmail: {
      type: String,
      default: ''
    },
    userRole: {
      type: String,
      default: 'user'
    },
    totalBalance: {
      type: Number,
      default: 0
    },
    loadingProfile: {
      type: Boolean,
      default: false
    },
    formatVND: {
      type: Function,
      default: null
    }
  },
  emits: ['save-profile'],
  setup(props, { emit }) {
    const localName = ref(props.userName || '')
    const imgError = ref(false)

    watch(() => props.userName, (newVal) => {
      localName.value = newVal || ''
    })

    const avatarInitial = computed(() => {
      const name = props.userName || 'Đ'
      return name.trim().charAt(0).toUpperCase()
    })

    const cultivationRealm = computed(() => {
      const bal = props.totalBalance || 0
      if (bal > 100000000) return 'Kim Đan Sơ Kỳ'
      if (bal > 20000000) return 'Trúc Cơ Trung Kỳ'
      if (bal > 5000000) return 'Trúc Cơ Sơ Kỳ'
      return 'Luyện Khí Tầng 9'
    })

    const progressPercent = computed(() => {
      const bal = props.totalBalance || 0
      if (bal <= 0) return 35
      const pct = Math.min(95, Math.max(20, Math.floor((bal % 10000000) / 100000)))
      return pct || 68
    })

    function formatAmount(val) {
      if (typeof props.formatVND === 'function') {
        return props.formatVND(val)
      }
      return new Intl.NumberFormat('vi-VN').format(val || 0) + ' Linh Thạch'
    }

    function handleSubmit() {
      const trimmed = localName.value.trim()
      if (trimmed) {
        emit('save-profile', trimmed)
      }
    }

    return {
      localName,
      imgError,
      avatarInitial,
      cultivationRealm,
      progressPercent,
      formatAmount,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.identity-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 1.5rem);
}

.identity-card {
  position: relative;
  background: rgba(23, 31, 51, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg, 1rem);
  padding: var(--space-lg, 1.5rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 1.5rem);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

.aura-glow {
  position: absolute;
  top: -6rem;
  right: -6rem;
  width: 12rem;
  height: 12rem;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.15) 0%, transparent 70%);
  filter: blur(32px);
  pointer-events: none;
}

.user-hero-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md, 1rem);
  text-align: center;
}

@media (min-width: 640px) {
  .user-hero-row {
    flex-direction: row;
    text-align: left;
  }
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar-ring {
  width: 92px;
  height: 92px;
  border-radius: 9999px;
  padding: 3px;
  background: linear-gradient(135deg, var(--color-primary, #7dd6cc), var(--color-primary-container, #449f96), var(--color-secondary, #c4c1fb));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.35);
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  object-fit: cover;
  background: #060e20;
}

.avatar-fallback {
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  background: #060e20;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary, #7dd6cc);
}

.spirit-status-orb {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 22px;
  height: 22px;
  border-radius: 9999px;
  background: #222a3d;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.ping-ring {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  background-color: var(--color-primary, #7dd6cc);
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.core-dot {
  position: relative;
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  background-color: var(--color-primary, #7dd6cc);
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.user-meta-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.tag-badges {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 0.25rem);
  margin-bottom: 0.25rem;
}

@media (min-width: 640px) {
  .tag-badges {
    justify-content: flex-start;
  }
}

.role-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.role-badge.admin {
  background: var(--color-primary-container, #449f96);
  color: #00302c;
}

.role-badge.user {
  background: rgba(125, 214, 204, 0.15);
  color: var(--color-primary, #7dd6cc);
}

.cultivation-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(34, 42, 61, 0.8);
  color: var(--color-on-surface-variant, #bdc9c6);
}

.user-display-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email-text {
  font-size: 0.8125rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Realm Stats Box */
.realm-stats-box {
  padding: var(--space-md, 1rem);
  background: rgba(6, 14, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md, 0.75rem);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.realm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.realm-label {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.realm-grade {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-tertiary, #e3c370);
  display: flex;
  align-items: center;
  gap: 4px;
}

.realm-star {
  font-size: 15px;
  font-variation-settings: 'FILL' 1;
}

.balance-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 2px;
}

.balance-label {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.balance-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
  font-family: var(--font-mono, monospace);
}

.progress-track {
  width: 100%;
  height: 6px;
  background: rgba(34, 42, 61, 0.8);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 4px;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, var(--color-primary, #7dd6cc), #9af2e8);
  box-shadow: 0 0 8px rgba(125, 214, 204, 0.5);
  transition: width 0.5s ease;
}

.progress-hint {
  font-size: 11px;
  color: rgba(189, 201, 198, 0.7);
  text-align: right;
  margin-top: 2px;
}

/* Form Styles */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
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

.field-sub-badge {
  font-size: 11px;
  color: var(--color-primary, #7dd6cc);
}

.field-locked-badge {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
  display: flex;
  align-items: center;
  gap: 3px;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 18px;
  pointer-events: none;
}

.stitch-input {
  width: 100%;
  height: 40px;
  padding: 0 12px 0 38px;
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
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3), 0 0 0 2px rgba(125, 214, 204, 0.25);
}

.locked-input {
  background: rgba(34, 42, 61, 0.4);
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: not-allowed;
  user-select: none;
}

.managed-cave-box {
  padding: 0.5rem 0.75rem;
  background: rgba(6, 14, 32, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md, 0.75rem);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cave-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cave-icon {
  color: var(--color-secondary, #c4c1fb);
  font-size: 20px;
}

.cave-name {
  font-size: 13px;
  color: var(--color-on-surface, #dae2fd);
}

.cave-role-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 9999px;
  background: var(--color-secondary-container, #444173);
  color: var(--color-on-secondary-container, #b3afe9);
}

.form-submit-row {
  padding-top: 4px;
}

.btn-save-profile {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-md, 0.75rem);
  background: var(--color-primary, #7dd6cc);
  color: #003733;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 0.25rem);
  border: none;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.3);
  transition: all 0.2s ease;
}

.btn-save-profile:hover:not(:disabled) {
  background: #9af2e8;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.45);
  transform: translateY(-1px);
}

.btn-save-profile:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-save-profile:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-icon {
  font-size: 18px;
}

/* Privileges Card */
.privileges-card {
  background: rgba(23, 31, 51, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-lg, 1rem);
  padding: var(--space-md, 1rem);
  display: flex;
  align-items: center;
  gap: var(--space-md, 1rem);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.privilege-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(198, 168, 88, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-tertiary, #e3c370);
  flex-shrink: 0;
}

.privilege-icon {
  font-size: 24px;
}

.privilege-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.privilege-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.privilege-desc {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
  line-height: 1.25rem;
}
</style>
