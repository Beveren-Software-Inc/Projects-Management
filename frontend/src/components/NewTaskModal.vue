<template>
  <Dialog
    :model-value="show"
    @update:model-value="$emit('close')"
    title="Create New Task"
    size="lg"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4 pt-1">
      <TextInput
        v-model="form.subject"
        label="Subject *"
        placeholder="e.g. Chart of Accounts Configuration"
        size="sm"
        required
      />

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Select
          v-model="form.project"
          label="Project *"
          placeholder="Select Project"
          :options="projectOptions"
          size="sm"
          required
        />
        <Select
          v-model="form.implementation_module"
          label="Implementation Module"
          placeholder="Select Module"
          :options="moduleOptions"
          size="sm"
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Select
          v-model="form.priority"
          label="Priority"
          :options="[
            { label: 'Low', value: 'Low' },
            { label: 'Medium', value: 'Medium' },
            { label: 'High', value: 'High' },
            { label: 'Urgent', value: 'Urgent' },
          ]"
          size="sm"
        />
        <TextInput
          v-model="form.exp_start_date"
          type="date"
          label="Start Date"
          size="sm"
          @change="onStartDateChange"
        />
        <TextInput
          v-model="form.exp_end_date"
          type="date"
          label="Due Date"
          size="sm"
        />
      </div>

      <Select
        v-model="selectedAssignee"
        label="Assign User"
        placeholder="Unassigned"
        :options="assigneeOptions"
        size="sm"
      />

      <div class="space-y-1">
        <label class="block text-xs font-medium text-ink-gray-7">Description / Checklist</label>
        <Textarea
          v-model="form.description"
          rows="3"
          placeholder="Detailed instructions or acceptance criteria..."
          size="sm"
        />
      </div>

      <div class="flex items-center gap-6 pt-1">
        <Checkbox
          v-model="form.is_milestone"
          label="Mark as Key Milestone"
        />
        <Checkbox
          v-model="form.client_visible"
          label="Visible to Client"
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
          :loading="loading"
          label="Create Task"
          @click="handleSubmit"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Dialog,
  Button,
  TextInput,
  Textarea,
  Select,
  Checkbox,
  toast,
} from 'frappe-ui'
import { createTask, getProjects, getImplementationModules, getUsers } from '../api'

const props = defineProps({
  show: Boolean,
  initialProject: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['close', 'created'])

const loading = ref(false)
const projects = ref([])
const modules = ref([])
const users = ref([])
const selectedAssignee = ref('')

const todayDate = new Date().toISOString().split('T')[0]
const nextWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

const form = ref({
  subject: '',
  project: props.initialProject || '',
  implementation_module: '',
  priority: 'Medium',
  exp_start_date: todayDate,
  exp_end_date: nextWeek,
  description: '',
  is_milestone: false,
  client_visible: true,
})

const projectOptions = computed(() => {
  return [
    { label: '-- Select Project --', value: '' },
    ...projects.value.map(p => ({
      label: p.project_name,
      value: p.name,
    })),
  ]
})

const moduleOptions = computed(() => {
  return [
    { label: '-- Select Module --', value: '' },
    ...modules.value.map(m => ({
      label: m.module_name,
      value: m.module_code,
    })),
  ]
})

const assigneeOptions = computed(() => {
  return [
    { label: '-- Unassigned --', value: '' },
    ...users.value.map(u => ({
      label: u.full_name || u.name,
      value: u.name,
    })),
  ]
})

onMounted(async () => {
  try {
    const [pList, mList, uList] = await Promise.all([
      getProjects(),
      getImplementationModules(),
      getUsers(),
    ])
    projects.value = pList || []
    modules.value = mList || []
    users.value = uList || []
    if (props.initialProject) {
      form.value.project = props.initialProject
    }
  } catch (e) {
    console.error(e)
  }
})

function onStartDateChange() {
  if (form.value.exp_start_date && form.value.exp_end_date) {
    if (form.value.exp_end_date < form.value.exp_start_date) {
      form.value.exp_end_date = form.value.exp_start_date
    }
  }
}

async function handleSubmit() {
  if (!form.value.subject || !form.value.project) {
    toast.error('Please enter subject and select a project')
    return
  }

  if (form.value.exp_start_date && form.value.exp_end_date) {
    if (form.value.exp_end_date < form.value.exp_start_date) {
      form.value.exp_end_date = form.value.exp_start_date
    }
  }

  loading.value = true
  try {
    const payload = {
      ...form.value,
      assignees: selectedAssignee.value ? [selectedAssignee.value] : [],
    }
    const res = await createTask(payload)
    toast.success('Task created successfully')
    emit('created', res)
    emit('close')
  } catch (e) {
    toast.error(e.message || 'Error creating task')
  } finally {
    loading.value = false
  }
}
</script>
