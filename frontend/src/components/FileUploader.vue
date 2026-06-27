<template>
  <div>
    <div
      class="upload-zone"
      :class="{ dragover }"
      @click="triggerInput"
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="handleDrop"
    >
      <p style="font-weight:500;">拖拽文件到此处，或点击选择</p>
      <p class="text-sm text-muted mt-2">支持 Excel、CSV、Word、PDF</p>
      <input ref="inputRef" type="file" multiple :accept="accept" style="display:none" @change="handleChange" />
    </div>

    <div v-if="files.length > 0" class="file-list">
      <div v-for="(f, i) in files" :key="f.name + i" class="file-item">
        <div class="file-item-info">
          <span class="file-icon">{{ fileIcon(f.name) }}</span>
          <div>
            <div>{{ f.name }}</div>
            <div class="text-xs text-muted">{{ formatSize(f.size) }}</div>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <span v-if="f.uploaded" class="badge badge-success">已上传</span>
          <span v-else-if="f.uploading"><span class="spinner"></span></span>
          <button class="btn btn-secondary btn-sm" @click="removeFile(i)">移除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { uploadFile } from '../api'

interface FileItem {
  name: string; size: number; type?: string; file: File
  uploading: boolean; uploaded: boolean; file_id?: string
}

const props = defineProps<{ accept?: string }>()
const emit = defineEmits<{ 'update:fileIds': [ids: string[]] }>()

const inputRef = ref<HTMLInputElement>()
const dragover = ref(false)
const files = ref<FileItem[]>([])

const fileIds = computed(() => files.value.filter(f => f.uploaded && f.file_id).map(f => f.file_id!))
const fileCount = computed(() => files.value.length)

function triggerInput() { inputRef.value?.click() }

function fileIcon(name: string) {
  const ext = name.split('.').pop()?.toLowerCase()
  const map: Record<string, string> = { xlsx: '▦', xls: '▦', csv: '▤', docx: '▯', pdf: '▭' }
  return map[ext || ''] || '▯'
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function addFiles(fileList: FileList | File[]) {
  for (const file of Array.from(fileList)) {
    files.value.push({ name: file.name, size: file.size,
      type: file.type || file.name.split('.').pop() || '', file,
      uploading: false, uploaded: false })
  }
  emit('update:fileIds', fileIds.value)
}

function removeFile(index: number) { files.value.splice(index, 1); emit('update:fileIds', fileIds.value) }
function handleDrop(e: DragEvent) { dragover.value = false; if (e.dataTransfer?.files) addFiles(e.dataTransfer.files) }
function handleChange(e: Event) { const el = e.target as HTMLInputElement; if (el.files) addFiles(el.files) }

async function uploadAll() {
  for (const f of files.value) {
    if (f.uploaded) continue
    f.uploading = true
    try { const res = await uploadFile(f.file); f.file_id = res.file_id; f.uploaded = true } catch {}
    f.uploading = false
  }
  emit('update:fileIds', fileIds.value)
}

defineExpose({ uploadAll, fileIds, fileCount })
</script>
