<template>
  <div class="card">
    <div class="flex items-center justify-between">
      <div class="task-status">
        <span v-if="status !== 'done' && status !== 'failed'"><span class="spinner"></span></span>
        <div>
          <div style="font-weight:500;">{{ statusLabel }}</div>
          <div class="text-xs text-muted mt-2">{{ progress || '准备中...' }}</div>
        </div>
      </div>
      <span v-if="status" class="badge" :class="statusBadgeClass">{{ statusText }}</span>
    </div>
    <div v-if="status !== 'done' && status !== 'failed'" class="progress-bar mt-4">
      <div class="progress-bar-fill" :style="{ width: percent + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { getTask } from '../api'

const props = defineProps<{ taskId: string }>()
const emit = defineEmits<{ done: [taskId: string]; failed: [error: string] }>()

const status = ref('')
const progress = ref('')
let timer: ReturnType<typeof setInterval> | null = null

const statusLabel = computed(() => {
  const map: Record<string, string> = { pending: '等待执行', parsing: '正在解析文件', analyzing: '正在分析数据', done: '分析完成', failed: '分析失败' }
  return map[status.value] || status.value
})

const statusText = computed(() => {
  const map: Record<string, string> = { pending: '等待', parsing: '解析', analyzing: '分析', done: '完成', failed: '失败' }
  return map[status.value] || status.value
})

const statusBadgeClass = computed(() => ({
  'badge-info': status.value === 'pending' || status.value === 'parsing',
  'badge-warning': status.value === 'analyzing',
  'badge-success': status.value === 'done',
  'badge-danger': status.value === 'failed',
}))

const percent = computed(() => {
  if (status.value === 'pending') return 5
  if (status.value === 'parsing') return 30
  if (status.value === 'analyzing') return 70
  if (status.value === 'done') return 100
  return 0
})

function poll() {
  timer = setInterval(async () => {
    try {
      const res = await getTask(props.taskId) as { status: string; progress: string }
      status.value = res.status; progress.value = res.progress
      if (res.status === 'done') { if (timer) clearInterval(timer); emit('done', props.taskId) }
      else if (res.status === 'failed') { if (timer) clearInterval(timer); emit('failed', res.progress || '未知错误') }
    } catch {}
  }, 3000)
}

poll()
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>
