<template>
  <div class="auth-realm-stitch" :class="{ 'modern-mode': currentTheme === 'modern' }">
    <!-- Ambient Sleek Vignette / Glow Orbs -->
    <div class="auth-ambient-glows" aria-hidden="true">
      <div class="glow-orb glow-orb-top"></div>
      <div class="glow-orb glow-orb-right"></div>
      <div class="glow-orb glow-orb-bottom"></div>
      <div class="glow-vignette"></div>
    </div>

    <div class="auth-layout-container">
      <!-- Top Brand Identity Header -->
      <header class="auth-brand-header">
        <div class="auth-header-top-row">
          <div class="auth-emblem-wrap">
            <span class="auth-yin-yang">☯</span>
          </div>
          <button
            id="btn-toggle-theme-login"
            class="auth-theme-btn"
            @click="$emit('switch-theme')"
            :title="currentTheme === 'modern' ? 'Chuyển sang Đạo Quán Tu Tiên' : 'Chuyển sang Giao Diện Hiện Đại'"
            type="button"
          >
            <span>{{ currentTheme === 'modern' ? '☀️ Giao Diện Sáng' : '🌙 Giao Diện Tối' }}</span>
          </button>
        </div>

        <h1 class="auth-brand-title">CÀN KHÔN LINH THẠCH CÁC</h1>
        <p class="auth-brand-subtitle">Hệ Thống Quản Lý Tài Chính & Khí Vận Tu Tiên</p>
      </header>

      <!-- Main Content Area with Mascot & Active Auth Card -->
      <main class="auth-main-content">
        <!-- Khí Linh Mascot Companion Visual -->
        <div class="mascot-companion-wrap">
          <div class="mascot-avatar-container">
            <!-- Subtle Jade & Purple Halo Glow -->
            <div class="mascot-halo-glow"></div>
            <!-- Circular Mascot Badge -->
            <div class="mascot-avatar-circle">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAuB9vPTXf7CrsJQY9wa0P5NDWIzup2RMcoeetiVtiztI5Eru0vk_dg0NyaXvOyX0501ZM0v4N1sMGQd9buuEVfcFJE0jvz94IGTEbIYkaYOySnbIT93zhCop7HU-DHrw6oMLrzQ24bTP1idQIlMZKC2v7KGjsdXxOLeE4H7qPsit9Nnx2rk78uFXzQthrSqSNOjugSy0Fee5ELDz7OprY4ht_7Z6iCWRtYilsEEuAwrtAwwEk5Ygvypp-YeK0qHifYQs"
                alt="Khí Linh"
                class="mascot-img"
                loading="eager"
              />
            </div>
            <!-- Active Status Beacon -->
            <span class="mascot-status-ping">
              <span class="ping-wave"></span>
              <span class="ping-dot"></span>
            </span>
          </div>
          <div class="mascot-meta">
            <span class="mascot-name">Khí Linh</span>
            <span class="mascot-dot">•</span>
            <span class="mascot-role">Hộ trì tài chính</span>
          </div>
        </div>

        <!-- Auth Card Slot -->
        <div class="auth-card-wrapper">
          <slot />
        </div>
      </main>

      <!-- Footer Trust & Security Note -->
      <footer class="auth-footer">
        <div class="auth-footer-trust">
          <span class="material-symbols-outlined trust-icon">verified_user</span>
          <span>Bảo mật bởi cơ chế Token Versioning &amp; Bản Mệnh Hồn Đăng</span>
        </div>
        <p class="auth-footer-copy">
          © 2025 Càn Khôn Linh Thạch Các. All spiritual assets preserved.
        </p>
      </footer>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentTheme: {
    type: String,
    default: 'xianxia'
  }
})

defineEmits(['switch-theme'])
</script>

<style scoped>
.auth-realm-stitch {
  min-height: 100vh;
  width: 100%;
  background-color: #0b1326;
  color: #dae2fd;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  position: relative;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* ─── AMBIENT GLOWS & VIGNETTE ─── */
.auth-ambient-glows {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(140px);
}

.glow-orb-top {
  top: -140px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 350px;
  background: rgba(43, 138, 130, 0.16);
}

.glow-orb-right {
  top: 30%;
  right: -90px;
  width: 450px;
  height: 450px;
  background: rgba(68, 65, 115, 0.22);
  filter: blur(160px);
}

.glow-orb-bottom {
  bottom: -90px;
  left: -80px;
  width: 500px;
  height: 500px;
  background: rgba(15, 23, 42, 0.85);
  filter: blur(120px);
}

.glow-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 40%, transparent 20%, #060e20 95%);
  opacity: 0.85;
}

