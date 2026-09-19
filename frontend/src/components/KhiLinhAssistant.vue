<template>
  <div class="khi-linh-root">
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- B. KHÍ LINH NHỎ: FLOATING ACTIVATION SWITCH ONLY            -->
    <!-- Biến mất khi Live System Mode active                        -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <div
      v-if="!isLiveActive"
      id="btn-khilinh-switch"
      class="khi-linh-floating-switch"
      :class="['state-' + agentState.toLowerCase()]"
      @click="activateLiveMode"
      role="button"
      tabindex="0"
      @keydown.enter="activateLiveMode"
      @keydown.space.prevent="activateLiveMode"
      title="Khí Linh Tiên Trí — Bấm để kích hoạt Live System Mode"
      aria-label="Kích hoạt Live System Mode"
    >
      <div class="spirit-halo"></div>

      <!-- Chibi Celestial Spirit SVG -->
      <div class="spirit-chibi-body">
        <svg viewBox="0 0 100 100" class="spirit-svg" aria-hidden="true">
          <defs>
            <radialGradient id="spiritGrad" cx="45%" cy="40%" r="55%">
              <stop offset="0%" stop-color="#ffffff" />
              <stop offset="40%" stop-color="#e0f7f5" />
              <stop offset="85%" stop-color="#a78bfa" />
              <stop offset="100%" stop-color="#6d28d9" />
            </radialGradient>
            <radialGradient id="spiritHaloGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="rgba(167, 139, 250, 0.7)" />
              <stop offset="70%" stop-color="rgba(124, 58, 237, 0.4)" />
              <stop offset="100%" stop-color="rgba(124, 58, 237, 0)" />
            </radialGradient>
            <filter id="spiritGlow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          <!-- Halo Aura -->
          <circle cx="50" cy="50" r="46" fill="url(#spiritHaloGrad)" class="halo-circle" />

          <!-- Tiny Celestial Floating Wings -->
          <path d="M16,56 C8,50 10,38 20,42 C20,32 32,32 34,44 Z" fill="rgba(255,255,255,0.85)" class="cloud-wing wing-left" />
          <path d="M84,56 C92,50 90,38 80,42 C80,32 68,32 66,44 Z" fill="rgba(255,255,255,0.85)" class="cloud-wing wing-right" />

          <!-- Spirit Orb Body -->
          <circle cx="50" cy="52" r="32" fill="url(#spiritGrad)" filter="url(#spiritGlow)" class="main-orb" />

          <!-- Yin-Yang Forehead Sigil -->
          <circle cx="50" cy="33" r="4.5" fill="#e8c874" opacity="0.9" />
          <circle cx="50" cy="33" r="2" fill="#7c3aed" />

          <!-- Eyes -->
          <ellipse cx="42" cy="50" rx="3.5" ry="4.5" fill="#1a103c" class="eye-left" />
          <circle cx="43.5" cy="48.5" r="1.5" fill="#ffffff" />
          <ellipse cx="58" cy="50" rx="3.5" ry="4.5" fill="#1a103c" class="eye-right" />
          <circle cx="59.5" cy="48.5" r="1.5" fill="#ffffff" />

          <!-- Blush -->
          <ellipse cx="34" cy="55" rx="3.5" ry="2" fill="rgba(255, 130, 180, 0.45)" />
          <ellipse cx="66" cy="55" rx="3.5" ry="2" fill="rgba(255, 130, 180, 0.45)" />

          <!-- Cute Smile -->
          <path d="M47,56 Q50,60 53,56" stroke="#1a103c" stroke-width="2" stroke-linecap="round" fill="none" />

          <!-- Bottom Floating Clouds -->
          <path d="M30,76 Q40,70 50,75 Q60,70 70,76 Q60,84 50,81 Q40,84 30,76 Z" fill="rgba(255, 255, 255, 0.9)" />
        </svg>
      </div>

      <!-- State Badge -->
      <div class="switch-badge">
        <span class="badge-icon">🔮</span>
      </div>

      <!-- Tooltip prompt -->
      <div class="switch-tooltip">
        <span>Bấm hoặc nói "Hệ thống"</span>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- PHẦN 3 & 4: LIVE SYSTEM MODE (DARK OVERLAY & SYSTEM FRAME)  -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="isLiveActive" class="system-mode-overlay" @click.self="deactivateLiveMode">
        <div class="system-frame" role="dialog" aria-modal="true" aria-labelledby="sys-title">
          <!-- Ambient Corner Runes -->
          <div class="frame-corner top-left"></div>
          <div class="frame-corner top-right"></div>
          <div class="frame-corner bottom-left"></div>
          <div class="frame-corner bottom-right"></div>

          <!-- ─── HEADER: KHÍ LINH GÓC TRÊN TRÁI & NÚT X GÓC TRÊN PHẢI ─── -->
          <div class="system-frame-header">
            <div class="spirit-header-left">
              <!-- Khí Linh Chibi xuất hiện ở góc trên bên trái của System Frame -->
              <div class="frame-spirit-orb" :class="'state-' + agentState.toLowerCase()">
                <div class="chibi-avatar-wrap">
                  <svg viewBox="0 0 100 100" class="chibi-small-svg">
                    <circle cx="50" cy="50" r="44" fill="url(#spiritGrad)" />
                    <circle cx="50" cy="33" r="3.5" fill="#e8c874" />
                    <ellipse cx="42" cy="50" rx="3.5" ry="4.5" fill="#1a103c" />
                    <ellipse cx="58" cy="50" rx="3.5" ry="4.5" fill="#1a103c" />
                    <circle cx="43.5" cy="48.5" r="1.5" fill="#ffffff" />
                    <circle cx="59.5" cy="48.5" r="1.5" fill="#ffffff" />
                    <path d="M47,56 Q50,60 53,56" stroke="#1a103c" stroke-width="2" stroke-linecap="round" fill="none" />
                  </svg>
                </div>
                <div class="spirit-pulse-ring" v-if="agentState === 'LISTENING' || agentState === 'SPEAKING'"></div>
              </div>

              <div class="system-title-group">
                <span id="sys-title" class="system-codename">[ HỆ THỐNG THẦN THỨC CÀN KHÔN ]</span>
                <div class="system-state-indicator" :class="'state-' + agentState.toLowerCase()">
                  <span class="pulse-beacon"></span>
                  <span class="state-label">{{ getStateDescription(agentState) }}</span>
                </div>
              </div>
            </div>

            <div class="spirit-header-right">
              <!-- Sound wave visualizer when listening/speaking -->
              <div v-if="agentState === 'LISTENING' || agentState === 'SPEAKING'" class="audio-wave-bars">
                <span class="bar bar-1"></span>
                <span class="bar bar-2"></span>
                <span class="bar bar-3"></span>
                <span class="bar bar-4"></span>
                <span class="bar bar-5"></span>
              </div>

              <!-- TTS Toggle -->
              <button
                class="sys-icon-btn"
                :class="{ active: ttsEnabled }"
                @click="toggleTTS"
                :title="ttsEnabled ? 'Tắt giọng nói Khí Linh' : 'Bật giọng nói Khí Linh'"
                aria-label="Bật/Tắt giọng đọc"
              >
                {{ ttsEnabled ? '🔊' : '🔇' }}
              </button>

              <!-- Close Button X: PHẦN 14 -->
              <button
                id="btn-close-live-system"
                class="sys-close-btn"
                @click="deactivateLiveMode"
                title="Đóng Live System Mode (Esc)"
                aria-label="Đóng giao diện Hệ Thống"
              >
                ✕
              </button>
            </div>
          </div>

          <!-- ─── BODY: PHẦN 4 & 5 — SYSTEM FRAME DISPLAY ─── -->
          <!-- KHÔNG hiển thị conversation history. KHÔNG hiển thị câu user nói -->
          <!-- Ban đầu hoàn toàn trống. Chỉ hiện response/processing/confirmation/result -->
          <div class="system-frame-body">
            <!-- 1. Trạng thái PROCESSING / ĐANG TRA CỨU: PHẦN 10 -->
            <div v-if="agentState === 'PROCESSING' || agentState === 'EXECUTING'" class="system-processing-state">
              <div class="celestial-spinner">
                <div class="spinner-ring"></div>
                <div class="spinner-rune">☯</div>
              </div>
              <div class="processing-text-group">
                <h4 class="processing-title">Đang tra cứu linh tịch...</h4>
                <p class="processing-sub">Khí Linh đang tính toán sổ sách và đạo pháp</p>
              </div>
            </div>

            <!-- 2. Hộp thoại XÁC NHẬN THAO TÁC: PHẦN 11 -->
            <div v-else-if="currentConfirmation" class="system-confirmation-box">
              <div class="conf-badge-header">
                <span class="conf-warn-icon">⚠️</span>
                <span class="conf-warn-title">XÁC NHẬN THAO TÁC HỆ THỐNG</span>
              </div>

              <div class="conf-action-name">
                {{ currentConfirmation.title }}
              </div>

              <div v-if="currentConfirmation.amount" class="conf-amount-highlight">
                {{ formatCurrency(currentConfirmation.amount) }}
              </div>

              <div class="conf-details-grid">
                <div v-if="currentConfirmation.note" class="conf-detail-row">
                  <span class="label">Nội dung:</span>
                  <span class="val">{{ currentConfirmation.note }}</span>
                </div>
                <div v-if="currentConfirmation.category" class="conf-detail-row">
                  <span class="label">Danh mục:</span>
                  <span class="val badge">{{ currentConfirmation.category }}</span>
                </div>
                <div v-if="currentConfirmation.wallet" class="conf-detail-row">
                  <span class="label">Túi tiền:</span>
                  <span class="val badge wallet">{{ currentConfirmation.wallet }}</span>
                </div>
                <div v-if="currentConfirmation.fromWallet" class="conf-detail-row">
                  <span class="label">Ví nguồn:</span>
                  <span class="val badge">{{ currentConfirmation.fromWallet }}</span>
                </div>
                <div v-if="currentConfirmation.toWallet" class="conf-detail-row">
                  <span class="label">Ví đích:</span>
                  <span class="val badge">{{ currentConfirmation.toWallet }}</span>
                </div>
                <div v-if="currentConfirmation.goal" class="conf-detail-row">
                  <span class="label">Mục tiêu:</span>
                  <span class="val badge">{{ currentConfirmation.goal }}</span>
                </div>
              </div>

              <div class="conf-prompt-question">
                Ký chủ có muốn xác nhận thực thi thao tác này không?
              </div>

              <!-- Buttons (User can also speak "Xác nhận" or "Hủy") -->
              <div class="conf-action-buttons">
                <button
                  id="btn-system-confirm"
                  class="btn-system-confirm"
                  @click="handleVoiceAction('Xác nhận')"
                >
                  ⚡ Xác Nhận (Nói "Xác nhận")
                </button>
                <button
                  id="btn-system-cancel"
                  class="btn-system-cancel"
                  @click="handleVoiceAction('Hủy')"
                >
                  Hủy Bỏ (Nói "Hủy")
                </button>
              </div>
            </div>

            <!-- 3. KẾT QUẢ / PHẢN HỒI HIỆN TẠI: PHẦN 10 -->
            <div v-else-if="currentDisplayContent" class="system-response-display">
              <div class="response-seal">
                <span class="seal-icon">📜</span>
                <span class="seal-tag">PHẢN HỒI THẦN THỨC</span>
                <span v-if="displaySecondsRemaining > 0" class="countdown-badge">
                  ⏱ Tự dọn sau {{ displaySecondsRemaining }}s
                </span>
              </div>

              <div class="response-main-text" v-html="formatResponseText(currentDisplayContent)"></div>

              <div v-if="currentExecutionResult" class="execution-result-card">
                <span class="exec-icon">✨</span>
                <span class="exec-text">{{ currentExecutionResult }}</span>
              </div>
            </div>

            <!-- 4. KHUNG TRỐNG KHI MỚI MỞ HOẶC SAU 10S: PHẦN 5 & PHẦN 13 -->
            <div v-else class="system-empty-standby">
              <div class="standby-sigil">
                <div class="sigil-outer-ring"></div>
                <div class="sigil-inner-rune">✨</div>
              </div>
              <p class="standby-hint">
                <span class="pulse-dot-cyan"></span>
                Khí Linh đang thường trực lắng nghe. Ký chủ chỉ cần trực tiếp truyền khẩu lệnh.
              </p>
              <div class="standby-examples">
                <span class="ex-chip">"Tháng này ta đã chi bao nhiêu?"</span>
                <span class="ex-chip">"Ăn sáng hết 50 nghìn"</span>
                <span class="ex-chip">"Ví tiền mặt còn bao nhiêu?"</span>
              </div>
            </div>
          </div>

          <!-- ─── FOOTER BAR: STATUS AND MIC ─── -->
          <div class="system-frame-footer">
            <div class="footer-status-left">
              <span class="status-dot" :class="'dot-' + agentState.toLowerCase()"></span>
              <span class="status-summary">{{ getFooterStatusText() }}</span>
            </div>

            <!-- Manual mic toggle for convenience / testing -->
            <div class="footer-controls-right">
              <button
                class="btn-live-mic-toggle"
                :class="{ active: isListening }"
                @click="toggleManualListening"
                :title="isListening ? 'Đang lắng nghe liên tục' : 'Bật lắng nghe'"
              >
                <span v-if="isListening">🔴 Đang Nghe...</span>
                <span v-else>🎙️ Tiếp Tục Nghe</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'KhiLinhAssistant',
  props: {
    api: {
      type: [Function, Object],
      required: true
    },
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['transactionCompleted', 'switchTab', 'update:isOpen'],
  setup(props, { emit }) {
    // ─── LIVE SYSTEM MODE STATE ───────────────────
    const isLiveActive = ref(props.isOpen || false)
    // States: SLEEPING | AWAKENING | LISTENING | PROCESSING | CONFIRMING | EXECUTING | SPEAKING | TIMEOUT | CLOSED | ERROR
    const agentState = ref(props.isOpen ? 'LISTENING' : 'SLEEPING')

    // ─── DISPLAY RESPONSE STATE (PHẦN 4, 5, 10, 13) ───
    const currentDisplayContent = ref('')
    const currentConfirmation = ref(null)
    const currentExecutionResult = ref('')
    const isProcessing = ref(false)
    const displaySecondsRemaining = ref(0)
    let displayTimer = null
    let countdownInterval = null

    // ─── STT (SPEECH RECOGNITION) STATE ───────────
    const isListening = ref(false)
    const speechSupported = ref(false)
    let recognitionInstance = null
    let wakeRecognitionInstance = null
    let restartTimer = null
    let silenceTimer = null
    let lastProcessedTranscript = ''
    let lastProcessedTime = 0

    // ─── TTS (SPEECH SYNTHESIS) STATE ─────────────
    const ttsEnabled = ref(localStorage.getItem('khilinh_tts') !== 'false') // default ON
    const isSpeakingTTS = ref(false)
    let synth = null
    let currentUtterance = null

    // Sync with parent prop
    watch(() => props.isOpen, (newVal) => {
      if (newVal && !isLiveActive.value) {
        activateLiveMode()
      } else if (!newVal && isLiveActive.value) {
        deactivateLiveMode()
      }
    })

    // ─── MOUNT / UNMOUNT LIFECYCLE ────────────────
    onMounted(() => {
      // 1. Kiểm tra Web Speech API
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRec) {
        speechSupported.value = true
        initRecognition(SpeechRec)
        initWakeRecognition(SpeechRec)
      }

      if ('speechSynthesis' in window) {
        synth = window.speechSynthesis
      }

      // 2. Lắng nghe wake event (từ văn bản hoặc custom trigger)
      window.addEventListener('khilinh-wake', handleWakeEvent)
      window.addEventListener('keydown', handleKeydown)

      if (props.isOpen) {
        activateLiveMode()
      } else {
        agentState.value = 'SLEEPING'
        startWakeRecognition()
      }
    })

    onUnmounted(() => {
      window.removeEventListener('khilinh-wake', handleWakeEvent)
      window.removeEventListener('keydown', handleKeydown)
      clearSilenceTimer()
      stopRecognition()
      stopWakeRecognition()
      if (synth) {
        try { synth.cancel() } catch (e) {}
      }
      clearDisplayTimeout()
    })

    function handleKeydown(e) {
      if (e.key === 'Escape' && isLiveActive.value) {
        deactivateLiveMode()
      }
    }

    function handleWakeEvent(e) {
      const phrase = typeof e.detail === 'string' ? e.detail : (e.detail?.message || '')
      if (!phrase) return
      const wakeRegex = /(?:hệ thống|he thong)[,\s]*(.*)/i
      const match = phrase.match(wakeRegex)
      if (match) {
        const trailing = (match[1] || '').trim()
        activateFromWakeWord(trailing)
      }
    }

    // ─── ACTIVATION & DEACTIVATION ────────────────
    // Clicking small Khí Linh enters Live Conversation directly
    function activateLiveMode() {
      if (isLiveActive.value) return
      isLiveActive.value = true
      emit('update:isOpen', true)
      agentState.value = 'LISTENING'

      clearDisplayContent()
      stopWakeRecognition()

      nextTick(() => {
        startRecognition()
        startSilenceTimer()
      })
    }

    // Wake-word "Hệ thống" activation
    function activateFromWakeWord(trailingCommand = '') {
      if (isLiveActive.value) return
      isLiveActive.value = true
      emit('update:isOpen', true)
      agentState.value = 'AWAKENING'

      clearDisplayContent()
      stopWakeRecognition()

      if (trailingCommand && trailingCommand.length > 1) {
        // Utterance contained wake word AND command together
        // Example: "Hệ thống, chuyển cho ta 1 triệu từ MoMo sang tiền mặt"
        nextTick(() => {
          handleVoiceAction(trailingCommand)
        })
      } else {
        // Wake word only: short spoken wake response without LLM round-trip
        const greeting = 'Dạ, Khí Linh nghe lệnh đạo hữu.'
        currentDisplayContent.value = greeting
        if (ttsEnabled.value) {
          speakAndResume(greeting)
        } else {
          agentState.value = 'LISTENING'
          startRecognition()
          startSilenceTimer()
        }
      }
    }

    // Hard close (X button or Esc)
    async function deactivateLiveMode() {
      // Cancel pending action on backend
      try {
        if (props.api && typeof props.api.post === 'function') {
          await props.api.post('/api/ai/cancel-pending')
        }
      } catch (e) {}

      deactivateLiveModeInternal()
    }

    function deactivateLiveModeInternal() {
      isLiveActive.value = false
      emit('update:isOpen', false)
      agentState.value = 'CLOSED'

      clearSilenceTimer()
      stopRecognition()
      if (synth) {
        try { synth.cancel() } catch (e) {}
      }
      isSpeakingTTS.value = false
      clearDisplayTimeout()
      clearDisplayContent()

      // Transition to SLEEPING and restart wake listener
      setTimeout(() => {
        agentState.value = 'SLEEPING'
        startWakeRecognition()
      }, 300)
    }

    // ─── 10-SECOND SILENCE TIMEOUT ─────────────────
    function startSilenceTimer() {
      clearSilenceTimer()
      if (!isLiveActive.value) return

      silenceTimer = setTimeout(async () => {
        await handleSilenceTimeout()
      }, 10000)
    }

    function clearSilenceTimer() {
      if (silenceTimer) {
        clearTimeout(silenceTimer)
        silenceTimer = null
      }
    }

    async function handleSilenceTimeout() {
      clearSilenceTimer()
      if (!isLiveActive.value) return

      // Cancel any active pending action on backend
      try {
        if (props.api && typeof props.api.post === 'function') {
          await props.api.post('/api/ai/cancel-pending')
        }
      } catch (e) {}

      agentState.value = 'TIMEOUT'
      stopRecognition()
      if (synth) {
        try { synth.cancel() } catch (e) {}
      }
      isSpeakingTTS.value = false
      clearDisplayTimeout()
      clearDisplayContent()

      // Close Live Mode and return to SLEEPING
      setTimeout(() => {
        deactivateLiveModeInternal()
      }, 600)
    }

    // ─── CONTINUOUS VOICE LOOP & INTERRUPT PROTECTION ───
    function initRecognition(SpeechRec) {
      try {
        recognitionInstance = new SpeechRec()
        recognitionInstance.lang = 'vi-VN'
        recognitionInstance.continuous = false
        recognitionInstance.interimResults = false

        recognitionInstance.onstart = () => {
          if (agentState.value !== 'SPEAKING' && !isSpeakingTTS.value) {
            isListening.value = true
            if (agentState.value !== 'PROCESSING' && agentState.value !== 'CONFIRMING' && agentState.value !== 'EXECUTING') {
              agentState.value = 'LISTENING'
            }
          }
        }

        recognitionInstance.onresult = (event) => {
          // TTS GATING: While Khí Linh is speaking TTS, drop speech
          if (agentState.value === 'SPEAKING' || isSpeakingTTS.value) {
            return
          }

          let transcript = ''
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              transcript += event.results[i][0].transcript
            }
          }

          const cleanMsg = transcript.trim()
          if (!cleanMsg) return

          // Prevent duplicate submission within 1.5 seconds
          const now = Date.now()
          if (cleanMsg.toLowerCase() === lastProcessedTranscript.toLowerCase() && (now - lastProcessedTime) < 1500) {
            return
          }
          lastProcessedTranscript = cleanMsg
          lastProcessedTime = now

          // Strip "hệ thống" prefix if repeated in continuous mode
          const wakeRegex = /(?:hệ thống|he thong)[,\s]*(.*)/i
          const wakeMatch = cleanMsg.match(wakeRegex)
          let cmd = cleanMsg
          if (wakeMatch) {
            cmd = (wakeMatch[1] || '').trim()
            if (!cmd) {
              // Just "hệ thống" repeated while already in live mode
              return
            }
          }

          // User responded, clear silence countdown
          clearSilenceTimer()

          handleVoiceAction(cmd)
        }

        recognitionInstance.onerror = (event) => {
          isListening.value = false
          if (isLiveActive.value && agentState.value !== 'SPEAKING' && agentState.value !== 'PROCESSING' && !isSpeakingTTS.value) {
            scheduleRestartRecognition()
          }
        }

        recognitionInstance.onend = () => {
          isListening.value = false
          if (isLiveActive.value && agentState.value !== 'SPEAKING' && agentState.value !== 'PROCESSING' && agentState.value !== 'EXECUTING' && !isSpeakingTTS.value) {
            scheduleRestartRecognition()
          }
        }
      } catch (err) {
        speechSupported.value = false
      }
    }

    function scheduleRestartRecognition() {
      clearTimeout(restartTimer)
      restartTimer = setTimeout(() => {
        if (isLiveActive.value && agentState.value !== 'SPEAKING' && agentState.value !== 'PROCESSING' && !isSpeakingTTS.value) {
          startRecognition()
        }
      }, 300)
    }

    function startRecognition() {
      if (!recognitionInstance || !isLiveActive.value) return
      if (agentState.value === 'SPEAKING' || isSpeakingTTS.value) return

      try {
        recognitionInstance.start()
      } catch (e) {
        // Recognition might already be running
      }
    }

    function stopRecognition() {
      clearTimeout(restartTimer)
      if (recognitionInstance) {
        try {
          recognitionInstance.abort()
        } catch (e) {}
      }
      isListening.value = false
    }

    function toggleManualListening() {
      if (isListening.value) {
        stopRecognition()
      } else {
        if (agentState.value !== 'SPEAKING' && !isSpeakingTTS.value) {
          startRecognition()
          startSilenceTimer()
        }
      }
    }

    // ─── WAKE PHRASE "HỆ THỐNG" (BACKGROUND LISTENER) ───
    function initWakeRecognition(SpeechRec) {
      try {
        wakeRecognitionInstance = new SpeechRec()
        wakeRecognitionInstance.lang = 'vi-VN'
        wakeRecognitionInstance.continuous = false
        wakeRecognitionInstance.interimResults = false

        wakeRecognitionInstance.onresult = (event) => {
          if (isLiveActive.value) return
          let text = ''
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              text += event.results[i][0].transcript
            }
          }
          const clean = text.trim()
          if (!clean) return

          const wakeRegex = /(?:hệ thống|he thong)[,\s]*(.*)/i
          const match = clean.match(wakeRegex)
          if (match) {
            const trailingCommand = (match[1] || '').trim()
            activateFromWakeWord(trailingCommand)
          }
          // Non-wake speech is completely ignored in SLEEPING mode
        }

        wakeRecognitionInstance.onerror = () => {
          // Silent fallback for background wake listener
        }

        wakeRecognitionInstance.onend = () => {
          // Restart background wake listener if live mode not active
          if (!isLiveActive.value && speechSupported.value) {
            setTimeout(() => startWakeRecognition(), 1000)
          }
        }
      } catch (e) {}
    }

    function startWakeRecognition() {
      if (!wakeRecognitionInstance || isLiveActive.value) return
      try {
        wakeRecognitionInstance.start()
      } catch (e) {}
    }

    function stopWakeRecognition() {
      if (wakeRecognitionInstance) {
        try {
          wakeRecognitionInstance.abort()
        } catch (e) {}
      }
    }

    // ─── AGENTCORE DISPATCH & LIFECYCLE ───
    async function handleVoiceAction(rawText) {
      if (!rawText || !rawText.trim()) return

      clearSilenceTimer()
      clearDisplayTimeout()

      stopRecognition()
      agentState.value = 'PROCESSING'
      isProcessing.value = true

      try {
        const { data } = await props.api.post(
          '/api/ai/chat',
          { message: rawText, mode: 'action' },
          { timeout: 25000 }
        )

        isProcessing.value = false

        // Phân loại kết quả trả về từ AgentCore
        if (data.state === 'CONFIRMING' && data.pending_confirmation) {
          agentState.value = 'CONFIRMING'
          const p = data.pending_confirmation
          currentConfirmation.value = {
            tool_name: p.tool_name,
            title: getToolActionTitle(p.tool_name),
            amount: p.args?.amount,
            note: p.args?.note || p.args?.target_name || p.args?.wallet_name,
            category: p.args?.category_name,
            wallet: p.args?.wallet_name,
            fromWallet: p.args?.from_wallet_name,
            toWallet: p.args?.to_wallet_name,
            goal: p.args?.goal_name
          }
          currentDisplayContent.value = ''
          currentExecutionResult.value = ''

          if (ttsEnabled.value && data.response) {
            speakAndResume(data.response)
          } else {
            resumeListeningDirectly()
            startSilenceTimer()
          }
        } else {
          currentConfirmation.value = null
          currentDisplayContent.value = data.response || 'Đã tiếp nhận mệnh lệnh.'

          if (data.state === 'SUCCESS' && data.tool_executed) {
            currentExecutionResult.value = 'Đồng bộ cơ sở dữ liệu thành công.'
            emit('transactionCompleted', {
              tool: data.tool_executed,
              result: data.tool_result
            })
          } else {
            currentExecutionResult.value = ''
          }

          if (ttsEnabled.value && currentDisplayContent.value) {
            speakAndResume(currentDisplayContent.value)
          } else {
            resumeListeningDirectly()
            startSilenceTimer()
          }
        }
      } catch (err) {
        isProcessing.value = false
        agentState.value = 'ERROR'
        currentConfirmation.value = null
        const errMsg = err.code === 'ECONNABORTED'
          ? 'Tiên Trí phản hồi quá thời gian do nghẽn mạng.'
          : (err.response?.data?.detail || 'Khí Linh gặp trở ngại khi kết nối đạo đường.')
        currentDisplayContent.value = '⚠️ ' + errMsg
        currentExecutionResult.value = ''

        if (ttsEnabled.value) {
          speakAndResume(errMsg)
        } else {
          resumeListeningDirectly()
          startSilenceTimer()
        }
      }
    }

    // ─── TTS PLAYBACK & RETURN TO LISTENING ───
    function speakAndResume(text) {
      clearSilenceTimer()

      if (!synth || !ttsEnabled.value) {
        resumeListeningDirectly()
        startSilenceTimer()
        return
      }

      try {
        synth.cancel()

        const cleanSpeech = text
          .replace(/\*\*(.*?)\*\*/g, '$1')
          .replace(/[#*`_~]/g, '')
          .replace(/[👉✅⚠️❌🔮✨📜⚡🟢🔴💵📊🍜🎯📈🏷️💰📅]/g, '')
          .replace(/VNĐ/gi, ' đồng')
          .replace(/đ\b/gi, ' đồng')
          .replace(/\b(\d+)\s*k\b/gi, '$1 nghìn')
          .replace(/\b(\d+)\s*tr\b/gi, '$1 triệu')
          .trim()

        if (!cleanSpeech) {
          resumeListeningDirectly()
          startSilenceTimer()
          return
        }

        const utter = new SpeechSynthesisUtterance(cleanSpeech)
        utter.lang = 'vi-VN'
        utter.rate = 1.05
        utter.pitch = 1.05
        currentUtterance = utter

        utter.onstart = () => {
          agentState.value = 'SPEAKING'
          isSpeakingTTS.value = true
          stopRecognition()
        }

        utter.onend = () => {
          currentUtterance = null
          isSpeakingTTS.value = false
          resumeListeningDirectly()
          startSilenceTimer()
        }

        utter.onerror = () => {
          currentUtterance = null
          isSpeakingTTS.value = false
          resumeListeningDirectly()
          startSilenceTimer()
        }

        synth.speak(utter)
      } catch (e) {
        isSpeakingTTS.value = false
        resumeListeningDirectly()
        startSilenceTimer()
      }
    }

    function resumeListeningDirectly() {
      if (agentState.value !== 'CONFIRMING') {
        agentState.value = 'LISTENING'
      }
      if (isLiveActive.value) {
        startRecognition()
      }
    }

    function clearDisplayTimeout() {
      if (displayTimer) {
        clearTimeout(displayTimer)
        displayTimer = null
      }
      if (countdownInterval) {
        clearInterval(countdownInterval)
        countdownInterval = null
      }
      displaySecondsRemaining.value = 0
    }

    function clearDisplayContent() {
      currentDisplayContent.value = ''
      currentConfirmation.value = null
      currentExecutionResult.value = ''
    }

    function toggleTTS() {
      ttsEnabled.value = !ttsEnabled.value
      localStorage.setItem('khilinh_tts', ttsEnabled.value.toString())
      if (!ttsEnabled.value && synth) {
        try { synth.cancel() } catch (e) {}
      }
    }

    // ─── FORMATTERS & HELPERS ─────────────────────
    function getToolActionTitle(toolName) {
      const titles = {
        create_expense: 'Ghi Nhận Khoản Chi Mới',
        create_income: 'Ghi Nhận Khoản Thu Mới',
        update_transaction: 'Chỉnh Sửa Bản Ghi Giao Dịch',
        delete_transaction: 'Xóa Bỏ Bản Ghi Giao Dịch',
        create_wallet: 'Khai Mở Túi Càn Khôn Mới',
        update_wallet: 'Cập Nhật Túi Càn Khôn',
        delete_wallet: 'Xóa Bỏ Túi Càn Khôn',
        transfer_money: 'Chuyển Linh Thạch Liên Ví',
        create_budget: 'Thiết Lập Ngân Sách Hạn Mức',
        update_budget: 'Cập Nhật Ngân Sách Hạn Mức',
        delete_budget: 'Hủy Bỏ Ngân Sách Hạn Mức',
        create_saving_goal: 'Lập Mục Tiêu Tiết Kiệm Mới',
        update_saving_goal: 'Cập Nhật Mục Tiêu Tiết Kiệm',
        delete_saving_goal: 'Xóa Mục Tiêu Tiết Kiệm',
        saving_goal_deposit: 'Tích Lũy Vào Mục Tiêu',
        saving_goal_withdraw: 'Rút Linh Thạch Khỏi Mục Tiêu',
        create_debt: 'Ghi Sổ Công Nợ Mới',
        settle_debt: 'Quyết Toán Tất Khoản Nợ',
        delete_debt: 'Xóa Khoản Nợ Khỏi Sổ',
        create_recurring_transaction: 'Thiết Lập Giao Dịch Định Kỳ',
        delete_recurring_transaction: 'Hủy Giao Dịch Định Kỳ'
      }
      return titles[toolName] || 'Thao Tác Hệ Thống'
    }

    function getStateDescription(state) {
      switch (state) {
        case 'SLEEPING': return 'Đang Trực Đợi Khẩu Lệnh "Hệ Thống"...'
        case 'AWAKENING': return 'Đang Khởi Động Thần Thức...'
        case 'LISTENING': return 'Đang Lắng Nghe Khẩu Quyết...'
        case 'PROCESSING': return 'Đang Tra Cứu Linh Tịch...'
        case 'SPEAKING': return 'Đang Truyền Âm Trả Lời...'
        case 'CONFIRMING': return 'Chờ Ký Chủ Xác Nhận...'
        case 'EXECUTING': return 'Đang Thực Thi Pháp Quyết...'
        case 'TIMEOUT': return 'Hết Thời Gian Chờ (Đã Dọn Lệnh)...'
        case 'CLOSED': return 'Đã Đóng Thần Thức'
        case 'SUCCESS': return 'Thao Tác Hoàn Tất'
        case 'ERROR': return 'Trở Ngại Hệ Thống'
        default: return 'Khí Linh Thường Trực'
      }
    }

    function getFooterStatusText() {
      if (agentState.value === 'SPEAKING') {
        return 'Khí Linh đang truyền âm phản hồi (User nói chen sẽ không nhận).'
      }
      if (agentState.value === 'LISTENING') {
        return 'Hội thoại liên tục: Đang lắng nghe, không cần gọi "Hệ thống" lại.'
      }
      if (agentState.value === 'PROCESSING') {
        return 'Đang đối chiếu dữ liệu tài chính với AgentCore...'
      }
      if (agentState.value === 'CONFIRMING') {
        return 'Đang chờ lệnh "Xác nhận", "Hủy", hoặc sửa đổi từ Ký Chủ.'
      }
      if (agentState.value === 'AWAKENING') {
        return 'Thần thức thức tỉnh, sẵn sàng tiếp nhận mệnh lệnh.'
      }
      if (agentState.value === 'TIMEOUT') {
        return 'Hết 10 giây im lặng. Đã hủy lệnh chờ và chuyển về chế độ ngủ.'
      }
      return 'Hệ thống Khí Linh sẵn sàng phục mệnh.'
    }

    function formatResponseText(text) {
      if (!text) return ''
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>')
    }

    function formatCurrency(amount) {
      if (amount === undefined || amount === null) return '0 VNĐ'
      const num = Number(amount)
      if (isNaN(num)) return amount + ' VNĐ'
      return num.toLocaleString('vi-VN') + ' VNĐ'
    }

    return {
      isLiveActive,
      agentState,
      currentDisplayContent,
      currentConfirmation,
      currentExecutionResult,
      isProcessing,
      displaySecondsRemaining,
      isListening,
      speechSupported,
      ttsEnabled,
      activateLiveMode,
      deactivateLiveMode,
      toggleManualListening,
      toggleTTS,
      handleVoiceAction,
      getStateDescription,
      getFooterStatusText,
      formatResponseText,
      formatCurrency
    }
  }
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════
   B. FLOATING ACTIVATION SWITCH (GÓC DƯỚI BÊN PHẢI)
   Tuyệt đối không phải chatbox, không mở ô nhập hay lịch sử
   ═══════════════════════════════════════════════════════════════ */
.khi-linh-root {
  position: relative;
}

.khi-linh-floating-switch {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 9990;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  filter: drop-shadow(0 8px 24px rgba(124, 58, 237, 0.45));
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease;
}

.khi-linh-floating-switch:hover {
  transform: translateY(-4px) scale(1.08);
  filter: drop-shadow(0 12px 32px rgba(139, 92, 246, 0.65));
}

.spirit-halo {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, rgba(124, 58, 237, 0.6), rgba(232, 200, 116, 0.6), rgba(124, 58, 237, 0.6));
  animation: rotateHalo 6s linear infinite;
  opacity: 0.85;
}

