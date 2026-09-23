<template>
  <div class="knowledge-intro-card">
    <!-- Ambient glow circle -->
    <div class="intro-glow-orb" aria-hidden="true"></div>

    <div class="intro-content-row">
      <!-- Chibi Avatar with Celestial Halo Frame -->
      <div class="character-visual-wrap">
        <KhiLinhCharacter
          size="lg"
          state="IDLE"
          :show-aura="true"
          :show-rings="true"
          :show-status-dot="true"
        />
      </div>

      <!-- Info & Welcoming Address -->
      <div class="intro-meta-col">
        <div class="badges-row">
          <h2 class="spirit-name">Khí Linh Động Phủ</h2>
          <span class="badge-pill jade">Tri Thức RAG Sẵn Sàng</span>
          <span class="badge-pill gold">Độ Nhạy: Thần Thức Cấp 7</span>
        </div>
        <p class="greeting-text">
          Thiện tai {{ userName || 'Ký Chủ' }}! Khí Linh đã sẵn sàng mở kho tàng thư tịch tài chính. Ta có thể tra cứu giao dịch, số dư các ví, ngân sách, nợ nần và giải đáp mọi quy tắc tu luyện tài chính một cách chuẩn xác nhất.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import KhiLinhCharacter from './KhiLinhCharacter.vue'

export default {
  name: 'KnowledgeIntroCard',
  components: {
    KhiLinhCharacter
  },
  props: {
    userName: {
      type: String,
      default: 'Ký Chủ'
    }
  }
}
</script>

<style scoped>
.knowledge-intro-card {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(34, 42, 61, 0.95) 0%, rgba(23, 31, 51, 0.9) 100%);
  border: 1px solid rgba(125, 214, 204, 0.28);
  padding: 1.125rem 1.25rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  margin-bottom: 0.5rem;
}

.intro-glow-orb {
  position: absolute;
  right: -2rem;
  bottom: -2rem;
  width: 9rem;
  height: 9rem;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.18) 0%, rgba(125, 214, 204, 0) 70%);
  border-radius: 50%;
  filter: blur(20px);
  pointer-events: none;
}

.intro-content-row {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.character-visual-wrap {
  position: relative;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.intro-meta-col {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
}

.badges-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.spirit-name {
  font-size: 0.975rem;
  font-weight: 700;
  color: #dae2fd;
  margin: 0;
}

.badge-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
}

.badge-pill.jade {
  background: rgba(125, 214, 204, 0.15);
  color: #7dd6cc;
  border: 1px solid rgba(125, 214, 204, 0.3);
}

.badge-pill.gold {
  background: rgba(227, 195, 112, 0.15);
  color: #e3c370;
  border: 1px solid rgba(227, 195, 112, 0.3);
}

.greeting-text {
  font-size: 0.825rem;
  line-height: 1.5;
  color: #bdc9c6;
  margin: 0;
}

@media (max-width: 640px) {
  .intro-content-row {
    flex-direction: column;
    text-align: center;
  }
  .badges-row {
    justify-content: center;
  }
}
</style>