/* ─── LAYOUT CONTAINER ─── */
.auth-layout-container {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
  padding: 2rem 1rem;
  max-width: 100%;
  box-sizing: border-box;
}

@media (min-width: 768px) {
  .auth-layout-container {
    padding: 2.5rem 1.5rem;
  }
}

/* ─── TOP BRAND HEADER ─── */
.auth-brand-header {
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.auth-header-top-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.auth-emblem-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-yin-yang {
  font-size: 26px;
  color: #7dd6cc;
  filter: drop-shadow(0 0 10px rgba(125, 214, 204, 0.6));
  animation: rotateEmblem 30s linear infinite;
  display: inline-block;
}

@keyframes rotateEmblem {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.auth-theme-btn {
  background: rgba(19, 27, 46, 0.85);
  border: 1px solid rgba(125, 214, 204, 0.3);
  color: #dae2fd;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.auth-theme-btn:hover {
  border-color: #7dd6cc;
  background: rgba(43, 138, 130, 0.2);
  color: #ffffff;
}

.auth-brand-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #ffffff;
  text-transform: uppercase;
  margin: 0;
}

@media (min-width: 768px) {
  .auth-brand-title {
    font-size: 1.45rem;
  }
}

.auth-brand-subtitle {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  letter-spacing: 0.02em;
}

/* ─── MAIN CONTENT ─── */
.auth-main-content {
  width: 100%;
  max-width: 440px;
  margin: auto auto;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ─── MASCOT COMPANION VISUAL ─── */
.mascot-companion-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.25rem;
  user-select: none;
}

.mascot-avatar-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mascot-halo-glow {
  position: absolute;
  inset: -6px;
  border-radius: 9999px;
  background: linear-gradient(135deg, rgba(43, 138, 130, 0.5), rgba(125, 214, 204, 0.3), rgba(196, 193, 251, 0.4));
  filter: blur(8px);
  transition: all 0.5s ease;
}

.mascot-avatar-circle {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 9999px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: #131b2e;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
}

.mascot-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top;
  border-radius: 9999px;
}

.mascot-status-ping {
  position: absolute;
  bottom: 0;
  right: 0;
  display: flex;
  width: 14px;
  height: 14px;
}

.ping-wave {
  position: absolute;
  display: inline-flex;
  width: 100%;
  height: 100%;
  border-radius: 9999px;
  background: #7dd6cc;
  opacity: 0.75;
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.ping-dot {
  position: relative;
  display: inline-flex;
  width: 14px;
  height: 14px;
  border-radius: 9999px;
  background: #2b8a82;
  border: 2px solid #0b1326;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.mascot-meta {
  margin-top: 0.5rem;
  font-size: 12px;
  font-weight: 500;
  color: #cbd5e1;
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.02em;
}

.mascot-name {
  color: #7dd6cc;
  font-weight: 600;
}

.mascot-dot {
  color: #64748b;
}

.mascot-role {
  color: #94a3b8;
  font-weight: 400;
}

/* ─── CARD WRAPPER ─── */
.auth-card-wrapper {
  width: 100%;
}

/* ─── FOOTER ─── */
.auth-footer {
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
  text-align: center;
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.auth-footer-trust {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: #94a3b8;
}

.trust-icon {
  font-size: 16px;
  color: #7dd6cc;
}

.auth-footer-copy {
  font-size: 11px;
  color: #64748b;
  margin: 0;
}

/* ─── MODERN MODE OVERRIDES ─── */
.modern-mode {
  background-color: #f1f5f9;
  color: #1e293b;
}
.modern-mode .glow-vignette {
  background: radial-gradient(circle at 50% 40%, transparent 40%, #e2e8f0 95%);
}
.modern-mode .auth-brand-title {
  color: #0f172a;
}
.modern-mode .auth-brand-subtitle {
  color: #475569;
}
.modern-mode .mascot-meta {
  color: #334155;
}
.modern-mode .mascot-role {
  color: #64748b;
}
.modern-mode .auth-footer-trust {
  color: #475569;
}
.modern-mode .auth-footer-copy {
  color: #94a3b8;
}
.modern-mode .auth-theme-btn {
  background: #ffffff;
  border-color: #cbd5e1;
  color: #0f172a;
}
</style>