@keyframes rotateHalo {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spirit-chibi-body {
  position: relative;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: floatBob 3s ease-in-out infinite;
}

@keyframes floatBob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.spirit-svg {
  width: 100%;
  height: 100%;
}

.switch-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #7c3aed, #4c1d95);
  border: 1.5px solid #e8c874;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  z-index: 3;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.switch-tooltip {
  position: absolute;
  right: 76px;
  white-space: nowrap;
  background: rgba(26, 16, 60, 0.95);
  color: #e9d5ff;
  border: 1px solid rgba(167, 139, 250, 0.5);
  border-radius: 12px;
  padding: 6px 12px;
  font-size: 12px;
  pointer-events: none;
  opacity: 0;
  transform: translateX(8px);
  transition: all 0.25s ease;
  box-shadow: 0 6px 18px rgba(0,0,0,0.3);
}

.khi-linh-floating-switch:hover .switch-tooltip {
  opacity: 1;
  transform: translateX(0);
}

/* ═══════════════════════════════════════════════════════════════
   PHẦN 3 & 4: LIVE SYSTEM MODE (DARK OVERLAY & SYSTEM FRAME)
   Màu chủ đạo: Tím (#7c3aed, #4c1d95). Chiếm ~65% viewport
   ═══════════════════════════════════════════════════════════════ */
