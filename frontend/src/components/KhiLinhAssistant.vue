<template>
  <div class="khi-linh-wrapper" :class="{ 'is-open': isOpen, 'is-minimized': isMinimized }">
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- P1: PERSISTENT FLOATING SPIRIT COMPANION ENTRY POINT       -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div
      v-if="!isOpen || isMinimized"
      class="khi-linh-floating-companion"
      :class="['state-' + agentState.toLowerCase(), { 'is-listening': isListening }]"
      @click="openAssistant"
      :title="'Khí Linh Tiên Trí — Trạng thái: ' + getStateLabel(agentState)"
      role="button"
      tabindex="0"
      @keydown.enter="openAssistant"
      @keydown.space.prevent="openAssistant"
      aria-label="Mở trợ lý Khí Linh AI"
    >
      <!-- Ethereal Spirit Glow Rings -->
      <div class="spirit-halo"></div>
      <div v-if="isListening" class="sound-wave-ring wave-1"></div>
      <div v-if="isListening" class="sound-wave-ring wave-2"></div>

      <!-- Chibi Celestial Spirit SVG -->
      <div class="spirit-chibi-body">
        <svg viewBox="0 0 100 100" class="spirit-svg" aria-hidden="true">
          <defs>
            <!-- Spirit Gradients -->
            <radialGradient id="spiritGrad" cx="45%" cy="40%" r="55%">
              <stop offset="0%" stop-color="#ffffff" />
              <stop offset="40%" stop-color="#e0f7f5" />
              <stop offset="85%" stop-color="#76dcd1" />
              <stop offset="100%" stop-color="#2b8a82" />
            </radialGradient>
            <radialGradient id="spiritHaloGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="rgba(232, 200, 116, 0.7)" />
              <stop offset="70%" stop-color="rgba(79, 168, 160, 0.4)" />
              <stop offset="100%" stop-color="rgba(79, 168, 160, 0)" />
            </radialGradient>
            <filter id="spiritGlow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          <!-- Halo Aura -->
          <circle cx="50" cy="50" r="46" fill="url(#spiritHaloGrad)" class="halo-circle" />

          <!-- Tiny Celestial Floating Clouds / Wings -->
          <path d="M16,56 C8,50 10,38 20,42 C20,32 32,32 34,44 Z" fill="rgba(255,255,255,0.85)" class="cloud-wing wing-left" />
          <path d="M84,56 C92,50 90,38 80,42 C80,32 68,32 66,44 Z" fill="rgba(255,255,255,0.85)" class="cloud-wing wing-right" />

          <!-- Spirit Orb Body -->
          <circle cx="50" cy="52" r="32" fill="url(#spiritGrad)" filter="url(#spiritGlow)" class="main-orb" />

          <!-- Yin-Yang Forehead Sigil -->
          <circle cx="50" cy="33" r="4.5" fill="#e8c874" opacity="0.9" />
          <circle cx="50" cy="33" r="2" fill="#2b8a82" />

          <!-- Cute Chibi Eyes (React to Agent State) -->
          <!-- SUCCESS: Joyful curved eyes -->
          <g v-if="agentState === 'SUCCESS'" class="eyes-success">
            <path d="M38,48 Q42,43 46,48" stroke="#1a3a5c" stroke-width="3" stroke-linecap="round" fill="none" />
            <path d="M54,48 Q58,43 62,48" stroke="#1a3a5c" stroke-width="3" stroke-linecap="round" fill="none" />
          </g>
          <!-- THINKING: Looking up in thought -->
          <g v-else-if="agentState === 'THINKING' || agentState === 'PLANNING'" class="eyes-thinking">
            <ellipse cx="43" cy="47" rx="3.5" ry="4.5" fill="#1a3a5c" />
            <circle cx="44" cy="45" r="1.5" fill="#ffffff" />
            <ellipse cx="59" cy="47" rx="3.5" ry="4.5" fill="#1a3a5c" />
            <circle cx="60" cy="45" r="1.5" fill="#ffffff" />
          </g>
          <!-- CONFIRMING: Wide alert eyes -->
          <g v-else-if="agentState === 'CONFIRMING'" class="eyes-confirming">
            <ellipse cx="42" cy="50" rx="4.5" ry="5.5" fill="#1a3a5c" />
            <circle cx="44" cy="48" r="2" fill="#ffffff" />
            <ellipse cx="58" cy="50" rx="4.5" ry="5.5" fill="#1a3a5c" />
            <circle cx="60" cy="48" r="2" fill="#ffffff" />
          </g>
          <!-- ERROR: Worried eyes -->
          <g v-else-if="agentState === 'ERROR'" class="eyes-error">
            <path d="M38,50 Q42,53 46,50" stroke="#c0392b" stroke-width="3" stroke-linecap="round" fill="none" />
            <path d="M54,50 Q58,53 62,50" stroke="#c0392b" stroke-width="3" stroke-linecap="round" fill="none" />
          </g>
          <!-- DEFAULT / IDLE / LISTENING: Cute blinking eyes -->
          <g v-else class="eyes-normal">
            <ellipse cx="42" cy="50" rx="3.5" ry="4.5" fill="#1a3a5c" class="eye-left" />
            <circle cx="43.5" cy="48.5" r="1.5" fill="#ffffff" />
            <ellipse cx="58" cy="50" rx="3.5" ry="4.5" fill="#1a3a5c" class="eye-right" />
            <circle cx="59.5" cy="48.5" r="1.5" fill="#ffffff" />
          </g>

          <!-- Rosy Blush -->
          <ellipse cx="34" cy="55" rx="3.5" ry="2" fill="rgba(255, 130, 150, 0.45)" />
          <ellipse cx="66" cy="55" rx="3.5" ry="2" fill="rgba(255, 130, 150, 0.45)" />

          <!-- Cute Smile Mouth -->
          <path v-if="agentState !== 'ERROR'" d="M47,56 Q50,60 53,56" stroke="#1a3a5c" stroke-width="2" stroke-linecap="round" fill="none" />
          <path v-else d="M47,58 Q50,55 53,58" stroke="#c0392b" stroke-width="2" stroke-linecap="round" fill="none" />

          <!-- Bottom Floating Clouds -->
          <path d="M30,76 Q40,70 50,75 Q60,70 70,76 Q60,84 50,81 Q40,84 30,76 Z" fill="rgba(255, 255, 255, 0.9)" />
        </svg>
      </div>

      <!-- State Status Badge on Companion -->
      <div class="companion-state-badge" :class="'badge-' + agentState.toLowerCase()">
        <span class="badge-icon">{{ getStateIcon(agentState) }}</span>
      </div>

      <!-- Floating Tooltip Prompt -->
      <div class="companion-tooltip" v-if="!isHoverMuted">
        <span class="tooltip-text">{{ getCompanionTooltip(agentState) }}</span>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- P0 & P1: KHÍ LINH INTERACTIVE SANCTUARY (DRAWER / PANEL)   -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div v-show="isOpen && !isMinimized" class="khi-linh-sanctuary">
      <!-- Sanctuary Header -->
      <div class="sanctuary-header">
        <div class="header-companion-avatar">
          <div class="mini-spirit-orb" :class="'state-' + agentState.toLowerCase()">
            <span>🔮</span>
          </div>
          <div class="header-titles">
            <div class="name-row">
              <h3 class="sanctuary-title">Khí Linh Tiên Trí</h3>
              <span class="dao-badge">AI Agent</span>
            </div>
            <!-- REAL AGENT STATE UI VISUAL BADGE -->
            <div class="real-agent-state-chip" :class="'state-' + agentState.toLowerCase()">
              <span class="pulse-dot"></span>
              <span class="state-text">{{ getStateLabel(agentState) }}</span>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <!-- P2: Audio TTS Toggle -->
          <button
            class="header-action-btn tts-btn"
            :class="{ active: ttsEnabled }"
            @click="toggleTTS"
            :title="ttsEnabled ? 'Tắt giọng nói Khí Linh' : 'Bật giọng nói Khí Linh'"
            aria-label="Bật/Tắt giọng đọc"
          >
            {{ ttsEnabled ? '🔊' : '🔇' }}
          </button>

          <!-- Clear History -->
          <button
            class="header-action-btn"
            @click="clearChat"
            title="Làm mới đàm đạo"
            aria-label="Làm mới trò chuyện"
          >
            🧹
          </button>

          <!-- Minimize Sanctuary -->
          <button
            class="header-action-btn"
            @click="isMinimized = true"
            title="Thu nhỏ Khí Linh"
            aria-label="Thu nhỏ"
          >
            🗕
          </button>

          <!-- Close Sanctuary -->
          <button
            class="header-action-btn close-btn"
            @click="closeAssistant"
            title="Đóng giao diện"
            aria-label="Đóng giao diện"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- Listening Wave Banner (Active strictly when isListening is true) -->
      <div v-if="isListening" class="listening-banner">
        <div class="listening-anim-waves">
          <span></span><span></span><span></span><span></span><span></span>
        </div>
        <div class="listening-text">
          <strong>Khí Linh đang lắng nghe...</strong>
          <span class="listening-sub">Nói lệnh tài chính của đạo hữu (tiếng Việt)</span>
        </div>
        <button class="btn-stop-listening" @click="stopListening" title="Dừng thu âm">
          ⏹ Dừng
        </button>
      </div>

      <!-- Chat History Area -->
      <div class="sanctuary-body" ref="chatScrollEl">
        <!-- Welcome Card -->
        <div class="khi-linh-welcome-card">
          <div class="welcome-top">
            <span class="welcome-symbol">☯</span>
            <h4>Kính chào Ký Chủ!</h4>
          </div>
          <p class="welcome-desc">
            Ta là <strong>Khí Linh Tiên Trí</strong>, trợ lý đắc lực kết nối trực tiếp với Đạo Đường Càn Khôn.
            Đạo hữu có thể tra cứu tài chính hoặc ra lệnh ghi nhận bằng văn bản hoặc giọng nói.
          </p>
          <div class="welcome-shortcuts">
            <button
              v-for="tip in quickPromptList"
              :key="tip"
              class="quick-tip-chip"
              @click="selectPrompt(tip)"
            >
              {{ tip }}
            </button>
          </div>
        </div>

        <!-- Chat Bubble Stream -->
        <div
          v-for="(msg, idx) in messages"
          :key="'msg-' + idx"
          :class="['chat-bubble-row', msg.role === 'user' ? 'row-user' : 'row-ai']"
        >
          <div class="bubble-avatar-wrapper">
            <span class="bubble-avatar">{{ msg.role === 'user' ? '🧙' : '🔮' }}</span>
          </div>

          <div class="bubble-content-box">
            <div class="bubble-header-info">
              <span class="sender-name">{{ msg.role === 'user' ? 'Ký Chủ' : 'Khí Linh' }}</span>
              <span class="msg-time">{{ msg.time }}</span>
            </div>

            <!-- Message Text -->
            <div class="bubble-text" v-html="formatMessage(msg.text)"></div>

            <!-- ═══════════════════════════════════════════════════════════ -->
            <!-- P0: FINANCIAL CONFIRMATION UX (MANDATORY CONFIRMATION CARD)-->
            <!-- ═══════════════════════════════════════════════════════════ -->
            <div
              v-if="msg.confirmation && msg.confirmation.isPending"
              class="financial-confirmation-card"
            >
              <div class="confirmation-card-header">
                <span class="confirm-icon">✨</span>
                <span class="confirm-spirit-title">Khí Linh Xác Nhận</span>
              </div>

              <div class="confirmation-action-title">
                {{ getToolActionTitle(msg.confirmation.tool_name) }}
              </div>

              <div class="confirmation-amount-highlight">
                {{ formatCurrency(msg.confirmation.args?.amount) }}
              </div>

              <div class="confirmation-details-list">
                <div v-if="msg.confirmation.args?.note" class="detail-item">
                  <span class="detail-label">Nội dung:</span>
                  <strong class="detail-value">{{ msg.confirmation.args.note }}</strong>
                </div>

                <div v-if="msg.confirmation.args?.category_name" class="detail-item">
                  <span class="detail-label">Danh mục:</span>
                  <span class="detail-badge">{{ msg.confirmation.args.category_name }}</span>
                </div>

                <div v-if="msg.confirmation.args?.wallet_name" class="detail-item">
                  <span class="detail-label">Túi tiền:</span>
                  <span class="detail-badge wallet">{{ msg.confirmation.args.wallet_name }}</span>
                </div>

                <div v-if="msg.confirmation.args?.from_wallet_name" class="detail-item">
                  <span class="detail-label">Ví nguồn:</span>
                  <span class="detail-badge wallet">{{ msg.confirmation.args.from_wallet_name }}</span>
                </div>

                <div v-if="msg.confirmation.args?.to_wallet_name" class="detail-item">
                  <span class="detail-label">Ví đích:</span>
                  <span class="detail-badge wallet">{{ msg.confirmation.args.to_wallet_name }}</span>
                </div>

                <div v-if="msg.confirmation.args?.goal_name" class="detail-item">
                  <span class="detail-label">Mục tiêu:</span>
                  <span class="detail-badge">{{ msg.confirmation.args.goal_name }}</span>
                </div>
              </div>

              <!-- P0: Real Confirmation / Cancellation Action Buttons -->
              <div class="confirmation-button-group">
                <button
                  id="btn-khilinh-confirm"
                  class="btn-confirm-action"
                  :disabled="agentState === 'EXECUTING'"
                  @click="handleConfirmCard(msg)"
                >
                  <span v-if="agentState === 'EXECUTING'">⏳ Đang thực hiện...</span>
                  <span v-else>✅ Xác nhận</span>
                </button>

                <button
                  id="btn-khilinh-cancel"
                  class="btn-cancel-action"
                  :disabled="agentState === 'EXECUTING'"
                  @click="handleCancelCard(msg)"
                >
                  ❌ Hủy
                </button>
              </div>
            </div>

            <!-- SUCCESS EXECUTION BADGE (If transaction was completed) -->
            <div v-if="msg.toolExecuted" class="tool-executed-card">
              <span class="executed-icon">📜</span>
              <span class="executed-text">Đã ghi nhận thành công vào sổ sách Càn Khôn!</span>
            </div>
          </div>
        </div>

        <!-- Dynamic Agent State Indicators (THINKING / PLANNING / EXECUTING) -->
        <div v-if="agentState === 'THINKING' || agentState === 'PLANNING'" class="agent-working-indicator">
          <div class="working-spirit-icon">🔮</div>
          <div class="working-content">
            <span class="working-label">
              {{ agentState === 'PLANNING' ? 'Khí Linh đang lập kế hoạch thao tác...' : 'Khí Linh đang suy nghĩ...' }}
            </span>
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <div v-if="agentState === 'EXECUTING'" class="agent-working-indicator executing">
          <div class="working-spirit-icon spin-runes">⚡</div>
          <div class="working-content">
            <span class="working-label">Đang truyền chân khí thực hiện biến động...</span>
            <div class="progress-bar-xianxia"><div class="progress-fill"></div></div>
          </div>
        </div>
      </div>

      <!-- Live Voice Transcript Preview (While speaking) -->
      <div v-if="liveTranscript" class="live-transcript-box">
        <span class="mic-glyph">🎙️</span>
        <span class="transcript-text">{{ liveTranscript }}</span>
      </div>

      <!-- Quick Suggestion Bar -->
      <div v-if="activeSuggestions.length" class="quick-suggestions-bar">
        <button
          v-for="sug in activeSuggestions"
          :key="sug"
          class="suggestion-chip"
          @click="selectPrompt(sug)"
        >
          {{ sug }}
        </button>
      </div>

      <!-- Sanctuary Footer & Input Area -->
      <div class="sanctuary-footer">
        <div class="chat-input-row">
          <!-- Text Input Field -->
          <input
            ref="inputFieldEl"
            v-model="inputQuery"
            type="text"
            class="khi-linh-input"
            placeholder="Hỏi số dư, ghi nhận chi tiêu (vd: Ăn trưa 45k)..."
            :disabled="agentState === 'THINKING' || agentState === 'PLANNING' || agentState === 'EXECUTING'"
            @keyup.enter="handleSend"
          />

          <!-- P2: Microphone Button for Vietnamese STT -->
          <button
            id="btn-khilinh-mic"
            class="mic-action-btn"
            :class="{ 'recording': isListening }"
            :disabled="!speechSupported || agentState === 'EXECUTING'"
            @click="toggleListening"
            :title="isListening ? 'Dừng lắng nghe' : 'Nói lệnh bằng giọng nói (Tiếng Việt)'"
            aria-label="Nói lệnh bằng giọng nói"
          >
            <span v-if="isListening" class="mic-wave-icon">🔴</span>
            <span v-else class="mic-idle-icon">🎙️</span>
          </button>

          <!-- Send Text Button -->
          <button
            id="btn-khilinh-send"
            class="send-action-btn"
            :disabled="!inputQuery.trim() || agentState === 'THINKING' || agentState === 'PLANNING' || agentState === 'EXECUTING'"
            @click="handleSend"
            title="Gửi lệnh"
            aria-label="Gửi lệnh"
          >
            ⚡
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

