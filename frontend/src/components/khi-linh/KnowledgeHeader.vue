<template>
  <div class="knowledge-header">
    <div class="header-left">
      <!-- Khí Linh Mini Chibi Avatar Frame -->
      <div class="avatar-frame">
        <KhiLinhCharacter
          size="sm"
          state="IDLE"
          :show-aura="true"
          :show-rings="false"
          :show-status-dot="false"
        />
      </div>

      <!-- Identity & Mode Meta -->
      <div class="identity-meta">
        <div class="title-row">
          <h1 class="main-title">Khí Linh</h1>
          <span class="mode-badge">Chỉ Đọc</span>
        </div>
        <p class="subtitle">
          Cố Vấn &amp; Tra Cứu Thần Thức Tài Chính (Chế độ Tri Thức / Read-Only)
        </p>
      </div>
    </div>

    <div class="header-right">
      <!-- Status Beacon -->
      <div class="status-beacon-wrap">
        <span class="beacon-pulse" aria-hidden="true"></span>
        <span class="beacon-text">Bát Quái Động Phủ v4.2</span>
      </div>

      <!-- Reset / Clear Consultation Button -->
      <button
        type="button"
        class="btn-clear-chat"
        title="Bắt đầu phiên đàm đạo mới"
        aria-label="Xóa lịch sử hội thoại hiện tại"
        @click="$emit('clear-history')"
      >
        <span class="material-symbols-outlined text-[18px]" aria-hidden="true">restart_alt</span>
        <span class="hidden-mobile">Làm Mới</span>
      </button>
    </div>
  </div>
</template>

<script>
import KhiLinhCharacter from './KhiLinhCharacter.vue'

export default {
  name: 'KnowledgeHeader',
  components: {
    KhiLinhCharacter
  },
  emits: ['clear-history']
}
</script>

<style scoped>
.knowledge-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md, 1rem);
  padding: 0.875rem 1.5rem;
  background: rgba(34, 42, 61, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(136, 147, 145, 0.2);
  border-top-left-radius: 14px;
  border-top-right-radius: 14px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md, 1rem);
  min-width: 0;
}

.avatar-frame {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.identity-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.main-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #7dd6cc;
  letter-spacing: 0.02em;
  margin: 0;
  line-height: 1.3;
}

.mode-badge {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: rgba(68, 159, 150, 0.25);
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.3);
}

.subtitle {
  font-size: 0.775rem;
  color: #889391;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.status-beacon-wrap {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #bdc9c6;
  padding: 0.25rem 0.625rem;
  background: rgba(19, 27, 46, 0.6);
  border-radius: 9999px;
  border: 1px solid rgba(125, 214, 204, 0.15);
}

.beacon-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #7dd6cc;
  box-shadow: 0 0 8px #7dd6cc;
  animation: pulseBeacon 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

@keyframes pulseBeacon {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(1.25);
  }
}

.beacon-text {
  font-family: inherit;
  font-weight: 500;
}

.btn-clear-chat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  background: rgba(45, 52, 73, 0.6);
  border: 1px solid rgba(136, 147, 145, 0.25);
  color: #dae2fd;
  font-size: 0.775rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-chat:hover {
  background: rgba(68, 159, 150, 0.2);
  border-color: rgba(125, 214, 204, 0.4);
  color: #7dd6cc;
}

@media (max-width: 640px) {
  .status-beacon-wrap {
    display: none;
  }
  .hidden-mobile {
    display: none;
  }
  .knowledge-header {
    padding: 0.75rem 1rem;
  }
}
</style>