.system-mode-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 5, 25, 0.88);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeInOverlay 0.35s ease-out;
}

@keyframes fadeInOverlay {
  from { opacity: 0; }
  to { opacity: 1; }
}

.system-frame {
  width: 65vw;
  height: 65vh;
  min-width: 360px;
  min-height: 420px;
  max-width: 960px;
  max-height: 700px;
  background: linear-gradient(145deg, rgba(26, 12, 56, 0.96) 0%, rgba(18, 8, 38, 0.98) 100%);
  border: 1.5px solid rgba(167, 139, 250, 0.45);
  border-radius: 24px;
  box-shadow:
    0 0 50px rgba(124, 58, 237, 0.35),
    inset 0 0 35px rgba(139, 92, 246, 0.12),
    0 24px 64px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  animation: scaleInFrame 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleInFrame {
  from { opacity: 0; transform: scale(0.92) translateY(12px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* Corner Rune Accents */
.frame-corner {
  position: absolute;
  width: 14px;
  height: 14px;
  border: 2px solid #e8c874;
  pointer-events: none;
  z-index: 10;
}
.frame-corner.top-left { top: 8px; left: 8px; border-right: none; border-bottom: none; }
.frame-corner.top-right { top: 8px; right: 8px; border-left: none; border-bottom: none; }
.frame-corner.bottom-left { bottom: 8px; left: 8px; border-right: none; border-top: none; }
.frame-corner.bottom-right { bottom: 8px; right: 8px; border-left: none; border-top: none; }

/* ─── SYSTEM FRAME HEADER ─── */
.system-frame-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(167, 139, 250, 0.25);
  background: rgba(30, 14, 66, 0.6);
}

.spirit-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Khí Linh Chibi ở góc trên bên trái frame */
.frame-spirit-orb {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: radial-gradient(circle, #7c3aed 0%, #4c1d95 100%);
  border: 1.5px solid #e8c874;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(167, 139, 250, 0.5);
}

.chibi-avatar-wrap {
  width: 40px;
  height: 40px;
}
.chibi-small-svg {
  width: 100%;
  height: 100%;
}

.spirit-pulse-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 2px solid rgba(167, 139, 250, 0.8);
  animation: pulseAura 1.8s ease-out infinite;
}

@keyframes pulseAura {
  0% { transform: scale(0.95); opacity: 1; }
  100% { transform: scale(1.35); opacity: 0; }
}

.system-title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.system-codename {
  font-family: 'Cinzel', 'Lora', serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: #e8c874;
  text-shadow: 0 0 10px rgba(232, 200, 116, 0.4);
}

.system-state-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #c4b5fd;
}

.pulse-beacon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a78bfa;
  box-shadow: 0 0 8px #a78bfa;
}
.state-sleeping .pulse-beacon { background: #8b5cf6; box-shadow: 0 0 6px #8b5cf6; opacity: 0.6; }
.state-awakening .pulse-beacon { background: #c084fc; box-shadow: 0 0 12px #c084fc; animation: blink 0.5s infinite; }
.state-listening .pulse-beacon { background: #34d399; box-shadow: 0 0 10px #34d399; animation: blink 1.2s infinite; }
.state-processing .pulse-beacon { background: #fbbf24; box-shadow: 0 0 10px #fbbf24; animation: blink 0.8s infinite; }
.state-speaking .pulse-beacon { background: #60a5fa; box-shadow: 0 0 10px #60a5fa; animation: blink 1s infinite; }
.state-confirming .pulse-beacon { background: #f87171; box-shadow: 0 0 10px #f87171; }
.state-timeout .pulse-beacon { background: #9ca3af; box-shadow: 0 0 6px #9ca3af; }
.state-closed .pulse-beacon { background: #6b7280; box-shadow: none; }

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.spirit-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Sound wave audio visualizer */
.audio-wave-bars {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 18px;
  padding: 0 8px;
}
.audio-wave-bars .bar {
  width: 3px;
  height: 100%;
  background: #a78bfa;
  border-radius: 2px;
  animation: waveDance 1.2s ease-in-out infinite;
}
.bar-1 { animation-delay: 0.1s; }
.bar-2 { animation-delay: 0.3s; }
.bar-3 { animation-delay: 0.5s; }
.bar-4 { animation-delay: 0.2s; }
.bar-5 { animation-delay: 0.4s; }

@keyframes waveDance {
  0%, 100% { height: 4px; }
  50% { height: 18px; }
}

.sys-icon-btn {
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  color: #ddd6fe;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.sys-icon-btn:hover {
  background: rgba(124, 58, 237, 0.4);
  color: #ffffff;
}

.sys-close-btn {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.2s;
}
.sys-close-btn:hover {
  background: rgba(239, 68, 68, 0.35);
  color: #ffffff;
  transform: scale(1.05);
}

/* ─── SYSTEM FRAME BODY: PHẦN 4, 5, 10, 11 ─── */
.system-frame-body {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
}

/* 1. Trạng thái PROCESSING */
.system-processing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  text-align: center;
  animation: fadeIn 0.3s ease;
}

.celestial-spinner {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-ring {
  position: absolute;
  inset: 0;
  border: 3px solid transparent;
  border-top-color: #a78bfa;
  border-right-color: #e8c874;
  border-radius: 50%;
  animation: spinRune 1.5s linear infinite;
}

@keyframes spinRune {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner-rune {
  font-size: 26px;
  color: #e8c874;
  text-shadow: 0 0 12px rgba(232, 200, 116, 0.6);
}

.processing-title {
  font-family: 'Lora', serif;
  font-size: 20px;
  color: #f3e8ff;
  font-weight: 600;
}
.processing-sub {
  font-size: 14px;
  color: #a78bfa;
}

/* 2. Hộp thoại CONFIRMATION: PHẦN 11 */
.system-confirmation-box {
  background: rgba(30, 12, 68, 0.85);
  border: 1.5px solid rgba(232, 200, 116, 0.7);
  border-radius: 18px;
  padding: 24px 28px;
  width: 100%;
  max-width: 580px;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5), 0 0 25px rgba(124, 58, 237, 0.3);
  animation: fadeInScale 0.3s ease;
  text-align: center;
}

@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.conf-badge-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}
.conf-warn-icon { font-size: 20px; }
.conf-warn-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #e8c874;
}

.conf-action-name {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 10px;
}

.conf-amount-highlight {
  font-size: 28px;
  font-weight: 800;
  color: #34d399;
  text-shadow: 0 0 14px rgba(52, 211, 153, 0.4);
  margin-bottom: 16px;
}

.conf-details-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(18, 8, 42, 0.7);
  border: 1px solid rgba(167, 139, 250, 0.25);
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 16px;
  text-align: left;
}
.conf-detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.conf-detail-row .label { color: #a78bfa; }
.conf-detail-row .val { color: #ffffff; font-weight: 600; }
.conf-detail-row .val.badge {
  background: rgba(124, 58, 237, 0.35);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
}
.conf-detail-row .val.badge.wallet {
  background: rgba(232, 200, 116, 0.25);
  color: #e8c874;
}

.conf-prompt-question {
  font-size: 14px;
  color: #ddd6fe;
  margin-bottom: 18px;
}

.conf-action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-system-confirm {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #ffffff;
  border: 1px solid #34d399;
  border-radius: 10px;
  padding: 10px 22px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
  transition: all 0.2s;
}
.btn-system-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
}

.btn-system-cancel {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 10px;
  padding: 10px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-system-cancel:hover {
  background: rgba(239, 68, 68, 0.35);
  color: #ffffff;
}

/* 3. Phản hồi hiện tại: PHẦN 10 */
.system-response-display {
  width: 100%;
  max-width: 680px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: fadeIn 0.3s ease;
}

.response-seal {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.seal-icon { font-size: 18px; }
.seal-tag {
  font-size: 12px;
  letter-spacing: 1.2px;
  font-weight: 700;
  color: #e8c874;
}
.countdown-badge {
  font-size: 11px;
  color: #a78bfa;
  background: rgba(124, 58, 237, 0.2);
  padding: 3px 8px;
  border-radius: 10px;
  border: 1px solid rgba(167, 139, 250, 0.3);
}

.response-main-text {
  font-family: 'Lora', serif;
  font-size: 20px;
  line-height: 1.8;
  color: #f5f3ff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
  margin-bottom: 20px;
}

.execution-result-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(52, 211, 153, 0.4);
  border-radius: 12px;
  padding: 8px 18px;
  color: #6ee7b7;
  font-size: 13px;
  font-weight: 600;
}

/* 4. Khung trống thường trực: PHẦN 5 & PHẦN 13 */
.system-empty-standby {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  text-align: center;
  opacity: 0.9;
}

.standby-sigil {
  position: relative;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sigil-outer-ring {
  position: absolute;
  inset: 0;
  border: 1.5px dashed rgba(167, 139, 250, 0.5);
  border-radius: 50%;
  animation: rotateHalo 12s linear infinite;
}
.sigil-inner-rune {
  font-size: 24px;
  color: #a78bfa;
  animation: floatBob 2.5s ease-in-out infinite;
}

.standby-hint {
  font-size: 15px;
  color: #c4b5fd;
  max-width: 480px;
  line-height: 1.6;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.pulse-dot-cyan {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22d3ee;
  box-shadow: 0 0 8px #22d3ee;
  display: inline-block;
  animation: blink 1.5s infinite;
}

.standby-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 6px;
}

.ex-chip {
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #ddd6fe;
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 14px;
}

/* ─── SYSTEM FRAME FOOTER ─── */
.system-frame-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: rgba(18, 8, 42, 0.75);
  border-top: 1px solid rgba(167, 139, 250, 0.2);
  font-size: 12px;
}

.footer-status-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a78bfa;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.dot-sleeping { background: #8b5cf6; box-shadow: 0 0 6px #8b5cf6; }
.dot-awakening { background: #c084fc; box-shadow: 0 0 8px #c084fc; animation: blink 0.5s infinite; }
.dot-listening { background: #34d399; box-shadow: 0 0 6px #34d399; }
.dot-speaking { background: #60a5fa; box-shadow: 0 0 6px #60a5fa; }
.dot-processing { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.dot-confirming { background: #f87171; box-shadow: 0 0 6px #f87171; }
.dot-timeout { background: #9ca3af; }
.dot-closed { background: #6b7280; }
.dot-idle { background: #94a3b8; }

.btn-live-mic-toggle {
  background: rgba(124, 58, 237, 0.25);
  border: 1px solid rgba(167, 139, 250, 0.4);
  color: #e9d5ff;
  border-radius: 8px;
  padding: 5px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-live-mic-toggle.active {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
  color: #fca5a5;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .system-frame {
    width: 92vw;
    height: 80vh;
    padding: 0;
  }
  .system-frame-body {
    padding: 20px 16px;
  }
  .response-main-text {
    font-size: 17px;
  }
}
</style>
