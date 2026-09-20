<template>
  <div
    v-if="show"
    class="role-modal-backdrop"
    role="dialog"
    aria-modal="true"
    aria-labelledby="role-modal-title"
    @click.self="$emit('close')"
  >
    <div class="role-modal-card">
      <div class="modal-header-row">
        <div class="shield-icon-box">
          <span class="material-symbols-outlined text-[28px]" aria-hidden="true">shield_lock</span>
        </div>
        <div class="modal-title-meta">
          <span class="modal-tag-text">Thao Tác Bảo Mật Cấp Cao</span>
          <h2 id="role-modal-title" class="modal-main-title">Xác Nhận Thay Đổi Vai Trò</h2>
        </div>
      </div>

      <div class="target-transition-box">
        <p class="target-prompt">
          Bạn có chắc chắn muốn chuyển đổi chức vị cho đạo hữu:
        </p>
        <div class="transition-row">
          <span class="user-from-name" :title="targetUser?.full_name || targetUser?.email">
            {{ targetUser?.full_name || targetUser?.email }}
          </span>
          <span class="material-symbols-outlined arrow-icon" aria-hidden="true">arrow_forward</span>
          <span class="role-to-name">
            {{ targetRole === 'admin' ? 'Quản Trị Viên (Admin)' : 'Đạo Hữu (User)' }}
          </span>
        </div>
      </div>

      <!-- High Privilege Warning Note -->
      <div class="privilege-warning-strip">
        <span class="material-symbols-outlined warning-icon" aria-hidden="true">warning</span>
        <span class="warning-text">
          <strong class="warning-highlight">Cảnh Báo:</strong> Quản trị viên sẽ có toàn quyền can thiệp vào phân quyền, khóa tài khoản và quản trị danh phận của các đệ tử khác trong tông môn.
        </span>
      </div>

      <!-- Action Buttons -->
      <div class="modal-actions-row">
        <button
          type="button"
          class="btn-cancel"
          :disabled="loading"
          @click="$emit('close')"
        >
          Hủy Bỏ
        </button>
        <button
          type="button"
          class="btn-confirm-role"
          :disabled="loading"
          @click="onConfirm"
        >
          <span v-if="loading" class="material-symbols-outlined spin-icon text-[16px]">progress_activity</span>
          <span>{{ loading ? 'Đang cập nhật...' : 'Xác Nhận Thay Đổi' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted } from 'vue'

export default {
  name: 'RoleConfirmModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    targetUser: {
      type: Object,
      default: null
    },
    targetRole: {
      type: String,
      default: 'user'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'close'],
  setup(props, { emit }) {
    function handleKeydown(e) {
      if (props.show && e.key === 'Escape' && !props.loading) {
        emit('close')
      }
    }

    function onConfirm() {
      if (props.targetUser) {
        emit('confirm', {
          user: props.targetUser,
          newRole: props.targetRole
        })
      }
    }

    onMounted(() => {
      window.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      window.removeEventListener('keydown', handleKeydown)
    })

    return {
      onConfirm
    }
  }
}
</script>

<style scoped>
.role-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(6, 14, 32, 0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: var(--space-md, 1rem);
}

.role-modal-card {
  width: 100%;
  max-width: 32rem;
  background: #131b2e;
  border: 1px solid rgba(227, 195, 112, 0.25);
  border-radius: var(--radius-xl, 1.5rem);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.6), 0 0 24px rgba(227, 195, 112, 0.1);
  padding: var(--space-lg, 1.5rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
  position: relative;
  overflow: hidden;
  animation: modal-zoom-in 0.2s ease-out;
}

@keyframes modal-zoom-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md, 1rem);
}

.shield-icon-box {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(198, 168, 88, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-tertiary, #e3c370);
  flex-shrink: 0;
}

.modal-title-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.modal-tag-text {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-tertiary, #e3c370);
}

.modal-main-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

/* Target Transition Box */
.target-transition-box {
  padding: var(--space-md, 1rem);
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(23, 31, 51, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.target-prompt {
  font-size: 0.875rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

.transition-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-xs, 0.25rem) 0;
  gap: 0.5rem;
}

.user-from-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow-icon {
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 18px;
  flex-shrink: 0;
}

.role-to-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-secondary, #c4c1fb);
  white-space: nowrap;
}

/* Warning Strip */
.privilege-warning-strip {
  display: flex;
  align-items: flex-start;
  gap: var(--space-xs, 0.25rem);
  padding: var(--space-sm, 0.5rem) var(--space-md, 1rem);
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(147, 0, 10, 0.25);
  border: 1px solid rgba(255, 180, 171, 0.25);
  color: #ffdad6;
}

.warning-icon {
  color: var(--color-error, #ffb4ab);
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.warning-text {
  font-size: 0.8125rem;
  line-height: 1.25rem;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.warning-highlight {
  color: var(--color-error, #ffb4ab);
  font-weight: 600;
}

/* Modal Action Buttons */
.modal-actions-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-sm, 0.5rem);
  padding-top: var(--space-xs, 0.25rem);
}

.btn-cancel {
  height: 40px;
  padding: 0 var(--space-md, 1rem);
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(45, 52, 73, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-on-surface, #dae2fd);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover:not(:disabled) {
  background: rgba(55, 65, 81, 0.9);
}

.btn-confirm-role {
  height: 40px;
  padding: 0 var(--space-lg, 1.5rem);
  border-radius: var(--radius-md, 0.75rem);
  background: var(--color-primary, #7dd6cc);
  color: #003733;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.3);
  transition: all 0.2s ease;
}

.btn-confirm-role:hover:not(:disabled) {
  background: #9af2e8;
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.45);
  transform: translateY(-1px);
}

.btn-confirm-role:disabled,
.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
