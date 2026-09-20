<template>
  <div
    :class="[isModal ? 'profile-modal-backdrop' : 'profile-view-root']"
    role="dialog"
    :aria-modal="isModal ? 'true' : undefined"
    aria-labelledby="profile-dialog-title"
    @click.self="handleBackdropClick"
  >
    <div :class="[isModal ? 'profile-modal-dialog' : 'profile-view-container']">
      <!-- ═══ HEADER ═══ -->
      <ProfileHeader
        :is-modal="isModal"
        :user-role="userRole"
        @close="$emit('close')"
      />

      <!-- ═══ MAIN 2-COLUMN GRID ═══ -->
      <div class="profile-main-grid">
        <!-- Left Column: Identity & Cultivation -->
        <div class="grid-left-col">
          <ProfileIdentityCard
            :user-name="userName"
            :user-email="userEmail"
            :user-role="userRole"
            :total-balance="totalBalance"
            :loading-profile="loadingProfile"
            :format-v-n-d="formatVND"
            @save-profile="$emit('save-profile', $event)"
          />
        </div>

        <!-- Right Column: Security Center -->
        <div class="grid-right-col">
          <!-- Bản Mệnh Hồn Đăng -->
          <SoulLampCard
            :loading-soul-lamp="loadingSoulLamp"
            @save-soul-lamp="$emit('save-soul-lamp', $event)"
          />

          <!-- Đổi Mật Khẩu Master -->
          <PasswordChangeCard
            :loading-password="loadingPassword"
            @change-password="$emit('change-password', $event)"
          />

          <!-- Đăng Xuất Khỏi Pháp Trận Card -->
          <div class="logout-security-card">
            <div class="logout-meta-group">
              <div class="logout-icon-box">
                <span class="material-symbols-outlined text-[22px]" aria-hidden="true">logout</span>
              </div>
              <div class="logout-text-info">
                <h2 class="logout-title">Đăng Xuất Khỏi Pháp Trận</h2>
                <span class="logout-subtitle">
                  Kết thúc phiên tu luyện hiện tại, bảo toàn linh khí tài khoản.
                </span>
              </div>
            </div>

            <button
              type="button"
              class="btn-logout-barrier"
              @click="confirmLogout"
            >
              <span class="material-symbols-outlined text-[18px]" aria-hidden="true">power_settings_new</span>
              <span>Đăng Xuất Khỏi Càn Khôn Các</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ═══ BOTTOM ROW: SECURITY ASSURANCE BADGES ═══ -->
      <div class="security-badges-row">
        <div class="sec-badge-card">
          <span class="material-symbols-outlined sec-badge-icon jade" aria-hidden="true">key</span>
          <div class="sec-badge-info">
            <span class="sec-badge-title">Bản Mệnh Hồn Đăng</span>
            <span class="sec-badge-desc">Bảo vệ phục hồi tài khoản</span>
          </div>
        </div>

        <div class="sec-badge-card">
          <span class="material-symbols-outlined sec-badge-icon indigo" aria-hidden="true">device_hub</span>
          <div class="sec-badge-info">
            <span class="sec-badge-title">Phiên Truy Cập An Toàn</span>
            <span class="sec-badge-desc">Xác thực mã bảo mật JWT</span>
          </div>
        </div>

        <div class="sec-badge-card">
          <span class="material-symbols-outlined sec-badge-icon gold" aria-hidden="true">timelapse</span>
          <div class="sec-badge-info">
            <span class="sec-badge-title">Vô Hiệu Hóa Tức Thì</span>
            <span class="sec-badge-desc">Tự hủy phiên khi đổi mật khẩu</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted } from 'vue'
import ProfileHeader from './ProfileHeader.vue'
import ProfileIdentityCard from './ProfileIdentityCard.vue'
import SoulLampCard from './SoulLampCard.vue'
import PasswordChangeCard from './PasswordChangeCard.vue'

