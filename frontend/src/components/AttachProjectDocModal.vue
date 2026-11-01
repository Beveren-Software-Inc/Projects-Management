<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
    <div class="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Modal Header -->
      <header class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
        <div>
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600">
              <Icon name="file-text" :size="16" />
            </span>
            <h2 class="text-base font-semibold text-slate-900">Attach Governance Document</h2>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">
            Attach official Scope docs, Discussion notes/MoM, or governed Google Drive links to {{ projectName }}.
          </p>
        </div>
        <button
          type="button"
          class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
          aria-label="Close"
          @click="$emit('close')"
        >
          <Icon name="x" :size="18" />
        </button>
      </header>

      <!-- Form Body -->
      <form class="p-6 space-y-4 text-xs" @submit.prevent="handleSubmit">
        
        <!-- Category & Mode -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-1">
            <label class="block font-medium text-slate-700">Document Category *</label>
            <select
              v-model="form.category"
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
              required
            >
              <option value="Scope Document">Scope Document</option>
              <option value="Discussion Notes & MoM">Discussion Notes & MoM</option>
              <option value="Architecture / Design">Architecture / Design</option>
              <option value="Commercial / SOW">Commercial / SOW</option>
              <option value="Governed Drive Link">Governed Google Drive Link</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="block font-medium text-slate-700">Attachment Method</label>
            <div class="flex items-center gap-2 pt-0.5">
              <button
                type="button"
                class="flex-1 py-1.5 px-3 rounded-lg border font-medium transition"
                :class="docType === 'file'
                  ? 'bg-emerald-50 border-emerald-500 text-emerald-700'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'"
                @click="docType = 'file'"
              >
                File Upload
              </button>
              <button
                type="button"
                class="flex-1 py-1.5 px-3 rounded-lg border font-medium transition"
                :class="docType === 'link'
                  ? 'bg-emerald-50 border-emerald-500 text-emerald-700'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'"
                @click="docType = 'link'"
              >
                Drive / URL Link
              </button>
            </div>
          </div>
        </div>

        <!-- Document Title -->
        <div class="space-y-1">
          <label class="block font-medium text-slate-700">Document Title *</label>
          <input
            v-model="form.title"
            type="text"
            required
            placeholder="e.g. Solution Blueprint & Scope v2.1 or Kick-off MoM"
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <!-- File Upload Section -->
        <div v-if="docType === 'file'" class="space-y-1">
          <label class="block font-medium text-slate-700">Choose File *</label>
          <div
            class="border-2 border-dashed rounded-xl p-4 text-center transition cursor-pointer"
            :class="selectedFile ? 'border-emerald-500 bg-emerald-50/20' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'"
            @click="$refs.fileInput.click()"
          >
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileChange"
            />
            <div v-if="selectedFile" class="flex items-center justify-center gap-2 text-emerald-700 font-medium">
              <Icon name="check-circle" :size="16" />
              <span>{{ selectedFile.name }} ({{ formatSize(selectedFile.size) }})</span>
            </div>
            <div v-else class="space-y-1 text-slate-500">
              <Icon name="upload-cloud" :size="24" class="mx-auto text-slate-400" />
              <p class="font-medium text-slate-700">Click to upload document</p>
              <p class="text-[11px] text-slate-400">PDF, Word, Excel, Images up to 25MB</p>
            </div>
          </div>
        </div>

        <!-- Link URL Section -->
        <div v-else class="space-y-1">
          <label class="block font-medium text-slate-700">Governed Google Drive or External URL *</label>
          <input
            v-model="form.url"
            type="url"
            required
            placeholder="https://drive.google.com/... or https://docs.google.com/..."
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <!-- Version, Owner & Access -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="space-y-1">
            <label class="block font-medium text-slate-700">Version</label>
            <input
              v-model="form.version"
              type="text"
              placeholder="e.g. v1.0"
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div class="space-y-1">
            <label class="block font-medium text-slate-700">Document Owner</label>
            <input
              v-model="form.owner"
              type="text"
              placeholder="e.g. Lead Consultant"
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div class="space-y-1">
            <label class="block font-medium text-slate-700">Classification</label>
            <select
              v-model="form.access_level"
              class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
            >
              <option value="Client Shared">Client Shared</option>
              <option value="Internal Only">Internal Only</option>
              <option value="Commercial Confidential">Commercial Confidential</option>
            </select>
          </div>
        </div>

        <!-- Notes -->
        <div class="space-y-1">
          <label class="block font-medium text-slate-700">Description / Summary of Scope & Notes</label>
          <textarea
            v-model="form.notes"
            rows="2"
            placeholder="Brief description of the document contents, approval status, or meeting takeaways..."
            class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <!-- Submit Buttons -->
        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
          <button
            type="button"
            class="px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition"
            @click="$emit('close')"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-5 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition flex items-center gap-1.5 disabled:opacity-50"
            :disabled="saving || (docType === 'file' && !selectedFile) || (docType === 'link' && !form.url)"
          >
            <div v-if="saving" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <Icon v-else name="check" :size="13" />
            <span>{{ saving ? 'Attaching...' : 'Attach Document' }}</span>
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
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
  saving.value = true
  try {
    let fileUrl = ''
    let fileName = ''
    let fileSize = 0

    if (docType.value === 'file') {
      if (!selectedFile.value) {
        alert('Please choose a file to upload.')
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

    alert('Document successfully attached to project!')
    emit('attached')
    emit('close')
  } catch (err) {
    console.error('Failed to attach document:', err)
    alert('Failed to attach document: ' + (err.message || err))
  } finally {
    saving.value = false
  }
}
</script>
