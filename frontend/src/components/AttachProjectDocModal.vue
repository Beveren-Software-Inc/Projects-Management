<template>
  <Dialog
    :model-value="true"
    @update:model-value="$emit('close')"
    title="Attach Governance Document"
    size="xl"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-surface-green-2 text-ink-green-7 flex items-center justify-center shrink-0">
          <Icon name="file-text" :size="16" />
        </div>
        <div>
          <h2 class="text-base font-semibold text-ink-gray-9">Attach Governance Document</h2>
          <p class="text-xs text-ink-gray-5 mt-0.5">
            Attach official Scope docs, Discussion notes/MoM, or governed Google Drive links to {{ projectName }}.
          </p>
        </div>
      </div>
    </template>

    <form class="space-y-4 pt-1" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Select
          v-model="form.category"
          label="Document Category *"
          :options="[
            { label: 'Scope Document', value: 'Scope Document' },
            { label: 'Discussion Notes & MoM', value: 'Discussion Notes & MoM' },
            { label: 'Architecture / Design', value: 'Architecture / Design' },
            { label: 'Commercial / SOW', value: 'Commercial / SOW' },
            { label: 'Governed Google Drive Link', value: 'Governed Drive Link' },
          ]"
          size="sm"
          required
        />

        <div class="space-y-1.5">
          <label class="block text-xs font-medium text-ink-gray-7">Attachment Method</label>
          <TabButtons
            :buttons="[
              { label: 'File Upload', value: 'file' },
              { label: 'Drive / URL Link', value: 'link' },
            ]"
            v-model="docType"
          />
        </div>
      </div>

      <TextInput
        v-model="form.title"
        label="Document Title *"
        placeholder="e.g. Solution Blueprint & Scope v2.1 or Kick-off MoM"
        size="sm"
        required
      />

      <!-- File Upload Section -->
      <div v-if="docType === 'file'" class="space-y-1">
        <label class="block text-xs font-medium text-ink-gray-7">Choose File *</label>
        <div
          class="border-2 border-dashed rounded-xl p-4 text-center transition cursor-pointer"
          :class="selectedFile ? 'border-outline-green-3 bg-surface-green-2/30' : 'border-outline-gray-3 hover:border-outline-gray-4 bg-surface-gray-1'"
          @click="$refs.fileInput.click()"
        >
          <input
            ref="fileInput"
            type="file"
            class="hidden"
            @change="handleFileChange"
          />
          <div v-if="selectedFile" class="flex items-center justify-center gap-2 text-ink-green-7 font-medium text-xs">
            <Icon name="check-circle" :size="16" />
            <span>{{ selectedFile.name }} ({{ formatSize(selectedFile.size) }})</span>
          </div>
          <div v-else class="space-y-1 text-ink-gray-5 text-xs">
            <Icon name="upload-cloud" :size="22" class="mx-auto text-ink-gray-4" />
            <p class="font-medium text-ink-gray-7">Click to upload document</p>
            <p class="text-[11px] text-ink-gray-4">PDF, Word, Excel, Images up to 25MB</p>
          </div>
        </div>
      </div>

      <!-- Link URL Section -->
      <div v-else>
        <TextInput
          v-model="form.url"
          type="url"
          label="Governed Google Drive or External URL *"
          placeholder="https://drive.google.com/... or https://docs.google.com/..."
          size="sm"
          required
        />
      </div>

      <!-- Version, Owner & Classification -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <TextInput
          v-model="form.version"
          label="Version"
          placeholder="e.g. v1.0"
          size="sm"
        />
        <TextInput
          v-model="form.owner"
          label="Document Owner"
          placeholder="e.g. Lead Consultant"
          size="sm"
        />
        <Select
          v-model="form.access_level"
          label="Classification"
          :options="[
            { label: 'Client Shared', value: 'Client Shared' },
            { label: 'Internal Only', value: 'Internal Only' },
            { label: 'Commercial Confidential', value: 'Commercial Confidential' },
          ]"
          size="sm"
        />
      </div>

      <!-- Notes / Description -->
      <div class="space-y-1">
        <label class="block text-xs font-medium text-ink-gray-7">Description / Summary of Scope & Notes</label>
        <Textarea
          v-model="form.notes"
          rows="2"
          placeholder="Brief description of document contents, approval status, or meeting takeaways..."
          size="sm"
        />
      </div>
    </form>

    <template #actions>
      <div class="flex items-center justify-end gap-2 w-full">
        <Button
          variant="subtle"
          size="sm"
          label="Cancel"
          @click="$emit('close')"
        />
        <Button
          theme="gray"
          variant="solid"
          size="sm"
          :loading="saving"
          :disabled="saving || (docType === 'file' && !selectedFile) || (docType === 'link' && !form.url)"
          label="Attach Document"
          @click="handleSubmit"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import {
  Dialog,
  Button,
  TextInput,
  Textarea,
  Select,
  TabButtons,
  toast,
} from 'frappe-ui'
import Icon from './Icon.vue'
import { attachProjectGovernanceDoc, uploadFile } from '../api'

const props = defineProps({
  projectName: { type: String, required: true },
})

const emit = defineEmits(['close', 'attached'])

const docType = ref('file')
const selectedFile = ref(null)
const fileInput = ref(null)
const saving = ref(false)

const form = ref({
  category: 'Scope Document',
  title: '',
  url: '',
  version: 'v1.0',
  owner: '',
  access_level: 'Client Shared',
  notes: '',
})

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    if (!form.value.title) {
      form.value.title = file.name.replace(/\.[^/.]+$/, '')
    }
  }
}

function formatSize(bytes) {
  if (!bytes) return ''
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

async function handleSubmit() {
  if (!form.value.title) {
    toast.error('Please enter a document title')
    return
  }

  saving.value = true
  try {
    let fileUrl = ''
    let fileName = ''
    let fileSize = 0

    if (docType.value === 'file') {
      if (!selectedFile.value) {
        toast.error('Please choose a file to upload.')
        return
      }
      const uploaded = await uploadFile('Project', props.projectName, selectedFile.value)
      fileUrl = uploaded.file_url
      fileName = uploaded.file_name || selectedFile.value.name
      fileSize = uploaded.file_size || selectedFile.value.size
    } else {
      fileUrl = form.value.url
      fileName = form.value.title
    }

    await attachProjectGovernanceDoc(props.projectName, {
      category: form.value.category,
      title: form.value.title,
      file_url: fileUrl,
      file_name: fileName,
      file_size: fileSize,
      url: form.value.url,
      version: form.value.version || 'v1.0',
      owner: form.value.owner,
      access_level: form.value.access_level,
      notes: form.value.notes,
    })

    toast.success('Document successfully attached to project!')
    emit('attached')
    emit('close')
  } catch (err) {
    console.error('Failed to attach document:', err)
    toast.error('Failed to attach document: ' + (err.message || err))
  } finally {
    saving.value = false
  }
}
</script>
