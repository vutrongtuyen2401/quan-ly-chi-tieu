<template>
  <header class="profile-header">
    <div class="header-left">
      <div class="header-tag-row">
        <span class="header-badge-tag">Thiết Lập Bản Thể &amp; Kết Giới</span>
        <span class="pulse-dot" aria-hidden="true"></span>
        <span class="header-sub-tag">
          {{ userRole === 'admin' ? 'Thần Thức Cấp 9 (Chưởng Môn)' : 'Thần Thức Cấp 4 (Đệ Tử)' }}
        </span>
      </div>
      <h1 class="header-title">Hồ Sơ Tu Giả &amp; Pháp Trận Bảo Mật</h1>
      <p class="header-desc">
        Quản lý đạo hiệu, thông tin định danh tông môn và bảo vệ kết giới tài chính qua Bản Mệnh Hồn Đăng.
      </p>
    </div>

    <div class="header-right">
      <div class="barrier-status-box">
        <span class="material-symbols-outlined barrier-icon" aria-hidden="true">verified_user</span>
        <div class="barrier-info">
          <span class="barrier-label">Trạng Thái Kết Giới</span>
          <span class="barrier-val">Kiên Cố • Linh Quang Hộ Thể</span>
        </div>
      </div>

      <button
        v-if="isModal"
        type="button"
        class="profile-close-btn"
        aria-label="Đóng hồ sơ bảo mật"
        @click="$emit('close')"
      >
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'ProfileHeader',
  props: {
    isModal: {
      type: Boolean,
      default: false
    },
    userRole: {
      type: String,
      default: 'user'
    }
  },
  emits: ['close']
}
</script>

<style scoped>
.profile-header {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-md, 1rem);
  padding-bottom: var(--space-md, 1rem);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

@media (min-width: 768px) {
  .profile-header {
    flex-direction: row;
    align-items: flex-end;
  }
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 0.25rem);
}

.header-tag-row {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 0.25rem);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.header-badge-tag {
  color: var(--color-primary, #7dd6cc);
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background-color: var(--color-primary, #7dd6cc);
  animation: pulse-glow 2s infinite ease-in-out;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.3); }
}

.header-sub-tag {
  color: var(--color-on-surface-variant, #bdc9c6);
}

.header-title {
  font-size: 1.625rem;
  font-weight: 600;
  line-height: 2rem;
  color: var(--color-on-surface, #dae2fd);
  letter-spacing: -0.015em;
  margin: 0;
}

@media (min-width: 768px) {
  .header-title {
    font-size: 1.875rem;
    line-height: 2.25rem;
  }
}

.header-desc {
  font-size: 0.875rem;
  line-height: 1.35rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 42rem;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  align-self: flex-start;
}

@media (min-width: 768px) {
  .header-right {
    align-self: auto;
  }
}

.barrier-status-box {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  background: rgba(34, 42, 61, 0.6);
  border: 1px solid rgba(125, 214, 204, 0.2);
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-md, 0.75rem);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

.barrier-icon {
  color: var(--color-primary, #7dd6cc);
  font-size: 20px;
  font-variation-settings: 'FILL' 1;
}

.barrier-info {
  display: flex;
  flex-direction: column;
}

.barrier-label {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.barrier-val {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
}

.profile-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(45, 52, 73, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile-close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: #ffb4ab;
  transform: scale(1.05);
}

.profile-close-btn:active {
  transform: scale(0.95);
}
</style>
