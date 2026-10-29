<template>
  <div class="knowledge-prompt-bar-section">
    <!-- Quick Prompt Suggestions Ribbon -->
    <div class="prompt-pills-ribbon">
      <div class="ribbon-label">
        <span class="material-symbols-outlined text-[15px] text-jade" aria-hidden="true">bolt</span>
        <span>Gợi ý pháp vấn:</span>
        <button
          v-if="hasCustomSuggestions"
          type="button"
          class="btn-clear-suggestions"
          title="Xóa toàn bộ lịch sử gợi ý pháp vấn"
          @click="$emit('clear-suggestions')"
        >
          <span class="material-symbols-outlined text-[14px]">delete_sweep</span>
          <span>Xóa Lịch Sử</span>
        </button>
      </div>

      <div class="pills-scroll-track">
        <div
          v-for="(chip, i) in displayedQuestions"
          :key="i"
          class="prompt-chip-pill"
        >
          <button
            type="button"
            class="prompt-chip-text"
            :disabled="loading"
            @click="$emit('send-message', chip)"
          >
            {{ chip }}
          </button>
          <button
            v-if="hasCustomSuggestions"
            type="button"
            class="chip-remove-btn"
            :title="`Xóa '${chip}' khỏi lịch sử gợi ý`"
            @click.stop="$emit('delete-suggestion', chip)"
          >
            <span class="material-symbols-outlined text-[12px]">close</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Chat Input Area -->
    <div class="input-action-bar">
      <div class="input-wrapper">
        <input
          v-model="inputText"
          type="text"
          class="knowledge-text-input"
          placeholder="Hỏi Khí Linh về tình hình tài chính, báo cáo hoặc quy tắc tu luyện..."
          :disabled="loading"
          @keyup.enter="handleSend"
        />

        <!-- Optional Voice Mic Indicator -->
        <button
          v-if="speechSupported"
          type="button"
          class="input-mic-btn"
          :class="{ listening: isListening }"
          :title="isListening ? 'Đang lắng nghe...' : 'Nhập lệnh bằng giọng nói'"
          aria-label="Nhập giọng nói"
          @click="toggleSpeech"
        >
          <span class="material-symbols-outlined text-[20px]" aria-hidden="true">
            {{ isListening ? 'mic' : 'mic_none' }}
          </span>
        </button>
      </div>

      <button
        type="button"
        class="btn-send-command"
        :disabled="loading || !inputText.trim()"
        @click="handleSend"
      >
        <span v-if="loading" class="material-symbols-outlined spin-icon text-[18px]">progress_activity</span>
        <span v-else class="material-symbols-outlined text-[18px]" aria-hidden="true">send</span>
        <span>{{ loading ? 'Đang gửi...' : 'Truyền Lệnh' }}</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'KnowledgePromptBar',
  props: {
    suggestedQuestions: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['send-message', 'clear-suggestions', 'delete-suggestion'],
  setup(props, { emit }) {
    const inputText = ref('')
    const isListening = ref(false)
    const speechSupported = ref(false)
    let recognition = null

    const defaultQuestions = [
      'Giao dịch mới nhất của ta là gì?',
      'Ta đang có tổng cộng bao nhiêu tiền?',
      'Tháng này ta đã chi bao nhiêu?',
      'Hạn mức ăn uống còn bao nhiêu?'
    ]

    const hasCustomSuggestions = computed(() => {
      return Boolean(props.suggestedQuestions && props.suggestedQuestions.length > 0)
    })

    const displayedQuestions = computed(() => {
      if (props.suggestedQuestions && props.suggestedQuestions.length > 0) {
        return props.suggestedQuestions
      }
      return defaultQuestions
    })

    function handleSend() {
      if (!inputText.value.trim() || props.loading) return
      const msg = inputText.value.trim()
      inputText.value = ''
      emit('send-message', msg)
    }

    function toggleSpeech() {
      if (!recognition) return
      if (isListening.value) {
        recognition.stop()
        isListening.value = false
      } else {
        try {
          recognition.start()
          isListening.value = true
        } catch (e) {
          console.warn('Speech recognition error:', e)
        }
      }
    }

    onMounted(() => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRecognition) {
        speechSupported.value = true
        try {
          recognition = new SpeechRecognition()
          recognition.continuous = false
          recognition.lang = 'vi-VN'
          recognition.interimResults = false

          recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript
            if (transcript) {
              inputText.value = transcript
              isListening.value = false
            }
          }

          recognition.onerror = () => {
            isListening.value = false
          }

          recognition.onend = () => {
            isListening.value = false
          }
        } catch (e) {
          speechSupported.value = false
        }
      }
    })

    onUnmounted(() => {
      if (recognition && isListening.value) {
        try { recognition.stop() } catch {}
      }
    })

    return {
      inputText,
      displayedQuestions,
      hasCustomSuggestions,
      isListening,
      speechSupported,
      handleSend,
      toggleSpeech
    }
  }
}
</script>