export default {
  name: 'ProfileView',
  components: {
    ProfileHeader,
    ProfileIdentityCard,
    SoulLampCard,
    PasswordChangeCard
  },
  props: {
    isModal: {
      type: Boolean,
      default: true
    },
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
    isUserAdmin: {
      type: Boolean,
      default: false
    },
    totalBalance: {
      type: Number,
      default: 0
    },
    loadingProfile: {
      type: Boolean,
      default: false
    },
    loadingSoulLamp: {
      type: Boolean,
      default: false
    },
    loadingPassword: {
      type: Boolean,
      default: false
    },
    formatVND: {
      type: Function,
      default: null
    }
  },
  emits: ['close', 'save-profile', 'save-soul-lamp', 'change-password', 'logout'],
  setup(props, { emit }) {
    function handleBackdropClick() {
      if (props.isModal) {
        emit('close')
      }
    }

    function handleKeydown(e) {
      if (props.isModal && e.key === 'Escape') {
        emit('close')
      }
    }

    function confirmLogout() {
      if (window.confirm('Đạo trưởng có chắc chắn muốn đăng xuất khỏi Càn Khôn Các?')) {
        emit('logout')
      }
    }

    onMounted(() => {
      if (props.isModal) {
        window.addEventListener('keydown', handleKeydown)
        document.body.style.overflow = 'hidden'
      }
    })

    onUnmounted(() => {
      if (props.isModal) {
        window.removeEventListener('keydown', handleKeydown)
        document.body.style.overflow = ''
      }
    })

    return {
      handleBackdropClick,
      confirmLogout
    }
  }
}
</script>

<style scoped>
/* ─── MODAL BACKDROP & CONTAINER ─── */
.profile-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(6, 14, 32, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-md, 1rem);
  overflow-y: auto;
}

@media (min-width: 768px) {
  .profile-modal-backdrop {
    padding: var(--space-xl, 2rem) var(--space-md, 1rem);
  }
}

.profile-modal-dialog {
  width: 100%;
  max-width: 76rem;
  background: #0b1326;
  border: 1px solid rgba(125, 214, 204, 0.2);
  border-radius: var(--radius-xl, 1.5rem);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.7), 0 0 32px rgba(125, 214, 204, 0.1);
  padding: var(--space-lg, 1.5rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 1.5rem);
  position: relative;
  margin: auto 0;
}

@media (min-width: 768px) {
  .profile-modal-dialog {
    padding: var(--space-xl, 2rem);
  }
}

/* ─── STANDALONE VIEW CONTAINER ─── */
.profile-view-root {
  width: 100%;
}

.profile-view-container {
  width: 100%;
  max-width: 76rem;
  margin: 0 auto;
  padding: var(--space-lg, 1.5rem) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 1.5rem);
}

/* ─── MAIN 2-COLUMN GRID ─── */
.profile-main-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg, 1.5rem);
}

@media (min-width: 1024px) {
  .profile-main-grid {
    grid-template-columns: 5fr 7fr;
  }
}

.grid-left-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 1.5rem);
}

.grid-right-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 1.5rem);
}

/* ─── LOGOUT SECURITY CARD ─── */
.logout-security-card {
  background: rgba(23, 31, 51, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 180, 171, 0.2);
  border-radius: var(--radius-lg, 1rem);
  padding: var(--space-lg, 1.5rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

@media (min-width: 640px) {
  .logout-security-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.logout-meta-group {
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
}

.logout-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(147, 0, 10, 0.3);
  color: var(--color-error, #ffb4ab);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logout-text-info {
  display: flex;
  flex-direction: column;
}

.logout-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.logout-subtitle {
  font-size: 12px;
  color: var(--color-on-surface-variant, #bdc9c6);
}

.btn-logout-barrier {
  height: 40px;
  padding: 0 var(--space-lg, 1.5rem);
  border-radius: var(--radius-md, 0.75rem);
  background: rgba(45, 52, 73, 0.6);
  border: 1px solid rgba(255, 180, 171, 0.3);
  color: var(--color-error, #ffb4ab);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 0.25rem);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.btn-logout-barrier:hover {
  background: rgba(147, 0, 10, 0.4);
  color: #ffdad6;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.3);
  transform: translateY(-1px);
}

.btn-logout-barrier:active {
  transform: scale(0.98);
}

/* ─── SECURITY BADGES ROW ─── */
.security-badges-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md, 1rem);
  padding-top: var(--space-xs, 0.25rem);
}

@media (min-width: 768px) {
  .security-badges-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

.sec-badge-card {
  padding: var(--space-md, 1rem);
  background: rgba(23, 31, 51, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md, 0.75rem);
  display: flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.sec-badge-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.sec-badge-icon.jade {
  color: var(--color-primary, #7dd6cc);
}

.sec-badge-icon.indigo {
  color: var(--color-secondary, #c4c1fb);
}

.sec-badge-icon.gold {
  color: var(--color-tertiary, #e3c370);
}

.sec-badge-info {
  display: flex;
  flex-direction: column;
}

.sec-badge-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.sec-badge-desc {
  font-size: 11px;
  color: var(--color-on-surface-variant, #bdc9c6);
}
</style>
