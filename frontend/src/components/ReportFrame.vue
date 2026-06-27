<template>
  <div>
    <div v-if="loading" class="empty-state">
      <span class="spinner"></span>
      <p>加载报告中...</p>
    </div>
    <div v-else-if="error" class="empty-state">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="htmlContent">
      <div class="flex items-center justify-between mb-4">
        <h3 style="font-weight:600;font-size:16px;">报告预览</h3>
        <button class="btn btn-secondary btn-sm" @click="openFullscreen">新窗口打开</button>
      </div>
      <iframe class="report-frame" :srcdoc="htmlContent" title="分析报告"></iframe>
    </div>
    <div v-else class="empty-state"><p>暂无内容</p></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getReportHtml } from '../api'

const props = defineProps<{ taskId: string }>()
const htmlContent = ref('')
const loading = ref(false)
const error = ref('')

async function loadReport() {
  if (!props.taskId) return
  loading.value = true; error.value = ''
  try { htmlContent.value = await getReportHtml(props.taskId) } catch (e: unknown) { error.value = e instanceof Error ? e.message : '加载失败' }
  loading.value = false
}

function openFullscreen() {
  if (!htmlContent.value) return
  const win = window.open('', '_blank')
  if (win) { win.document.write(htmlContent.value); win.document.close() }
}

watch(() => props.taskId, loadReport)
onMounted(loadReport)
</script>
