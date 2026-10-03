<template>
  <!-- ═══════ TAB 8: AI CHAT ═══════ -->
  <section class="tab-panel">
    <h2 class="section-title">💬 Khấu Bái Khí Linh — Trợ Lý AI Gemini</h2>

    <div class="chat-container">
      <div class="chat-messages" ref="chatMessagesEl">
        <div class="chat-welcome">
          <div class="chat-ai-avatar">🔮</div>
          <p>Kính chào Ký Chủ! Ta là <strong>Khí Linh Tiên Trí</strong>, trợ lý tài chính AI phong cách tu tiên. Hãy hỏi ta bất cứ điều gì về tài chính của đạo hữu!</p>
        </div>
        <div v-for="(msg, idx) in chatMessages" :key="idx"
             :class="['chat-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
          <div class="bubble-avatar">{{ msg.role === 'user' ? '🧙' : '🔮' }}</div>
          <div class="bubble-content" v-html="formatChatText(msg.text)"></div>
        </div>
        <div v-if="chatLoading" class="chat-bubble ai-bubble">
          <div class="bubble-avatar">🔮</div>
          <div class="bubble-content typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      <div v-if="suggestedQuestions.length > 0" class="suggested-questions-container">
        <span class="suggested-chip" v-for="q in suggestedQuestions" :key="q" @click="chatInput = q">
          {{ q }}
        </span>
      </div>
      <div class="chat-input-area">
        <input v-model="chatInput" type="text"
               placeholder="Hỏi Tiên Trí về tài chính..."
               @keyup.enter="sendChat" />
        <button class="btn-jade-sm" @click="sendChat" :disabled="chatLoading || !chatInput.trim()">
          ⚡ Gửi
        </button>
      </div>
    </div>
  </section>
</template>

<script>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useAiStore } from '../stores/ai'
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'ChatView',
  setup() {
    const store = useAiStore()
    const chatMessagesEl = ref(null)

    function scrollChat() {
      const el = chatMessagesEl.value
      if (el) el.scrollTop = el.scrollHeight
    }

    // Cuộn xuống tin nhắn mới nhất khi mở tab và mỗi khi có tin nhắn mới / đang chờ trả lời
    onMounted(() => nextTick(scrollChat))
    watch(() => [store.chatMessages.length, store.chatLoading], () => nextTick(scrollChat))

    return { ...useAppBindings(), chatMessagesEl }
  },
}
</script>
