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

      <!-- Chibi Celestial Spirit Character -->
      <div class="spirit-chibi-body">
        <KhiLinhCharacter
          size="md"
          :state="agentState"
          :show-aura="true"
          :show-rings="true"
          :show-status-dot="false"
        />
      </div>

      <!-- State Badge -->
      <div class="switch-badge" :class="'badge-' + agentState.toLowerCase()">
        <span class="badge-dot"></span>
      </div>

      <!-- Tooltip prompt -->
      <div class="switch-tooltip">
        <span>Bấm hoặc nói "Hệ thống"</span>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- STITCH SYSTEM WINDOW: CELESTIAL MODERN SYSTEM CONSOLE        -->
    <!-- Desktop 70–80% viewport | Mobile 90–95% viewport             -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="isLiveActive" class="system-mode-overlay" @click.self="deactivateLiveMode">
        <div class="system-window-shell" role="dialog" aria-modal="true" aria-labelledby="sys-title">
          <!-- 4 Corner Technical Cut Accents -->
          <div class="shell-corner corner-tl"></div>
          <div class="shell-corner corner-tr"></div>
          <div class="shell-corner corner-bl"></div>
          <div class="shell-corner corner-br"></div>

          <!-- ─── HEADER: HỆ THỐNG · KHÍ LINH & NÚT ĐÓNG X ─── -->
          <div class="system-header">
            <div class="system-header-left">
              <span class="header-beacon-pulse"></span>
              <h2 id="sys-title" class="system-header-title">
                HỆ THỐNG · KHÍ LINH
                <span class="system-badge-tag">[CAN-KHON::SYS-01] · TU TIÊN HỘ TRÌ</span>
              </h2>
            </div>

            <div class="system-header-right">
              <!-- Sound wave visualizer when listening/speaking -->
              <div v-if="agentState === 'LISTENING' || agentState === 'SPEAKING'" class="audio-wave-visualizer" title="Tần số linh âm">
                <span class="bar bar-1"></span>
                <span class="bar bar-2"></span>
                <span class="bar bar-3"></span>
                <span class="bar bar-4"></span>
                <span class="bar bar-5"></span>
              </div>

              <!-- TTS Toggle -->
              <button
                class="sys-tool-btn"
                :class="{ active: ttsEnabled }"
                @click="toggleTTS"
                :title="ttsEnabled ? 'Tắt giọng nói Khí Linh' : 'Bật giọng nói Khí Linh'"
                aria-label="Bật/Tắt giọng đọc"
              >
                {{ ttsEnabled ? '🔊' : '🔇' }}
              </button>

              <!-- Close Button X: Full Live Session Close -->
              <button
                id="btn-close-live-system"
                class="sys-close-x-btn"
                @click="deactivateLiveMode"
                title="Đóng Hệ Thống Khí Linh (Esc)"
                aria-label="Đóng giao diện Hệ Thống"
              >
                ✕
              </button>
            </div>
          </div>

          <!-- ─── BODY CONTAINER (Scrollable Inner Console) ─── -->
          <div class="system-body-container">
            <div class="outer-system-console">
              <!-- Spiritual Coordinates & Telemetry Overline Strip -->
              <div class="telemetry-strip">
                <div class="telemetry-left">
                  <span class="telemetry-sys-id">
                    <span class="telemetry-ping-dot"></span>
                    [CAN-KHON::SYS-01]
                  </span>
                  <span class="telemetry-sync-rate hidden-mobile">
                    TÂM THỨC LIÊN KẾT: 99.87%
                  </span>
                </div>
                <div class="telemetry-right" :class="'state-' + agentState.toLowerCase()">
                  <span class="telemetry-state-icon">☯</span>
                  <span class="telemetry-state-text">{{ getPhapTranStatus(agentState) }}</span>
                </div>
              </div>

              <!-- Main System Grid: Left Portal (Avatar) + Right Dialogue Stream -->
              <div class="system-grid">
                <!-- Left Portal: Chibi Khí Linh Portal -->
                <div class="spirit-portal-card">
                  <div class="portal-micro micro-tl"></div>
                  <div class="portal-micro micro-tr"></div>
                  <div class="portal-micro micro-bl"></div>
                  <div class="portal-micro micro-br"></div>

                  <!-- Chibi Portal Center with Sacred Aura Rings -->
                  <div class="chibi-portal-character-wrap">
                    <KhiLinhCharacter
                      size="portal"
                      :state="agentState"
                      :show-aura="true"
                      :show-rings="true"
                      :show-status-dot="false"
                    />
                  </div>

                  <div class="spirit-portal-meta">
                    <div class="spirit-name-row">
                      <span class="spirit-name">Tiểu Linh Nhi</span>
                      <span class="spirit-verified-badge" title="Khí Linh Chính Tông">✓</span>
                    </div>
                    <p class="spirit-realm-title">Khí Linh Đệ Thất Giai · Hộ Trì Ngân Khố</p>
                    <div class="spirit-state-pill" :class="'state-' + agentState.toLowerCase()">
                      <span class="state-dot-mini"></span>
                      <span>{{ getStateDescription(agentState) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Right Stream: Dialogue & Action Cards -->
                <div class="action-stream-col">
                  <!-- User Voice Transcript Echo -->
                  <div v-if="lastUserUtterance" class="user-voice-transcript-banner">
                    <div class="user-transcript-label">
                      <span class="user-mic-spark">🎙️</span>
                      <span>BẠN VỪA NÓI:</span>
                    </div>
                    <p class="user-transcript-phrase">"{{ lastUserUtterance }}"</p>
                  </div>

                  <!-- 1. Trạng thái PROCESSING / ĐANG TRA CỨU LINH TỊCH -->
                  <div v-if="isProcessing || agentState === 'PROCESSING' || agentState === 'EXECUTING'" class="system-processing-state">
                    <div class="celestial-spinner">
                      <div class="spinner-ring"></div>
                      <div class="spinner-rune">☯</div>
                    </div>
                    <div class="processing-text-group">
                      <h4 class="processing-title">Đang tra cứu linh tịch...</h4>
                      <p class="processing-sub">Khí Linh đang đối chiếu dữ liệu tài chính với AgentCore</p>
                    </div>
                  </div>

                  <!-- 2. Hộp thoại XÁC NHẬN PHÁP LỆNH (CONFIRMATION TALISMAN CARD) -->
                  <div v-else-if="currentConfirmation" class="talisman-confirmation-card">
                    <div class="portal-micro micro-tl"></div>
                    <div class="portal-micro micro-tr"></div>
                    <div class="portal-micro micro-bl"></div>
                    <div class="portal-micro micro-br"></div>

                    <!-- Watermark Talisman Circle -->
                    <div class="talisman-watermark" aria-hidden="true">
                      <svg viewBox="0 0 100 100" fill="none" stroke="currentColor">
                        <circle cx="50" cy="50" r="40" stroke-width="4"></circle>
                        <rect height="50" stroke-width="3" width="50" x="25" y="25"></rect>
                        <circle cx="50" cy="50" r="15" stroke-width="2"></circle>
                      </svg>
                    </div>

                    <!-- Talisman Header -->
                    <div class="talisman-header">
                      <div class="talisman-title-group">
                        <div class="talisman-gold-bar"></div>
                        <div>
                          <h3 class="talisman-title">Xác Nhận Thao Tác</h3>
                          <p class="talisman-subtitle">{{ currentConfirmation.title }}</p>
                        </div>
                      </div>
                      <span class="talisman-type-badge">
                        {{ currentConfirmation.tool_name === 'transfer_money' ? 'Atomic Transfer' : 'Ghi Chép Ngân Khố' }}
                      </span>
                    </div>

                    <!-- Flow Diagram (4 Variants: Transfer / Expense / Income / Goal) -->
                    <div class="transaction-flow-grid">
                      <!-- SOURCE ENTITY -->
                      <div class="flow-box source-box">
                        <span class="flow-label">
                          {{ currentConfirmation.tool_name === 'create_income' ? 'Nguồn Thu / Danh Mục' : 'Từ Nguồn Quỹ' }}
                        </span>
                        <div class="flow-content">
                          <div class="flow-icon-wrap source-icon">
                            <span>{{ currentConfirmation.tool_name === 'create_income' ? '📥' : '💳' }}</span>
                          </div>
                          <div class="flow-meta">
                            <p class="flow-name truncate">
                              {{ currentConfirmation.fromWallet || currentConfirmation.wallet || currentConfirmation.category || 'Mặc định' }}
                            </p>
                            <p class="flow-sub">Nguồn thực thi</p>
                          </div>
                        </div>
                      </div>

                      <!-- FLOW ARROW -->
                      <div class="flow-arrow-col">
                        <span class="flow-arrow-icon">➔</span>
                      </div>

                      <!-- TARGET ENTITY -->
                      <div class="flow-box target-box">
                        <span class="flow-label">
                          {{ currentConfirmation.tool_name === 'create_expense' ? 'Danh Mục Chi' : (currentConfirmation.goal ? 'Mục Tiêu Tiết Kiệm' : 'Đến Đích Quỹ') }}
                        </span>
                        <div class="flow-content">
                          <div class="flow-icon-wrap target-icon">
                            <span>{{ currentConfirmation.goal ? '🎯' : (currentConfirmation.category ? '🏷️' : '💰') }}</span>
                          </div>
                          <div class="flow-meta">
                            <p class="flow-name truncate">
                              {{ currentConfirmation.toWallet || currentConfirmation.goal || currentConfirmation.category || currentConfirmation.wallet || 'Chung' }}
                            </p>
                            <p class="flow-sub">Đích luân chuyển</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Large Figure Presentation -->
                    <div v-if="currentConfirmation.amount" class="large-figure-panel">
                      <div>
                        <span class="figure-label">Lượng Linh Thạch Luân Chuyển</span>
                        <div class="figure-row">
                          <span class="figure-amount">{{ formatCurrency(currentConfirmation.amount) }}</span>
                        </div>
                      </div>
                      <div class="figure-fee-box">
                        <span class="fee-label">Phí Pháp Lực (Tự Động)</span>
                        <span class="fee-value">0 Đ</span>
                      </div>
                    </div>

                    <!-- Extra Details (Note, etc.) -->
                    <div v-if="currentConfirmation.note" class="talisman-note-row">
                      <span class="note-label">Nội dung ghi chú:</span>
                      <span class="note-val">{{ currentConfirmation.note }}</span>
                    </div>

                    <!-- Question Prompt -->
                    <p class="conf-question-text">
                      Ký chủ có muốn xác nhận thực thi pháp lệnh này không?
                      <span class="conf-question-sub">(Nói "Xác nhận", "Hủy", hoặc nhấn nút bên dưới)</span>
                    </p>

                    <!-- Action Buttons -->
                    <div class="talisman-actions">
                      <button
                        id="btn-system-cancel"
                        class="btn-talisman-cancel"
                        @click="handleVoiceAction('Hủy')"
                        type="button"
                      >
                        HỦY BỎ PHÁP LỆNH
                      </button>
                      <button
                        id="btn-system-confirm"
                        class="btn-talisman-confirm"
                        @click="handleVoiceAction('Xác nhận')"
                        type="button"
                      >
                        <span class="confirm-check-icon">✓</span>
                        <span>XÁC NHẬN GIAO DỊCH</span>
                      </button>
                    </div>
                  </div>

                  <!-- 3. KẾT QUẢ / PHẢN HỒI THẦN THỨC / MISSING PARAM WAITING -->
                  <div v-else-if="currentDisplayContent" class="system-reply-bubble">
                    <div class="reply-header-tag">
                      <span class="sparkle-icon">✨</span>
                      <span>KHÍ LINH HIỂU & PHẢN HỒI</span>
                      <span v-if="displaySecondsRemaining > 0" class="countdown-tag">
                        ⏱ Tự dọn sau {{ displaySecondsRemaining }}s
                      </span>
                    </div>

                    <div class="reply-card">
                      <div class="reply-text" v-html="formatResponseText(currentDisplayContent)"></div>
                    </div>

                    <div v-if="currentExecutionResult" class="execution-result-tag">
                      <span class="exec-spark">✨</span>
                      <span>{{ currentExecutionResult }}</span>
                    </div>
                  </div>

                  <!-- 4. KHUNG TRỐNG THƯỜNG TRỰC KHI MỚI MỞ / STANDBY -->
                  <div v-else class="system-standby-view">
                    <div class="standby-rune-circle">
                      <div class="rune-outer-ring"></div>
                      <div class="rune-inner-symbol">✨</div>
                    </div>
                    <p class="standby-lead-text">
                      <span class="pulse-beacon-cyan"></span>
                      Khí Linh đang thường trực lắng nghe. Ký chủ hãy trực tiếp truyền khẩu lệnh giọng nói.
                    </p>
                    <div class="standby-prompts-row">
                      <button class="prompt-chip" @click="handleVoiceAction('Tháng này ta đã chi bao nhiêu?')">
                        "Tháng này ta đã chi bao nhiêu?"
                      </button>
                      <button class="prompt-chip" @click="handleVoiceAction('Ăn sáng hết 50 nghìn ví tiền mặt')">
                        "Ăn sáng hết 50 nghìn ví tiền mặt"
                      </button>
                      <button class="prompt-chip" @click="handleVoiceAction('Chuyển 500k từ MoMo sang Tiền mặt')">
                        "Chuyển 500k từ MoMo sang Tiền mặt"
                      </button>
                      <button class="prompt-chip" @click="handleVoiceAction('Ví tiền mặt còn bao nhiêu?')">
                        "Ví tiền mặt còn bao nhiêu?"
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ─── FOOTER BAR: STATUS & CONTROLS ─── -->
              <div class="system-console-footer">
                <!-- Status & Mic -->
                <div class="footer-telemetry-row">
                  <div class="footer-status-info">
                    <span class="status-indicator-dot" :class="'dot-' + agentState.toLowerCase()"></span>
                    <span class="status-text-desc">{{ getFooterStatusText() }}</span>
                  </div>

                  <div class="footer-controls">
                    <button
                      id="btn-khilinh-mic"
                      class="btn-mic-stream-toggle"
                      :class="{ active: isListening }"
                      @click="toggleManualListening"
                      :title="isListening ? 'Đang lắng nghe liên tục' : 'Bật lắng nghe'"
                    >
                      <span v-if="isListening">🔴 Đang Nghe...</span>
                      <span v-else>🎙️ Bật Mic</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import KhiLinhCharacter from './khi-linh/KhiLinhCharacter.vue'

export default {
  name: 'KhiLinhAssistant',
  components: {
    KhiLinhCharacter
  },
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
    const isSubmitting = isProcessing
    const hasSubmittedUtterance = ref(false)
    const lastSpokenText = ref('')
    const lastUserUtterance = ref('')
    const quickActionChips = ref([
      '💰 Số dư',
      '📊 Tổng quan',
      '📅 Tháng này',
      '🏷️ Chi theo mục',
      '🎯 Mục tiêu',
      '📜 Sổ nợ'
    ])
    const displaySecondsRemaining = ref(0)
    let displayTimer = null
    let countdownInterval = null

    // ─── STT (SPEECH RECOGNITION) STATE ───────────
    const isListening = ref(false)
    const speechSupported = ref(false)
    let recognitionInstance = null
    let isRecognitionRunning = false
    let restartTimer = null
    let silenceTimer = null
    let ttsWatchdogTimer = null
    let hasUserInteracted = false
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
      }

      if ('speechSynthesis' in window) {
        synth = window.speechSynthesis
      }

      // 2. Lắng nghe wake & voice event
      window.addEventListener('khilinh-wake', handleWakeEvent)
      window.addEventListener('khilinh-voice', handleVoiceEvent)
      window.addEventListener('keydown', handleKeydown)

      if (props.isOpen) {
        activateLiveMode()
      } else {
        agentState.value = 'SLEEPING'
        startRecognition()
      }
    })

    onUnmounted(() => {
      window.removeEventListener('khilinh-wake', handleWakeEvent)
      window.removeEventListener('khilinh-voice', handleVoiceEvent)
      window.removeEventListener('keydown', handleKeydown)
      clearSilenceTimer()
      clearTTSWatchdog()
      stopRecognition()
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

    function handleVoiceEvent(e) {
      const phrase = typeof e.detail === 'string' ? e.detail : (e.detail?.message || '')
      if (!phrase) return

      if (!isLiveActive.value) {
        // Not active: only wake word can activate
        const wakeRegex = /(?:hệ thống|he thong)[,\s]*(.*)/i
        const match = phrase.match(wakeRegex)
        if (match) {
          const trailing = (match[1] || '').trim()
          activateFromWakeWord(trailing)
        }
        return
      }

      // Active live mode: strip repeated wake word if present
      const wakeRegex = /(?:hệ thống|he thong)[,\s]*(.*)/i
      const wakeMatch = phrase.match(wakeRegex)
      let cmd = phrase
      if (wakeMatch) {
        cmd = (wakeMatch[1] || '').trim()
        if (!cmd) return
      }
      clearSilenceTimer()
      handleVoiceAction(cmd)
    }

    // ─── ACTIVATION & DEACTIVATION ────────────────
    async function ensureMicrophonePermission() {
      hasUserInteracted = true
      if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
          stream.getTracks().forEach(track => track.stop())
          return true
        } catch (e) {
          console.warn('[Khí Linh Mic Permission]', e)
          return false
        }
      }
      return true
    }

    // Clicking small Khí Linh enters Live Conversation directly
    async function activateLiveMode() {
      if (isLiveActive.value) return
      isLiveActive.value = true
      hasUserInteracted = true
      emit('update:isOpen', true)
      agentState.value = 'LISTENING'

      clearDisplayContent()
      stopRecognition()

      await ensureMicrophonePermission()

      nextTick(() => {
        startRecognition()
        startSilenceTimer()
      })
    }

    // Wake-word "Hệ thống" activation
    function activateFromWakeWord(trailingCommand = '') {
      if (isLiveActive.value) return
      isLiveActive.value = true
      hasUserInteracted = true
      emit('update:isOpen', true)
      agentState.value = 'AWAKENING'

      clearDisplayContent()
      stopRecognition()

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
      clearTTSWatchdog()
      stopRecognition()
      if (synth) {
        try { synth.cancel() } catch (e) {}
      }
      isSpeakingTTS.value = false
      clearDisplayTimeout()
      clearDisplayContent()

      // Transition to SLEEPING and restart listener
      setTimeout(() => {
        agentState.value = 'SLEEPING'
        startRecognition()
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
    function clearTTSWatchdog() {
      if (ttsWatchdogTimer) {
        clearTimeout(ttsWatchdogTimer)
        ttsWatchdogTimer = null
      }
    }

    function cancelCurrentTTS() {
      clearTTSWatchdog()
      if (synth) {
        try { synth.cancel() } catch (e) {}
      }
      currentUtterance = null
      isSpeakingTTS.value = false
    }

    function initRecognition(SpeechRec) {
      try {
        recognitionInstance = new SpeechRec()
        recognitionInstance.lang = 'vi-VN'
        recognitionInstance.continuous = false
        recognitionInstance.interimResults = false

        recognitionInstance.onstart = () => {
          isRecognitionRunning = true
          if (isLiveActive.value) {
            isListening.value = true
            if (agentState.value !== 'SPEAKING' && agentState.value !== 'PROCESSING' && agentState.value !== 'CONFIRMING' && agentState.value !== 'EXECUTING') {
              agentState.value = 'LISTENING'
            }
          } else {
            isListening.value = false
          }
        }

        // Voice Barge-in detection: Intercept user speech during TTS playback
        recognitionInstance.onspeechstart = () => {
          if (isSpeakingTTS.value) {
            cancelCurrentTTS()
            agentState.value = 'LISTENING'
          }
        }

        recognitionInstance.onresult = (event) => {
          // Barge-in: Cancel TTS if still speaking
          if (isSpeakingTTS.value) {
            cancelCurrentTTS()
            agentState.value = 'LISTENING'
          }

          let transcript = ''
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              transcript += event.results[i][0].transcript
            }
          }

          const cleanMsg = transcript.trim()
          if (!cleanMsg) return

          // Case 1: In SLEEPING mode -> listen for wake word "Hệ thống"
          if (!isLiveActive.value) {
            const wakeRegex = /(?:hệ thống|he thong)[,\s]*(.*)/i
            const wakeMatch = cleanMsg.match(wakeRegex)
            if (wakeMatch) {
              const trailing = (wakeMatch[1] || '').trim()
              activateFromWakeWord(trailing)
            }
            return
          }

          // Case 2: In LIVE CONVERSATION mode
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
          isRecognitionRunning = false
          isListening.value = false
          if (agentState.value !== 'PROCESSING' && agentState.value !== 'EXECUTING') {
            scheduleRestartRecognition()
          }
        }

        recognitionInstance.onend = () => {
          isRecognitionRunning = false
          isListening.value = false
          if (agentState.value !== 'PROCESSING' && agentState.value !== 'EXECUTING') {
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
        if (isLiveActive.value && agentState.value !== 'PROCESSING' && agentState.value !== 'EXECUTING') {
          startRecognition()
        }
      }, isLiveActive.value ? 300 : 800)
    }

    function startRecognition() {
      if (!recognitionInstance || isRecognitionRunning) return
      if (agentState.value === 'PROCESSING' || agentState.value === 'EXECUTING') return

      try {
        isRecognitionRunning = true
        recognitionInstance.start()
      } catch (e) {
        isRecognitionRunning = false
      }
    }

    function stopRecognition() {
      clearTimeout(restartTimer)
      isRecognitionRunning = false
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
        if (agentState.value !== 'PROCESSING' && agentState.value !== 'EXECUTING') {
          startRecognition()
          startSilenceTimer()
        }
      }
    }

    // ─── AGENTCORE DISPATCH & LIFECYCLE ───
    async function handleVoiceAction(rawText) {
      if (!rawText || !rawText.trim()) return

      const cleanText = rawText.trim()
      lastUserUtterance.value = cleanText

      if (isSpeakingTTS.value) {
        cancelCurrentTTS()
      }

      clearSilenceTimer()
      clearDisplayTimeout()

      stopRecognition()
      agentState.value = 'PROCESSING'
      isProcessing.value = true

      try {
        const { data } = await props.api.post(
          '/api/ai/chat',
          { message: cleanText, mode: 'action' },
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
            amount: p.args?.amount || p.args?.limit_amount || p.args?.target_amount,
            note: p.args?.note || (p.tool_name !== 'create_saving_goal' ? p.args?.target_name : '') || p.args?.wallet_name,
            category: p.args?.category_name,
            wallet: p.args?.wallet_name,
            fromWallet: p.args?.from_wallet_name,
            toWallet: p.args?.to_wallet_name,
            goal: p.args?.target_name || p.args?.goal_name
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

          if (data.state === 'SUCCESS' || data.state === 'IDLE') {
            agentState.value = 'IDLE'
          }

          if (ttsEnabled.value && currentDisplayContent.value) {
            lastSpokenText.value = currentDisplayContent.value
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

    // ─── TTS PLAYBACK & RETURN TO LISTENING (WITH BARGE-IN SUPPORT) ───
    function speakAndResume(text) {
      clearSilenceTimer()
      clearTTSWatchdog()

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

        // Watchdog timer: If browser drops onend, guarantee recovery of STT
        const safetyDuration = Math.max(4000, cleanSpeech.length * 150 + 2500)
        ttsWatchdogTimer = setTimeout(() => {
          clearTTSWatchdog()
          currentUtterance = null
          isSpeakingTTS.value = false
          resumeListeningDirectly()
          startSilenceTimer()
        }, safetyDuration)

        utter.onstart = () => {
          agentState.value = 'SPEAKING'
          isSpeakingTTS.value = true
          // Keep recognition active for user barge-in interruption
          if (!isRecognitionRunning && isLiveActive.value) {
            startRecognition()
          }
        }

        utter.onend = () => {
          clearTTSWatchdog()
          currentUtterance = null
          isSpeakingTTS.value = false
          resumeListeningDirectly()
          startSilenceTimer()
        }

        utter.onerror = () => {
          clearTTSWatchdog()
          currentUtterance = null
          isSpeakingTTS.value = false
          resumeListeningDirectly()
          startSilenceTimer()
        }

        synth.speak(utter)
      } catch (e) {
        clearTTSWatchdog()
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
      lastUserUtterance.value = ''
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
        case 'PROCESSING': return 'Đang xử lý'
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
        return 'Khí Linh đang truyền âm phản hồi (Bạn có thể nói chen bất kỳ lúc nào để ngắt lời).'
      }
      if (agentState.value === 'LISTENING') {
        return 'Hội thoại liên tục: Đang lắng nghe, không cần gọi "Hệ thống" lại.'
      }
      if (agentState.value === 'PROCESSING') {
        return 'Đang xử lý: Đang đối chiếu dữ liệu tài chính với AgentCore...'
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

    function getPhapTranStatus(state) {
      switch (state) {
        case 'LISTENING': return 'Pháp Trận · Đang Lắng Nghe'
        case 'PROCESSING':
        case 'EXECUTING': return 'Pháp Trận · Đang Lĩnh Hội (Đang xử lý)'
        case 'CONFIRMING': return 'Pháp Trận · Chờ Xác Nhận'
        case 'SPEAKING': return 'Pháp Trận · Đang Truyền Âm'
        case 'SUCCESS': return 'Pháp Trận · Đã Hoàn Tất'
        case 'ERROR': return 'Pháp Trận · Trở Ngại'
        case 'TIMEOUT': return 'Pháp Trận · Hết Hạn Chờ'
        default: return 'Pháp Trận · Đang Giám Sát'
      }
    }

    return {
      isLiveActive,
      agentState,
      currentDisplayContent,
      currentConfirmation,
      currentExecutionResult,
      isProcessing,
      isSubmitting,
      hasSubmittedUtterance,
      lastSpokenText,
      lastUserUtterance,
      quickActionChips,
      displaySecondsRemaining,
      isListening,
      speechSupported,
      ttsEnabled,
      getPhapTranStatus,
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
  width: 18px;
  height: 18px;
  background: var(--color-surface, #0b1326);
  border: 1.5px solid var(--color-primary, #7dd6cc);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  box-shadow: 0 0 8px rgba(125, 214, 204, 0.6);
}

.switch-badge .badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary, #7dd6cc);
  display: block;
}

.switch-badge.badge-listening .badge-dot {
  background: #7dd6cc;
  box-shadow: 0 0 6px #7dd6cc;
  animation: pingDot 1.2s infinite;
}

.switch-badge.badge-thinking .badge-dot {
  background: #c4c1fb;
  box-shadow: 0 0 6px #c4c1fb;
}

.switch-badge.badge-confirming .badge-dot {
  background: #e3c370;
  box-shadow: 0 0 6px #e3c370;
}

.switch-badge.badge-executing .badge-dot {
  background: #7dd6cc;
  box-shadow: 0 0 8px #7dd6cc;
}

.switch-badge.badge-error .badge-dot {
  background: #ffb4ab;
  box-shadow: 0 0 6px #ffb4ab;
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
   STITCH CELESTIAL SYSTEM CONSOLE STYLES (PHASE 4B)
   Color palette: Spiritual Jade (#7dd6cc), Celestial Indigo (#c4c1fb),
   Talisman Gold (#e3c370), Deep Midnight Surface (#0b1326, #171f33)
   ═══════════════════════════════════════════════════════════════ */
.system-mode-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 14, 32, 0.78);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  animation: fadeInOverlay 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInOverlay {
  from { opacity: 0; }
  to { opacity: 1; }
}

.system-window-shell {
  position: relative;
  width: min(78vw, 1060px);
  max-height: 85vh;
  background: rgba(23, 31, 51, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1rem;
  border: 1px solid rgba(125, 214, 204, 0.3);
  outline: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 50px rgba(43, 138, 130, 0.25), 0 20px 50px rgba(0, 0, 0, 0.85);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: scaleInShell 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleInShell {
  from { opacity: 0; transform: scale(0.95) translateY(12px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* 4 Corner Technical Cut Accents */
.shell-corner {
  position: absolute;
  width: 1.5rem;
  height: 1.5rem;
  pointer-events: none;
  z-index: 20;
}
.shell-corner.corner-tl {
  top: 0; left: 0;
  border-top: 2px solid var(--color-primary, #7dd6cc);
  border-left: 2px solid var(--color-primary, #7dd6cc);
  border-top-left-radius: 0.5rem;
}
.shell-corner.corner-tr {
  top: 0; right: 0;
  border-top: 2px solid var(--color-tertiary, #e3c370);
  border-right: 2px solid var(--color-tertiary, #e3c370);
  border-top-right-radius: 0.5rem;
}
.shell-corner.corner-bl {
  bottom: 0; left: 0;
  border-bottom: 2px solid var(--color-secondary, #c4c1fb);
  border-left: 2px solid var(--color-secondary, #c4c1fb);
  border-bottom-left-radius: 0.5rem;
}
.shell-corner.corner-br {
  bottom: 0; right: 0;
  border-bottom: 2px solid var(--color-primary, #7dd6cc);
  border-right: 2px solid var(--color-primary, #7dd6cc);
  border-bottom-right-radius: 0.5rem;
}

/* ─── SYSTEM HEADER ─── */
.system-header {
  height: 3.5rem;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(34, 42, 61, 0.65);
  border-bottom: 1px solid rgba(125, 214, 204, 0.2);
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.system-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-beacon-pulse {
  width: 0.625rem;
  height: 0.625rem;
  border-radius: 9999px;
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 10px #7dd6cc;
  animation: beaconPulse 2s ease-in-out infinite;
}

@keyframes beaconPulse {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.25); opacity: 1; }
}

.system-header-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  letter-spacing: -0.01em;
  margin: 0;
}

.system-badge-tag {
  font-family: monospace;
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  background: rgba(125, 214, 204, 0.12);
  border: 1px solid rgba(125, 214, 204, 0.3);
  color: var(--color-primary, #7dd6cc);
  letter-spacing: 0.05em;
  font-weight: 500;
}

.system-header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.audio-wave-visualizer {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 18px;
  padding: 0 6px;
}
.audio-wave-visualizer .bar {
  width: 3px;
  height: 100%;
  background: var(--color-primary, #7dd6cc);
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

.sys-tool-btn {
  background: rgba(6, 14, 32, 0.6);
  border: 1px solid rgba(125, 214, 204, 0.3);
  color: var(--color-on-surface, #dae2fd);
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}
.sys-tool-btn:hover {
  background: rgba(34, 42, 61, 0.8);
  border-color: var(--color-primary, #7dd6cc);
}

.sys-close-x-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(6, 14, 32, 0.8);
  border: 1px solid rgba(125, 214, 204, 0.3);
  color: var(--color-on-surface-variant, #bdc9c6);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s;
}
.sys-close-x-btn:hover {
  border-color: var(--color-primary, #7dd6cc);
  color: var(--color-primary, #7dd6cc);
  background: rgba(34, 42, 61, 0.9);
  transform: scale(1.06);
}

/* ─── SYSTEM BODY CONTAINER ─── */
.system-body-container {
  padding: 1.25rem 1.5rem;
  max-height: calc(85vh - 3.5rem);
  overflow-y: auto;
}

.outer-system-console {
  background: rgba(6, 14, 32, 0.9);
  backdrop-filter: blur(24px);
  border-radius: 0.75rem;
  border: 1px solid rgba(125, 214, 204, 0.2);
  box-shadow: inset 0 0 20px rgba(196, 193, 251, 0.05), 0 12px 36px rgba(0,0,0,0.5);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Telemetry Strip */
.telemetry-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.875rem;
  border-radius: 0.5rem;
  background: linear-gradient(90deg, rgba(125, 214, 204, 0.12), rgba(196, 193, 251, 0.08), rgba(227, 195, 112, 0.08));
  border: 1px solid rgba(125, 214, 204, 0.25);
  box-shadow: 0 0 15px rgba(43, 138, 130, 0.1);
}

.telemetry-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.telemetry-sys-id {
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--color-primary, #7dd6cc);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.telemetry-ping-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 9999px;
  background: var(--color-primary, #7dd6cc);
  animation: pingDot 1.5s infinite;
}

@keyframes pingDot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.4; }
}

.telemetry-sync-rate {
  font-size: 0.6875rem;
  letter-spacing: 0.04em;
  color: var(--color-outline, #889391);
}

.telemetry-right {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-tertiary, #e3c370);
  text-transform: uppercase;
}

.telemetry-state-icon {
  font-size: 0.875rem;
}

/* ─── SYSTEM GRID (LEFT PORTAL + RIGHT STREAM) ─── */
.system-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.25rem;
  align-items: stretch;
}

/* Left Spirit Portal Card */
.spirit-portal-card {
  background: rgba(19, 27, 46, 0.85);
  border: 1px solid rgba(125, 214, 204, 0.3);
  border-radius: 0.75rem;
  padding: 1.25rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(43, 138, 130, 0.15);
}

.portal-micro {
  position: absolute;
  width: 0.5rem;
  height: 0.5rem;
  pointer-events: none;
}
.portal-micro.micro-tl { top: 4px; left: 4px; border-top: 1px solid var(--color-primary, #7dd6cc); border-left: 1px solid var(--color-primary, #7dd6cc); }
.portal-micro.micro-tr { top: 4px; right: 4px; border-top: 1px solid var(--color-tertiary, #e3c370); border-right: 1px solid var(--color-tertiary, #e3c370); }
.portal-micro.micro-bl { bottom: 4px; left: 4px; border-bottom: 1px solid var(--color-secondary, #c4c1fb); border-left: 1px solid var(--color-secondary, #c4c1fb); }
.portal-micro.micro-br { bottom: 4px; right: 4px; border-bottom: 1px solid var(--color-primary, #7dd6cc); border-right: 1px solid var(--color-primary, #7dd6cc); }

.chibi-portal-character-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
  padding: 0.5rem 0;
}

.spirit-portal-meta {
  margin-top: 0.875rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.spirit-name-row {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
}

.spirit-verified-badge {
  color: var(--color-primary, #7dd6cc);
  font-size: 0.875rem;
  font-weight: 700;
}

.spirit-realm-title {
  font-size: 0.75rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

.spirit-state-pill {
  margin-top: 0.375rem;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  background: rgba(34, 42, 61, 0.8);
  border: 1px solid rgba(125, 214, 204, 0.25);
  font-size: 0.6875rem;
  color: var(--color-secondary, #c4c1fb);
}

.state-dot-mini {
  width: 5px;
  height: 5px;
  border-radius: 9999px;
  background: var(--color-primary, #7dd6cc);
}

/* Right Stream Column */
.action-stream-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
  min-height: 280px;
}

/* 1. Trạng thái PROCESSING */
.system-processing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  text-align: center;
  padding: 2rem 1rem;
  animation: fadeIn 0.3s ease;
}

.celestial-spinner {
  position: relative;
  width: 4.5rem;
  height: 4.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-ring {
  position: absolute;
  inset: 0;
  border: 3px solid transparent;
  border-top-color: var(--color-primary, #7dd6cc);
  border-right-color: var(--color-tertiary, #e3c370);
  border-radius: 50%;
  animation: spinRune 1.5s linear infinite;
}

@keyframes spinRune {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner-rune {
  font-size: 1.625rem;
  color: var(--color-tertiary, #e3c370);
  text-shadow: 0 0 12px rgba(227, 195, 112, 0.6);
}

.processing-title {
  font-size: 1.125rem;
  color: var(--color-on-surface, #dae2fd);
  font-weight: 600;
  margin: 0;
}
.processing-sub {
  font-size: 0.8125rem;
  color: var(--color-secondary, #c4c1fb);
  margin: 0.25rem 0 0 0;
}

/* 2. Talisman Confirmation Card */
.talisman-confirmation-card {
  background: rgba(19, 27, 46, 0.95);
  border: 2px solid rgba(125, 214, 204, 0.35);
  outline: 1px solid rgba(227, 195, 112, 0.3);
  border-radius: 0.75rem;
  padding: 1.25rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 25px rgba(43, 138, 130, 0.15);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: fadeIn 0.25s ease;
}

.talisman-watermark {
  position: absolute;
  right: -2rem;
  bottom: -2rem;
  width: 12rem;
  height: 12rem;
  opacity: 0.07;
  color: var(--color-primary, #7dd6cc);
  pointer-events: none;
}

.talisman-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(125, 214, 204, 0.2);
}

.talisman-title-group {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.talisman-gold-bar {
  width: 0.25rem;
  height: 1.5rem;
  background: var(--color-tertiary, #e3c370);
  border-radius: 9999px;
  box-shadow: 0 0 8px #e3c370;
}

.talisman-title {
  font-size: 0.9375rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -0.01em;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.talisman-subtitle {
  font-size: 0.6875rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  text-transform: uppercase;
  margin: 0;
}

.talisman-type-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  background: rgba(68, 65, 115, 0.5);
  border: 1px solid rgba(196, 193, 251, 0.4);
  color: var(--color-secondary, #c4c1fb);
  font-size: 0.6875rem;
  font-weight: 600;
}

.transaction-flow-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.75rem;
  align-items: center;
}

.flow-box {
  background: rgba(23, 31, 51, 0.85);
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid rgba(196, 193, 251, 0.25);
}

.source-box {
  border-color: rgba(196, 193, 251, 0.3);
}

.target-box {
  border-color: rgba(125, 214, 204, 0.3);
}

.flow-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-outline, #889391);
  display: block;
  margin-bottom: 0.375rem;
}

.flow-content {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.flow-icon-wrap {
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.source-icon {
  background: rgba(68, 65, 115, 0.6);
  border: 1px solid rgba(196, 193, 251, 0.4);
}

.target-icon {
  background: rgba(68, 159, 150, 0.6);
  border: 1px solid rgba(125, 214, 204, 0.4);
}

.flow-meta {
  min-width: 0;
  flex: 1;
}

.flow-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-on-surface, #dae2fd);
  margin: 0;
}

.flow-sub {
  font-size: 0.6875rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  margin: 0;
}

.flow-arrow-col {
  display: flex;
  justify-content: center;
  color: var(--color-primary, #7dd6cc);
  font-size: 1.25rem;
  font-weight: 700;
  filter: drop-shadow(0 0 6px rgba(125, 214, 204, 0.6));
}

.large-figure-panel {
  background: rgba(34, 42, 61, 0.6);
  border: 1px solid rgba(227, 195, 112, 0.25);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.figure-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-tertiary, #e3c370);
  display: block;
  font-weight: 500;
}

.figure-amount {
  font-size: 1.625rem;
  font-weight: 700;
  color: var(--color-primary, #7dd6cc);
  letter-spacing: -0.02em;
  text-shadow: 0 0 12px rgba(125, 214, 204, 0.35);
}

.figure-fee-box {
  text-align: right;
}

.fee-label {
  font-size: 0.6875rem;
  color: var(--color-outline, #889391);
  display: block;
}

.fee-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-primary, #7dd6cc);
}

.talisman-note-row {
  background: rgba(23, 31, 51, 0.6);
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  display: flex;
  gap: 0.5rem;
}
.note-label { color: var(--color-outline, #889391); }
.note-val { color: var(--color-on-surface, #dae2fd); font-weight: 500; }

.conf-question-text {
  font-size: 0.8125rem;
  color: var(--color-on-surface, #dae2fd);
  text-align: center;
  line-height: 1.5;
  margin: 0;
}

.conf-question-sub {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-outline, #889391);
  margin-top: 0.125rem;
}

.talisman-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-talisman-cancel {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  background: rgba(45, 52, 73, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--color-on-surface-variant, #bdc9c6);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-talisman-cancel:hover {
  background: rgba(49, 57, 77, 0.95);
  color: var(--color-on-surface, #dae2fd);
}

.btn-talisman-confirm {
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  background: var(--color-primary-container, #449f96);
  border: 1px solid rgba(125, 214, 204, 0.4);
  color: var(--color-on-primary, #003733);
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(43, 138, 130, 0.35);
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: all 0.2s;
}
.btn-talisman-confirm:hover {
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 22px rgba(125, 214, 204, 0.5);
  transform: translateY(-1px);
}
.confirm-check-icon {
  font-size: 1rem;
  font-weight: 800;
}

/* 2.5 User Voice Transcript Banner */
.user-voice-transcript-banner {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  background: rgba(34, 42, 61, 0.6);
  border: 1px dashed rgba(125, 214, 204, 0.35);
  border-radius: 0.625rem;
  padding: 0.5rem 0.875rem;
  animation: fadeIn 0.2s ease;
}

.user-transcript-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--color-primary, #7dd6cc);
  text-transform: uppercase;
}

.user-mic-spark {
  font-size: 0.75rem;
}

.user-transcript-phrase {
  font-size: 0.875rem;
  color: var(--color-on-surface, #dae2fd);
  font-style: italic;
  margin: 0;
  line-height: 1.4;
}

/* 3. Reply / Response Bubble */
.system-reply-bubble {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  animation: fadeIn 0.25s ease;
}

.reply-header-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--color-primary, #7dd6cc);
  text-transform: uppercase;
}

.countdown-tag {
  margin-left: auto;
  font-size: 0.6875rem;
  color: var(--color-secondary, #c4c1fb);
  background: rgba(68, 65, 115, 0.4);
  border: 1px solid rgba(196, 193, 251, 0.3);
  border-radius: 0.25rem;
  padding: 0.125rem 0.375rem;
}

.reply-card {
  background: rgba(23, 31, 51, 0.9);
  border: 1px solid rgba(125, 214, 204, 0.25);
  border-radius: 0.75rem;
  border-top-left-radius: 0;
  padding: 1rem 1.25rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

.reply-text {
  font-size: 0.875rem;
  line-height: 1.7;
  color: var(--color-on-surface, #dae2fd);
}

.execution-result-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 0.5rem;
  padding: 0.375rem 0.875rem;
  color: #a7f3d0;
  font-size: 0.75rem;
  font-weight: 600;
  align-self: flex-start;
}

/* 4. Standby View */
.system-standby-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
  padding: 1rem 0;
  animation: fadeIn 0.3s ease;
}

.standby-rune-circle {
  position: relative;
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rune-outer-ring {
  position: absolute;
  inset: 0;
  border: 1.5px dashed rgba(125, 214, 204, 0.5);
  border-radius: 50%;
  animation: rotateAuraRings 12s linear infinite;
}

.rune-inner-symbol {
  font-size: 1.5rem;
  color: var(--color-primary, #7dd6cc);
}

.standby-lead-text {
  font-size: 0.875rem;
  color: var(--color-on-surface-variant, #bdc9c6);
  max-width: 480px;
  line-height: 1.6;
  margin: 0;
}

.pulse-beacon-cyan {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 8px #7dd6cc;
  display: inline-block;
  margin-right: 0.25rem;
}

.standby-prompts-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  max-width: 520px;
  margin-top: 0.25rem;
}

.prompt-chip {
  background: rgba(34, 42, 61, 0.7);
  border: 1px solid rgba(125, 214, 204, 0.25);
  color: var(--color-on-surface, #dae2fd);
  font-size: 0.75rem;
  padding: 0.35rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.prompt-chip:hover {
  background: rgba(68, 159, 150, 0.2);
  border-color: var(--color-primary, #7dd6cc);
  color: var(--color-primary, #7dd6cc);
  transform: translateY(-1px);
}

/* ─── FOOTER STATUS & COMMAND INPUT ─── */
.system-console-footer {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(125, 214, 204, 0.15);
}

.footer-telemetry-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.footer-status-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-secondary, #c4c1fb);
}

.status-indicator-dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  flex-shrink: 0;
}
.dot-listening { background: var(--color-primary, #7dd6cc); box-shadow: 0 0 6px #7dd6cc; }
.dot-speaking { background: var(--color-secondary, #c4c1fb); box-shadow: 0 0 6px #c4c1fb; }
.dot-processing { background: var(--color-tertiary, #e3c370); box-shadow: 0 0 6px #e3c370; }
.dot-confirming { background: var(--color-tertiary, #e3c370); box-shadow: 0 0 8px #e3c370; }
.dot-success { background: #10b981; box-shadow: 0 0 6px #10b981; }
.dot-error { background: #ffb4ab; box-shadow: 0 0 6px #ffb4ab; }
.dot-timeout { background: #889391; }
.dot-closed, .dot-sleeping { background: #444173; }

.btn-mic-stream-toggle {
  background: rgba(68, 65, 115, 0.4);
  border: 1px solid rgba(196, 193, 251, 0.35);
  color: var(--color-secondary, #c4c1fb);
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-mic-stream-toggle.active {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
  color: #ffb4ab;
}

/* ─── ACCESSIBILITY & REDUCED MOTION ─── */
@media (prefers-reduced-motion: reduce) {
  .aura-rings-svg,
  .spirit-halo,
  .spirit-chibi-body,
  .rune-outer-ring,
  .spinner-ring,
  .header-beacon-pulse,
  .telemetry-ping-dot,
  .audio-wave-visualizer .bar {
    animation: none !important;
  }
}

/* ─── RESPONSIVE BREAKPOINTS ─── */
@media (max-width: 768px) {
  .system-window-shell {
    width: 94vw;
    max-height: 92vh;
  }
  .system-body-container {
    padding: 0.875rem;
  }
  .outer-system-console {
    padding: 0.875rem;
  }
  .system-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .aura-rings-wrap {
    width: 8rem;
    height: 8rem;
  }
  .chibi-portal-orb {
    width: 5.5rem;
    height: 5.5rem;
  }
  .transaction-flow-grid {
    grid-template-columns: 1fr;
  }
  .flow-arrow-col {
    transform: rotate(90deg);
    padding: 0.25rem 0;
  }
  .large-figure-panel {
    flex-direction: column;
    align-items: flex-start;
  }
  .figure-fee-box {
    text-align: left;
  }
  .talisman-actions {
    flex-direction: column-reverse;
  }
  .btn-talisman-cancel,
  .btn-talisman-confirm {
    width: 100%;
    justify-content: center;
  }
  .hidden-mobile {
    display: none !important;
  }
}
</style>
