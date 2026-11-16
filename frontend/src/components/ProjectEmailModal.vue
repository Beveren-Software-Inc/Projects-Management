<template>
  <Dialog
    :model-value="true"
    @update:model-value="$emit('close')"
    size="4xl"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-surface-blue-2 text-ink-blue-7 flex items-center justify-center shrink-0">
          <Icon name="mail" :size="16" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base font-semibold text-ink-gray-9">Send Customer Communication</h2>
            <Badge theme="blue" variant="subtle" size="sm" :label="project?.project_name || projectName" />
          </div>
          <p class="text-sm text-ink-gray-5 mt-0.5">
            Auto-generate progress summaries, feedback requests, or kickoff notes and track them in Project Activity.
          </p>
        </div>
      </div>
    </template>

    <div class="space-y-4 pt-1">
      <!-- Template Selector Bar using TabButtons -->
      <div class="flex items-center gap-2 overflow-x-auto pb-1">
        <span class="text-ink-gray-5 font-medium text-xs uppercase tracking-wider shrink-0">Template:</span>
        <TabButtons
          :options="templates.map(t => ({ label: t.label, value: t.id }))"
          v-model="selectedTemplate"
          @update:model-value="fetchTemplate"
        />
      </div>

      <!-- Loading State for Template Fetch -->
      <div v-if="templateLoading" class="py-12 flex flex-col items-center justify-center text-ink-gray-4 space-y-2">
        <LoadingIndicator class="w-6 h-6 text-ink-blue-7" />
        <span class="text-sm">Preparing email content from project tasks and stats...</span>
      </div>

      <template v-else>
        <!-- Email Header Form (Recipients, CC, Subject) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-surface-gray-1 p-3.5 rounded-xl border border-outline-gray-2 text-sm">
          <TextInput
            v-model="form.recipients"
            label="To Recipients * (comma-separated)"
            placeholder="customer@example.com"
            size="sm"
            required
          />
          <TextInput
            v-model="form.cc"
            label="CC Recipients (optional team & leads)"
            placeholder="pm@beverensoftware.com, partner@beverensoftware.com"
            size="sm"
          />
          <div class="md:col-span-2">
            <TextInput
              v-model="form.subject"
              label="Subject Line *"
              placeholder="Subject of the email..."
              size="sm"
              required
            />
          </div>
        </div>

        <!-- Mode Toggle: Visual Preview vs Edit HTML -->
        <div class="flex items-center justify-between border-b border-outline-gray-2 pb-2">
          <TabButtons
            :options="[
              { label: 'Visual Email Preview', value: 'preview' },
              { label: 'Edit Email HTML / Notes', value: 'edit' },
            ]"
            v-model="viewMode"
          />
          <span class="text-xs text-ink-gray-4">
            {{ viewMode === 'preview' ? 'Customer inbox rendering' : 'Customize HTML markup directly' }}
          </span>
        </div>

        <!-- Visual Email Preview Tab -->
        <div v-show="viewMode === 'preview'" class="border border-outline-gray-2 rounded-xl overflow-hidden bg-surface-gray-1 p-4 max-h-[40vh] overflow-y-auto">
          <div
            class="max-w-2xl mx-auto bg-surface-white rounded-lg shadow-xs border border-outline-gray-1 p-6 email-body-preview"
            v-html="form.content"
          />
        </div>

        <!-- Edit HTML Tab -->
        <div v-show="viewMode === 'edit'" class="space-y-1">
          <Textarea
            v-model="form.content"
            rows="12"
            placeholder="HTML Email template content..."
            class="font-mono text-sm"
            size="sm"
          />
        </div>

        <!-- Attachments Selection -->
        <div class="border border-outline-gray-2 rounded-xl p-3.5 bg-surface-gray-1 space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5 text-sm font-medium text-ink-gray-7">
              <Icon name="paperclip" :size="14" />
              <span>Attach Project Documents</span>
            </div>
            <span class="text-xs text-ink-gray-4">Included as email attachments</span>
          </div>

          <div v-if="projectDocs.length" class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
            <label
              v-for="doc in projectDocs"
              :key="doc.id"
              class="flex items-center gap-2 p-2 bg-surface-white rounded-lg border border-outline-gray-2 hover:border-outline-gray-3 cursor-pointer text-sm"
            >
              <input
                type="checkbox"
                :value="doc.file_url || doc.url"
                v-model="form.selectedAttachments"
                class="rounded text-blue-600 focus:ring-blue-500"
              />
              <span class="truncate flex-1 font-medium text-ink-gray-8">{{ doc.title }}</span>
              <Badge theme="gray" variant="subtle" size="sm" :label="doc.category" />
            </label>
          </div>
          <div v-else class="text-sm text-ink-gray-4 italic">
            No scope or governance documents attached yet. Use "Attach Doc" on the project page to add files.
          </div>
        </div>
      </template>
    </div>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div class="text-xs text-ink-gray-5 flex items-center gap-1">
          <Icon name="info" :size="12" />
          <span>Logged in Project Activity and historical snapshots.</span>
        </div>
        <div class="flex items-center gap-2">
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
            :loading="sending"
            :disabled="sending || templateLoading || !form.recipients || !form.subject"
            label="Send to Customer"
            @click="handleSend"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  Dialog,
  Button,
  Badge,
  TextInput,
  Textarea,
  TabButtons,
  LoadingIndicator,
  toast,
} from 'frappe-ui'
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
    toast.error('Failed to load template: ' + (err.message || err))
  } finally {
    templateLoading.value = false
  }
}

async function handleSend() {
  const recipientsList = form.value.recipients
    .split(',')
    .map(r => r.trim())
    .filter(Boolean)

  if (!recipientsList.length) {
    toast.error('Please provide at least one recipient email address.')
    return
  }

  if (!form.value.subject.trim()) {
    toast.error('Please enter a subject line.')
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

    toast.success('Email successfully sent to customer and logged in project activity!')
    emit('sent')
    emit('close')
  } catch (err) {
    console.error('Failed to send project email:', err)
    toast.error('Failed to send email: ' + (err.message || err))
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
