<template>
  <div
    class="khi-linh-character-container"
    :class="[
      `size-${size}`,
      `state-${normalizedState}`,
      {
        'is-interactive': interactive,
        'has-aura': showAura
      }
    ]"
    :role="ariaHidden ? undefined : 'img'"
    :aria-hidden="ariaHidden ? 'true' : undefined"
    :aria-label="ariaHidden ? undefined : `${alt} (${stateDescription})`"
  >
    <!-- 1. Ambient Spiritual Glow (Dynamic multi-tint aura) -->
    <div v-if="showAura" class="kl-ambient-glow" aria-hidden="true"></div>

    <!-- 2. Sacred Geometry Rotating Aura Rings (Stitch Celestial System) -->
    <div
      v-if="showAura && showRings && (size === 'portal' || size === 'lg' || size === 'md')"
      class="kl-aura-rings-wrap"
      aria-hidden="true"
    >
      <svg class="kl-aura-rings-svg" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="44"
          fill="none"
          class="ring-primary"
          stroke="currentColor"
          stroke-dasharray="3 4"
          stroke-width="0.75"
        />
        <circle
          cx="50"
          cy="50"
          r="38"
          fill="none"
          class="ring-secondary"
          stroke="currentColor"
          stroke-dasharray="1 6"
          stroke-width="0.5"
        />
        <polygon class="poly-rune poly-top" fill="currentColor" points="50,4 53,10 47,10" />
        <polygon class="poly-rune poly-bottom" fill="currentColor" points="50,96 53,90 47,90" />
        <polygon class="poly-rune poly-left" fill="currentColor" points="4,50 10,53 10,47" />
        <polygon class="poly-rune poly-right" fill="currentColor" points="96,50 90,53 90,47" />
      </svg>
    </div>

    <!-- 3. Character Core Framing & Optical Alignment -->
    <div class="kl-character-core">
      <!-- Canonical Chibi Artwork (Local) -->
      <img
        v-if="!imgFailed"
        :src="chibiJpgUrl"
        :alt="alt"
        class="kl-character-image"
        @error="handleImgError"
      />
      <!-- High-fidelity Vector SVG Companion Fallback -->
      <img
        v-else
        :src="chibiSvgUrl"
        :alt="alt"
        class="kl-character-svg-fallback"
      />

      <!-- Subtle spiritual light sheen overlay -->
      <div class="kl-energy-sheen" aria-hidden="true"></div>
    </div>

    <!-- 4. Optional State Beacon / Status Node -->
    <div
      v-if="showStatusDot"
      class="kl-status-node"
      :class="`node-${normalizedState}`"
      aria-hidden="true"
    >
      <span class="kl-status-pulse"></span>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import chibiJpgUrl from '../../assets/khi-linh/khi-linh-chibi.jpg'
import chibiSvgUrl from '../../assets/khi-linh/khi-linh-chibi.svg'

