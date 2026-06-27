<template>
  <div>
    <div class="template-grid">
      <div
        v-for="t in templates"
        :key="t.id"
        class="template-card"
        :class="{ selected: t.id === modelValue }"
        @click="$emit('update:modelValue', t.id)"
      >
        <div class="name">{{ t.name }}</div>
        <div class="desc">{{ t.description }}</div>
        <div class="file-types">{{ t.file_types?.join(' · ') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTemplates } from '../api'

interface Template { id: string; name: string; description: string; file_types: string[] }

defineProps<{ modelValue: string }>()
defineEmits<{ 'update:modelValue': [id: string] }>()

const templates = ref<Template[]>([])

onMounted(async () => {
  try { const res = await getTemplates() as { templates: Template[] }; templates.value = res.templates || [] } catch {}
})
</script>
