<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
    <div class="relative w-full max-w-4xl max-h-[92vh] flex flex-col bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Modal Header -->
      <header class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/60">
        <div>
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-blue-50 text-blue-600">
              <Icon name="mail" :size="16" />
            </span>
            <h2 class="text-base font-semibold text-slate-900">Send Customer Communication</h2>
            <span class="px-2 py-0.5 text-[11px] font-medium bg-blue-100/70 text-blue-700 rounded-full">
              {{ project?.project_name || projectName }}
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">
            Auto-generate progress summaries, feedback requests, or kickoff notes and track them in Project Activity.
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

      <!-- Template Selector Bar -->
      <div class="px-6 py-2.5 bg-slate-100/60 border-b border-slate-200/80 flex items-center gap-1.5 overflow-x-auto text-xs">
        <span class="text-slate-500 font-medium text-[11px] uppercase tracking-wider me-2 shrink-0">Template:</span>
        <button
          v-for="t in templates"
          :key="t.id"
          type="button"
          class="px-3 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 shrink-0"
          :class="selectedTemplate === t.id
            ? 'bg-blue-600 text-white shadow-xs'
            : 'bg-white text-slate-700 hover:bg-slate-200/80 border border-slate-200'"
          @click="changeTemplate(t.id)"
        >
          <Icon :name="t.icon" :size="13" />
          {{ t.label }}
        </button>
      </div>

      <!-- Modal Body -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4">
        
        <!-- Loading State for Template Fetch -->
        <div v-if="templateLoading" class="py-12 flex flex-col items-center justify-center text-slate-400 space-y-2">
          <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span class="text-xs">Preparing email content from project tasks and stats...</span>
        </div>

        <template v-else>
          <!-- Email Header Form (Recipients, CC, Subject) -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200/80 text-xs">
            <div class="space-y-1">
              <label class="block font-medium text-slate-700">
                To Recipients <span class="text-slate-400 font-normal">(comma-separated)</span>
              </label>
              <input
                v-model="form.recipients"
                type="text"
                placeholder="customer@example.com"
                class="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            
            <div class="space-y-1">
              <label class="block font-medium text-slate-700">
                CC Recipients <span class="text-slate-400 font-normal">(optional team & leads)</span>
              </label>
              <input
                v-model="form.cc"
                type="text"
                placeholder="pm@beverensoftware.com, partner@beverensoftware.com"
                class="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div class="md:col-span-2 space-y-1">
              <label class="block font-medium text-slate-700">Subject Line</label>
              <input
                v-model="form.subject"
                type="text"
                placeholder="Subject of the email..."
                class="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-medium text-slate-800 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <!-- Content Mode Toggle: Visual Preview vs Edit HTML -->
          <div class="flex items-center justify-between border-b border-slate-200 pb-2">
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="px-3 py-1 text-xs font-medium rounded-md transition"
                :class="viewMode === 'preview'
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-600 hover:bg-slate-100'"
                @click="viewMode = 'preview'"
              >
                <span class="flex items-center gap-1.5">
                  <Icon name="eye" :size="13" /> Visual Email Preview
                </span>
              </button>
              <button
                type="button"
                class="px-3 py-1 text-xs font-medium rounded-md transition"
                :class="viewMode === 'edit'
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-600 hover:bg-slate-100'"
                @click="viewMode = 'edit'"
              >
                <span class="flex items-center gap-1.5">
                  <Icon name="edit-2" :size="13" /> Edit Email HTML / Notes
                </span>
              </button>
            </div>
            <span class="text-[11px] text-slate-400">
              {{ viewMode === 'preview' ? 'Customer inbox view' : 'Customize text or add notes' }}
            </span>
          </div>

          <!-- Visual Email Preview Tab -->
          <div v-show="viewMode === 'preview'" class="border border-slate-200 rounded-xl overflow-hidden bg-slate-50/40 p-4">
            <div
              class="max-w-2xl mx-auto bg-white rounded-lg shadow-sm border border-slate-100 p-6 email-body-preview"
              v-html="form.content"
            />
          </div>

          <!-- Edit HTML Tab -->
          <div v-show="viewMode === 'edit'" class="space-y-2">
            <textarea
              v-model="form.content"
              rows="14"
              class="w-full p-3 font-mono text-xs bg-slate-900 text-emerald-300 rounded-xl border border-slate-700 focus:outline-none focus:border-blue-500"
              placeholder="HTML Email template content..."
            />
          </div>

          <!-- Attachments Selection -->
          <div class="border border-slate-200 rounded-xl p-3.5 bg-slate-50/50 space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5 text-xs font-medium text-slate-700">
                <Icon name="paperclip" :size="14" />
                <span>Attach Project Documents</span>
              </div>
              <span class="text-[11px] text-slate-400">Included as email attachments or direct links</span>
            </div>

            <div v-if="projectDocs.length" class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              <label
                v-for="doc in projectDocs"
                :key="doc.id"
                class="flex items-center gap-2 p-2 bg-white rounded-lg border border-slate-200 hover:border-slate-300 cursor-pointer text-xs"
              >
                <input
                  type="checkbox"
                  :value="doc.file_url || doc.url"
                  v-model="form.selectedAttachments"
                  class="rounded text-blue-600 focus:ring-blue-500"
                />
                <span class="truncate flex-1 font-medium text-slate-700">{{ doc.title }}</span>
                <span class="text-[10px] text-slate-400 uppercase">{{ doc.category }}</span>
              </label>
            </div>
            <div v-else class="text-xs text-slate-400 italic">
              No scope or governance documents attached to this project yet. Use "Attach Document" on the project files tab to upload scope or discussion notes.
            </div>
          </div>
        </template>
      </div>

      <!-- Modal Footer -->
      <footer class="flex items-center justify-between px-6 py-3.5 border-t border-slate-200 bg-slate-50">
        <div class="text-[11px] text-slate-500 flex items-center gap-1">
          <Icon name="info" :size="12" />
          <span>This email will be logged in Project Activity and preserved in historical snapshots.</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-200/80 rounded-lg transition"
            @click="$emit('close')"
          >
            Cancel
          </button>
          <button
            type="button"
            class="px-5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition flex items-center gap-1.5 disabled:opacity-50"
            :disabled="sending || templateLoading || !form.recipients || !form.subject"
            @click="handleSend"
          >
            <div v-if="sending" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <Icon v-else name="send" :size="13" />
            <span>{{ sending ? 'Sending...' : 'Send to Customer' }}</span>
          </button>
        </div>
      </footer>

    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Icon from './Icon.vue'