export default {
  name: 'KhiLinhCharacter',
  props: {
    size: {
      type: String,
      default: 'md',
      validator: val => ['sm', 'md', 'lg', 'portal'].includes(val)
    },
    state: {
      type: String,
      default: 'IDLE'
    },
    showAura: {
      type: Boolean,
      default: true
    },
    showRings: {
      type: Boolean,
      default: true
    },
    showStatusDot: {
      type: Boolean,
      default: false
    },
    interactive: {
      type: Boolean,
      default: false
    },
    alt: {
      type: String,
      default: 'Khí Linh - Tiên Linh Càn Khôn'
    },
    ariaHidden: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    const imgFailed = ref(false)

    function handleImgError() {
      imgFailed.value = true
    }

    const normalizedState = computed(() => {
      const s = (props.state || 'IDLE').toUpperCase()
      if (['WAITING_INPUT', 'LISTENING'].includes(s)) return 'listening'
      if (['THINKING', 'PROCESSING'].includes(s)) return 'thinking'
      if (['CONFIRMING', 'PENDING_CONFIRMATION'].includes(s)) return 'confirming'
      if (['EXECUTING', 'RUNNING'].includes(s)) return 'executing'
      if (['SUCCESS', 'COMPLETED', 'RESOLVED'].includes(s)) return 'success'
      if (['ERROR', 'FAILED', 'REJECTED'].includes(s)) return 'error'
      if (['SLEEPING', 'STANDBY', 'RESTING'].includes(s)) return 'sleeping'
      return 'idle'
    })

    const stateDescription = computed(() => {
      switch (normalizedState.value) {
        case 'listening':
          return 'Đang lắng nghe'
        case 'thinking':
          return 'Đang suy nghĩ'
        case 'confirming':
          return 'Chờ xác nhận pháp lệnh'
        case 'executing':
          return 'Đang thi triển pháp thuật'
        case 'success':
          return 'Thành công viên mãn'
        case 'error':
          return 'Trở ngại linh lực'
        case 'sleeping':
          return 'Đang thiền định'
        default:
          return 'Sẵn sàng tương tác'
      }
    })

    return {
      chibiJpgUrl,
      chibiSvgUrl,
      imgFailed,
      handleImgError,
      normalizedState,
      stateDescription
    }
  }
}
</script>

<style scoped>
/* ─── CONTAINER FOUNDATION ─── */
.khi-linh-character-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  flex-shrink: 0;
  vertical-align: middle;
}

/* ─── SIZE DEFINITIONS ─── */
/* Size: Small (38px) - Chat rows, header */
.khi-linh-character-container.size-sm {
  width: 38px;
  height: 38px;
}

.khi-linh-character-container.size-sm .kl-character-core {
  width: 38px;
  height: 38px;
  border-width: 1.5px;
}

/* Size: Medium (60px) - Floating switch button */
.khi-linh-character-container.size-md {
  width: 62px;
  height: 62px;
}

.khi-linh-character-container.size-md .kl-character-core {
  width: 52px;
  height: 52px;
  border-width: 2px;
}

/* Size: Large (104px) - Knowledge Intro Card */
.khi-linh-character-container.size-lg {
  width: 108px;
  height: 108px;
}

.khi-linh-character-container.size-lg .kl-character-core {
  width: 92px;
  height: 92px;
  border-width: 2.5px;
}

/* Size: Portal (148px) - System Window Center Portal */
.khi-linh-character-container.size-portal {
  width: 156px;
  height: 156px;
}

.khi-linh-character-container.size-portal .kl-character-core {
  width: 118px;
  height: 118px;
  border-width: 3px;
}

/* ─── 1. AMBIENT GLOW LAYER ─── */
.kl-ambient-glow {
  position: absolute;
  inset: -12%;
  border-radius: 50%;
  pointer-events: none;
  z-index: 1;
  opacity: 0.6;
  filter: blur(10px);
  transition: background 0.6s ease, opacity 0.6s ease, transform 0.6s ease;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.35) 0%, rgba(68, 65, 115, 0.15) 60%, transparent 80%);
}

.size-portal .kl-ambient-glow {
  inset: -18%;
  filter: blur(16px);
}

.size-lg .kl-ambient-glow {
  inset: -14%;
  filter: blur(12px);
}

.size-sm .kl-ambient-glow {
  inset: -8%;
  filter: blur(6px);
  opacity: 0.4;
}

/* ─── 2. SACRED GEOMETRY AURA RINGS ─── */
.kl-aura-rings-wrap {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 2;
  animation: klAuraRotate 24s linear infinite;
}