export default {
  name: 'KhiLinhAssistant',
  props: {
    api: {
      type: Function,
      required: true
    },
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:isOpen', 'transactionCompleted', 'switchTab'],
  setup(props, { emit }) {
    // ─── AGENT STATE ─────────────────────────────
    // IDLE | THINKING | PLANNING | CONFIRMING | EXECUTING | SUCCESS | ERROR
    const agentState = ref('IDLE')
    const isMinimized = ref(false)
    const isHoverMuted = ref(false)

    // ─── CHAT & MESSAGES ──────────────────────────
    const messages = ref([])
    const inputQuery = ref('')
    const inputFieldEl = ref(null)
    const chatScrollEl = ref(null)
    const activeSuggestions = ref([
      'Ví tiền mặt còn bao nhiêu?',
      'Tháng này tôi tiêu bao nhiêu?',
      'Tôi vừa ăn sáng hết 50 nghìn.',
      'Chuyển 500 nghìn từ ví A sang ví B.'
    ])

    const quickPromptList = [
      '💵 Ví tiền mặt còn bao nhiêu?',
      '📊 Tháng này tôi tiêu bao nhiêu?',
      '🍜 Tôi vừa ăn sáng hết 50 nghìn',
      '🎯 Đưa 200k vào mục tiêu mua laptop',
      '📈 Tình hình ngân sách các danh mục'
    ]

    // ─── P2: VOICE / STT STATE ────────────────────
    const isListening = ref(false)
    const liveTranscript = ref('')
    const speechSupported = ref(false)
    let recognitionInstance = null

    // ─── P2: TTS STATE ────────────────────────────
    const ttsEnabled = ref(localStorage.getItem('khilinh_tts') === 'true')
    let synth = null

    // ─── INITIALIZATION ───────────────────────────
    onMounted(() => {
      // Check STT support
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRec) {
        speechSupported.value = true
        initSpeechRecognition(SpeechRec)
      } else {
        speechSupported.value = false
      }

      // Check TTS support
      if ('speechSynthesis' in window) {
        synth = window.speechSynthesis
      }

      // Initial greeting if empty
      if (messages.value.length === 0) {
        messages.value.push({
          role: 'ai',
          text: 'Kính chào Ký Chủ! Khí Linh Tiên Trí sẵn sàng phục mệnh. Đạo hữu cần tra cứu ngân lượng hay ghi nhận sổ sách hôm nay?',
          time: getCurrentTimeStr()
        })
      }
    })

    onUnmounted(() => {
      if (recognitionInstance) {
        try { recognitionInstance.abort() } catch (e) {}
      }
      if (synth) {
        try { synth.cancel() } catch (e) {}
      }
    })

    // Auto-scroll on new messages
    watch(
      () => messages.value.length,
      () => {
        nextTick(() => scrollToBottom())
      }
    )

    // When assistant opens, focus input
    watch(
      () => props.isOpen,
      (open) => {
        if (open) {
          isMinimized.value = false
          nextTick(() => {
            scrollToBottom()
            if (inputFieldEl.value) inputFieldEl.value.focus()
          })
        }
      }
    )

    // ─── OPEN / CLOSE HANDLERS ────────────────────
    function openAssistant() {
      emit('update:isOpen', true)
      isMinimized.value = false
    }

    function closeAssistant() {
      emit('update:isOpen', false)
    }

    function clearChat() {
      messages.value = [
        {
          role: 'ai',
          text: 'Sổ đàm đạo đã được dọn sạch. Khí Linh đã sẵn sàng cho mệnh lệnh mới của đạo hữu!',
          time: getCurrentTimeStr()
        }
      ]
      agentState.value = 'IDLE'
    }

    // ─── P0: SEND CHAT & REAL AGENT CORE FLOW ─────
    async function handleSend() {
      const q = inputQuery.value.trim()
      if (!q || agentState.value === 'THINKING' || agentState.value === 'EXECUTING') return

      inputQuery.value = ''
      liveTranscript.value = ''
      await processUserMessage(q)
    }

    function selectPrompt(prompt) {
      inputQuery.value = prompt
      handleSend()
    }

    async function processUserMessage(text) {
      // 1. Add user message to UI
      messages.value.push({
        role: 'user',
        text: text,
        time: getCurrentTimeStr()
      })
      await nextTick()
      scrollToBottom()

      // 2. Set Agent State to THINKING
      agentState.value = 'THINKING'

      try {
        // 3. Connect to REAL /api/ai/chat
        const { data } = await props.api.post(
          '/api/ai/chat',
          { message: text },
          { timeout: 25000 }
        )

        // 4. Update real state from Agent Core response
        if (data.state) {
          agentState.value = data.state
        } else {
          agentState.value = 'IDLE'
        }

        // Prepare confirmation object if present
        let confirmationObj = null
        if (data.state === 'CONFIRMING' && data.pending_confirmation) {
          confirmationObj = {
            isPending: true,
            tool_name: data.pending_confirmation.tool_name,
            args: data.pending_confirmation.args || {},
            summary: data.pending_confirmation.summary || ''
          }
        }

        // Add AI message
        messages.value.push({
          role: 'ai',
          text: data.response || 'Đã tiếp nhận mệnh lệnh.',
          time: getCurrentTimeStr(),
          confirmation: confirmationObj,
          toolExecuted: data.tool_executed || null
        })

        // Speak AI response if TTS is enabled
        if (ttsEnabled.value && data.response) {
          speakText(data.response)
        }

        // If financial mutation was confirmed and executed, emit event to refresh parent data
        if (data.state === 'SUCCESS' && data.tool_executed) {
          emit('transactionCompleted', {
            tool: data.tool_executed,
            result: data.tool_result
          })
        }
      } catch (err) {
        agentState.value = 'ERROR'
        const errMsg = err.code === 'ECONNABORTED'
          ? 'Tiên Trí phản hồi quá thời gian quy định do nghẽn mạng. Đạo hữu vui lòng gửi lại.'
          : (err.response?.data?.detail || 'Khí Linh tạm thời gặp trở ngại khi kết nối đạo đường.')

        messages.value.push({
          role: 'ai',
          text: '⚠️ ' + errMsg,
          time: getCurrentTimeStr()
        })
      } finally {
        await nextTick()
        scrollToBottom()
      }
    }

    // ─── P0: CONFIRMATION UX HANDLERS ─────────────
    async function handleConfirmCard(msg) {
      if (msg.confirmation) {
        msg.confirmation.isPending = false
      }
      agentState.value = 'EXECUTING'
      await processUserMessage('Xác nhận')
    }

    async function handleCancelCard(msg) {
      if (msg.confirmation) {
        msg.confirmation.isPending = false
      }
      agentState.value = 'IDLE'
      await processUserMessage('Hủy')
    }

    // ─── P2: SPEECH-TO-TEXT (STT) ─────────────────
    function initSpeechRecognition(SpeechRec) {
      try {
        recognitionInstance = new SpeechRec()
        recognitionInstance.lang = 'vi-VN'
        recognitionInstance.continuous = false
        recognitionInstance.interimResults = true

        recognitionInstance.onstart = () => {
          isListening.value = true
          agentState.value = 'LISTENING'
          liveTranscript.value = ''
        }

        recognitionInstance.onresult = (event) => {
          let interim = ''
          let final = ''

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              final += transcript
            } else {
              interim += transcript
            }
          }

          liveTranscript.value = final || interim
          if (final.trim()) {
            inputQuery.value = final.trim()
          }
        }

        recognitionInstance.onerror = (event) => {
          isListening.value = false
          agentState.value = 'IDLE'

          let userNotice = ''
          if (event.error === 'not-allowed') {
            userNotice = 'Đạo hữu chưa cấp quyền micro cho trình duyệt.'
          } else if (event.error === 'no-speech') {
            userNotice = 'Khí Linh chưa nghe rõ khẩu quyết, xin đạo hữu thử lại.'
          } else if (event.error === 'network') {
            userNotice = 'Trở ngại đường truyền khi nhận dạng giọng nói.'
          }

          if (userNotice) {
            messages.value.push({
              role: 'ai',
              text: '🎙️ ' + userNotice,
              time: getCurrentTimeStr()
            })
          }
        }

        recognitionInstance.onend = () => {
          isListening.value = false
          if (agentState.value === 'LISTENING') {
            agentState.value = 'IDLE'
          }

          // If transcript is available and valid, auto-submit
          const recognized = inputQuery.value.trim()
          if (recognized && recognized.length > 1) {
            handleSend()
          }
        }
      } catch (err) {
        speechSupported.value = false
      }
    }

    function toggleListening() {
      if (!speechSupported.value || !recognitionInstance) return

      if (isListening.value) {
        stopListening()
      } else {
        startListening()
      }
    }

    function startListening() {
      if (!recognitionInstance) return
      try {
        liveTranscript.value = ''
        recognitionInstance.start()
      } catch (err) {
        // If already started, stop then restart
        try {
          recognitionInstance.abort()
          recognitionInstance.start()
        } catch (e) {}
      }
    }

    function stopListening() {
      if (!recognitionInstance) return
      try {
        recognitionInstance.stop()
      } catch (err) {
        try { recognitionInstance.abort() } catch (e) {}
      }
      isListening.value = false
      if (agentState.value === 'LISTENING') {
        agentState.value = 'IDLE'
      }
    }

    // ─── P2: TEXT-TO-SPEECH (TTS) ─────────────────
    function toggleTTS() {
      ttsEnabled.value = !ttsEnabled.value
      localStorage.setItem('khilinh_tts', ttsEnabled.value.toString())
      if (!ttsEnabled.value && synth) {
        synth.cancel()
      }
    }

    function speakText(text) {
      if (!synth || !ttsEnabled.value) return

      try {
        synth.cancel()
        // Clean markdown & symbols for natural Vietnamese speech
        const cleanText = text
          .replace(/\*\*(.*?)\*\*/g, '$1')
          .replace(/[#*`_~]/g, '')
          .replace(/[👉✅⚠️❌🔮✨]/g, '')
          .replace(/VNĐ/g, 'đồng')
          .replace(/k\b/gi, ' nghìn')
          .trim()

        if (!cleanText) return

        const utter = new SpeechSynthesisUtterance(cleanText)
        utter.lang = 'vi-VN'
        utter.rate = 1.05
        utter.pitch = 1.1

        synth.speak(utter)
      } catch (err) {
        // Fallback: silent failure on TTS
      }
    }

    // ─── HELPERS & FORMATTERS ─────────────────────
    function scrollToBottom() {
      if (chatScrollEl.value) {
        chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight
      }
    }

    function getCurrentTimeStr() {
      const now = new Date()
      return now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0')
    }

    function formatCurrency(amount) {
      if (amount === undefined || amount === null) return '0 VNĐ'
      const num = Number(amount)
      if (isNaN(num)) return amount + ' VNĐ'
      return num.toLocaleString('vi-VN') + ' VNĐ'
    }

    function formatMessage(txt) {
      if (!txt) return ''
      // Escape HTML
      let sanitized = txt
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      // Bold **...**
      sanitized = sanitized.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Bullet points
      sanitized = sanitized.replace(/\n- (.*?)(?=\n|$)/g, '<br>• $1')
      // Newlines
      sanitized = sanitized.replace(/\n/g, '<br>')

      return sanitized
    }

    function getStateLabel(st) {
      switch (st) {
        case 'IDLE': return 'Đang chờ'
        case 'LISTENING': return 'Đang lắng nghe'
        case 'THINKING': return 'Đang suy nghĩ'
        case 'PLANNING': return 'Lập kế hoạch'
        case 'CONFIRMING': return 'Chờ xác nhận'
        case 'EXECUTING': return 'Đang thực hiện'
        case 'SUCCESS': return 'Đã hoàn tất'
        case 'ERROR': return 'Gặp trở ngại'
        default: return st
      }
    }

    function getStateIcon(st) {
      switch (st) {
        case 'IDLE': return '🟢'
        case 'LISTENING': return '🎙️'
        case 'THINKING': return '🔮'
        case 'PLANNING': return '📜'
        case 'CONFIRMING': return '⚠️'
        case 'EXECUTING': return '⚡'
        case 'SUCCESS': return '✅'
        case 'ERROR': return '❌'
        default: return '🟢'
      }
    }

    function getCompanionTooltip(st) {
      switch (st) {
        case 'LISTENING': return 'Khí Linh đang lắng nghe...'
        case 'THINKING': return 'Khí Linh đang suy nghĩ...'
        case 'CONFIRMING': return 'Cần đạo hữu xác nhận!'
        case 'EXECUTING': return 'Đang thực hiện...'
        case 'SUCCESS': return 'Đã hoàn tất thao tác!'
        case 'ERROR': return 'Có điều gì đó chưa ổn.'
        default: return 'Bấm để trò chuyện cùng Khí Linh!'
      }
    }

    function getToolActionTitle(toolName) {
      switch (toolName) {
        case 'create_expense': return 'Ghi nhận khoản chi'
        case 'create_income': return 'Ghi nhận khoản thu'
        case 'transfer_money': return 'Chuyển tiền liên ví'
        case 'saving_goal_deposit': return 'Nạp tiền mục tiêu tích lũy'
        default: return 'Xác nhận biến động tài chính'
      }
    }

    return {
      agentState,
      isMinimized,
      isHoverMuted,
      messages,
      inputQuery,
      inputFieldEl,
      chatScrollEl,
      activeSuggestions,
      quickPromptList,
      isListening,
      liveTranscript,
      speechSupported,
      ttsEnabled,
      openAssistant,
      closeAssistant,
      clearChat,
      handleSend,
      selectPrompt,
      handleConfirmCard,
      handleCancelCard,
      toggleListening,
      stopListening,
      toggleTTS,
      getStateLabel,
      getStateIcon,
      getCompanionTooltip,
      getToolActionTitle,
      formatCurrency,
      formatMessage
    }
  }
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   KHÍ LINH COMPONENT STYLES — CELESTIAL XIANXIA IDENTITY
   ═══════════════════════════════════════════════════════════════ */

/* ─── P1: PERSISTENT FLOATING COMPANION ─────────────────────── */
.khi-linh-floating-companion {
  position: fixed;
  bottom: 26px;
  right: 26px;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.25s ease;
  animation: floatBob 3.5s ease-in-out infinite;
}

.khi-linh-floating-companion:hover {
  transform: translateY(-4px) scale(1.08);
}

.khi-linh-floating-companion:focus-visible {
  outline: 3px solid #e8c874;
  outline-offset: 4px;
}

/* Spirit Halo Glow */
.spirit-halo {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(79, 168, 160, 0.5) 0%, rgba(232, 200, 116, 0.25) 60%, transparent 80%);
  filter: blur(4px);
  animation: haloPulse 3s ease-in-out infinite;
  z-index: 1;
}

