<template>
  <div>
    <h2 style="font-size:22px;font-weight:700;margin-bottom:28px;letter-spacing:-0.4px;">文件分析</h2>

    <div class="card">
      <h3 class="card-title">上传文件</h3>
      <FileUploader ref="uploaderRef" @update:file-ids="onFileChange" />
    </div>

    <div class="card">
      <h3 class="card-title">选择模板</h3>
      <TemplateSelector v-model="templateId" />
    </div>

    <div class="card">
      <h3 class="card-title">开始分析</h3>
      <div v-if="!templateId" class="text-sm text-muted">请先选择分析模板</div>
      <div v-else-if="pendingFileCount === 0" class="text-sm text-muted">请先添加文件</div>
      <div v-else>
        <p class="text-sm text-muted mb-4">已添加 {{ pendingFileCount }} 个文件，模板：{{ templateId }}</p>
        <button class="btn btn-primary btn-lg" :disabled="analyzing" @click="startAnalysis">
          <span v-if="analyzing"><span class="spinner"></span></span>
          {{ analyzing ? '分析中' : '开始分析' }}
        </button>
      </div>
    </div>

    <TaskProgress v-if="currentTaskId" :task-id="currentTaskId" @done="onDone" @failed="onFailed" />

    <div v-if="showReport">
      <ReportFrame :task-id="currentTaskId" />
      <div class="feedback-section">
        <h4>对结果不满意？</h4>
        <p class="text-sm text-muted mb-4">描述缺失的内容，AI 会重新分析</p>
        <textarea v-model="feedbackText" class="textarea mb-4" rows="2" placeholder="例如：缺少各科目占比分析"></textarea>
        <div class="flex gap-4">
          <router-link :to="'/report/' + currentTaskId">
            <button class="btn btn-secondary">查看报告</button>
          </router-link>
          <button class="btn btn-primary" :disabled="!feedbackText.trim() || submittingFeedback" @click="sendFeedback">
            {{ submittingFeedback ? '提交中' : '提交反馈，重新分析' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="card mt-8" style="border-left:3px solid #ef4444;">
      <p style="color:#ef4444;font-weight:500;">{{ errorMsg }}</p>
      <button class="btn btn-secondary mt-4 btn-sm" @click="reset">重新开始</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUploader from '../components/FileUploader.vue'
import TemplateSelector from '../components/TemplateSelector.vue'
import TaskProgress from '../components/TaskProgress.vue'
import ReportFrame from '../components/ReportFrame.vue'
import { runAnalysis, submitFeedback } from '../api'

const uploaderRef = ref<InstanceType<typeof FileUploader>>()
const fileIds = ref<string[]>([])
const pendingFileCount = ref(0)
const templateId = ref('')
const currentTaskId = ref('')
const analyzing = ref(false)
const showReport = ref(false)
const errorMsg = ref('')
const feedbackText = ref('')
const submittingFeedback = ref(false)

function onFileChange(ids: string[]) {
  fileIds.value = ids
  if (uploaderRef.value) pendingFileCount.value = uploaderRef.value.fileCount
}

async function startAnalysis() {
  if (!uploaderRef.value) return
  analyzing.value = true; errorMsg.value = ''; showReport.value = false
  try {
    await uploaderRef.value.uploadAll()
    const res = await runAnalysis(fileIds.value, templateId.value) as { task_id: string }
    currentTaskId.value = res.task_id
  } catch (e: unknown) { errorMsg.value = e instanceof Error ? e.message : '启动失败'; analyzing.value = false }
}

function onDone(taskId: string) { analyzing.value = false; showReport.value = true; currentTaskId.value = taskId }
function onFailed(err: string) { analyzing.value = false; errorMsg.value = err }

async function sendFeedback() {
  if (!feedbackText.value.trim() || !currentTaskId.value) return
  submittingFeedback.value = true
  try {
    const res = await submitFeedback(currentTaskId.value, 'partial', [], feedbackText.value) as { task_id: string }
    currentTaskId.value = res.task_id; showReport.value = false; feedbackText.value = ''; analyzing.value = true
  } catch { alert('提交失败') }
  submittingFeedback.value = false
}

function reset() { currentTaskId.value = ''; analyzing.value = false; showReport.value = false; errorMsg.value = ''; feedbackText.value = '' }
</script>