.kl-aura-rings-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.ring-primary {
  color: var(--color-primary, #7dd6cc);
  opacity: 0.75;
}

.ring-secondary {
  color: var(--color-secondary, #c4c1fb);
  opacity: 0.6;
}

.poly-rune {
  transform-origin: 50px 50px;
}

.poly-top,
.poly-bottom {
  color: var(--color-tertiary, #e3c370);
  opacity: 0.9;
}

.poly-left,
.poly-right {
  color: var(--color-primary, #7dd6cc);
  opacity: 0.85;
}

/* ─── 3. CHARACTER CORE FRAMING ─── */
.kl-character-core {
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
  background: radial-gradient(circle at 50% 30%, #171f33 0%, #0b1326 100%);
  border-style: solid;
  border-color: rgba(125, 214, 204, 0.5);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5), inset 0 0 12px rgba(125, 214, 204, 0.2);
  transition: transform 0.4s ease, border-color 0.4s ease, box-shadow 0.4s ease;
}

/* Optical centering: character face and ears are in the upper 70% */
.kl-character-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 28%;
  display: block;
  transform: scale(1.18);
  transition: transform 0.4s ease, filter 0.4s ease;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3));
}

.kl-character-svg-fallback {
  width: 100%;
  height: 100%;
  display: block;
}

/* Subtle spiritual sheen */
.kl-energy-sheen {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0) 50%, rgba(125, 214, 204, 0.15) 100%);
  mix-blend-mode: overlay;
}

/* ─── 4. STATUS INDICATOR NODE ─── */
.kl-status-node {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  z-index: 4;
  border: 2px solid var(--color-surface, #0b1326);
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 8px rgba(125, 214, 204, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.size-sm .kl-status-node {
  width: 10px;
  height: 10px;
  border-width: 1.5px;
}

.size-lg .kl-status-node,
.size-portal .kl-status-node {
  width: 18px;
  height: 18px;
  border-width: 2.5px;
}

.kl-status-pulse {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #ffffff;
  display: block;
}

/* ─── STATE-BASED VISUAL VARIANTS ─── */

/* 1. STATE: IDLE (Default peaceful guardian) */
.state-idle .kl-character-core {
  border-color: rgba(125, 214, 204, 0.5);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5), 0 0 14px rgba(125, 214, 204, 0.25);
  animation: klFloatIdle 5s ease-in-out infinite;
}

/* 2. STATE: SLEEPING (Deep meditation, waiting / wake-word standby) */
.state-sleeping {
  opacity: 0.85;
}

.state-sleeping .kl-character-core {
  border-color: rgba(196, 193, 251, 0.35);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.6), 0 0 8px rgba(68, 65, 115, 0.3);
  animation: klBreatheSlow 6s ease-in-out infinite;
}

.state-sleeping .kl-ambient-glow {
  opacity: 0.3;
  background: radial-gradient(circle, rgba(196, 193, 251, 0.2) 0%, rgba(68, 65, 115, 0.1) 70%, transparent 90%);
}

.state-sleeping .kl-aura-rings-wrap {
  animation-duration: 36s;
  opacity: 0.4;
}

/* 3. STATE: LISTENING (Active audio attention) */
.state-listening .kl-character-core {
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 20px rgba(125, 214, 204, 0.5), inset 0 0 10px rgba(125, 214, 204, 0.4);
  animation: klPulseActive 1.8s ease-in-out infinite;
}

.state-listening .kl-ambient-glow {
  opacity: 0.85;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.5) 0%, rgba(68, 159, 150, 0.25) 50%, transparent 80%);
}

.state-listening .kl-aura-rings-wrap {
  animation-duration: 12s;
}

.node-listening {
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.8);
}