.spirit-chibi-body {
  position: relative;
  width: 100%;
  height: 100%;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spirit-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 6px 14px rgba(26, 58, 92, 0.35));
}

/* State Badge on Companion */
.companion-state-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  z-index: 4;
}

.badge-confirming {
  background: #fef08a;
  border: 1px solid #eab308;
  animation: badgeAttention 1s ease-in-out infinite;
}

.badge-executing {
  background: #bbf7d0;
  border: 1px solid #22c55e;
}

.badge-error {
  background: #fecaca;
  border: 1px solid #ef4444;
}

/* Floating Tooltip */
.companion-tooltip {
  position: absolute;
  right: 80px;
  bottom: 14px;
  background: rgba(26, 58, 92, 0.92);
  backdrop-filter: blur(8px);
  color: #f5f5f0;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-family: 'Inter', sans-serif;
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(232, 200, 116, 0.4);
  pointer-events: none;
  opacity: 0;
  transform: translateX(8px);
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 10;
}

.khi-linh-floating-companion:hover .companion-tooltip {
  opacity: 1;
  transform: translateX(0);
}

/* Listening Audio Wave Pulse */
.sound-wave-ring {
  position: absolute;
  inset: -12px;
  border-radius: 50%;
  border: 2px solid #38bdf8;
  opacity: 0;
  animation: soundRipple 1.8s cubic-bezier(0.1, 0.6, 0.3, 1) infinite;
  z-index: 0;
}

