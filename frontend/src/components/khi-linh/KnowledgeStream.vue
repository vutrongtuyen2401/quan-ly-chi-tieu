<template>
  <div class="knowledge-stream" ref="streamContainer">
    <!-- Stream Date Pill -->
    <div class="date-pill-row">
      <span class="date-pill">
        Hôm nay • {{ formattedTodayDate }}
      </span>
    </div>

    <!-- Message List -->
    <div class="messages-container">
      <template v-for="(msg, idx) in messages" :key="idx">
        <!-- 1. User Message (Right Aligned) -->
        <div v-if="msg.role === 'user'" class="message-row user-row">
          <div class="bubble-meta-col user-meta">
            <div class="user-bubble">
              <p class="bubble-text">{{ msg.text }}</p>
            </div>
            <span class="bubble-timestamp">
              {{ userName || 'Đạo Hữu' }}
            </span>
          </div>

          <!-- User Initial Avatar Orb -->
          <div class="user-avatar-orb" :title="userName || 'Đạo Hữu'">
            <span>{{ userInitial }}</span>
          </div>
        </div>

        <!-- 2. Khí Linh Response (Left Aligned) -->
        <div v-else class="message-row ai-row">
          <!-- Khí Linh Chibi Avatar -->
          <div class="ai-avatar-wrap">
            <KhiLinhCharacter
              size="sm"
              state="IDLE"
              :show-aura="true"
              :show-rings="false"
              :show-status-dot="false"
            />
          </div>

          <div class="bubble-meta-col ai-meta">
            <div class="ai-identity-badge-row">
              <span class="ai-name">Khí Linh</span>
              <span class="ai-rank-badge">Thần Thức Cấp 7</span>
            </div>

            <div class="ai-bubble">
              <div class="ai-rich-content" v-html="formatResponseText(msg.text)"></div>

              <!-- Source / Context Attribution Tag -->
              <div class="ai-source-tag">
                <span class="material-symbols-outlined text-[14px]" aria-hidden="true">verified</span>
                <span>Phản hồi từ Thần Thức Bát Quái • Tri Thức RAG</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 3. Thinking / Processing State -->
      <div v-if="loading" class="message-row ai-row thinking-row">
        <div class="ai-avatar-wrap pulse-glow">
          <KhiLinhCharacter
            size="sm"
            state="THINKING"
            :show-aura="true"
            :show-rings="false"
            :show-status-dot="false"
          />
        </div>

        <div class="bubble-meta-col ai-meta">
          <div class="ai-identity-badge-row">
            <span class="ai-name">Khí Linh</span>
            <span class="ai-rank-badge thinking">Đang Tra Cứu</span>
          </div>

          <div class="ai-bubble thinking-bubble">
            <div class="thinking-spinner-wrap">
              <span class="celestial-rune-spin">☯</span>
            </div>
            <div class="thinking-text-group">
              <span class="thinking-title">Khí Linh đang tra cứu linh tịch tài chính...</span>
              <span class="thinking-sub">Thần thức đang tính toán sổ sách và kết nối kho tri thức Bát Quái</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, watch } from 'vue'
import KhiLinhCharacter from './KhiLinhCharacter.vue'

