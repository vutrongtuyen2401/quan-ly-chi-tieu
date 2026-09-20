<template>
  <div class="knowledge-panel-workspace">
    <!-- Ambient Celestial Backdrop Glow -->
    <div class="ambient-glow-orb purple" aria-hidden="true"></div>
    <div class="ambient-glow-orb jade" aria-hidden="true"></div>

    <!-- Main System Frame for Khí Linh Knowledge -->
    <div class="knowledge-system-frame">
      <!-- 1. Header Bar -->
      <KnowledgeHeader @clear-history="$emit('clear-history')" />

      <!-- 2. Intro Welcome Card -->
      <div class="intro-container">
        <KnowledgeIntroCard />
      </div>

      <!-- 3. Message Stream -->
      <KnowledgeStream
        :messages="chatMessages"
        :loading="chatLoading"
        :user-name="userName"
      />

      <!-- 4. Quick Prompt Pills & Input Action Bar -->
      <KnowledgePromptBar
        :suggested-questions="suggestedQuestions"
        :loading="chatLoading"
        @send-message="$emit('send-message', $event)"
      />
    </div>
  </div>
</template>

<script>
import KnowledgeHeader from './KnowledgeHeader.vue'
import KnowledgeIntroCard from './KnowledgeIntroCard.vue'
import KnowledgeStream from './KnowledgeStream.vue'
import KnowledgePromptBar from './KnowledgePromptBar.vue'

export default {
  name: 'KnowledgePanel',
  components: {
    KnowledgeHeader,
    KnowledgeIntroCard,
    KnowledgeStream,
    KnowledgePromptBar
  },
  props: {
    chatMessages: {
      type: Array,
      default: () => []
    },
    chatLoading: {
      type: Boolean,
      default: false
    },
    suggestedQuestions: {
      type: Array,
      default: () => []
    },
    userName: {
      type: String,
      default: 'Đạo Hữu'
    }
  },
  emits: ['send-message', 'clear-history']
}
</script>

<style scoped>
.knowledge-panel-workspace {
  position: relative;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding-bottom: var(--space-2xl, 2rem);
  animation: fadeInKnowledge 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInKnowledge {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ambient glow background orbs */
.ambient-glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(48px);
  pointer-events: none;
  opacity: 0.35;
}

.ambient-glow-orb.purple {
  top: -2rem;
  right: 15%;
  width: 18rem;
  height: 18rem;
  background: rgba(68, 65, 115, 0.4);
}

.ambient-glow-orb.jade {
  top: 30%;
  left: -2rem;
  width: 16rem;
  height: 16rem;
  background: rgba(125, 214, 204, 0.2);
}

/* Main System Frame */
.knowledge-system-frame {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  background: rgba(19, 27, 46, 0.92);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(136, 147, 145, 0.25);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(125, 214, 204, 0.08);
  overflow: hidden;
}

.intro-container {
  padding: 1rem 1.5rem 0 1.5rem;
}

@media (max-width: 640px) {
  .intro-container {
    padding: 0.75rem 0.75rem 0 0.75rem;
  }
  .knowledge-panel-workspace {
    padding-bottom: 1rem;
  }
}
</style>