.sound-wave-ring.wave-2 {
  animation-delay: 0.6s;
}

/* ─── P0: SANCTUARY DRAWER / MODAL ──────────────────────────── */
.khi-linh-sanctuary {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 420px;
  max-width: calc(100vw - 32px);
  height: 640px;
  max-height: calc(100vh - 48px);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-radius: 20px;
  border: 1px solid rgba(232, 200, 116, 0.55);
  box-shadow: 0 16px 40px rgba(26, 58, 92, 0.25), 0 0 24px rgba(79, 168, 160, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
  animation: sanctuarySlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Sanctuary Header */
.sanctuary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: linear-gradient(135deg, rgba(43, 138, 130, 0.12) 0%, rgba(232, 200, 116, 0.15) 100%);
  border-bottom: 1px solid rgba(232, 200, 116, 0.35);
}

.header-companion-avatar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mini-spirit-orb {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: radial-gradient(circle, #e0f7f5 0%, #76dcd1 80%, #2b8a82 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(43, 138, 130, 0.35);
}

.header-titles {
  display: flex;
  flex-direction: column;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sanctuary-title {
  font-family: 'Lora', serif;
  font-size: 15px;
  font-weight: 700;
  color: #1a3a5c;
  margin: 0;
}

.dao-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 10px;
  background: rgba(232, 200, 116, 0.3);
  color: #78530b;
  font-weight: 600;
}

/* REAL AGENT STATE UI BADGE */
.real-agent-state-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  color: #2b8a82;
  margin-top: 2px;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #2b8a82;
  display: inline-block;
  animation: pulseDot 1.5s ease-in-out infinite;
}

.real-agent-state-chip.state-listening .pulse-dot {
  background: #0284c7;
}
.real-agent-state-chip.state-listening {
  color: #0284c7;
}

.real-agent-state-chip.state-confirming .pulse-dot {
  background: #d97706;
}
.real-agent-state-chip.state-confirming {
  color: #d97706;
}

.real-agent-state-chip.state-executing .pulse-dot {
  background: #059669;
}
.real-agent-state-chip.state-executing {
  color: #059669;
}

.real-agent-state-chip.state-error .pulse-dot {
  background: #dc2626;
}
.real-agent-state-chip.state-error {
  color: #dc2626;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.header-action-btn {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: 8px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 13px;
  color: #1a3a5c;
  transition: all 0.2s ease;
}

.header-action-btn:hover {
  background: #ffffff;
  border-color: #2b8a82;
  transform: translateY(-1px);
}

.header-action-btn.tts-btn.active {
  background: rgba(79, 168, 160, 0.2);
  border-color: #2b8a82;
}

.header-action-btn.close-btn:hover {
  background: #fee2e2;
  color: #ef4444;
  border-color: #ef4444;
}

/* ─── P2: LISTENING WAVE BANNER ──────────────────────────────── */
.listening-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: linear-gradient(90deg, #e0f2fe 0%, #bae6fd 100%);
  border-bottom: 1px solid #7dd3fc;
  animation: bannerFade 0.25s ease;
}

.listening-anim-waves {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 18px;
}

.listening-anim-waves span {
  width: 3px;
  height: 100%;
  background: #0284c7;
  border-radius: 2px;
  animation: soundBar 0.9s ease-in-out infinite alternate;
}

.listening-anim-waves span:nth-child(2) { animation-delay: 0.15s; }
.listening-anim-waves span:nth-child(3) { animation-delay: 0.3s; }
.listening-anim-waves span:nth-child(4) { animation-delay: 0.45s; }
.listening-anim-waves span:nth-child(5) { animation-delay: 0.6s; }

.listening-text {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: #0369a1;
  flex: 1;
  margin-left: 10px;
}

.listening-sub {
  font-size: 10px;
  color: #0284c7;
}

.btn-stop-listening {
  background: #0284c7;
  color: #ffffff;
  border: none;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
}

/* ─── SANCTUARY BODY & CHAT ─────────────────────────────────── */
.sanctuary-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  scroll-behavior: smooth;
}