/* 4. STATE: THINKING / PROCESSING (Contemplative wisdom) */
.state-thinking .kl-character-core {
  border-color: var(--color-secondary, #c4c1fb);
  box-shadow: 0 0 22px rgba(196, 193, 251, 0.45), inset 0 0 12px rgba(196, 193, 251, 0.3);
  animation: klShimmerWisdom 2.4s ease-in-out infinite;
}

.state-thinking .kl-ambient-glow {
  opacity: 0.8;
  background: radial-gradient(circle, rgba(196, 193, 251, 0.45) 0%, rgba(68, 65, 115, 0.3) 60%, transparent 80%);
}

.state-thinking .kl-aura-rings-wrap {
  animation-duration: 16s;
}

.node-thinking {
  background: var(--color-secondary, #c4c1fb);
  box-shadow: 0 0 10px rgba(196, 193, 251, 0.8);
}

/* 5. STATE: CONFIRMING (Authoritative talisman confirmation) */
.state-confirming .kl-character-core {
  border-color: var(--color-tertiary, #e3c370);
  box-shadow: 0 0 24px rgba(227, 195, 112, 0.5), inset 0 0 12px rgba(227, 195, 112, 0.35);
  animation: klPulseTalisman 2s ease-in-out infinite;
}

.state-confirming .kl-ambient-glow {
  opacity: 0.85;
  background: radial-gradient(circle, rgba(227, 195, 112, 0.45) 0%, rgba(198, 168, 88, 0.25) 55%, transparent 80%);
}

.node-confirming {
  background: var(--color-tertiary, #e3c370);
  box-shadow: 0 0 10px rgba(227, 195, 112, 0.9);
}

/* 6. STATE: EXECUTING (Dynamic energy flow) */
.state-executing .kl-character-core {
  border-color: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 28px rgba(125, 214, 204, 0.6), 0 0 14px rgba(227, 195, 112, 0.4);
  animation: klPulseActive 1.2s ease-in-out infinite;
}

.state-executing .kl-ambient-glow {
  opacity: 0.95;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.55) 0%, rgba(227, 195, 112, 0.25) 60%, transparent 85%);
}

.state-executing .kl-aura-rings-wrap {
  animation-duration: 8s;
}

.node-executing {
  background: var(--color-primary, #7dd6cc);
  box-shadow: 0 0 12px #7dd6cc;
}

/* 7. STATE: SUCCESS (Warm celestial joy) */
.state-success .kl-character-core {
  border-color: #7dd6cc;
  box-shadow: 0 0 26px rgba(125, 214, 204, 0.7), inset 0 0 14px rgba(125, 214, 204, 0.4);
}

.state-success .kl-ambient-glow {
  opacity: 0.9;
  background: radial-gradient(circle, rgba(125, 214, 204, 0.6) 0%, rgba(68, 159, 150, 0.3) 50%, transparent 80%);
}

.node-success {
  background: #7dd6cc;
  box-shadow: 0 0 10px #7dd6cc;
}

/* 8. STATE: ERROR (Soft protective warning) */
.state-error .kl-character-core {
  border-color: #ffb4ab;
  box-shadow: 0 0 20px rgba(255, 180, 171, 0.5), inset 0 0 10px rgba(255, 180, 171, 0.3);
}

.state-error .kl-ambient-glow {
  opacity: 0.75;
  background: radial-gradient(circle, rgba(255, 180, 171, 0.4) 0%, rgba(147, 0, 10, 0.2) 60%, transparent 80%);
}

.node-error {
  background: #ffb4ab;
  box-shadow: 0 0 10px #ffb4ab;
}

/* ─── INTERACTIVE HOVER EFFECTS ─── */
.is-interactive {
  cursor: pointer;
}

.is-interactive:hover .kl-character-core {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6), 0 0 20px rgba(125, 214, 204, 0.4);
}

.is-interactive:active .kl-character-core {
  transform: translateY(0) scale(0.98);
}

/* ─── SUBTLE KEYFRAME ANIMATIONS ─── */
@keyframes klAuraRotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes klFloatIdle {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

@keyframes klBreatheSlow {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(0.97);
  }
}

@keyframes klPulseActive {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.025);
  }
}

@keyframes klShimmerWisdom {
  0%, 100% {
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    transform: scale(1.02);
    filter: brightness(1.08);
  }
}

@keyframes klPulseTalisman {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
}

/* ─── ACCESSIBILITY: PREFERS REDUCED MOTION ─── */
@media (prefers-reduced-motion: reduce) {
  .kl-aura-rings-wrap,
  .kl-character-core,
  .kl-ambient-glow {
    animation: none !important;
    transition: none !important;
  }

  .is-interactive:hover .kl-character-core,
  .is-interactive:active .kl-character-core {
    transform: none !important;
  }
}
</style>