<style scoped>
.knowledge-prompt-bar-section {
  display: flex;
  flex-direction: column;
  background: rgba(34, 42, 61, 0.8);
  border-top: 1px solid rgba(136, 147, 145, 0.2);
  border-bottom-left-radius: 14px;
  border-bottom-right-radius: 14px;
  overflow: hidden;
}

/* Quick Prompt Ribbon */
.prompt-pills-ribbon {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1.25rem;
  background: rgba(23, 31, 51, 0.6);
  border-bottom: 1px solid rgba(136, 147, 145, 0.15);
  overflow-x: auto;
}

.prompt-pills-ribbon::-webkit-scrollbar {
  display: none;
}

.ribbon-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #889391;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.text-jade {
  color: #7dd6cc;
}

.pills-scroll-track {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: nowrap;
}

.prompt-chip {
  font-family: inherit;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  background: rgba(45, 52, 73, 0.7);
  border: 1px solid rgba(136, 147, 145, 0.25);
  color: #dae2fd;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.prompt-chip:hover:not(:disabled) {
  background: rgba(68, 159, 150, 0.25);
  border-color: rgba(125, 214, 204, 0.4);
  color: #7dd6cc;
  transform: translateY(-1px);
}

.prompt-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Input Action Bar */
.input-action-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
}

.input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.knowledge-text-input {
  font-family: inherit;
  width: 100%;
  height: 44px;
  background: rgba(6, 14, 32, 0.85);
  border: 1px solid rgba(136, 147, 145, 0.3);
  border-radius: 12px;
  padding: 0 2.75rem 0 1rem;
  color: #dae2fd;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3);
}

.knowledge-text-input:focus {
  border-color: #7dd6cc;
  box-shadow: 0 0 0 1px rgba(125, 214, 204, 0.4), inset 0 2px 6px rgba(0, 0, 0, 0.3);
}

.knowledge-text-input::placeholder {
  color: #889391;
}

.input-mic-btn {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #889391;
  cursor: pointer;
  transition: all 0.2s ease;
}

.input-mic-btn:hover {
  color: #7dd6cc;
  background: rgba(125, 214, 204, 0.1);
}

.input-mic-btn.listening {
  color: #ffb4ab;
  animation: micPulse 1.5s infinite;
}

@keyframes micPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

.btn-send-command {
  font-family: inherit;
  height: 44px;
  padding: 0 1.25rem;
  border-radius: 12px;
  background: #7dd6cc;
  color: #003733;
  border: none;
  font-size: 0.875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(125, 214, 204, 0.3);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  flex-shrink: 0;
}

.btn-send-command:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(125, 214, 204, 0.45);
}

.btn-send-command:active:not(:disabled) {
  transform: scale(0.97);
}

.btn-send-command:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .input-action-bar {
    padding: 0.75rem;
    gap: 0.5rem;
  }
  .prompt-pills-ribbon {
    padding: 0.5rem 0.75rem;
  }
  .btn-send-command {
    padding: 0 0.875rem;
  }
}

.btn-clear-suggestions {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 8px;
  padding: 2px 7px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 6px;
  color: #fca5a5;
  font-size: 0.68rem;
  font-weight: 500;
  cursor: pointer;
  text-transform: none;
  letter-spacing: normal;
  transition: all 0.2s ease;
}

.btn-clear-suggestions:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
  color: #ffffff;
}

.prompt-chip-pill {
  display: inline-flex;
  align-items: center;
  background: rgba(45, 52, 73, 0.7);
  border: 1px solid rgba(136, 147, 145, 0.25);
  border-radius: 9999px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.prompt-chip-pill:hover {
  background: rgba(68, 159, 150, 0.25);
  border-color: rgba(125, 214, 204, 0.4);
  transform: translateY(-1px);
}

.prompt-chip-text {
  font-family: inherit;
  padding: 0.35rem 0.65rem 0.35rem 0.75rem;
  background: transparent;
  border: none;
  color: #dae2fd;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.2s ease;
}

.prompt-chip-pill:hover .prompt-chip-text {
  color: #7dd6cc;
}

.prompt-chip-text:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chip-remove-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-right: 6px;
  padding: 0;
  background: rgba(148, 163, 184, 0.2);
  border: none;
  border-radius: 50%;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip-remove-btn:hover {
  background: rgba(239, 68, 68, 0.85);
  color: #ffffff;
}

</style>