/* Welcome Card */
.khi-linh-welcome-card {
  background: linear-gradient(135deg, rgba(238, 244, 248, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%);
  border: 1px dashed rgba(79, 168, 160, 0.5);
  border-radius: 14px;
  padding: 14px;
  text-align: left;
}

.welcome-top {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.welcome-symbol {
  color: #2b8a82;
  font-size: 14px;
}

.khi-linh-welcome-card h4 {
  font-family: 'Lora', serif;
  font-size: 14px;
  color: #1a3a5c;
  margin: 0;
}

.welcome-desc {
  font-size: 12px;
  line-height: 1.5;
  color: #476582;
  margin-bottom: 10px;
}

.welcome-shortcuts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.quick-tip-chip {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: 12px;
  padding: 4px 9px;
  font-size: 11px;
  color: #1a3a5c;
  cursor: pointer;
  transition: all 0.15s ease;
}

.quick-tip-chip:hover {
  background: #e0f7f5;
  border-color: #2b8a82;
  transform: translateY(-1px);
}

/* Chat Rows */
.chat-bubble-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  width: 100%;
}

.chat-bubble-row.row-user {
  flex-direction: row-reverse;
}

.bubble-avatar-wrapper {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.bubble-content-box {
  max-width: 82%;
  display: flex;
  flex-direction: column;
}

.chat-bubble-row.row-user .bubble-content-box {
  align-items: flex-end;
}

.bubble-header-info {
  display: flex;
  gap: 8px;
  font-size: 10px;
  color: #6b88a5;
  margin-bottom: 2px;
  padding: 0 4px;
}

.bubble-text {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}

.row-user .bubble-text {
  background: linear-gradient(135deg, #2b8a82 0%, #1e5a55 100%);
  color: #ffffff;
  border-bottom-right-radius: 3px;
  box-shadow: 0 3px 10px rgba(43, 138, 130, 0.25);
}

.row-ai .bubble-text {
  background: #ffffff;
  color: #1a3a5c;
  border: 1px solid rgba(232, 200, 116, 0.35);
  border-bottom-left-radius: 3px;
  box-shadow: 0 3px 10px rgba(26, 58, 92, 0.06);
}

/* ═══════════════════════════════════════════════════════════════
   P0: FINANCIAL CONFIRMATION UX CARD
   ═══════════════════════════════════════════════════════════════ */
.financial-confirmation-card {
  margin-top: 10px;
  background: linear-gradient(180deg, #fffbeb 0%, #fef3c7 100%);
  border: 2px solid #e8c874;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(232, 200, 116, 0.35);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.confirmation-card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #b45309;
}

.confirmation-action-title {
  font-family: 'Lora', serif;
  font-size: 15px;
  font-weight: 700;
  color: #1a3a5c;
}

.confirmation-amount-highlight {
  font-size: 20px;
  font-weight: 800;
  color: #c0392b;
  letter-spacing: 0.5px;
  padding: 4px 0;
}

.confirmation-details-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #476582;
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(232, 200, 116, 0.3);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  color: #78530b;
}

.detail-value {
  color: #1a3a5c;
}

.detail-badge {
  background: #fef9c3;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 600;
  color: #854d0e;
}

.detail-badge.wallet {
  background: #e0f2fe;
  color: #0369a1;
}

.confirmation-button-group {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.btn-confirm-action {
  flex: 1;
  background: linear-gradient(135deg, #2b8a82 0%, #1e5a55 100%);
  color: #ffffff;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  box-shadow: 0 3px 8px rgba(43, 138, 130, 0.35);
  transition: all 0.2s ease;
}

.btn-confirm-action:hover:not(:disabled) {
  background: linear-gradient(135deg, #37a89e 0%, #2b8a82 100%);
  transform: translateY(-1px);
}

.btn-cancel-action {
  flex: 1;
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #f87171;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel-action:hover:not(:disabled) {
  background: #fecaca;
  transform: translateY(-1px);
}

.tool-executed-card {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 11px;
  color: #15803d;
  font-weight: 600;
}

/* Agent Working Indicators */
.agent-working-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px dashed rgba(79, 168, 160, 0.4);
  width: fit-content;
}

.working-content {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.working-label {
  font-size: 11px;
  color: #2b8a82;
  font-style: italic;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #2b8a82;
  border-radius: 50%;
  animation: typingDot 1.4s ease-in-out infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

.progress-bar-xianxia {
  width: 120px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #2b8a82, #e8c874, #2b8a82);
  background-size: 200% 100%;
  animation: progressRunes 1.5s linear infinite;
}

/* Live Voice Transcript */
.live-transcript-box {
  padding: 6px 14px;
  background: #eff6ff;
  border-top: 1px solid #bfdbfe;
  font-size: 12px;
  color: #1e40af;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Quick Suggestions Bar */
.quick-suggestions-bar {
  display: flex;
  gap: 6px;
  padding: 6px 14px;
  overflow-x: auto;
  border-top: 1px solid rgba(232, 200, 116, 0.25);
  background: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
}

.suggestion-chip {
  background: #ffffff;
  border: 1px solid rgba(79, 168, 160, 0.35);
  border-radius: 12px;
  padding: 3px 8px;
  font-size: 11px;
  color: #1a3a5c;
  cursor: pointer;
  transition: all 0.15s ease;
}

.suggestion-chip:hover {
  background: #e0f7f5;
  border-color: #2b8a82;
}

/* Sanctuary Footer */
.sanctuary-footer {
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.85);
  border-top: 1px solid rgba(232, 200, 116, 0.35);
}

.chat-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.khi-linh-input {
  flex: 1;
  padding: 9px 14px;
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: 12px;
  font-size: 13px;
  outline: none;
  background: #ffffff;
  color: #1a3a5c;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.khi-linh-input:focus {
  border-color: #2b8a82;
  box-shadow: 0 0 0 2px rgba(43, 138, 130, 0.2);
}

.mic-action-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(232, 200, 116, 0.6);
  background: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s ease;
}

.mic-action-btn:hover:not(:disabled) {
  background: #e0f7f5;
  border-color: #2b8a82;
}

.mic-action-btn.recording {
  background: #fee2e2;
  border-color: #ef4444;
  animation: micPulse 1s infinite;
}

.send-action-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #2b8a82 0%, #1e5a55 100%);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(43, 138, 130, 0.3);
  transition: all 0.2s ease;
}

.send-action-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #37a89e 0%, #2b8a82 100%);
  transform: translateY(-1px);
}

.send-action-btn:disabled,
.mic-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ═══════════════════════════════════════════════════════════════
   ANIMATIONS & KEYFRAMES
   ═══════════════════════════════════════════════════════════════ */
@keyframes floatBob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-7px); }
}

@keyframes haloPulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.15); opacity: 0.9; }
}