import { getProjectEmailTemplate, sendProjectEmail } from '../api'

const props = defineProps({
  project: { type: Object, required: true },
  projectName: { type: String, default: '' },
})

const emit = defineEmits(['close', 'sent'])

const templates = [
  { id: 'weekly_update', label: 'Weekly Update', icon: 'activity' },
  { id: 'monthly_feedback', label: 'Monthly Feedback', icon: 'star' },
  { id: 'kickoff', label: 'Project Kick-off', icon: 'flag' },
  { id: 'sales_handover', label: 'Sales Handover', icon: 'check-square' },
  { id: 'custom', label: 'Custom Note', icon: 'file-text' },
]

const selectedTemplate = ref('weekly_update')
const templateLoading = ref(false)
const sending = ref(false)
const viewMode = ref('preview')

const form = ref({
  recipients: '',
  cc: '',
  subject: '',
  content: '',
  selectedAttachments: [],
})

const projectDocs = computed(() => {
  return props.project?.governance?.documents || []
})

async function fetchTemplate(type) {
  templateLoading.value = true
  try {
    const res = await getProjectEmailTemplate(props.project.name || props.projectName, type)
    if (res) {
      form.value.subject = res.subject || ''
      form.value.content = res.content || ''
      form.value.recipients = (res.recipients || []).join(', ')
      form.value.cc = (res.cc || []).join(', ')
    }
  } catch (err) {
    console.error('Failed to load email template:', err)
    alert('Failed to load template: ' + (err.message || err))
  } finally {
    templateLoading.value = false
  }
}

function changeTemplate(type) {
  selectedTemplate.value = type
  fetchTemplate(type)
}

async function handleSend() {
  const recipientsList = form.value.recipients
    .split(',')
    .map(r => r.trim())
    .filter(Boolean)

  if (!recipientsList.length) {
    alert('Please provide at least one recipient email address.')
    return
  }

  if (!form.value.subject.trim()) {
    alert('Please enter a subject line.')
    return
  }

  const ccList = form.value.cc
    .split(',')
    .map(r => r.trim())
    .filter(Boolean)

  sending.value = true
  try {
    await sendProjectEmail(props.project.name || props.projectName, {
      template_type: selectedTemplate.value,
      subject: form.value.subject,
      content: form.value.content,
      recipients: recipientsList,
      cc: ccList,
      attachments: form.value.selectedAttachments,
    })

    alert('Email successfully sent to customer and logged in project activity!')
    emit('sent')
    emit('close')
  } catch (err) {
    console.error('Failed to send project email:', err)
    alert('Failed to send email: ' + (err.message || err))
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  fetchTemplate(selectedTemplate.value)
})
</script>

<style scoped>
.email-body-preview :deep(table) {
  width: 100%;
}
</style>