export default {
  name: 'KnowledgeStream',
  components: {
    KhiLinhCharacter
  },
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    userName: {
      type: String,
      default: 'Đạo Hữu'
    }
  },
  setup(props) {
    const streamContainer = ref(null)

    const userInitial = computed(() => {
      const name = props.userName || 'Đạo Hữu'
      const parts = name.trim().split(/\s+/)
      return parts[parts.length - 1].charAt(0).toUpperCase() || 'Đ'
    })

    const formattedTodayDate = computed(() => {
      const now = new Date()
      const day = String(now.getDate()).padStart(2, '0')
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const year = now.getFullYear()
      return `Ngày ${day} Tháng ${month}, Năm ${year}`
    })

    function formatResponseText(text) {
      if (!text) return ''
      let safe = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong class="hl-bold">$1</strong>')
      safe = safe.replace(/\*(.*?)\*/g, '<em class="hl-italic">$1</em>')
      safe = safe.replace(/`([^`]+)`/g, '<code class="inline-rune-code">$1</code>')
      safe = safe.replace(/(\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*(?:₫|VNĐ|VND|đồng|đ|linh thạch))/gi, '<span class="hl-currency">$1</span>')
      safe = safe.replace(/\n/g, '<br/>')

      return safe
    }

    function scrollToBottom() {
      nextTick(() => {
        if (streamContainer.value) {
          streamContainer.value.scrollTop = streamContainer.value.scrollHeight
        }
      })
    }

    watch(() => props.messages.length, () => {
      scrollToBottom()
    })

    watch(() => props.loading, (newVal) => {
      if (newVal) scrollToBottom()
    })

    return {
      streamContainer,
      userInitial,
      formattedTodayDate,
      formatResponseText,
      scrollToBottom
    }
  }
}
</script>

<style scoped>
.knowledge-stream {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-height: 420px;
  max-height: 640px;
  scroll-behavior: smooth;
}

/* Custom subtle scrollbar */
.knowledge-stream::-webkit-scrollbar {
  width: 6px;
}
.knowledge-stream::-webkit-scrollbar-track {
  background: rgba(11, 19, 38, 0.4);
}
.knowledge-stream::-webkit-scrollbar-thumb {
  background: rgba(125, 214, 204, 0.25);
  border-radius: 9999px;
}
.knowledge-stream::-webkit-scrollbar-thumb:hover {
  background: rgba(125, 214, 204, 0.5);
}

.date-pill-row {
  display: flex;
  justify-content: center;
  margin: 0.25rem 0;
}

.date-pill {
  display: inline-block;
  padding: 0.25rem 0.875rem;
  border-radius: 9999px;
  background: rgba(45, 52, 73, 0.5);
  border: 1px solid rgba(136, 147, 145, 0.2);
  color: #889391;
  font-size: 0.75rem;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  width: 100%;
}

/* User Message */
.user-row {
  justify-content: flex-end;
  padding-left: 2.5rem;
}

.user-meta {
  align-items: flex-end;
  max-width: 80%;
}

.user-bubble {
  background: #444173;
  color: #dae2fd;
  padding: 0.875rem 1.125rem;
  border-radius: 14px;
  border-top-right-radius: 2px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(196, 193, 251, 0.2);
}

.user-bubble .bubble-text {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #ffffff;
  word-break: break-word;
}

.bubble-timestamp {
  font-size: 0.725rem;
  color: #889391;
  margin-top: 0.25rem;
  padding-right: 0.25rem;
}

.user-avatar-orb {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #c4c1fb;
  color: #2d2a5b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  box-shadow: 0 2px 8px rgba(196, 193, 251, 0.3);
  flex-shrink: 0;
}

/* AI Message */
.ai-row {
  justify-content: flex-start;
  padding-right: 2.5rem;
}

.ai-avatar-wrap {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-meta {
  align-items: flex-start;
  max-width: 85%;
}

.bubble-meta-col {
  display: flex;
  flex-direction: column;
}

.ai-identity-badge-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.ai-name {
  font-size: 0.875rem;
  font-weight: 700;
  color: #7dd6cc;
}

.ai-rank-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  background: rgba(34, 42, 61, 0.8);
  border: 1px solid rgba(125, 214, 204, 0.25);
  color: #bdc9c6;
  font-size: 0.7rem;
  font-weight: 500;
}

.ai-rank-badge.thinking {
  background: rgba(227, 195, 112, 0.15);
  border-color: rgba(227, 195, 112, 0.35);
  color: #e3c370;
}

.ai-bubble {
  background: #171f33;
  border: 1px solid rgba(136, 147, 145, 0.22);
  border-radius: 14px;
  border-top-left-radius: 2px;
  padding: 1rem 1.25rem;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ai-rich-content {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #dae2fd;
  word-break: break-word;
}

.ai-rich-content :deep(.hl-bold) {
  color: #ffffff;
  font-weight: 600;
}

.ai-rich-content :deep(.hl-italic) {
  color: #7dd6cc;
  font-style: italic;
}

.ai-rich-content :deep(.hl-currency) {
  color: #e3c370;
  font-weight: 600;
  font-family: monospace;
}

.ai-source-tag {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.725rem;
  color: #889391;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(136, 147, 145, 0.15);
}

/* Thinking Bubble */
.thinking-bubble {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  background: rgba(23, 31, 51, 0.85);
  border-color: rgba(125, 214, 204, 0.3);
}

.thinking-spinner-wrap {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(125, 214, 204, 0.12);
  border: 1px solid rgba(125, 214, 204, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.celestial-rune-spin {
  font-size: 1.125rem;
  color: #7dd6cc;
  display: inline-block;
  animation: runeSpin 3s linear infinite;
}

@keyframes runeSpin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.thinking-text-group {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.thinking-title {
  font-size: 0.825rem;
  font-weight: 600;
  color: #7dd6cc;
}

.thinking-sub {
  font-size: 0.725rem;
  color: #889391;
}

.pulse-glow {
  animation: avatarPulse 2s infinite ease-in-out;
}

@keyframes avatarPulse {
  0%, 100% {
    box-shadow: 0 0 12px rgba(125, 214, 204, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(125, 214, 204, 0.65);
  }
}

@media (max-width: 640px) {
  .knowledge-stream {
    padding: 0.75rem;
    max-height: 520px;
  }
  .user-row {
    padding-left: 0.5rem;
  }
  .ai-row {
    padding-right: 0.5rem;
  }
  .user-meta, .ai-meta {
    max-width: 90%;
  }
}
</style>