@keyframes pulseDot {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
}

@keyframes soundRipple {
  0% { transform: scale(0.9); opacity: 0.8; }
  100% { transform: scale(1.6); opacity: 0; }
}

@keyframes soundBar {
  0% { height: 20%; }
  100% { height: 100%; }
}

@keyframes micPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 rgba(239, 68, 68, 0); }
  50% { transform: scale(1.08); box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
}

@keyframes badgeAttention {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

@keyframes typingDot {
  0%, 100% { transform: translateY(0); opacity: 0.4; }
  50% { transform: translateY(-4px); opacity: 1; }
}

@keyframes progressRunes {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

@keyframes sanctuarySlideUp {
  0% { opacity: 0; transform: translateY(24px) scale(0.96); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

/* ═══════════════════════════════════════════════════════════════
   ACCESSIBILITY & REDUCED MOTION
   ═══════════════════════════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {
  .khi-linh-floating-companion,
  .spirit-halo,
  .sound-wave-ring,
  .pulse-dot,
  .typing-dots span,
  .progress-fill {
    animation: none !important;
    transition: none !important;
  }
}

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE DESIGN (MOBILE ADAPTATION)
   ═══════════════════════════════════════════════════════════════ */
@media (max-width: 480px) {
  .khi-linh-floating-companion {
    bottom: 16px;
    right: 16px;
    width: 60px;
    height: 60px;
  }

  .khi-linh-sanctuary {
    bottom: 12px;
    right: 12px;
    width: calc(100vw - 24px);
    height: calc(100vh - 24px);
    border-radius: 16px;
  }
}
</style>
