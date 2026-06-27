<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesRef">
      <div v-if="messages.length === 0" class="empty-state">
        <p>向知识库提问，获取有依据的答案</p>
        <p class="text-xs text-muted mt-2">已索引：{{ collections.join('、') || '加载中...' }}</p>
      </div>

      <div v-for="(msg, i) in messages" :key="i" class="chat-message" :class="msg.role"
        v-html="msg.role === 'assistant' ? renderMd(msg.content) : escapeHtml(msg.content)">
      </div>

      <div v-if="loading" class="chat-message assistant"><span class="spinner"></span></div>
    </div>

    <div class="chat-input-area">
      <input v-model="question" class="input" placeholder="输入问题..." @keydown.enter="send" :disabled="loading" />
      <button class="btn btn-primary" @click="send" :disabled="loading || !question.trim()">发送</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { askKnowledge, getCollections } from '../api'

interface Message { role: 'user' | 'assistant'; content: string }

const messages = ref<Message[]>([])
const question = ref('')
const loading = ref(false)
const sessionId = ref('')
const collections = ref<string[]>([])
const messagesRef = ref<HTMLElement>()

onMounted(async () => {
  try { const res = await getCollections() as { collections: { name: string }[] }; collections.value = (res.collections || []).map(c => c.name) } catch {}
})

function escapeHtml(text: string) { const d = document.createElement('div'); d.textContent = text; return d.innerHTML }
function renderMd(text: string) {
  let h = escapeHtml(text)
  h = h.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  h = h.replace(/^&gt;\s?(.*)$/gm, '<blockquote>$1</blockquote>')
  h = h.replace(/\n/g, '<br>')
  return h
}

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', content: q }); question.value = ''; loading.value = true
  try {
    const res = await askKnowledge(q, undefined, sessionId.value) as { answer: string; session_id: string }
    sessionId.value = res.session_id; messages.value.push({ role: 'assistant', content: res.answer })
  } catch (e: unknown) {
    messages.value.push({ role: 'assistant', content: `Error: ${e instanceof Error ? e.message : 'failed'}` })
  }
  loading.value = false
  await nextTick()
  if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
}
</script>
