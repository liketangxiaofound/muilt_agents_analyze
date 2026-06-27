<template>
  <div>
    <h2 style="font-size:22px;font-weight:700;margin-bottom:28px;letter-spacing:-0.4px;">报告</h2>

    <div v-if="!taskId || taskId === 'latest'" class="card">
      <h3 class="card-title">历史任务</h3>

      <div v-if="tasks.length === 0" class="empty-state">
        <p>暂无分析任务</p>
        <router-link to="/analysis" class="btn btn-primary mt-4">创建分析</router-link>
      </div>

      <table v-else>
        <thead><tr><th>任务</th><th>模板</th><th>状态</th><th>时间</th><th></th></tr></thead>
        <tbody>
          <tr v-for="t in tasks" :key="t.id">
            <td><code style="font-size:12px;">{{ t.id }}</code></td>
            <td>{{ t.template_id || '-' }}</td>
            <td><span class="badge" :class="{
              'badge-success': t.status === 'done',
              'badge-warning': t.status === 'analyzing',
              'badge-danger': t.status === 'failed',
              'badge-info': t.status === 'pending',
            }">{{ t.status }}</span></td>
            <td class="text-xs text-muted">{{ t.created_at }}</td>
            <td>
              <button v-if="t.status === 'done'" class="btn btn-secondary btn-sm" @click="selectTask(t.id)">查看</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="currentTask && currentTask !== 'latest'">
      <div class="mb-4"><router-link to="/report/latest" class="text-sm">&larr; 返回列表</router-link></div>
      <ReportFrame :task-id="currentTask" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ReportFrame from '../components/ReportFrame.vue'
import { getTasks } from '../api'

interface TaskItem { id: string; template_id: string; status: string; created_at: string }
const route = useRoute(); const router = useRouter()
const taskId = ref(route.params.id as string || 'latest')
const currentTask = ref<string | null>(null)
const tasks = ref<TaskItem[]>([])

function selectTask(id: string) { currentTask.value = id; router.replace(`/report/${id}`) }

onMounted(async () => {
  try { const res = await getTasks() as { tasks: TaskItem[] }; tasks.value = res.tasks || [] } catch {}
  if (taskId.value && taskId.value !== 'latest') currentTask.value = taskId.value
})
</script>
